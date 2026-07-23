from __future__ import annotations

from html import escape

import streamlit as st


def apply_page_style() -> None:
    st.html(
        """
        <style>
        :root {
            --lex-black: #0B0F14;
            --lex-night: #111827;
            --lex-gold: #C9A227;
            --lex-gold-light: #D8B45A;
            --lex-white: #F5F7FA;
            --lex-gray: #9CA3AF;
        }

        [data-testid="stAppViewContainer"] {
            background:
                radial-gradient(
                    circle at top right,
                    rgba(201, 162, 39, 0.08),
                    transparent 30%
                ),
                linear-gradient(180deg, var(--lex-black), var(--lex-night));
        }

        [data-testid="stHeader"] {
            background: var(--lex-black);
            border-bottom: 1px solid rgba(201, 162, 39, 0.18);
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #080D13 0%, #0B1421 100%);
            border-right: 1px solid rgba(201, 162, 39, 0.30);
        }

        [data-testid="stSidebar"] * {
            color: var(--lex-white) !important;
        }

        [data-testid="stSidebarNav"] a {
            border-radius: 9px;
            margin-bottom: 5px;
        }

        [data-testid="stSidebarNav"] a:hover {
            background: rgba(201, 162, 39, 0.10);
        }

        [data-testid="stSidebarNav"] a[aria-current="page"] {
            background: rgba(201, 162, 39, 0.16);
            border-left: 3px solid var(--lex-gold);
        }

        .block-container {
            max-width: 1180px;
            padding-top: 2.5rem;
            padding-bottom: 7rem;
        }

        h1, h2, h3, p, li, label,
        [data-testid="stMarkdownContainer"] {
            color: var(--lex-white);
        }

        [data-testid="stCaptionContainer"] {
            color: var(--lex-gray);
        }

        .lex-page-kicker {
            color: var(--lex-gold-light);
            font-size: 13px;
            font-weight: 900;
            letter-spacing: 0.18em;
            text-transform: uppercase;
            margin-bottom: 9px;
        }

        .lex-page-title {
            color: var(--lex-white);
            font-family: Georgia, serif;
            font-size: clamp(36px, 5vw, 58px);
            font-weight: 800;
            line-height: 1.08;
            margin-bottom: 14px;
        }

        .lex-page-description {
            max-width: 840px;
            color: #C7CDD6;
            font-size: 18px;
            line-height: 1.75;
            margin-bottom: 32px;
        }

        .lex-panel {
            padding: 24px;
            border: 1px solid rgba(201, 162, 39, 0.23);
            border-radius: 18px;
            background:
                linear-gradient(
                    145deg,
                    rgba(17, 24, 39, 0.96),
                    rgba(11, 15, 20, 0.96)
                );
            box-shadow: 0 12px 28px rgba(0, 0, 0, 0.20);
        }

        .lex-feature-card {
            min-height: 205px;
            padding: 23px;
            border: 1px solid rgba(201, 162, 39, 0.19);
            border-radius: 16px;
            background: rgba(255, 255, 255, 0.035);
        }

        .lex-feature-icon {
            color: var(--lex-gold-light);
            font-size: 25px;
            margin-bottom: 15px;
        }

        .lex-feature-title {
            color: var(--lex-white);
            font-size: 18px;
            font-weight: 850;
            margin-bottom: 9px;
        }

        .lex-feature-text {
            color: var(--lex-gray);
            font-size: 14px;
            line-height: 1.65;
        }

        .lex-status {
            display: inline-flex;
            align-items: center;
            width: fit-content;
            padding: 6px 11px;
            border: 1px solid rgba(201, 162, 39, 0.36);
            border-radius: 999px;
            background: rgba(201, 162, 39, 0.08);
            color: var(--lex-gold-light);
            font-size: 11px;
            font-weight: 900;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }

        .lex-note {
            padding: 18px 20px;
            border: 1px solid rgba(201, 162, 39, 0.20);
            border-left: 4px solid var(--lex-gold);
            border-radius: 13px;
            background: rgba(201, 162, 39, 0.055);
            color: #D1D5DB;
            font-size: 14px;
            line-height: 1.65;
        }

        .stButton > button,
        .stLinkButton > a,
        [data-testid="stPageLink"] a {
            border-radius: 10px;
            font-weight: 800;
        }

        div[data-baseweb="input"] > div,
        div[data-baseweb="select"] > div,
        div[data-baseweb="textarea"] > div {
            background: rgba(255, 255, 255, 0.045);
            border-color: rgba(201, 162, 39, 0.24);
        }

        @media (max-width: 760px) {
            .block-container {
                padding-left: 1rem;
                padding-right: 1rem;
            }

            .lex-page-description {
                font-size: 16px;
            }

            .lex-feature-card {
                min-height: auto;
            }
        }
        </style>
        """
    )


def render_page_heading(kicker: str, title: str, description: str) -> None:
    st.html(
        f"""
        <div class="lex-page-kicker">{escape(kicker)}</div>
        <div class="lex-page-title">{escape(title)}</div>
        <div class="lex-page-description">{escape(description)}</div>
        """
    )


def render_feature_card(icon: str, title: str, text: str) -> None:
    st.html(
        f"""
        <div class="lex-feature-card">
            <div class="lex-feature-icon">{escape(icon)}</div>
            <div class="lex-feature-title">{escape(title)}</div>
            <div class="lex-feature-text">{escape(text)}</div>
        </div>
        """
    )
