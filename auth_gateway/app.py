from __future__ import annotations

import html
import os
import time
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from pathlib import Path
from urllib.parse import parse_qs, quote

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import FileResponse, HTMLResponse, RedirectResponse, Response
from starlette.routing import Route

from auth_gateway.security import (
    create_session_token,
    csrf_matches,
    decode_session_token,
    new_csrf_token,
    safe_redirect_url,
    session_matches_password_state,
)
from database.connection import init_database
from database.models import User, UserStatus
from services.access_control_service import reset_password_with_token
from services.auth_service import AuthError, authenticate
from services.user_service import (
    RegistrationData,
    bootstrap_admin_from_env,
    get_user,
    register_user,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ASSETS_DIR = PROJECT_ROOT / "assets"
SESSION_COOKIE = "dmt_ai_session"
CSRF_COOKIE = "dmt_ai_csrf"
SESSION_LIFETIME_SECONDS = int(os.getenv("AUTH_SESSION_LIFETIME_SECONDS", "43200"))
LOGIN_WINDOW_SECONDS = 15 * 60
LOGIN_ATTEMPT_LIMIT = 8
_login_attempts: dict[str, deque[float]] = defaultdict(deque)


def _required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"A variável {name} precisa ser configurada.")
    return value


def _session_secret() -> str:
    secret = _required_env("AUTH_SESSION_SECRET")
    if len(secret) < 32:
        raise RuntimeError("AUTH_SESSION_SECRET precisa ter ao menos 32 caracteres.")
    return secret


def _auth_public_url() -> str:
    return _required_env("AUTH_PUBLIC_URL").rstrip("/")


def _lex_public_url() -> str:
    return _required_env("LEX_PUBLIC_URL").rstrip("/")


def _fiscus_public_url() -> str:
    return _required_env("FISCUS_PUBLIC_URL").rstrip("/")


def _allowed_hosts() -> set[str]:
    return {
        host
        for host in (
            _hostname(_auth_public_url()),
            _hostname(_lex_public_url()),
            _hostname(_fiscus_public_url()),
        )
        if host
    }


def _hostname(url: str) -> str:
    from urllib.parse import urlsplit

    return str(urlsplit(url).hostname or "")


def _cookie_domain() -> str | None:
    value = os.getenv("AUTH_COOKIE_DOMAIN", "").strip()
    return value or None


def _redirect_target(value: str | None) -> str:
    return safe_redirect_url(
        value,
        allowed_hosts=_allowed_hosts(),
        default_url=_lex_public_url(),
    )


def _security_headers(response: Response) -> Response:
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "img-src 'self' data:; "
        "style-src 'self' 'unsafe-inline'; "
        "form-action 'self'; "
        "frame-ancestors 'none'; "
        "base-uri 'none'"
    )
    return response


def _set_csrf_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        CSRF_COOKIE,
        token,
        max_age=3600,
        secure=True,
        httponly=True,
        samesite="strict",
        path="/",
    )


def _set_session_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        SESSION_COOKIE,
        token,
        max_age=SESSION_LIFETIME_SECONDS,
        secure=True,
        httponly=True,
        samesite="lax",
        path="/",
        domain=_cookie_domain(),
    )


def _delete_session_cookie(response: Response) -> None:
    response.delete_cookie(
        SESSION_COOKIE,
        path="/",
        domain=_cookie_domain(),
        secure=True,
        httponly=True,
        samesite="lax",
    )


async def _form_data(request: Request) -> dict[str, str]:
    body = (await request.body()).decode("utf-8", errors="replace")
    values = parse_qs(body, keep_blank_values=True)
    return {key: items[-1] if items else "" for key, items in values.items()}


def _csrf_is_valid(request: Request, form: dict[str, str]) -> bool:
    return csrf_matches(
        request.cookies.get(CSRF_COOKIE),
        form.get("csrf_token"),
    )


def _rate_key(request: Request, identifier: str) -> str:
    forwarded = request.headers.get("x-forwarded-for", "")
    address = forwarded.split(",", 1)[0].strip()
    if not address and request.client:
        address = request.client.host
    return f"{address}:{identifier.strip().lower()[:80]}"


def _login_is_rate_limited(key: str) -> bool:
    now = time.monotonic()
    attempts = _login_attempts[key]
    while attempts and now - attempts[0] > LOGIN_WINDOW_SECONDS:
        attempts.popleft()
    return len(attempts) >= LOGIN_ATTEMPT_LIMIT


