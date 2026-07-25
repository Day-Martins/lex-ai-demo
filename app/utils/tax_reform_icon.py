from __future__ import annotations

from html import escape


def tax_reform_calculator_icon(css_class: str = "") -> str:
    """Retorna a estrutura segura do ícone da calculadora tributária."""

    safe_class = escape(css_class, quote=True)
    return (
        f'<div class="tax-reform-calculator-icon {safe_class}" '
        'data-icon="tax-reform-calculator" role="img" '
        'aria-label="Calculadora da Reforma Tributária">'
        '<div class="tax-icon-display"><div>+</div><div>=</div></div>'
        '<div class="tax-icon-key tax-icon-key-one"></div>'
        '<div class="tax-icon-key tax-icon-key-two"></div>'
        '<div class="tax-icon-key tax-icon-key-three"></div>'
        '<div class="tax-icon-key tax-icon-key-four"></div>'
        '<div class="tax-icon-trend">↗</div>'
        "</div>"
    )
