from __future__ import annotations

import unittest
from datetime import datetime, timezone

from auth_gateway.security import (
    create_session_token,
    csrf_matches,
    decode_session_token,
    safe_redirect_url,
    session_matches_password_state,
)


class AuthGatewaySecurityTest(unittest.TestCase):
    SECRET = "segredo-de-teste-com-mais-de-trinta-e-dois-caracteres"

    def test_session_token_is_signed_and_expires(self) -> None:
        password_changed_at = datetime(2026, 7, 25, tzinfo=timezone.utc)
        token = create_session_token(
            user_id=42,
            secret=self.SECRET,
            password_changed_at=password_changed_at,
            now=1_000,
            lifetime_seconds=600,
        )

        identity = decode_session_token(token, secret=self.SECRET, now=1_100)
        self.assertIsNotNone(identity)
        assert identity is not None
        self.assertEqual(identity.user_id, 42)
        self.assertTrue(
            session_matches_password_state(identity, password_changed_at)
        )
        self.assertIsNone(
            decode_session_token(token, secret=self.SECRET, now=1_600)
        )

    def test_tampered_session_token_is_rejected(self) -> None:
        token = create_session_token(
            user_id=7,
            secret=self.SECRET,
            now=2_000,
        )
        payload, signature = token.split(".", 1)
        replacement = "B" if payload[-1] == "A" else "A"
        tampered = f"{payload[:-1]}{replacement}.{signature}"
        self.assertIsNone(
            decode_session_token(tampered, secret=self.SECRET, now=2_100)
        )

    def test_redirect_accepts_only_https_platform_hosts(self) -> None:
        allowed = {
            "lex.example.com",
            "fiscus.example.com",
            "acesso.example.com",
        }
        default = "https://lex.example.com"
        self.assertEqual(
            safe_redirect_url(
                "https://fiscus.example.com/Calculadora_Reforma",
                allowed_hosts=allowed,
                default_url=default,
            ),
            "https://fiscus.example.com/Calculadora_Reforma",
        )
        self.assertEqual(
            safe_redirect_url(
                "https://malicioso.example/roubo",
                allowed_hosts=allowed,
                default_url=default,
            ),
            default,
        )
        self.assertEqual(
            safe_redirect_url(
                "javascript:alert(1)",
                allowed_hosts=allowed,
                default_url=default,
            ),
            default,
        )

    def test_csrf_requires_matching_non_empty_values(self) -> None:
        self.assertTrue(csrf_matches("abc", "abc"))
        self.assertFalse(csrf_matches("abc", "def"))
        self.assertFalse(csrf_matches(None, None))


if __name__ == "__main__":
    unittest.main()
