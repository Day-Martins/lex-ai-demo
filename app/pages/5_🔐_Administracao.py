from __future__ import annotations

from datetime import datetime

import pandas as pd
import streamlit as st

# Página administrativa da navegação principal.
from database.models import UserStatus
from services.access_control_service import (
    approve_user,
    block_user,
    reactivate_user,
    reject_user,
    request_password_reset,
)
from services.auth_service import AuthError
from services.email_service import email_is_configured
from services.user_service import list_users
from utils.footer import render_footer
from utils.page_style import apply_page_style, render_page_heading
from utils.session import prepare_application, require_user


st.set_page_config(
    page_title="Administração | LEX AI",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_page_style()
prepare_application()
admin = require_user(admin=True)


def format_date(value: datetime | None) -> str:
    if value is None:
        return "—"
    return value.strftime("%d/%m/%Y %H:%M")


def show_delivery_result(result, success_message: str) -> None:
    delivery = result.delivery
    if delivery is None or delivery.ok:
        message = success_message
    else:
        message = f"{success_message} {delivery.message}"
    st.session_state["admin_flash"] = (
        "success" if delivery is None or delivery.ok else "warning",
        message,
    )
    st.rerun()


render_page_heading(
    "Gestão de acesso",
    "Administração",
    (
        "Analise novos cadastros, bloqueie ou reative contas e envie links "
        "temporários para redefinição de senha. Nenhuma senha fica visível "
        "para o administrador."
    ),
)

flash = st.session_state.pop("admin_flash", None)
if flash:
    level, message = flash
    getattr(st, level)(message)

users = list_users()
pending = [user for user in users if user.status == UserStatus.PENDING.value]
approved = [user for user in users if user.status == UserStatus.APPROVED.value]
blocked = [user for user in users if user.status == UserStatus.BLOCKED.value]
rejected = [user for user in users if user.status == UserStatus.REJECTED.value]

metric_1, metric_2, metric_3, metric_4 = st.columns(4)
metric_1.metric("Pendentes", len(pending))
metric_2.metric("Ativos", len(approved))
metric_3.metric("Bloqueados", len(blocked))
metric_4.metric("Não aprovados", len(rejected))

st.markdown("## Solicitações pendentes")
if not pending:
    st.info("Não há cadastros aguardando análise.")
else:
    for candidate in pending:
        with st.expander(
            f"{candidate.full_name} · {candidate.username}",
            expanded=True,
        ):
            st.write(f"**E-mail:** {candidate.email}")
            st.write(
                f"**Perfil:** {candidate.professional_role or 'Não informado'}"
            )
            st.write(
                f"**Área de interesse:** {candidate.legal_area or 'Não informada'}"
            )
            st.caption(f"Solicitado em {format_date(candidate.created_at)}")

            approve_col, reject_col = st.columns(2)
            with approve_col:
                if st.button(
                    "Aprovar cadastro",
                    key=f"approve_{candidate.id}",
                    type="primary",
                    use_container_width=True,
                ):
                    try:
                        result = approve_user(admin.id, candidate.id)
                        show_delivery_result(
                            result,
                            "Cadastro aprovado.",
                        )
                    except AuthError as exc:
                        st.error(str(exc))
            with reject_col:
                if st.button(
                    "Não aprovar",
                    key=f"reject_{candidate.id}",
                    use_container_width=True,
                ):
                    try:
                        result = reject_user(admin.id, candidate.id)
                        show_delivery_result(
                            result,
                            "Solicitação marcada como não aprovada.",
                        )
                    except AuthError as exc:
                        st.error(str(exc))

st.markdown("## Gerenciar usuários")
managed_users = [user for user in users if not user.is_admin]
if not managed_users:
    st.info("Ainda não há usuários para gerenciar.")
else:
    labels = {
        user.id: f"{user.full_name} · {user.username} · {user.status}"
        for user in managed_users
    }
    selected_id = st.selectbox(
        "Selecione um usuário",
        options=list(labels),
        format_func=lambda user_id: labels[user_id],
    )
    selected = next(user for user in managed_users if user.id == selected_id)

    detail_1, detail_2 = st.columns(2)
    with detail_1:
        st.write(f"**E-mail:** {selected.email}")
        st.write(f"**Perfil:** {selected.professional_role or 'Não informado'}")
    with detail_2:
        st.write(f"**Status:** {selected.status}")
        st.write(f"**Último acesso:** {format_date(selected.last_login_at)}")

    action_1, action_2, action_3 = st.columns(3)
    with action_1:
        if selected.status == UserStatus.BLOCKED.value:
            if st.button(
                "Reativar acesso",
                key=f"reactivate_{selected.id}",
                use_container_width=True,
            ):
                try:
                    reactivate_user(admin.id, selected.id)
                    st.session_state["admin_flash"] = (
                        "success",
                        "Acesso reativado.",
                    )
                    st.rerun()
                except AuthError as exc:
                    st.error(str(exc))
        else:
            if st.button(
                "Bloquear acesso",
                key=f"block_{selected.id}",
                use_container_width=True,
                disabled=selected.status != UserStatus.APPROVED.value,
            ):
                try:
                    block_user(admin.id, selected.id)
                    st.session_state["admin_flash"] = (
                        "success",
                        "Acesso bloqueado.",
                    )
                    st.rerun()
                except AuthError as exc:
                    st.error(str(exc))

    with action_2:
        if st.button(
            "Enviar redefinição de senha",
            key=f"reset_{selected.id}",
            use_container_width=True,
            disabled=(
                not email_is_configured()
                or selected.status
                not in {
                    UserStatus.APPROVED.value,
                    UserStatus.BLOCKED.value,
                }
            ),
            help=(
                "Envia ao usuário um link temporário. O administrador não "
                "define nem visualiza a nova senha."
            ),
        ):
            try:
                result = request_password_reset(admin.id, selected.id)
                show_delivery_result(
                    result,
                    "Link de redefinição enviado.",
                )
            except AuthError as exc:
                st.error(str(exc))

    with action_3:
        if selected.status in {
            UserStatus.REJECTED.value,
            UserStatus.BLOCKED.value,
        }:
            if st.button(
                "Aprovar acesso",
                key=f"approve_managed_{selected.id}",
                use_container_width=True,
            ):
                try:
                    result = approve_user(admin.id, selected.id)
                    show_delivery_result(result, "Acesso aprovado.")
                except AuthError as exc:
                    st.error(str(exc))

    if not email_is_configured():
        st.warning(
            "O envio de e-mail ainda não está configurado. Aprovações e "
            "bloqueios funcionam, mas a confirmação e o reset por e-mail "
            "dependem da configuração SMTP."
        )

st.markdown("## Visão geral")
table_rows = [
    {
        "Nome": user.full_name,
        "Usuário": user.username,
        "E-mail": user.email,
        "Status": user.status,
        "Administrador": "Sim" if user.is_admin else "Não",
        "Cadastro": format_date(user.created_at),
        "Último acesso": format_date(user.last_login_at),
    }
    for user in users
]
st.dataframe(
    pd.DataFrame(table_rows),
    use_container_width=True,
    hide_index=True,
)

render_footer()
