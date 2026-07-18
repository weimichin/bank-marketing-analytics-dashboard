"""Shared visual theme for the dashboard: professional BI portfolio styling.

Text colors are pinned explicitly (not left to inherit from Streamlit's
auto light/dark theme detection) so contrast stays correct regardless of the
user's OS/browser color-scheme preference. The base theme itself is also
pinned in .streamlit/config.toml.
"""

from __future__ import annotations

import streamlit as st

# ── Color palette ──────────────────────────────────────────────────────────
ACCENT = "#1F5C99"          # Primary blue
ACCENT_TEAL = "#0D9488"     # Accent teal
ACCENT_LIGHT = "#E8F1FA"
ACCENT_DARK = "#0F2D4D"
TEXT_MAIN = "#1E293B"
TEXT_MUTED = "#64748B"
BORDER = "#E2E8F0"
BG_APP = "#F1F5F9"
BG_CARD = "#FFFFFF"
BG_HERO = "linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 100%)"

SHADOW_SM = "0 1px 3px rgba(15, 23, 42, 0.06), 0 1px 2px rgba(15, 23, 42, 0.04)"
SHADOW_MD = "0 4px 16px rgba(15, 23, 42, 0.08), 0 2px 6px rgba(15, 23, 42, 0.04)"

WARNING_BG = "#FFF7ED"
WARNING_BORDER = "#F97316"
WARNING_TEXT = "#9A3412"

# Reserved exclusively for the small-sample "ring" marker on scatter/quadrant charts.
ALERT_RED = "#C0392B"

PLOTLY_COLORWAY = [ACCENT, "#0D9488", "#6FA0C7", "#2E3A46", "#8C97A3"]

# ── Chart styling tokens (Plotly) ─────────────────────────────────────────
FONT_HEADING = "'Source Sans Pro', 'Segoe UI', system-ui, sans-serif"
FONT_BODY_FAMILY = "'Inter', 'Segoe UI', system-ui, sans-serif"
CHART_FONT = FONT_BODY_FAMILY
CHART_NEUTRAL = "#94A3B8"
CHART_GRID = "#EEF1F4"
CHART_BAR_GAP = 0.55
CHART_BAR_GROUP_GAP = 0.14
CHART_BAR_WIDTH = 0.46
CHART_BAR_CORNER_RADIUS = 5
CHART_BAR_VOLUME_COLOR = "#A9C6E0"
CHART_SCATTER_SIZE_MAX = 36
CHART_SCATTER_SIZE_MIN = 10
CHART_REFERENCE_LINE_WIDTH = 1.5
CHART_QUADRANT_COLORS = {
    "Q1: High Conversion + High Contribution": ACCENT,
    "Q2: High Conversion + Low Contribution": ACCENT_TEAL,
    "Q3: Low Conversion + High Contribution": "#6FA0C7",
    "Q4: Low Conversion + Low Contribution": CHART_NEUTRAL,
}
CHART_QUADRANT_LEGEND_LABELS = {
    "Q1: High Conversion + High Contribution": "Q1",
    "Q2: High Conversion + Low Contribution": "Q2",
    "Q3: Low Conversion + High Contribution": "Q3",
    "Q4: Low Conversion + Low Contribution": "Q4",
}
CHART_QUADRANT_COLORS_BY_LEGEND = {
    CHART_QUADRANT_LEGEND_LABELS[key]: color for key, color in CHART_QUADRANT_COLORS.items()
}
CHART_LINE_WIDTH = 2.5
CHART_LINE_WIDTH_PRIMARY = 3
CHART_LINE_MARKER_SIZE = 7
CHART_LINE_MARKER_SIZE_EMPHASIS = 8
CHART_SUBSCRIPTION_LINE_COLOR = WARNING_BORDER
CHART_SUBSCRIPTION_LINE_DASH = "dot"
CHART_MACRO_LINE_COLORS = [ACCENT, ACCENT_TEAL, "#6FA0C7"]
CHART_HEATMAP_COLORSCALE = [
    [0.0, "#B0BEC5"],
    [0.5, "#F8FAFC"],
    [1.0, ACCENT],
]
CHART_HEATMAP_ZMIN = -1
CHART_HEATMAP_ZMAX = 1

# ── Typography scale (each level strictly larger than the next) ────────────
# Page title > Section > Subsection > Segment label > Body > Caption > Meta
FONT_PAGE_TITLE = "2.15rem"
FONT_SECTION = "27px"
FONT_SUBSECTION = "1.28rem"
FONT_SEGMENT = "1.02rem"    # Module segment labels, card titles, insight headers
FONT_BODY = "0.94rem"
FONT_BODY_COMPACT = "0.875rem"  # ~14px at 16px root
FONT_BODY_COMPACT_PX = "14px"
FONT_CARD_TITLE_PX = "15px"
FONT_CAPTION = "0.82rem"
FONT_CAPTION_PX = "13px"
FONT_META = "0.72rem"       # KPI labels, badges, eyebrows — not section headings
FONT_FOOTER_AUTHORS = "11.5px"  # Flaticon author credits — below meta tier
FONT_KPI_VALUE = "1.22rem"
CODE_INLINE_SIZE = "0.9em"
# Back-compat aliases used in CSS rules below
FONT_CARD_TITLE = FONT_SEGMENT
FONT_INSIGHT_LABEL = FONT_SEGMENT

# ── Spacing rhythm (16px base) ─────────────────────────────────────────────
SPACE_BLOCK = "1rem"
SPACE_SEGMENT_TOP = "1.1rem"
SPACE_SEGMENT_LABEL_BOTTOM = "0.55rem"
SPACE_CONTENT_TOP = "0.5rem"  # matches [data-testid="stTabs"] margin-top


