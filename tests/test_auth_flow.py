from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from database.connection import configure_database, init_database, session_scope
from database.models import User, UserStatus
from services.access_control_service import (
    approve_user,
    block_user,
    reactivate_user,
    request_password_reset,
    reset_password_with_token,
)
from services.auth_service import AuthError, authenticate, hash_password
from services.user_service import RegistrationData, register_user


class AuthFlowTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        database_path = Path(self.temp_dir.name) / "test.db"
        configure_database(f"sqlite:///{database_path}")
        init_database()

        with session_scope() as session:
            admin = User(
                username="dmt",
                email="admin@example.com",
                full_name="DMT Administrador",
                password_hash=hash_password("AdminSeguro123"),
                status=UserStatus.APPROVED.value,
                is_admin=True,
            )
            session.add(admin)
            session.flush()
            self.admin_id = admin.id

    def tearDown(self) -> None:
        configure_database()
        self.temp_dir.cleanup()

    def test_registration_approval_block_and_reset(self) -> None:
        user = register_user(
            RegistrationData(
                username="advogada.teste",
                email="advogada@example.com",
                full_name="Advogada de Teste",
                password="SenhaInicial123",
                professional_role="Advogado(a)",
                legal_area="Direito Tributário",
            )
        )

        pending_login = authenticate("advogada.teste", "SenhaInicial123")
        self.assertFalse(pending_login.ok)
        self.assertIn("aguardando aprovação", pending_login.message)

        approve_user(self.admin_id, user.id, notify=False)
        approved_login = authenticate("advogada@example.com", "SenhaInicial123")
        self.assertTrue(approved_login.ok)

        block_user(self.admin_id, user.id)
        blocked_login = authenticate("advogada.teste", "SenhaInicial123")
        self.assertFalse(blocked_login.ok)
        self.assertIn("bloqueado", blocked_login.message)

        reset = request_password_reset(
            self.admin_id,
            user.id,
            notify=False,
        )
        self.assertIsNotNone(reset.reset_token)
        reset_password_with_token(reset.reset_token or "", "NovaSenhaSegura456")

        old_password = authenticate("advogada.teste", "SenhaInicial123")
        self.assertFalse(old_password.ok)
        with self.assertRaises(AuthError):
            reset_password_with_token(
                reset.reset_token or "",
                "OutraSenhaSegura789",
            )

        reactivate_user(self.admin_id, user.id)
        new_password = authenticate("advogada.teste", "NovaSenhaSegura456")
        self.assertTrue(new_password.ok)

    def test_password_is_never_stored_in_plain_text(self) -> None:
        password = "SenhaNuncaVisivel789"
        user = register_user(
            RegistrationData(
                username="usuario.seguro",
                email="seguro@example.com",
                full_name="Usuário Seguro",
                password=password,
            )
        )
        with session_scope() as session:
            stored = session.get(User, user.id)
            self.assertIsNotNone(stored)
            assert stored is not None
            self.assertNotEqual(stored.password_hash, password)
            self.assertTrue(stored.password_hash.startswith("scrypt$"))


if __name__ == "__main__":
    unittest.main()
