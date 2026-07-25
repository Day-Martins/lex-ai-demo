from __future__ import annotations

import os
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

import bcrypt
from starlette.testclient import TestClient

os.environ["AUTH_COOKIE_DOMAIN"] = ".example.com"
os.environ["AUTH_PUBLIC_URL"] = "https://acesso.example.com"
os.environ["AUTH_SESSION_SECRET"] = (
    "segredo-http-de-teste-com-mais-de-trinta-e-dois-caracteres"
)
os.environ["FISCUS_PUBLIC_URL"] = "https://fiscus.example.com"
os.environ["LEX_PUBLIC_URL"] = "https://lex.example.com"
os.environ["LEGACY_ADMIN_USERNAME"] = "dmt"
os.environ["LEGACY_ADMIN_PASSWORD_HASH"] = bcrypt.hashpw(
    b"SenhaDmtLegada123",
    bcrypt.gensalt(rounds=4),
).decode("utf-8")
os.environ["LEGACY_CLIENT_USERNAME"] = "cliente-teste"
os.environ["LEGACY_CLIENT_PASSWORD_HASH"] = bcrypt.hashpw(
    b"SenhaClienteLegada123",
    bcrypt.gensalt(rounds=4),
).decode("utf-8")

from auth_gateway.app import (  # noqa: E402
    CSRF_COOKIE,
    SESSION_COOKIE,
    _login_attempts,
    app,
)
from database.connection import (  # noqa: E402
    configure_database,
    init_database,
    session_scope,
)
from database.models import User, UserStatus  # noqa: E402
from services.auth_service import change_password, hash_password  # noqa: E402


class AuthGatewayHttpTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        database_path = Path(self.temp_dir.name) / "gateway.db"
        configure_database(f"sqlite:///{database_path}")
        init_database()
        _login_attempts.clear()

        with session_scope() as session:
            session.add(
                User(
                    username="advogada.integrada",
                    email="advogada@example.com",
                    full_name="Advogada Integrada",
                    password_hash=hash_password("SenhaIntegrada123"),
                    status=UserStatus.APPROVED.value,
                    is_admin=False,
                )
            )

        self.client_context = TestClient(
            app,
            base_url="https://acesso.example.com",
        )
        self.client = self.client_context.__enter__()

    def tearDown(self) -> None:
        self.client_context.__exit__(None, None, None)
        configure_database()
        self.temp_dir.cleanup()

    def _csrf(self) -> str:
        response = self.client.get("/login")
        self.assertEqual(response.status_code, 200)
        token = self.client.cookies.get(CSRF_COOKIE)
        self.assertTrue(token)
        return str(token)

    def test_login_follows_existing_lex_visual_identity(self) -> None:
        response = self.client.get("/login")
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "Plataforma de Inteligência Jurídica Especializada",
            response.text,
        )
        self.assertIn("A LEX AI reúne inteligências artificiais", response.text)
        self.assertNotIn("Uma conta.", response.text)
        self.assertNotIn("Duas plataformas.", response.text)

    def test_login_csp_allows_redirects_to_both_platforms(self) -> None:
        response = self.client.get("/login")

        policy = response.headers["content-security-policy"]
        self.assertIn(
            "form-action 'self' https://lex.example.com "
            "https://fiscus.example.com;",
            policy,
        )

    def _login(self) -> None:
        csrf_token = self._csrf()
        response = self.client.post(
            "/login",
            data={
                "csrf_token": csrf_token,
                "identifier": "advogada.integrada",
                "password": "SenhaIntegrada123",
                "next": "https://fiscus.example.com",
            },
            follow_redirects=False,
        )
        self.assertEqual(response.status_code, 303)
        self.assertTrue(self.client.cookies.get(SESSION_COOKIE))

    def test_login_cookie_authorizes_lex_and_fiscus(self) -> None:
        csrf_token = self._csrf()
        response = self.client.post(
            "/login",
            data={
                "csrf_token": csrf_token,
                "identifier": "advogada.integrada",
                "password": "SenhaIntegrada123",
                "next": "https://fiscus.example.com/Calculadora_Reforma",
            },
            follow_redirects=False,
        )

        self.assertEqual(response.status_code, 303)
        self.assertEqual(
            response.headers["location"],
            "https://fiscus.example.com/Calculadora_Reforma",
        )
        self.assertTrue(self.client.cookies.get(SESSION_COOKIE))

        verification = self.client.get(
            "/verify",
            headers={
                "X-Forwarded-Host": "lex.example.com",
                "X-Forwarded-Proto": "https",
                "X-Forwarded-Uri": "/Especialidades",
            },
            follow_redirects=False,
        )
        self.assertEqual(verification.status_code, 204)
        self.assertEqual(
            verification.headers["x-auth-username"],
            "advogada.integrada",
        )
        self.assertEqual(
            verification.headers["x-auth-name"],
            "Advogada Integrada",
        )

    def test_invalid_login_does_not_create_session(self) -> None:
        csrf_token = self._csrf()
        response = self.client.post(
            "/login",
            data={
                "csrf_token": csrf_token,
                "identifier": "advogada.integrada",
                "password": "SenhaIncorreta123",
                "next": "https://lex.example.com",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("senha inválidos", response.text)
        self.assertIsNone(self.client.cookies.get(SESSION_COOKIE))

    def test_existing_dmt_account_accepts_and_migrates_legacy_password(self) -> None:
        with session_scope() as session:
            session.add(
                User(
                    username="dmt",
                    email="dmt@example.com",
                    full_name="DMT Administrador",
                    password_hash=hash_password("OutraSenhaAtual123"),
                    status=UserStatus.APPROVED.value,
                    is_admin=True,
                )
            )

        csrf_token = self._csrf()
        response = self.client.post(
            "/login",
            data={
                "csrf_token": csrf_token,
                "identifier": "dmt",
                "password": "SenhaDmtLegada123",
                "next": "https://lex.example.com",
            },
            follow_redirects=False,
        )
        self.assertEqual(response.status_code, 303)

        with session_scope() as session:
            user = session.query(User).filter_by(username="dmt").one()
            self.assertTrue(user.password_hash.startswith("$2"))
            self.assertTrue(user.is_admin)

    def test_cliente_teste_is_created_from_legacy_access(self) -> None:
        csrf_token = self._csrf()
        response = self.client.post(
            "/login",
            data={
                "csrf_token": csrf_token,
                "identifier": "cliente-teste",
                "password": "SenhaClienteLegada123",
                "next": "https://fiscus.example.com",
            },
            follow_redirects=False,
        )
        self.assertEqual(response.status_code, 303)

        with session_scope() as session:
            user = session.query(User).filter_by(
                username="cliente-teste"
            ).one()
            self.assertEqual(user.status, UserStatus.APPROVED.value)
            self.assertFalse(user.is_admin)

    def test_old_legacy_password_cannot_return_after_password_change(self) -> None:
        csrf_token = self._csrf()
        response = self.client.post(
            "/login",
            data={
                "csrf_token": csrf_token,
                "identifier": "cliente-teste",
                "password": "SenhaClienteLegada123",
                "next": "https://fiscus.example.com",
            },
            follow_redirects=False,
        )
        self.assertEqual(response.status_code, 303)

        with session_scope() as session:
            user = session.query(User).filter_by(
                username="cliente-teste"
            ).one()
            user_id = user.id

        change_password(
            user_id,
            "SenhaClienteLegada123",
            "NovaSenhaCliente456",
        )
        self.client.get("/logout", follow_redirects=False)

        csrf_token = self._csrf()
        rejected = self.client.post(
            "/login",
            data={
                "csrf_token": csrf_token,
                "identifier": "cliente-teste",
                "password": "SenhaClienteLegada123",
                "next": "https://fiscus.example.com",
            },
        )
        self.assertEqual(rejected.status_code, 200)
        self.assertIn("senha inválidos", rejected.text)

    def test_blocked_account_loses_access_to_both_platforms(self) -> None:
        self._login()
        with session_scope() as session:
            user = session.query(User).filter_by(
                username="advogada.integrada"
            ).one()
            user.status = UserStatus.BLOCKED.value

        verification = self.client.get(
            "/verify",
            headers={
                "X-Forwarded-Host": "fiscus.example.com",
                "X-Forwarded-Proto": "https",
                "X-Forwarded-Uri": "/",
            },
            follow_redirects=False,
        )
        self.assertEqual(verification.status_code, 303)
        self.assertIsNone(self.client.cookies.get(SESSION_COOKIE))

    def test_password_change_revokes_existing_shared_session(self) -> None:
        self._login()
        with session_scope() as session:
            user = session.query(User).filter_by(
                username="advogada.integrada"
            ).one()
            user.password_changed_at = datetime.now(timezone.utc)

        verification = self.client.get(
            "/verify",
            headers={
                "X-Forwarded-Host": "lex.example.com",
                "X-Forwarded-Proto": "https",
                "X-Forwarded-Uri": "/",
            },
            follow_redirects=False,
        )
        self.assertEqual(verification.status_code, 303)
        self.assertIsNone(self.client.cookies.get(SESSION_COOKIE))

    def test_unauthenticated_verification_redirects_to_branded_login(self) -> None:
        response = self.client.get(
            "/verify",
            headers={
                "X-Forwarded-Host": "fiscus.example.com",
                "X-Forwarded-Proto": "https",
                "X-Forwarded-Uri": "/Monitor_Legislativo",
            },
            follow_redirects=False,
        )
        self.assertEqual(response.status_code, 303)
        self.assertTrue(
            response.headers["location"].startswith(
                "https://acesso.example.com/login?next="
            )
        )


if __name__ == "__main__":
    unittest.main()
