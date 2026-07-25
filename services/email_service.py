from __future__ import annotations

import html
import os
import smtplib
from dataclasses import dataclass
from email.message import EmailMessage
from urllib.parse import urlencode


@dataclass(frozen=True)
class DeliveryResult:
    ok: bool
    message: str


def email_is_configured() -> bool:
    return bool(
        os.getenv("SMTP_HOST", "").strip()
        and os.getenv("SMTP_FROM", "").strip()
    )


def _lex_public_url() -> str:
    return os.getenv(
        "LEX_PUBLIC_URL",
        "https://lex.54-94-43-149.sslip.io",
    ).rstrip("/")


def _auth_public_url() -> str:
    return os.getenv(
        "AUTH_PUBLIC_URL",
        f"{_lex_public_url()}/Acesso",
    ).rstrip("/")


def _access_url(**params: str) -> str:
    base_url = f"{_auth_public_url()}/login"
    if not params:
        return base_url
    return f"{base_url}?{urlencode(params)}"


def _reset_url(raw_token: str) -> str:
    return f"{_auth_public_url()}/reset?{urlencode({'token': raw_token})}"


def send_email(to_email: str, subject: str, html_body: str) -> DeliveryResult:
    host = os.getenv("SMTP_HOST", "").strip()
    sender = os.getenv("SMTP_FROM", "").strip()
    if not host or not sender:
        return DeliveryResult(
            False,
            "O envio de e-mail ainda não está configurado.",
        )

    port = int(os.getenv("SMTP_PORT", "587"))
    username = os.getenv("SMTP_USERNAME", "").strip()
    password = os.getenv("SMTP_PASSWORD", "")
    use_tls = os.getenv("SMTP_USE_TLS", "true").lower() in {"1", "true", "yes"}
    use_ssl = os.getenv("SMTP_USE_SSL", "false").lower() in {"1", "true", "yes"}

    message = EmailMessage()
    message["From"] = sender
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(
        "Este e-mail foi enviado pela LEX AI. Abra a versão HTML para ver "
        "todos os detalhes."
    )
    message.add_alternative(html_body, subtype="html")

    try:
        smtp_class = smtplib.SMTP_SSL if use_ssl else smtplib.SMTP
        with smtp_class(host, port, timeout=20) as smtp:
            if use_tls and not use_ssl:
                smtp.starttls()
            if username:
                smtp.login(username, password)
            smtp.send_message(message)
        return DeliveryResult(True, "E-mail enviado.")
    except (OSError, smtplib.SMTPException):
        return DeliveryResult(
            False,
            "Não foi possível enviar o e-mail neste momento.",
        )


def send_approval_email(to_email: str, full_name: str) -> DeliveryResult:
    safe_name = html.escape(full_name)
    login_url = html.escape(_access_url(), quote=True)
    return send_email(
        to_email,
        "Seu acesso à LEX AI e à FISCUS AI foi aprovado",
        f"""
        <div style="font-family:Arial,sans-serif;color:#111827;line-height:1.6">
          <h2 style="color:#0B0F14">Acesso aprovado</h2>
          <p>Olá, {safe_name}.</p>
          <p>
            Seu cadastro integrado foi aprovado pelo administrador.
            A senha definida no cadastro dá acesso à LEX AI e à FISCUS AI.
          </p>
          <p>
            <a href="{login_url}" style="color:#8A6D12;font-weight:700">
              Entrar nas plataformas
            </a>
          </p>
          <p style="font-size:13px;color:#6B7280">
            A LEX AI nunca envia ou solicita sua senha por e-mail.
          </p>
        </div>
        """,
    )


def send_rejection_email(to_email: str, full_name: str) -> DeliveryResult:
    safe_name = html.escape(full_name)
    return send_email(
        to_email,
        "Atualização sobre seu cadastro na LEX AI",
        f"""
        <div style="font-family:Arial,sans-serif;color:#111827;line-height:1.6">
          <h2>Solicitação de acesso</h2>
          <p>Olá, {safe_name}.</p>
          <p>
            Sua solicitação de cadastro não foi aprovada neste momento.
            Caso precise de esclarecimentos, entre em contato com a equipe
            responsável pela LEX AI.
          </p>
        </div>
        """,
    )


def send_reset_email(
    to_email: str,
    full_name: str,
    raw_token: str,
) -> DeliveryResult:
    safe_name = html.escape(full_name)
    reset_url = html.escape(
        _reset_url(raw_token),
        quote=True,
    )
    return send_email(
        to_email,
        "Redefinição de senha da LEX AI",
        f"""
        <div style="font-family:Arial,sans-serif;color:#111827;line-height:1.6">
          <h2>Redefinição de senha</h2>
          <p>Olá, {safe_name}.</p>
          <p>
            O administrador iniciou uma redefinição de senha para sua conta.
            O link abaixo é temporário e pode ser utilizado uma única vez.
          </p>
          <p>
            <a href="{reset_url}" style="color:#8A6D12;font-weight:700">
              Definir uma nova senha
            </a>
          </p>
          <p style="font-size:13px;color:#6B7280">
            Se você não esperava esta mensagem, entre em contato com o
            administrador. Nenhuma senha foi enviada ou revelada.
          </p>
        </div>
        """,
    )