def inject_css() -> None:
    st.markdown(
        f"""
        <style>
        /* dashboard-design-v57 — dual-font typography system */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Source+Sans+Pro:wght@400;600;700&display=swap');

        html, body, .stApp {{
            background-color: {BG_APP};
            color: {TEXT_MAIN};
            font-family: {FONT_BODY_FAMILY};
        }}
        .stApp [data-testid="stMain"] p,
        .stApp [data-testid="stMain"] li,
        .stApp [data-testid="stMain"] span:not(.db-kpi-value__num):not([data-testid="stIconMaterial"]):not(.db-footer__label),
        .stApp [data-testid="stMain"] label,
        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] li,
        section[data-testid="stSidebar"] span:not([data-testid="stIconMaterial"]),
        section[data-testid="stSidebar"] label {{
            color: {TEXT_MAIN};
            font-family: {FONT_BODY_FAMILY};
            font-size: {FONT_BODY};
            line-height: 1.6;
        }}

        /* Streamlit chrome — preserve Material icon ligatures (sidebar toggle, toolbar) */
        span[data-testid="stIconMaterial"],
        [data-testid="stExpandSidebarButton"] span,
        [data-testid="stExpandSidebarButton"] p,
        [data-testid="stSidebarCollapseButton"] span,
        [data-testid="stBaseButton-header"] span,
        .stAppToolbar span,
        .stAppToolbar p,
        .stAppHeader button span,
        .stAppHeader button p,
        .material-symbols-rounded,
        .material-icons {{
            font-family: "Material Symbols Rounded" !important;
            font-feature-settings: "liga" !important;
            -webkit-font-feature-settings: "liga" !important;
            font-variation-settings: "FILL" 0, "wght" 400, "GRAD" 0, "opsz" 24 !important;
            -webkit-font-smoothing: antialiased;
            letter-spacing: normal !important;
            text-transform: none !important;
            line-height: 1 !important;
            font-style: normal !important;
            font-weight: 400 !important;
        }}
        span[data-testid="stIconMaterial"] {{
            font-size: 1.5rem !important;
            speak: never;
            display: inline-block;
            white-space: nowrap;
            word-wrap: normal;
            direction: ltr;
        }}

        /* ── Inline code — unified chip style (dataset variables, app-wide) ── */
        [data-testid="stMain"] code,
        [data-testid="stHtml"] code,
        [data-testid="stMarkdownContainer"] code,
        .db-surface-card code,
        .db-card-body code,
        .db-module-card code,
        .db-module-takeaway code {{
            font-family: {FONT_BODY_FAMILY} !important;
            font-size: {CODE_INLINE_SIZE} !important;
            font-weight: 500 !important;
            font-style: normal !important;
            background-color: {ACCENT_LIGHT} !important;
            color: {ACCENT_DARK} !important;
            padding: 0.1em 0.35em !important;
            border-radius: 4px !important;
            border: none !important;
            box-shadow: none !important;
        }}

        /* ── Sidebar ── */
        section[data-testid="stSidebar"] {{
            background-color: {BG_CARD};
            border-right: 1px solid {BORDER};
            box-shadow: 2px 0 12px rgba(15, 23, 42, 0.04);
        }}
        section[data-testid="stSidebar"] * {{
            color: {TEXT_MAIN};
        }}
        section[data-testid="stSidebar"] h2 {{
            font-family: {FONT_HEADING} !important;
            font-size: 1.15rem !important;
            font-weight: 700 !important;
            color: {ACCENT_DARK} !important;
            margin-bottom: 0.15rem !important;
        }}
        .db-sidebar-brand {{
            margin: 0 0 0.15rem;
        }}
        .db-sidebar-brand__row {{
            display: flex;
            align-items: center;
            gap: 0.55rem;
        }}
        .db-sidebar-brand__icon {{
            width: 1.35rem;
            height: 1.35rem;
            flex-shrink: 0;
            object-fit: contain;
        }}
        .db-sidebar-brand__title,
        .db-sidebar-brand__title *,
        section[data-testid="stSidebar"] .db-sidebar-brand__title,
        section[data-testid="stSidebar"] .db-sidebar-brand__title * {{
            font-family: {FONT_HEADING} !important;
            font-size: 1.15rem !important;
            font-weight: 700 !important;
            color: {ACCENT_DARK} !important;
            margin: 0;
            line-height: 1.2;
        }}
        section[data-testid="stSidebar"] h3 {{
            font-family: {FONT_HEADING} !important;
            font-size: {FONT_SEGMENT} !important;
            font-weight: 700 !important;
            text-transform: uppercase !important;
            letter-spacing: 0.06em !important;
            color: {TEXT_MUTED} !important;
            margin-top: 1.25rem !important;
        }}
        section[data-testid="stSidebar"] .stCaption, section[data-testid="stSidebar"] small {{
            color: {TEXT_MUTED} !important;
            font-size: {FONT_CAPTION} !important;
        }}
        section[data-testid="stSidebar"] .stRadio label p {{
            display: inline-flex !important;
            align-items: flex-start !important;
            flex-wrap: wrap !important;
            gap: 0.35rem !important;
            font-family: {FONT_HEADING} !important;
            font-size: 15.5px !important;
            font-weight: 500 !important;
            line-height: 1.35 !important;
            margin: 0 !important;
            padding: 0 !important;
        }}
        section[data-testid="stSidebar"] .stRadio label {{
            align-items: flex-start !important;
        }}
        section[data-testid="stSidebar"] .stRadio label p img {{
            width: 1.15em !important;
            height: 1.15em !important;
            min-width: 1.15em !important;
            margin: 0.05em 0 0 0 !important;
            flex-shrink: 0 !important;
            vertical-align: top !important;
            display: inline-block !important;
            object-fit: contain !important;
        }}

        /* ── Layout & whitespace ── */
        .block-container {{
            padding-top: 2rem;
            padding-bottom: 3rem;
            max-width: 1280px;
        }}
        [data-testid="stVerticalBlock"] {{
            gap: {SPACE_BLOCK};
        }}
        hr {{
            margin: 0.75rem 0 !important;
            border: none !important;
            border-top: 1px solid {BORDER} !important;
            opacity: 1 !important;
        }}
        [data-testid="stMarkdownContainer"]:empty {{
            display: none !important;
            margin: 0 !important;
            padding: 0 !important;
            min-height: 0 !important;
        }}
        [data-testid="stElementContainer"]:has([data-testid="stMarkdownContainer"]:empty) {{
            display: none !important;
            margin: 0 !important;
            padding: 0 !important;
            min-height: 0 !important;
        }}

        /* ── Typography hierarchy ── */
        h1 {{
            font-family: {FONT_HEADING} !important;
            font-size: {FONT_PAGE_TITLE} !important;
            font-weight: 700 !important;
            letter-spacing: -0.02em !important;
            line-height: 1.2 !important;
            color: {ACCENT_DARK} !important;
            margin-bottom: 0.35rem !important;
        }}
        h2, [data-testid="stHeadingWithActionElements"] h2 {{
            font-family: {FONT_HEADING} !important;
            font-size: {FONT_SECTION} !important;
            font-weight: 600 !important;
            color: {ACCENT_DARK} !important;
            margin-top: 1.75rem !important;
            margin-bottom: 0.75rem !important;
            letter-spacing: -0.01em !important;
        }}
        h3, h4, h5 {{
            font-family: {FONT_HEADING} !important;
            color: {ACCENT_DARK};
            font-weight: 600;
        }}
        h3 {{ font-size: {FONT_SUBSECTION} !important; margin-top: 1.25rem !important; }}
        h4 {{ font-size: {FONT_SEGMENT} !important; }}
        h5 {{ font-size: {FONT_SEGMENT} !important; color: {TEXT_MUTED} !important; }}
        [data-testid="stCaptionContainer"] {{
            color: {TEXT_MUTED} !important;
            font-family: {FONT_BODY_FAMILY} !important;
            font-size: {FONT_CAPTION} !important;
            line-height: 1.5 !important;
        }}

        .db-section-heading,
        .db-section-heading *,
        h2.db-section-heading,
        [data-testid="stMarkdownContainer"] h2.db-section-heading,
        [data-testid="stMarkdownContainer"] h2.db-section-heading * {{
            font-family: {FONT_HEADING} !important;
            font-size: {FONT_SECTION} !important;
            font-weight: 600 !important;
            color: {ACCENT_DARK} !important;
            line-height: 1.3 !important;
            margin: 0 !important;
        }}
        .db-section-heading {{
            margin-top: 1.25rem !important;
            margin-bottom: 0.5rem !important;
            padding-bottom: 0.45rem;
            border-bottom: 2px solid {ACCENT_LIGHT};
            letter-spacing: -0.01em;
        }}
        [data-testid="stElementContainer"]:has(.db-section-heading) {{
            margin-top: 0 !important;
            margin-bottom: 0 !important;
        }}
        [data-testid="stHeadingWithActionElements"] {{
            margin: 0 !important;
            padding: 0 !important;
        }}
        .db-subsection-heading,
        .db-subsection-heading *,
        h4.db-subsection-heading,
        [data-testid="stMarkdownContainer"] h4.db-subsection-heading,
        [data-testid="stMarkdownContainer"] h4.db-subsection-heading * {{
            font-family: {FONT_HEADING} !important;
            font-size: {FONT_SUBSECTION} !important;
            font-weight: 600 !important;
            color: {ACCENT_DARK} !important;
            line-height: 1.35 !important;
            margin: 0 !important;
        }}

        /* Level-4 segment labels — heading font; body copy uses Inter below */
        .db-insight-header,
        .db-insight-header__text,
        .db-question-box__label,
        .db-question-box__label-text,
        .db-card-title,
        .db-card .db-card-title,
        .db-section-tag {{
            font-family: {FONT_HEADING} !important;
            font-size: {FONT_SEGMENT} !important;
        }}
        h4.db-card-title,
        [data-testid="stHtml"] h4.db-card-title,
        [data-testid="stMarkdownContainer"] h4.db-card-title {{
            font-size: {FONT_CARD_TITLE_PX} !important;
        }}

        /* ── Hero (Home) ── */
        .db-hero {{
            background: {BG_HERO};
            border: 1px solid {BORDER};
            border-radius: 16px;
            padding: 2.25rem 2.5rem 2rem;
            margin-bottom: 0.5rem;
            box-shadow: {SHADOW_MD};
        }}
        .db-hero__eyebrow {{
            font-family: {FONT_HEADING} !important;
            font-size: {FONT_META};
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            color: {ACCENT_TEAL};
            margin-bottom: 0.6rem;
        }}
        .db-hero__title {{
            font-family: {FONT_HEADING} !important;
            font-size: {FONT_PAGE_TITLE};
            font-weight: 700;
            color: {ACCENT_DARK};
            margin: 0 0 0.5rem;
            line-height: 1.2;
            letter-spacing: -0.02em;
        }}
        .db-hero__subtitle {{
            font-family: {FONT_BODY_FAMILY} !important;
            font-size: 11px;
            font-weight: 400;
            color: {TEXT_MUTED};
            margin: 10px 0;
            line-height: 1.55;
            max-width: 52rem;
        }}
        .db-hero__kpis {{
            margin-top: 1.75rem;
            padding-top: 1.5rem;
            border-top: 1px solid {BORDER};
        }}

        /* ── KPI cards ── */
        .db-kpi-row {{
            display: flex;
            flex-wrap: nowrap;
            gap: 0.875rem;
            align-items: stretch;
            justify-content: space-between;
            width: 100%;
            margin: 0.25rem 0 0.5rem;
        }}
        .db-kpi-card {{
            background-color: {BG_CARD};
            border: 1px solid {BORDER};
            border-radius: 12px;
            padding: 16px 14px;
            width: 100%;
            min-width: 0;
            max-width: 100%;
            min-height: 96px;
            height: 96px;
            box-sizing: border-box;
            box-shadow: {SHADOW_SM};
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            overflow: hidden;
            transition: box-shadow 0.15s ease;
        }}
        .db-kpi-card:hover {{
            box-shadow: {SHADOW_MD};
        }}
        .db-kpi-label {{
            color: {TEXT_MUTED} !important;
            font-family: {FONT_HEADING} !important;
            font-weight: 600;
            font-size: {FONT_META};
            line-height: 1.35;
            margin: 0 0 0.4rem;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            min-height: 2.7em;
            display: flex;
            align-items: center;
            justify-content: center;
            white-space: normal;
            text-align: center;
            max-width: 100%;
        }}
        .db-kpi-value,
        [data-testid="stHtml"] .db-kpi-value,
        [data-testid="stMarkdownContainer"] .db-kpi-value {{
            font-family: {FONT_BODY_FAMILY} !important;
            font-size: {FONT_KPI_VALUE};
            line-height: 1.2;
            letter-spacing: -0.02em;
            max-width: 100%;
            white-space: nowrap;
            text-align: center;
        }}
        .db-kpi-value__num,
        .db-kpi-value .db-kpi-value__num,
        .db-kpi-value span,
        [data-testid="stMarkdownContainer"] .db-kpi-value span {{
            color: {ACCENT} !important;
            font-family: {FONT_BODY_FAMILY} !important;
            font-weight: 700 !important;
            font-size: {FONT_KPI_VALUE} !important;
            line-height: 1.2;
            letter-spacing: -0.02em;
        }}
        [data-testid="column"] .db-kpi-card {{
            width: 100%;
        }}
        [data-testid="stElementContainer"]:has(.db-kpi-card) {{
            margin-bottom: 0 !important;
        }}

        /* ── Surface cards (shared) ── */
        .db-card {{
            background-color: {BG_CARD};
            border: 1px solid {BORDER};
            border-left: 3px solid {ACCENT_TEAL};
            border-radius: 12px;
            padding: 1.25rem 1.5rem;
            margin-bottom: 0;
            height: 100%;
            min-height: 120px;
            box-sizing: border-box;
            box-shadow: {SHADOW_SM};
            word-wrap: break-word;
            overflow-wrap: anywhere;
            display: flex;
            flex-direction: column;
        }}
        .db-card, .db-card div, .db-card span {{
            color: {TEXT_MAIN} !important;
        }}
        .db-card h4,
        .db-card .db-card-title,
        .db-card-title {{
            margin-top: 0;
            margin-bottom: 0.5rem;
            color: {ACCENT_DARK} !important;
            font-family: {FONT_HEADING} !important;
            font-weight: 600;
            line-height: 1.35;
        }}
        .db-card-body,
        [data-testid="stHtml"] .db-card-body {{
            color: {TEXT_MAIN} !important;
            font-family: {FONT_BODY_FAMILY} !important;
            font-size: {FONT_BODY_COMPACT_PX} !important;
            line-height: 1.6;
            margin: 0 0 0.35rem;
            flex: 1;
        }}
        .db-card-body b,
        [data-testid="stHtml"] .db-card-body b {{
            font-size: {FONT_BODY_COMPACT_PX} !important;
        }}
        .db-card--business-question .db-card-body,
        .db-card--business-question .db-card-body span,
        [data-testid="stHtml"] .db-card--business-question .db-card-body,
        [data-testid="stMarkdownContainer"] .db-card--business-question .db-card-body,
        [data-testid="stMarkdownContainer"] .db-card--business-question .db-card-body span {{
            font-size: {FONT_BODY_COMPACT_PX} !important;
            line-height: 1.6 !important;
            color: {TEXT_MAIN} !important;
        }}
        .db-card--dataset-source .db-card-title,
        .db-card--dataset-source .db-card-body,
        .db-card--dataset-source .db-card-body span,
        .db-card--dataset-source h4,
        [data-testid="stHtml"] .db-card--dataset-source .db-card-body,
        [data-testid="stHtml"] .db-card--dataset-source .db-card-title,
        [data-testid="stHtml"] .db-card--dataset-source h4,
        [data-testid="stMarkdownContainer"] .db-card--dataset-source .db-card-body,
        [data-testid="stMarkdownContainer"] .db-card--dataset-source .db-card-title {{
            font-size: {FONT_BODY_COMPACT_PX} !important;
            line-height: 1.55 !important;
            color: {TEXT_MUTED} !important;
        }}
        .db-card--dataset-source .db-card-title,
        .db-card--dataset-source h4,
        [data-testid="stHtml"] .db-card--dataset-source .db-card-title,
        [data-testid="stHtml"] .db-card--dataset-source h4,
        [data-testid="stMarkdownContainer"] .db-card--dataset-source .db-card-title,
        [data-testid="stMarkdownContainer"] .db-card--dataset-source h4 {{
            font-size: {FONT_CARD_TITLE_PX} !important;
            font-weight: 600 !important;
        }}
        .db-surface-card {{
            background-color: {BG_CARD};
            border: 1px solid {BORDER};
            border-radius: 12px;
            padding: 1.25rem 1.5rem;
            box-shadow: {SHADOW_SM};
            color: {TEXT_MAIN} !important;
            font-family: {FONT_BODY_FAMILY} !important;
            font-size: {FONT_BODY};
            line-height: 1.6;
            margin: 0;
            box-sizing: border-box;
            word-wrap: break-word;
            overflow-wrap: anywhere;
        }}
        .db-surface-card--warning {{
            background-color: {WARNING_BG};
            border-color: {WARNING_BORDER};
        }}
        .db-module-header {{
            margin: 0;
            padding: 1.25rem 0 0.85rem;
        }}
        .db-module-header__title,
        .db-module-header__title-text,
        .db-module-header__title-text *,
        [data-testid="stMarkdownContainer"] .db-module-header__title,
        [data-testid="stMarkdownContainer"] .db-module-header__title-text,
        [data-testid="stMarkdownContainer"] .db-module-header__title-text * {{
            font-family: {FONT_HEADING} !important;
            font-size: {FONT_PAGE_TITLE} !important;
            font-weight: 700 !important;
            color: {ACCENT_DARK} !important;
            letter-spacing: 3px;
            line-height: 1.2;
        }}
        .db-module-header__title {{
            margin: 0 0 0.35rem;
            text-align: center;
        }}
        .db-module-header__title-row {{
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.7rem;
            margin: 0 0 0.35rem;
        }}
        .db-module-header__icon {{
            width: 2.4rem;
            height: 2.4rem;
            flex-shrink: 0;
            object-fit: contain;
        }}
        .db-module-header__title-text {{
            margin: 0;
        }}
        .db-module-header__subtitle {{
            font-family: {FONT_BODY_FAMILY} !important;
            font-size: {FONT_BODY};
            font-weight: 500;
            color: {TEXT_MUTED} !important;
            margin: 0;
            line-height: 1.55;
            text-align: center;
        }}
        .db-surface-card ul.db-surface-list {{
            margin: 0;
            padding-left: 1.25rem;
        }}
        .db-surface-card ul.db-surface-list li {{
            margin: 0 0 0.5rem;
            padding: 0;
        }}
        .db-surface-card ul.db-surface-list li:last-child {{
            margin-bottom: 0;
        }}
        .db-surface-card .db-surface-underline {{
            text-decoration: underline;
            text-underline-offset: 0.15em;
        }}
        .db-card-title--spaced {{
            margin-top: 0.25rem;
            margin-bottom: 0.65rem;
        }}
        .db-card-title--warning {{
            color: {WARNING_TEXT} !important;
        }}

        /* ── Insight sections ── */
        .db-insight-block {{
            margin: {SPACE_SEGMENT_TOP} 0 {SPACE_SEGMENT_LABEL_BOTTOM};
        }}
        /* Business Impact / Interpretation Notes: equal gap above & below label */
        .db-insight-block--follows-card {{
            margin-top: {SPACE_SEGMENT_LABEL_BOTTOM} !important;
        }}
        [data-testid="stElementContainer"]:has(.db-insight-block) {{
            margin-top: 0 !important;
            margin-bottom: 0 !important;
            padding: 0 !important;
        }}
        [data-testid="stElementContainer"]:has(.db-surface-card) {{
            margin-bottom: 0 !important;
            padding-bottom: 0 !important;
        }}
        .db-insight-header {{
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.45rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            color: {TEXT_MUTED};
            margin: 0;
        }}
        .db-insight-header--takeaway {{ color: {ACCENT}; }}
        .db-insight-header--impact {{ color: {ACCENT_TEAL}; }}
        .db-insight-header--warning {{ color: {WARNING_BORDER}; }}
        .db-insight-header--evidence {{ color: {ACCENT}; }}
        .db-insight-header--tables {{ color: {ACCENT_TEAL}; }}
        .db-insight-block--tier-section .db-insight-header {{
            font-size: {FONT_SECTION} !important;
            font-weight: 600 !important;
            letter-spacing: -0.01em;
            text-transform: none;
        }}
        .db-insight-header__icon {{
            width: 1.15em;
            height: 1.15em;
            flex-shrink: 0;
            object-fit: contain;
        }}
        .db-insight-block--tier-section .db-insight-header__icon {{
            width: 1.35em;
            height: 1.35em;
        }}
        .db-insight-header__text {{
            margin: 0;
            font-size: inherit !important;
            font-weight: inherit !important;
            color: inherit !important;
            line-height: inherit;
            letter-spacing: inherit;
            text-transform: inherit;
        }}
        .db-insight-block--tier-section .db-insight-header__text {{
            letter-spacing: 2px;
        }}
        .db-insight-block--home-executive .db-insight-header__text {{
            display: inline-block !important;
            border-bottom: 2px solid {ACCENT} !important;
            padding-bottom: 2px !important;
        }}
        .db-insight-block--home-highlights .db-insight-header__icon {{
            display: none !important;
        }}
        .db-insight-block--home-dataset .db-insight-header__icon {{
            display: none !important;
        }}

        /* ── Home Executive Summary rhythm ── */
        [data-testid="stElementContainer"]:has(.db-insight-block--home-objective) + [data-testid="stElementContainer"] [data-testid="stMarkdownContainer"] {{
            background-color: {BG_CARD};
            border: 1px solid {BORDER};
            border-radius: 12px;
            padding: 1.25rem 1.5rem;
            box-shadow: {SHADOW_SM};
            color: {TEXT_MAIN} !important;
            font-size: {FONT_BODY};
            font-family: {FONT_BODY_FAMILY} !important;
            line-height: 1.6;
            margin: 0;
            box-sizing: border-box;
            word-wrap: break-word;
            overflow-wrap: anywhere;
        }}
        /* home-card typography via data-db-font (modifier classes may be stripped in stHtml) */
        [data-db-font="compact"],
        [data-testid="stHtml"] [data-db-font="compact"] {{
            font-family: {FONT_BODY_FAMILY} !important;
            font-size: {FONT_BODY_COMPACT_PX} !important;
            line-height: 1.6 !important;
            color: {TEXT_MAIN} !important;
        }}
        [data-db-font="meta"],
        [data-db-font="meta"] .db-card-body,
        [data-testid="stHtml"] [data-db-font="meta"],
        [data-testid="stHtml"] [data-db-font="meta"] .db-card-body {{
            font-family: {FONT_BODY_FAMILY} !important;
            font-size: {FONT_BODY_COMPACT_PX} !important;
            line-height: 1.55 !important;
            color: {TEXT_MUTED} !important;
        }}
        [data-db-font="meta"] .db-card-title,
        [data-db-font="meta"] h4,
        [data-testid="stHtml"] [data-db-font="meta"] .db-card-title,
        [data-testid="stHtml"] [data-db-font="meta"] h4 {{
            font-family: {FONT_HEADING} !important;
            font-size: {FONT_CARD_TITLE_PX} !important;
            line-height: 1.55 !important;
            color: {TEXT_MUTED} !important;
            font-weight: 600 !important;
        }}
        /* Three Business Questions — 14px body (1–2px below Project Objective) */
        [data-testid="stElementContainer"]:has(.db-insight-block--home-questions) + [data-testid="stElementContainer"] .db-card {{
            border: 1px solid {ACCENT_TEAL} !important;
            border-left: 1px solid {ACCENT_TEAL} !important;
        }}
        [data-testid="stElementContainer"]:has(.db-insight-block--home-questions) + [data-testid="stElementContainer"] [data-db-font="compact"],
        [data-testid="stElementContainer"]:has(.db-insight-block--home-questions) + [data-testid="stElementContainer"] .db-card .db-card-body {{
            font-size: {FONT_BODY_COMPACT_PX} !important;
            line-height: 1.6 !important;
            color: {TEXT_MAIN} !important;
        }}
        /* Dataset Source — muted 14px body / 15px title */
        [data-testid="stElementContainer"]:has(.db-insight-block--home-dataset) + [data-testid="stElementContainer"] [data-db-font="meta"].db-card,
        [data-testid="stHtml"] [data-db-font="meta"].db-card {{
            border-left: 1px solid {BORDER} !important;
        }}
        [data-testid="stElementContainer"]:has(.db-insight-block--home-dataset) + [data-testid="stElementContainer"] [data-db-font="meta"],
        [data-testid="stElementContainer"]:has(.db-insight-block--home-dataset) + [data-testid="stElementContainer"] [data-db-font="meta"] .db-card-body,
        [data-testid="stHtml"] [data-db-font="meta"] .db-card-body {{
            font-size: {FONT_BODY_COMPACT_PX} !important;
            line-height: 1.55 !important;
            color: {TEXT_MUTED} !important;
        }}
        [data-testid="stElementContainer"]:has(.db-insight-block--home-dataset) + [data-testid="stElementContainer"] [data-db-font="meta"] .db-card-title,
        [data-testid="stElementContainer"]:has(.db-insight-block--home-dataset) + [data-testid="stElementContainer"] [data-db-font="meta"] h4,
        [data-testid="stHtml"] [data-db-font="meta"] h4 {{
            font-size: {FONT_CARD_TITLE_PX} !important;
            line-height: 1.55 !important;
            color: {TEXT_MUTED} !important;
        }}
        /* Three Business Questions: remove extra tail below the card row */
        [data-testid="stElementContainer"]:has(.db-insight-block--home-questions) + [data-testid="stElementContainer"] {{
            margin-bottom: 0 !important;
            padding-bottom: 0 !important;
        }}
        [data-testid="stElementContainer"]:has(.db-insight-block--home-questions) + [data-testid="stElementContainer"] [data-testid="stHorizontalBlock"] {{
            margin-bottom: 0 !important;
        }}
        [data-testid="stElementContainer"]:has(.db-insight-block--home-questions) + [data-testid="stElementContainer"] [data-testid="stHtml"],
        [data-testid="stElementContainer"]:has(.db-insight-block--home-questions) + [data-testid="stElementContainer"] [data-testid="stMarkdownContainer"] {{
            margin-bottom: 0 !important;
            padding-bottom: 0 !important;
        }}
        [data-testid="stElementContainer"]:has(.db-insight-block--home-findings) + [data-testid="stElementContainer"]:has([data-testid="stTabs"]) {{
            margin-bottom: 0 !important;
            padding-bottom: 0 !important;
        }}
        /* Business Recommendations — mirror Key Findings: heading margins + 0.5rem body offset */
        [data-testid="stElementContainer"]:has(.db-insight-block--home-recommendations) {{
            margin-top: -{SPACE_SEGMENT_LABEL_BOTTOM} !important;
            margin-bottom: 0 !important;
            padding: 0 !important;
        }}
        .db-insight-block--home-recommendations {{
            margin-top: {SPACE_SEGMENT_TOP} !important;
            margin-bottom: {SPACE_SEGMENT_LABEL_BOTTOM} !important;
        }}
        [data-testid="stElementContainer"]:has(.db-insight-block--home-recommendations) + [data-testid="stElementContainer"] {{
            margin-top: {SPACE_CONTENT_TOP} !important;
            margin-bottom: 0 !important;
            padding-top: 0 !important;
        }}

        /* ── Business question ── */
        .db-question-box {{
            background-color: {BG_CARD};
            border: 1px solid {ACCENT_TEAL};
            border-radius: 12px;
            padding: 1.25rem 1.5rem;
            font-family: {FONT_BODY_FAMILY} !important;
            font-size: {FONT_BODY};
            font-weight: 500;
            margin: 0;
            box-shadow: {SHADOW_SM};
            line-height: 1.55;
        }}
        [data-testid="stElementContainer"]:has(.db-question-box) {{
            margin-top: 0 !important;
            margin-bottom: 0 !important;
        }}
        .db-question-box__label {{
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.45rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            color: {ACCENT_TEAL};
            margin-bottom: 0.45rem;
        }}
        .db-question-box__icon {{
            width: 1.15em;
            height: 1.15em;
            flex-shrink: 0;
            object-fit: contain;
        }}
        .db-question-box__label-text {{
            margin: 0;
            font-size: inherit !important;
            font-weight: inherit !important;
            color: inherit !important;
            line-height: inherit;
            letter-spacing: inherit;
            text-transform: inherit;
        }}
        .db-question-box__text {{
            color: {ACCENT_DARK} !important;
            font-family: {FONT_BODY_FAMILY} !important;
            font-weight: 600;
            margin: 0;
            text-align: center;
        }}
        .db-question-box--body-left .db-question-box__text {{
            text-align: left !important;
        }}

        /* ── Module highlight cards ── */
        .db-module-card {{
            background-color: {BG_CARD};
            border: 1px solid {BORDER};
            border-radius: 14px;
            padding: 1.35rem 1.5rem;
            width: 100%;
            height: 100%;
            min-height: 200px;
            box-sizing: border-box;
            box-shadow: {SHADOW_SM};
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
            word-wrap: break-word;
            overflow-wrap: anywhere;
            transition: box-shadow 0.15s ease;
        }}
        .db-module-card:hover {{
            box-shadow: {SHADOW_MD};
        }}
        .db-module-card, .db-module-card div, .db-module-card span {{
            color: {TEXT_MAIN} !important;
        }}
        .db-module-card .db-tag {{
            display: inline-block;
            background-color: {ACCENT_LIGHT};
            color: {ACCENT_DARK} !important;
            font-family: {FONT_HEADING} !important;
            font-size: {FONT_META};
            font-weight: 700;
            padding: 4px 11px;
            border-radius: 999px;
            letter-spacing: 0.04em;
            text-transform: uppercase;
            align-self: flex-start;
        }}
        .db-module-card .db-module-title {{
            margin: 0;
            color: {ACCENT_DARK} !important;
            font-family: {FONT_HEADING} !important;
            font-size: {FONT_SEGMENT};
            font-weight: 600;
            line-height: 1.35;
        }}
        .db-module-card .db-module-takeaway {{
            margin: 0;
            font-size: {FONT_BODY};
            font-family: {FONT_BODY_FAMILY} !important;
            line-height: 1.6;
            color: {TEXT_MUTED} !important;
            flex: 1;
        }}

        .db-section-tag {{
            display: inline-block;
            background-color: {ACCENT};
            color: white !important;
            font-family: {FONT_HEADING} !important;
            font-weight: 700;
            padding: 4px 12px;
            border-radius: 6px;
            margin-bottom: 6px;
            letter-spacing: 0.04em;
            text-transform: uppercase;
        }}

        .db-note-card {{
            background-color: {WARNING_BG};
            border: 1px solid {WARNING_BORDER};
            border-radius: 12px;
            padding: 1rem 1.25rem;
            box-shadow: {SHADOW_SM};
        }}

        .db-caption {{
            color: {TEXT_MUTED} !important;
            font-family: {FONT_BODY_FAMILY} !important;
            font-size: {FONT_CAPTION};
            line-height: 1.5;
        }}

        .db-footer {{
            margin-top: 1.5rem;
            padding-top: 1.15rem;
            border-top: 1px solid {BORDER};
            font-family: {FONT_BODY_FAMILY} !important;
            font-size: {FONT_CAPTION};
            line-height: 1.6;
        }}
        .db-footer, .db-footer * {{
            font-family: {FONT_BODY_FAMILY} !important;
            color: {TEXT_MUTED} !important;
        }}
        .db-footer a {{
            color: {ACCENT} !important;
        }}
        .db-footer__meta {{
            display: flex;
            flex-direction: column;
            gap: 0.35rem;
            margin: 0;
        }}
        .db-footer__line,
        [data-testid="stMarkdownContainer"] .db-footer__line,
        .stApp .db-footer .db-footer__line {{
            margin: 0;
            font-size: {FONT_BODY_COMPACT_PX} !important;
            line-height: 1.6;
        }}
        [data-testid="stHtml"] .db-footer__label,
        [data-testid="stHtml"] .db-footer__line,
        [data-testid="stHtml"] .db-footer__line span {{
            font-weight: 400 !important;
            font-size: {FONT_BODY_COMPACT_PX} !important;
            color: {TEXT_MUTED} !important;
        }}
        .db-footer-attribution {{
            margin-top: 0.75rem;
            padding-top: 0.65rem;
            border-top: 1px solid {BORDER};
            font-size: {FONT_META};
            line-height: 1.5;
        }}
        [data-testid="stMarkdownContainer"] .db-footer-attribution strong,
        .db-footer .db-footer-attribution strong {{
            font-weight: 400 !important;
        }}
        .db-footer-attribution__authors {{
            margin-top: 0.15rem;
            font-size: {FONT_FOOTER_AUTHORS};
            line-height: 1.5;
        }}
        .db-footer-attribution__authors a {{
            font-size: inherit;
        }}

        /* ── Native Streamlit widgets ── */
        div[data-testid="stMetric"] {{
            background-color: {BG_CARD};
            border: 1px solid {BORDER};
            border-radius: 12px;
            padding: 14px 18px;
            box-shadow: {SHADOW_SM};
        }}
        button[data-baseweb="tab"] {{
            height: auto !important;
            min-height: 2.75rem;
            padding: 0.55rem 1.15rem !important;
            margin: 0 !important;
            border-radius: 8px !important;
            flex: 0 0 auto !important;
            width: auto !important;
            max-width: none !important;
        }}
        button[data-baseweb="tab"] p {{
            font-family: {FONT_HEADING} !important;
            color: {TEXT_MUTED};
            font-weight: 600;
            font-size: 0.9rem;
            white-space: nowrap !important;
            line-height: 1.3;
            margin: 0 !important;
        }}
        button[aria-selected="true"] {{
            background-color: {ACCENT_LIGHT} !important;
        }}
        button[aria-selected="true"] p {{
            color: {ACCENT} !important;
        }}
        div[data-testid="stExpander"] {{
            border: 1px solid {BORDER};
            border-radius: 12px;
            background-color: {BG_CARD};
            box-shadow: {SHADOW_SM};
        }}
        div[data-testid="stExpander"] summary {{
            font-family: {FONT_HEADING} !important;
            color: {TEXT_MAIN};
            font-weight: 600;
            font-size: {FONT_SEGMENT} !important;
        }}
        div[data-testid="stDataFrame"],
        div[data-testid="stDataFrame"] * {{
            font-family: {FONT_BODY_FAMILY} !important;
        }}
        div[data-testid="stDataFrame"] {{
            border: 1px solid {BORDER};
            border-radius: 12px;
            box-shadow: {SHADOW_SM};
            overflow: hidden;
        }}
        .stButton > button {{
            border-radius: 8px;
            font-weight: 600;
            font-size: 0.88rem;
            border-color: {BORDER};
            transition: all 0.15s ease;
        }}
        .stButton > button:hover {{
            border-color: {ACCENT};
            color: {ACCENT};
        }}

        /* ── Evidence / tables section spacing ── */
        [data-testid="stElementContainer"]:has([data-testid="stTabs"]) {{
            margin-bottom: 0 !important;
            padding-bottom: 0 !important;
        }}
        [data-testid="stTabs"] {{
            position: relative;
            z-index: 3;
            margin-top: 0.5rem;
            margin-bottom: 0.65rem !important;
        }}
        [data-testid="stTabs"] [data-baseweb="tab-list"],
        [data-testid="stTabs"] [role="tablist"] {{
            position: relative;
            z-index: 4;
            display: flex !important;
            flex-wrap: wrap !important;
            align-items: stretch !important;
            gap: 0.55rem 0.8rem !important;
            padding: 0.2rem 0 0.65rem 0 !important;
        }}
        [data-testid="stTabs"] [data-baseweb="tab-panel"],
        [data-testid="stTabs"] [role="tabpanel"] {{
            padding-top: 0.65rem !important;
            padding-bottom: 0 !important;
            margin-bottom: 0 !important;
        }}

        /* Module 2 Supporting Tables — balanced two-row tab grid (5 + 4, centered) */
        [data-testid="stElementContainer"]:has(.db-insight-block--m2-supporting-tables)
            + [data-testid="stElementContainer"] [data-baseweb="tab-list"],
        [data-testid="stElementContainer"]:has(.db-insight-block--m2-supporting-tables)
            + [data-testid="stElementContainer"] [role="tablist"] {{
            display: flex !important;
            flex-wrap: wrap !important;
            justify-content: center !important;
            align-items: stretch !important;
            gap: 0.5rem 0.7rem !important;
            padding: 0.2rem 0 0.65rem 0 !important;
        }}
        [data-testid="stElementContainer"]:has(.db-insight-block--m2-supporting-tables)
            + [data-testid="stElementContainer"] button[data-baseweb="tab"] {{
            flex: 0 0 calc(20% - 0.75rem) !important;
            min-width: 6.5rem !important;
            max-width: 9rem !important;
            width: auto !important;
            padding: 0.5rem 0.6rem !important;
        }}
        [data-testid="stElementContainer"]:has(.db-insight-block--m2-supporting-tables)
            + [data-testid="stElementContainer"] button[data-baseweb="tab"] p {{
            white-space: normal !important;
            text-align: center;
            line-height: 1.3;
            font-size: 0.85rem;
        }}
        [data-testid="stTabs"] [data-baseweb="tab-panel"][aria-hidden="true"],
        [data-testid="stTabs"] div[role="tabpanel"][hidden] {{
            display: none !important;
            pointer-events: none !important;
        }}
        [data-testid="stTabs"] [data-baseweb="tab-panel"][aria-hidden="true"] iframe,
        [data-testid="stTabs"] div[role="tabpanel"][hidden] iframe,
        [data-testid="stTabs"] [data-baseweb="tab-panel"][aria-hidden="true"] [data-testid="dashboard-plotly-chart"],
        [data-testid="stTabs"] div[role="tabpanel"][hidden] [data-testid="dashboard-plotly-chart"] {{
            display: none !important;
            visibility: hidden !important;
            height: 0 !important;
            min-height: 0 !important;
            overflow: hidden !important;
            pointer-events: none !important;
        }}
        [data-testid="stHtml"]:has([data-testid="dashboard-plotly-chart"]) {{
            overflow: visible !important;
        }}
        [data-testid="stHtml"] {{
            overflow: hidden;
        }}
        [data-testid="stPlotlyChart"] {{
            margin-top: 0.75rem;
            margin-bottom: 0 !important;
        }}
        div[data-testid="stExpander"] {{
            margin-bottom: 0 !important;
        }}

        /* ── Layout helpers ── */
        div[data-testid="stHorizontalBlock"] {{
            gap: 1rem;
            align-items: stretch;
        }}
        div[data-testid="stHorizontalBlock"]:has(.db-card),
        div[data-testid="stHorizontalBlock"]:has(.db-module-card) {{
            align-items: stretch !important;
        }}
        div[data-testid="stHorizontalBlock"]:has(.db-card) > div[data-testid="column"],
        div[data-testid="stHorizontalBlock"]:has(.db-module-card) > div[data-testid="column"] {{
            min-width: 0;
            display: flex !important;
            flex-direction: column;
            align-self: stretch !important;
        }}
        div[data-testid="stHorizontalBlock"]:has(.db-card) > div[data-testid="column"] > div[data-testid="stVerticalBlock"],
        div[data-testid="stHorizontalBlock"]:has(.db-module-card) > div[data-testid="column"] > div[data-testid="stVerticalBlock"] {{
            flex: 1 1 auto;
            height: 100%;
            display: flex;
            flex-direction: column;
        }}
        div[data-testid="stHorizontalBlock"]:has(.db-card) [data-testid="stElementContainer"],
        div[data-testid="stHorizontalBlock"]:has(.db-module-card) [data-testid="stElementContainer"]:has(.db-module-card) {{
            flex: 1 1 auto;
            display: flex;
            flex-direction: column;
            min-height: 0;
        }}
        div[data-testid="stHorizontalBlock"]:has(.db-card) [data-testid="stHtml"],
        div[data-testid="stHorizontalBlock"]:has(.db-card) [data-testid="stMarkdownContainer"],
        div[data-testid="stHorizontalBlock"]:has(.db-module-card) [data-testid="stHtml"] {{
            flex: 1 1 auto;
            display: flex;
            flex-direction: column;
            height: 100%;
            min-height: 0;
        }}
        div[data-testid="stHorizontalBlock"]:has(.db-card) .db-card,
        div[data-testid="stHorizontalBlock"]:has(.db-module-card) .db-module-card {{
            flex: 1 1 auto;
            height: 100%;
        }}
        div[data-testid="column"] > div[data-testid="stVerticalBlock"] {{
            height: 100%;
        }}
        [data-testid="stAppViewContainer"],
        [data-testid="stMain"],
        section.main,
        .block-container {{
            overflow-x: clip;
        }}
        [data-testid="stVerticalBlockBorderWrapper"] {{
            height: auto !important;
            overflow: visible !important;
        }}
        [data-testid="stMarkdownContainer"] p,
        [data-testid="stMarkdownContainer"] li,
        .stMarkdown p,
        .stMarkdown li {{
            overflow-wrap: anywhere;
            word-break: break-word;
            white-space: normal;
            margin-top: 0;
            margin-bottom: 0.5rem;
        }}
        [data-testid="stMarkdownContainer"] p:last-child,
        [data-testid="stMarkdownContainer"] li:last-child,
        .stMarkdown p:last-child,
        .stMarkdown li:last-child {{
            margin-bottom: 0;
        }}
        [data-testid="stPlotlyChart"] {{
            width: 100% !important;
            max-width: 100%;
        }}
        [data-testid="stImage"] img {{
            max-width: 100%;
            height: auto;
            border-radius: 8px;
        }}

        /* Inline code — final override (beats Streamlit default markdown chips) */
        [data-testid="stAppViewContainer"] [data-testid="stMain"] code,
        [data-testid="stAppViewContainer"] [data-testid="stExpander"] code,
        [data-testid="stAppViewContainer"] [data-testid="stTabs"] code {{
            font-family: {FONT_BODY_FAMILY} !important;
            font-size: {CODE_INLINE_SIZE} !important;
            font-weight: 500 !important;
            font-style: normal !important;
            background-color: {ACCENT_LIGHT} !important;
            color: {ACCENT_DARK} !important;
            padding: 0.1em 0.35em !important;
            border-radius: 4px !important;
            border: none !important;
            box-shadow: none !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def inject_home_card_css() -> None:
    """Home-only card typography overrides (re-applied after importlib.reload in home.render)."""
    st.markdown(
        f"""
        <style>
        /* home-card-typography-v5 */
        [data-testid="stMarkdownContainer"] .db-insight-block--home-executive .db-insight-header__text {{
            display: inline-block !important;
            border-bottom: 2px solid {ACCENT} !important;
            padding-bottom: 2px !important;
        }}
        [data-testid="stMarkdownContainer"] .db-insight-block--home-highlights .db-insight-header__icon {{
            display: none !important;
        }}
        [data-testid="stMarkdownContainer"] .db-insight-block--home-dataset .db-insight-header__icon {{
            display: none !important;
        }}
        [data-db-font="meta"].db-card,
        [data-testid="stHtml"] [data-db-font="meta"].db-card {{
            border-left: 1px solid {BORDER} !important;
        }}
        [data-testid="stHtml"] .db-card--home-question {{
            border: 1px solid {ACCENT_TEAL} !important;
            border-left: 1px solid {ACCENT_TEAL} !important;
        }}
        [data-db-font="compact"],
        [data-testid="stHtml"] [data-db-font="compact"] {{
            font-family: {FONT_BODY_FAMILY} !important;
            font-size: {FONT_BODY_COMPACT_PX} !important;
            line-height: 1.6 !important;
            color: {TEXT_MAIN} !important;
        }}
        [data-db-font="meta"],
        [data-db-font="meta"] .db-card-body,
        [data-testid="stHtml"] [data-db-font="meta"] .db-card-body {{
            font-family: {FONT_BODY_FAMILY} !important;
            font-size: {FONT_BODY_COMPACT_PX} !important;
            line-height: 1.55 !important;
            color: {TEXT_MUTED} !important;
        }}
        [data-db-font="meta"] .db-card-title,
        [data-db-font="meta"] h4,
        [data-testid="stHtml"] [data-db-font="meta"] .db-card-title,
        [data-testid="stHtml"] [data-db-font="meta"] h4 {{
            font-family: {FONT_HEADING} !important;
            font-size: {FONT_CARD_TITLE_PX} !important;
            line-height: 1.55 !important;
            color: {TEXT_MUTED} !important;
            font-weight: 600 !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