def _record_login_failure(key: str) -> None:
    _login_attempts[key].append(time.monotonic())


def _clear_login_failures(key: str) -> None:
    _login_attempts.pop(key, None)


def _input(
    label: str,
    name: str,
    *,
    input_type: str = "text",
    value: str = "",
    placeholder: str = "",
    autocomplete: str = "",
    required: bool = True,
) -> str:
    safe_name = html.escape(name, quote=True)
    safe_type = html.escape(input_type, quote=True)
    return f"""
        <label for="{safe_name}">{html.escape(label)}</label>
        <input
            id="{safe_name}"
            name="{safe_name}"
            type="{safe_type}"
            value="{html.escape(value, quote=True)}"
            placeholder="{html.escape(placeholder, quote=True)}"
            autocomplete="{html.escape(autocomplete, quote=True)}"
            {"required" if required else ""}
        >
    """


def _page(
    *,
    title: str,
    eyebrow: str,
    heading: str,
    description: str,
    form_html: str,
    alternate_html: str,
    error: str = "",
    success: str = "",
) -> HTMLResponse:
    alert = ""
    if error:
        alert = f'<div class="alert error">{html.escape(error)}</div>'
    elif success:
        alert = f'<div class="alert success">{html.escape(success)}</div>'

    document = f"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)} | LEX AI</title>
  <link rel="icon" href="/assets/lex-neutro.png" type="image/png">
  <style>
    :root {{
      color-scheme: dark;
      --black: #0b0f14;
      --night: #111827;
      --gold: #c9a227;
      --gold-light: #e2c15d;
      --text: #f5f7fa;
      --muted: #aeb7c4;
      --line: rgba(201, 162, 39, .3);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      min-height: 100vh;
      margin: 0;
      font-family: "Source Sans 3", "Source Sans Pro", -apple-system,
        BlinkMacSystemFont, "Segoe UI", sans-serif;
      color: var(--text);
      background:
        radial-gradient(circle at top right, rgba(201, 162, 39, .08), transparent 28rem),
        linear-gradient(180deg, var(--black), var(--night));
    }}
    .shell {{
      width: min(960px, calc(100% - 32px));
      margin: 0 auto;
      padding: clamp(44px, 8vw, 82px) 0 64px;
    }}
    .institutional {{
      text-align: center;
    }}
    .institutional h1 {{
      margin: 0;
      color: var(--text);
      font-family: Georgia, "Times New Roman", serif;
      font-size: clamp(3.1rem, 8vw, 4.6rem);
      font-weight: 800;
      letter-spacing: clamp(.28rem, 1.2vw, .58rem);
      line-height: 1;
    }}
    .tagline {{
      margin: 42px 0 0;
      color: var(--gold);
      font-size: clamp(.76rem, 2.2vw, 1.02rem);
      font-weight: 900;
      letter-spacing: clamp(.13rem, .55vw, .25rem);
      text-transform: uppercase;
    }}
    .divider {{
      width: min(56%, 560px);
      height: 1px;
      margin: 54px auto 42px;
      background: linear-gradient(90deg, transparent, var(--gold), transparent);
    }}
    .intro {{
      max-width: 900px;
      margin: 0 auto;
      color: var(--muted);
      font-size: clamp(1rem, 2.2vw, 1.18rem);
      line-height: 1.75;
    }}
    .card {{
      width: min(500px, 100%);
      margin: 50px auto 0;
      padding: clamp(26px, 5vw, 40px);
      border: 1px solid var(--line);
      border-top: 3px solid var(--gold);
      border-radius: 18px;
      background: linear-gradient(145deg, rgba(19,29,44,.98), rgba(13,21,33,.98));
      box-shadow: 0 18px 48px rgba(0, 0, 0, .28);
    }}
    .card .eyebrow {{
      color: var(--gold);
      font-size: .75rem;
      font-weight: 900;
      letter-spacing: .18em;
      text-transform: uppercase;
      text-align: center;
    }}
    .card h2 {{
      margin: 10px 0 8px;
      color: var(--text);
      font-size: clamp(1.75rem, 5vw, 2.2rem);
      line-height: 1.15;
      text-align: center;
    }}
    .description {{
      color: var(--muted);
      line-height: 1.55;
      margin: 0 0 22px;
      text-align: center;
    }}
    label {{
      display: block;
      margin: 15px 0 7px;
      color: #dce4ee;
      font-size: .9rem;
      font-weight: 700;
    }}
    input, select {{
      width: 100%;
      border: 1px solid rgba(201, 162, 39, .25);
      border-radius: 11px;
      background: rgba(5, 10, 17, .62);
      color: var(--text);
      padding: 13px 14px;
      font: inherit;
      outline: none;
    }}
    input:focus, select:focus {{
      border-color: var(--gold-light);
      box-shadow: 0 0 0 3px rgba(201, 162, 39, .13);
    }}
    button {{
      width: 100%;
      margin-top: 22px;
      border: 1px solid var(--gold-light);
      border-radius: 11px;
      background: linear-gradient(135deg, #c9a227, #e2c15d);
      color: #07111f;
      padding: 13px 18px;
      font: inherit;
      font-weight: 900;
      cursor: pointer;
    }}
    button:hover {{ filter: brightness(1.06); }}
    .alert {{
      margin: 0 0 18px;
      padding: 12px 14px;
      border-radius: 10px;
      font-size: .92rem;
      line-height: 1.45;
    }}
    .error {{
      color: #ffd5d5;
      border: 1px solid rgba(255, 105, 105, .35);
      background: rgba(160, 38, 38, .18);
    }}
    .success {{
      color: #c9f5d6;
      border: 1px solid rgba(75, 192, 112, .35);
      background: rgba(35, 126, 65, .18);
    }}
    .alternate {{
      margin-top: 22px;
      padding-top: 20px;
      border-top: 1px solid rgba(255,255,255,.09);
      color: var(--muted);
      text-align: center;
      font-size: .92rem;
    }}
    a {{ color: var(--gold-light); font-weight: 750; text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    .privacy {{
      margin-top: 18px;
      color: #8995a5;
      font-size: .78rem;
      line-height: 1.5;
      text-align: center;
    }}
    .hint {{
      margin: 7px 0 0;
      color: #8796aa;
      font-size: .78rem;
      line-height: 1.4;
    }}
    @media (max-width: 480px) {{
      .shell {{ width: min(100% - 22px, 960px); padding-top: 34px; }}
      .tagline {{ margin-top: 30px; line-height: 1.65; }}
      .divider {{ width: 76%; margin: 38px auto 30px; }}
      .card {{ margin-top: 36px; padding: 25px 20px; }}
    }}
  </style>
</head>
<body>
  <main class="shell">
    <section class="institutional">
      <h1>LEX AI</h1>
      <p class="tagline">Plataforma de Inteligência Jurídica Especializada</p>
      <div class="divider"></div>
      <p class="intro">
        A LEX AI reúne inteligências artificiais especializadas em diferentes
        ramos do Direito, com regras, fontes e conhecimentos próprios para uma
        experiência jurídica mais precisa, organizada e segura.
      </p>
    </section>
    <section class="card">
      <div class="eyebrow">{html.escape(eyebrow)}</div>
      <h2>{html.escape(heading)}</h2>
      <p class="description">{html.escape(description)}</p>
      {alert}
      {form_html}
      <div class="alternate">{alternate_html}</div>
      <p class="privacy">
        A mesma conta aprovada também permite acessar a FISCUS AI. Sua senha
        nunca é armazenada em texto legível.
      </p>
    </section>
  </main>
</body>
</html>"""
    return _security_headers(HTMLResponse(document))


def _csrf_form_token(request: Request) -> str:
    return request.cookies.get(CSRF_COOKIE) or new_csrf_token()


async def health(_: Request) -> Response:
    return Response("ok", media_type="text/plain")


async def home(_: Request) -> Response:
    return RedirectResponse("/login", status_code=303)


async def logo(_: Request) -> Response:
    return FileResponse(
        ASSETS_DIR / "lex_neutro.png",
        media_type="image/png",
        headers={"Cache-Control": "public, max-age=86400"},
    )


async def login(request: Request) -> Response:
    error = ""
    submitted_identifier = ""
    next_url = _redirect_target(request.query_params.get("next"))

    if request.method == "POST":
        form = await _form_data(request)
        next_url = _redirect_target(form.get("next"))
        submitted_identifier = form.get("identifier", "")
        if not _csrf_is_valid(request, form):
            error = "A sessão do formulário expirou. Tente novamente."
        else:
            rate_key = _rate_key(request, submitted_identifier)
            if _login_is_rate_limited(rate_key):
                error = (
                    "Muitas tentativas consecutivas. Aguarde alguns minutos "
                    "antes de tentar novamente."
                )
            else:
                result = authenticate(
                    submitted_identifier,
                    form.get("password", ""),
                )
                if result.ok and result.user is not None:
                    _clear_login_failures(rate_key)
                    token = create_session_token(
                        user_id=result.user.id,
                        secret=_session_secret(),
                        password_changed_at=result.user.password_changed_at,
                        lifetime_seconds=SESSION_LIFETIME_SECONDS,
                    )
                    response = RedirectResponse(next_url, status_code=303)
                    _set_session_cookie(response, token)
                    return _security_headers(response)
                _record_login_failure(rate_key)
                error = result.message

    csrf_token = _csrf_form_token(request)
    form_html = f"""
      <form method="post" action="/login">
        <input type="hidden" name="csrf_token" value="{html.escape(csrf_token, quote=True)}">
        <input type="hidden" name="next" value="{html.escape(next_url, quote=True)}">
        {_input("Usuário ou e-mail", "identifier", value=submitted_identifier, placeholder="seu.usuario ou voce@exemplo.com", autocomplete="username")}
        {_input("Senha", "password", input_type="password", autocomplete="current-password")}
        <button type="submit">Entrar nas plataformas</button>
      </form>
    """
    response = _page(
        title="Entrar",
        eyebrow="Acesso integrado",
        heading="Boas-vindas",
        description="Use a conta aprovada na LEX AI para acessar as duas plataformas.",
        form_html=form_html,
        alternate_html=(
            'Ainda não possui conta? '
            f'<a href="/cadastro?next={quote(next_url, safe="")}">Solicitar cadastro</a>'
        ),
        error=error,
    )
    _set_csrf_cookie(response, csrf_token)
    return response


async def registration(request: Request) -> Response:
    error = ""
    success = ""
    next_url = _redirect_target(request.query_params.get("next"))
    values: dict[str, str] = {}

    if request.method == "POST":
        values = await _form_data(request)
        next_url = _redirect_target(values.get("next"))
        if not _csrf_is_valid(request, values):
            error = "A sessão do formulário expirou. Tente novamente."
        elif values.get("password") != values.get("confirmation"):
            error = "As senhas não coincidem."
        elif values.get("accepted") != "yes":
            error = "Confirme que compreende o fluxo de aprovação."
        else:
            try:
                register_user(
                    RegistrationData(
                        username=values.get("username", ""),
                        email=values.get("email", ""),
                        full_name=values.get("full_name", ""),
                        password=values.get("password", ""),
                        professional_role=values.get("professional_role") or None,
                        legal_area=values.get("legal_area") or None,
                    )
                )
                success = (
                    "Cadastro enviado. Assim que o administrador aprovar, "
                    "esta mesma conta dará acesso à LEX AI e à FISCUS AI."
                )
                values = {}
            except AuthError as exc:
                error = str(exc)

    csrf_token = _csrf_form_token(request)
    role_options = (
        "Advogado(a)",
        "Contador(a)",
        "Consultor(a)",
        "Empresário(a)",
        "Estudante",
        "Outro",
    )
    role_markup = "".join(
        (
            f'<option value="{html.escape(option, quote=True)}"'
            f'{" selected" if values.get("professional_role") == option else ""}>'
            f"{html.escape(option)}</option>"
        )
        for option in role_options
    )
    form_html = f"""
      <form method="post" action="/cadastro">
        <input type="hidden" name="csrf_token" value="{html.escape(csrf_token, quote=True)}">
        <input type="hidden" name="next" value="{html.escape(next_url, quote=True)}">
        {_input("Nome completo", "full_name", value=values.get("full_name", ""), autocomplete="name")}
        {_input("E-mail", "email", input_type="email", value=values.get("email", ""), autocomplete="email")}
        {_input("Nome de usuário", "username", value=values.get("username", ""), placeholder="letras minúsculas, números, ponto ou hífen", autocomplete="username")}
        <label for="professional_role">Perfil profissional</label>
        <select id="professional_role" name="professional_role" required>{role_markup}</select>
        {_input("Área de interesse (opcional)", "legal_area", value=values.get("legal_area", ""), placeholder="Ex.: Direito Tributário", required=False)}
        {_input("Crie uma senha", "password", input_type="password", autocomplete="new-password")}
        <p class="hint">Use ao menos 10 caracteres, com letra maiúscula, minúscula e número.</p>
        {_input("Confirme a senha", "confirmation", input_type="password", autocomplete="new-password")}
        <label style="display:flex;gap:9px;align-items:flex-start;font-weight:500">
          <input style="width:auto;margin-top:3px" type="checkbox" name="accepted" value="yes" required>
          Compreendo que o cadastro depende de aprovação administrativa.
        </label>
        <button type="submit">Solicitar cadastro integrado</button>
      </form>
    """
    response = _page(
        title="Solicitar cadastro",
        eyebrow="Conta única",
        heading="Crie seu acesso",
        description=(
            "Após a aprovação, use a mesma conta na LEX AI e na FISCUS AI."
        ),
        form_html=form_html,
        alternate_html=(
            'Já possui uma conta? '
            f'<a href="/login?next={quote(next_url, safe="")}">Entrar</a>'
        ),
        error=error,
        success=success,
    )
    _set_csrf_cookie(response, csrf_token)
    return response


async def reset_password(request: Request) -> Response:
    error = ""
    success = ""
    token = request.query_params.get("token", "")

    if request.method == "POST":
        form = await _form_data(request)
        token = form.get("token", "")
        if not _csrf_is_valid(request, form):
            error = "A sessão do formulário expirou. Tente novamente."
        elif form.get("password") != form.get("confirmation"):
            error = "As senhas não coincidem."
        else:
            try:
                reset_password_with_token(token, form.get("password", ""))
                success = "Senha alterada. Você já pode entrar com a nova senha."
            except AuthError as exc:
                error = str(exc)

    csrf_token = _csrf_form_token(request)
    form_html = f"""
      <form method="post" action="/reset">
        <input type="hidden" name="csrf_token" value="{html.escape(csrf_token, quote=True)}">
        <input type="hidden" name="token" value="{html.escape(token, quote=True)}">
        {_input("Nova senha", "password", input_type="password", autocomplete="new-password")}
        {_input("Confirme a nova senha", "confirmation", input_type="password", autocomplete="new-password")}
        <button type="submit">Salvar nova senha</button>
      </form>
    """
    response = _page(
        title="Redefinir senha",
        eyebrow="Segurança",
        heading="Defina uma nova senha",
        description="O link é temporário e deixa de funcionar depois do primeiro uso.",
        form_html=form_html,
        alternate_html='<a href="/login">Voltar para o login</a>',
        error=error,
        success=success,
    )
    _set_csrf_cookie(response, csrf_token)
    return response


def _session_user(request: Request) -> User | None:
    identity = decode_session_token(
        request.cookies.get(SESSION_COOKIE, ""),
        secret=_session_secret(),
    )
    if identity is None:
        return None

    user = get_user(identity.user_id)
    if (
        user is None
        or user.status != UserStatus.APPROVED.value
        or not session_matches_password_state(identity, user.password_changed_at)
    ):
        return None
    return user


async def verify(request: Request) -> Response:
    user = _session_user(request)
    if user is None:
        proto = request.headers.get("x-forwarded-proto", "https")
        host = request.headers.get("x-forwarded-host", "")
        uri = request.headers.get("x-forwarded-uri", "/")
        target = _redirect_target(f"{proto}://{host}{uri}")
        location = f"{_auth_public_url()}/login?next={quote(target, safe='')}"
        response = RedirectResponse(location, status_code=303)
        _delete_session_cookie(response)
        return _security_headers(response)

    return Response(
        status_code=204,
        headers={
            "X-Auth-User-Id": str(user.id),
            "X-Auth-Username": user.username,
            "X-Auth-Name": user.full_name,
            "X-Auth-Email": user.email,
            "X-Auth-Admin": "true" if user.is_admin else "false",
        },
    )


async def logout(request: Request) -> Response:
    next_url = _redirect_target(request.query_params.get("next"))
    location = f"{_auth_public_url()}/login?next={quote(next_url, safe='')}"
    response = RedirectResponse(location, status_code=303)
    _delete_session_cookie(response)
    return _security_headers(response)


@asynccontextmanager
async def lifespan(_: Starlette):
    init_database()
    bootstrap_admin_from_env()
    yield

app = Starlette(
    debug=False,
    lifespan=lifespan,
    routes=[
        Route("/", home),
        Route("/health", health),
        Route("/assets/lex-neutro.png", logo),
        Route("/favicon.ico", logo),
        Route("/login", login, methods=["GET", "POST"]),
        Route("/cadastro", registration, methods=["GET", "POST"]),
        Route("/reset", reset_password, methods=["GET", "POST"]),
        Route("/verify", verify),
        Route("/logout", logout),
    ],
)
