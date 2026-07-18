"""Reusable UI building blocks shared by every dashboard page.

All components only render data/text that is passed in - they never compute
new statistics. They exist purely to present already-completed analysis
results consistently across Home / Module 1 / Module 2 / Module 3.
"""

from __future__ import annotations

import base64
import html
import re
from pathlib import Path
from typing import Literal

import pandas as pd
import streamlit as st

from dashboard.data.home_content import FLATICON_CREDITS
from dashboard.theme import (
    ACCENT,
    ACCENT_DARK,
    ACCENT_LIGHT,
    ACCENT_TEAL,
    ALERT_RED,
    BG_CARD,
    BORDER,
    CHART_BAR_CORNER_RADIUS,
    CHART_BAR_GAP,
    CHART_BAR_GROUP_GAP,
    CHART_BAR_VOLUME_COLOR,
    CHART_BAR_WIDTH,
    CHART_FONT,
    CHART_GRID,
    CHART_HEATMAP_COLORSCALE,
    CHART_HEATMAP_ZMAX,
    CHART_HEATMAP_ZMIN,
    CHART_NEUTRAL,
    CHART_LINE_MARKER_SIZE,
    CHART_LINE_MARKER_SIZE_EMPHASIS,
    CHART_LINE_WIDTH,
    CHART_LINE_WIDTH_PRIMARY,
    CHART_MACRO_LINE_COLORS,
    CHART_QUADRANT_COLORS,
    CHART_QUADRANT_COLORS_BY_LEGEND,
    CHART_QUADRANT_LEGEND_LABELS,
    CHART_REFERENCE_LINE_WIDTH,
    CHART_SCATTER_SIZE_MAX,
    CHART_SCATTER_SIZE_MIN,
    CHART_SUBSCRIPTION_LINE_COLOR,
    CHART_SUBSCRIPTION_LINE_DASH,
    FONT_BODY,
    FONT_BODY_COMPACT_PX,
    FONT_BODY_FAMILY,
    FONT_CARD_TITLE_PX,
    FONT_HEADING,
    FONT_KPI_VALUE,
    FONT_META,
    FONT_SEGMENT,
    PLOTLY_COLORWAY,
    SHADOW_SM,
    SPACE_SEGMENT_LABEL_BOTTOM,
    SPACE_SEGMENT_TOP,
    TEXT_MAIN,
    TEXT_MUTED,
    WARNING_BORDER,
)

FIGURES_DIR = Path(__file__).resolve().parent.parent / "images"
ASSETS_DIR = Path(__file__).resolve().parent / "assets"
DASHBOARD_ICON = ASSETS_DIR / "dashboard-icon.png"
HOME_NAV_ICON = ASSETS_DIR / "home-nav-icon.png"
EXECUTIVE_SUMMARY_ICON = ASSETS_DIR / "executive-summary-icon.png"
SUPPORTING_EVIDENCE_ICON = ASSETS_DIR / "supporting-evidence-icon.png"
SUPPORTING_TABLES_ICON = ASSETS_DIR / "supporting-tables-icon.png"
PROJECT_OBJECTIVE_ICON = ASSETS_DIR / "project-objective-icon.png"
BUSINESS_QUESTION_ICON = ASSETS_DIR / "business-question-icon.png"
BUSINESS_QUESTIONS_ICON = ASSETS_DIR / "business-questions-icon.png"
KEY_FINDINGS_ICON = ASSETS_DIR / "key-findings-icon.png"
BUSINESS_RECOMMENDATIONS_ICON = ASSETS_DIR / "business-recommendations-icon.png"
MODULE_HIGHLIGHTS_ICON = ASSETS_DIR / "module-highlights-icon.png"
MODULE2_NAV_ICON = ASSETS_DIR / "module2-nav-icon.png"
DATASET_SOURCE_ICON = ASSETS_DIR / "dataset-source-icon.png"

_INLINE_MARKUP_RE = re.compile(
    r"(<b>.*?</b>|~~.*?~~|`[^`]+`)", flags=re.IGNORECASE | re.DOTALL
)


def _image_data_uri(path: Path) -> str:
    data = path.read_bytes()
    b64 = base64.b64encode(data).decode("ascii")
    suffix = path.suffix.lower().lstrip(".")
    mime = "image/png" if suffix == "png" else f"image/{suffix}"
    return f"data:{mime};base64,{b64}"


def _surface_content_html(text: str) -> str:
    """Prepare narrative strings for db-surface-card HTML (preserves <b>, `code`, ~~underline~~)."""
    parts: list[str] = []
    pos = 0
    for match in _INLINE_MARKUP_RE.finditer(text):
        parts.append(html.escape(text[pos : match.start()]))
        chunk = match.group(0)
        if chunk.startswith("<b>"):
            inner = chunk[3:-4]
            parts.append(f"<strong>{html.escape(inner)}</strong>")
        elif chunk.startswith("~~"):
            inner = chunk[2:-2]
            parts.append(f'<u class="db-surface-underline">{html.escape(inner)}</u>')
        else:
            inner = chunk[1:-1]
            parts.append(f"<code>{html.escape(inner)}</code>")
        pos = match.end()
    parts.append(html.escape(text[pos:]))
    return "".join(parts)


def _surface_list_html(items: list[str]) -> str:
    lis = "".join(f"<li>{_surface_content_html(item)}</li>" for item in items)
    return f'<ul class="db-surface-list">{lis}</ul>'

# Shared small-sample visual language, reused by every module so the same
# color/marker/caption always means the same thing everywhere in the app.
SMALL_SAMPLE_COLOR = WARNING_BORDER
# Bar charts use a slightly softer orange so flagged categories stay visible
# without overpowering the primary series color.
SMALL_SAMPLE_BAR_COLOR = "#E8945A"
SMALL_SAMPLE_CAPTION = "🟠 Orange bars = small sample (n < 100) — interpret with caution."

# Scatter/bubble charts (e.g. Quadrant Analysis) keep each category's own
# fill color untouched and instead ring small-sample points in red, with a
# dedicated "Small Sample" legend entry - this avoids clashing with any
# category color that happens to already be orange/amber.
SMALL_SAMPLE_RING_COLOR = ALERT_RED
SMALL_SAMPLE_RING_CAPTION = "⭕ Red-ringed points (see \"Small Sample\" in legend) = small sample (n < 100) — interpret with caution."
SMALL_SAMPLE_LEGEND_LABEL = "Small sample (n<100)"
SUBSCRIPTION_RATE_TRACE_NAME = "Subscription Rate"


def small_sample_colors(df: pd.DataFrame, flag_col: str = "small_sample", base_color: str = ACCENT) -> list[str]:
    """Per-row marker colors: flagged rows get the shared warning color, others the accent color."""
    if flag_col not in df.columns:
        return [base_color] * len(df)
    return [SMALL_SAMPLE_BAR_COLOR if str(v).lower() == "yes" else base_color for v in df[flag_col]]


def small_sample_labels(df: pd.DataFrame, label_col: str, flag_col: str = "small_sample") -> list[str]:
    """Category labels with a small-sample marker (⚠) appended, for axis ticks / point text."""
    if flag_col not in df.columns:
        return df[label_col].astype(str).tolist()
    return [
        f"{label} ⚠" if str(flag).lower() == "yes" else str(label)
        for label, flag in zip(df[label_col], df[flag_col])
    ]


def scale_bubble_sizes(counts: pd.Series) -> list[float]:
    """Map segment counts to a consistent, readable bubble diameter range."""
    if counts.empty:
        return []
    cmin, cmax = float(counts.min()), float(counts.max())
    if cmax == cmin:
        mid = (CHART_SCATTER_SIZE_MAX + CHART_SCATTER_SIZE_MIN) / 2
        return [mid] * len(counts)
    scaled = CHART_SCATTER_SIZE_MIN + (counts.astype(float) - cmin) / (cmax - cmin) * (
        CHART_SCATTER_SIZE_MAX - CHART_SCATTER_SIZE_MIN
    )
    return scaled.tolist()


def build_quadrant_chart(df: pd.DataFrame, refs: dict, feature_name: str):
    """Build a styled quadrant scatter chart with locked colors and sizing."""
    import plotly.graph_objects as go

    cat_col = "category"
    labels = small_sample_labels(df, cat_col)
    label_by_index = dict(zip(df.index, labels))
    size_by_index = dict(zip(df.index, scale_bubble_sizes(df["count"])))
    fig = go.Figure()

    for quadrant, color in CHART_QUADRANT_COLORS.items():
        subset = df[df["quadrant"] == quadrant]
        if subset.empty:
            continue
        sizes = [size_by_index[idx] for idx in subset.index]
        fig.add_trace(
            go.Scatter(
                x=subset["subscription_rate"],
                y=subset["contribution_to_yes"],
                mode="markers+text",
                name=CHART_QUADRANT_LEGEND_LABELS[quadrant],
                text=[label_by_index[idx] for idx in subset.index],
                textposition="top center",
                textfont=dict(family=CHART_FONT, size=11, color=TEXT_MAIN),
                customdata=subset[["count", "subscription_rate", "contribution_to_yes", "small_sample"]].values,
                hovertemplate=(
                    "<b>%{text}</b><br>"
                    "Count (n): %{customdata[0]}<br>"
                    "Subscription Rate: %{customdata[1]:.2%}<br>"
                    "Contribution to Subscribers: %{customdata[2]:.2%}<br>"
                    "Small Sample (n<100): %{customdata[3]}<extra></extra>"
                ),
                marker=dict(
                    size=sizes,
                    color=color,
                    opacity=0.9,
                    line=dict(width=1.5, color="#FFFFFF"),
                ),
                cliponaxis=False,
            )
        )

    ring_sizes = None
    if "small_sample" in df.columns:
        flagged = df[df["small_sample"].astype(str).str.lower() == "yes"]
        if not flagged.empty:
            ring_sizes = [size_by_index[idx] + 10 for idx in flagged.index]
    ring_trace = small_sample_ring_trace(
        df,
        "subscription_rate",
        "contribution_to_yes",
        ring_sizes=ring_sizes,
    )
    if ring_trace is not None:
        fig.add_trace(ring_trace)

    fig.add_vline(
        x=refs["mean_rate"],
        line_dash="dash",
        line_color=CHART_NEUTRAL,
        line_width=CHART_REFERENCE_LINE_WIDTH,
    )
    fig.add_hline(
        y=refs["mean_contribution"],
        line_dash="dash",
        line_color=CHART_NEUTRAL,
        line_width=CHART_REFERENCE_LINE_WIDTH,
    )
    fig.update_layout(
        title=f"Quadrant Analysis — {feature_name} (Conversion Rate × Contribution to Subscribers)",
        xaxis_title="Conversion Rate (subscription_rate)",
        yaxis_title="Contribution to Total Positive Class",
        xaxis_tickformat=".0%",
        yaxis_tickformat=".0%",
        height=560,
        uirevision="dashboard-quadrant-v8",
    )
    apply_plotly_theme(fig)
    return finalize_quadrant_chart(fig)


def small_sample_ring_trace(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    flag_col: str = "small_sample",
    ring_size: int = 26,
    ring_sizes: list[float] | None = None,
):
    """A separate overlay trace that rings small-sample points in red.

    Used on scatter/bubble charts (e.g. Quadrant Analysis) instead of
    recoloring the point itself, so a category's own fill color is never
    confused with the small-sample indicator. Returns ``None`` if nothing in
    ``df`` is flagged, so callers can skip adding it.
    """
    import plotly.graph_objects as go

    if flag_col not in df.columns:
        return None
    flagged = df[df[flag_col].astype(str).str.lower() == "yes"]
    if flagged.empty:
        return None
    return go.Scatter(
        x=flagged[x_col],
        y=flagged[y_col],
        mode="markers",
        # For "-open" marker symbols, Plotly.js strokes the visible ring using
        # `marker.color` itself (not `marker.line.color`, which only adds a
        # second outer border) - both must be set to red, otherwise the ring
        # silently falls back to the layout's colorway (rendering gray) while
        # the caption/legend text still says red.
        marker=dict(
            symbol="circle-open",
            size=ring_sizes if ring_sizes is not None else ring_size,
            color=SMALL_SAMPLE_RING_COLOR,
            line=dict(color=SMALL_SAMPLE_RING_COLOR, width=3),
        ),
        name=SMALL_SAMPLE_LEGEND_LABEL,
        showlegend=True,
        hoverinfo="skip",
    )


_MODULE_CARD_STYLE = (
    f"background:{BG_CARD};border:1px solid {BORDER};border-radius:14px;padding:1.35rem 1.5rem;"
    f"width:100%;height:100%;flex:1 1 auto;box-sizing:border-box;box-shadow:{SHADOW_SM};"
    "display:flex;flex-direction:column;gap:0.5rem;min-height:200px;"
    "word-wrap:break-word;overflow-wrap:anywhere;"
)
_MODULE_TAG_STYLE = (
    f"display:inline-block;background:{ACCENT_LIGHT};color:{ACCENT_DARK};"
    f"font-family:{FONT_HEADING};font-size:{FONT_META};font-weight:700;padding:4px 11px;border-radius:999px;"
    "letter-spacing:0.04em;text-transform:uppercase;align-self:flex-start;"
)
_MODULE_TITLE_STYLE = (
    f"margin:0;color:{ACCENT_DARK};font-family:{FONT_HEADING};"
    f"font-size:{FONT_SEGMENT};font-weight:600;line-height:1.35;"
)
_MODULE_TAKEAWAY_STYLE = (
    f"margin:0;color:{TEXT_MUTED};font-family:{FONT_BODY_FAMILY};"
    f"font-size:{FONT_BODY};line-height:1.6;flex:1;"
)


def business_question_card(label: str, question: str, *, number: int | None = None) -> None:
    """Home business-question card — data-db-font + inline px (stHtml strips modifier classes)."""
    body_style = (
        f"font-family:{FONT_BODY_FAMILY};font-size:{FONT_BODY_COMPACT_PX} !important;"
        f"line-height:1.6 !important;color:{TEXT_MAIN} !important;margin:0;flex:1;"
    )
    title_style = (
        f"font-family:{FONT_HEADING};font-size:{FONT_SEGMENT};font-weight:600;"
        f"line-height:1.35;color:{ACCENT_DARK};margin:0 0 0.5rem;"
    )
    card_style = f"border:1px solid {ACCENT_TEAL};border-left:1px solid {ACCENT_TEAL};"
    if number is not None:
        num_style = f"color:{ACCENT_TEAL};font-weight:700;margin-right:0.35em;"
        title_html = f'<span style="{num_style}">{number}</span>{html.escape(label)}'
    else:
        title_html = html.escape(label)
    st.html(
        f'<div class="db-card db-card--home-question" style="{card_style}">'
        f'<div class="db-card-title" style="{title_style}">{title_html}</div>'
        f'<div class="db-card-body" data-db-font="compact" style="{body_style}">'
        f"{html.escape(question)}</div></div>",
        width="stretch",
    )


def dataset_source_card(src: dict[str, str]) -> None:
    """Home dataset metadata card — 14px body / 15px title via data-db-font + inline px."""
    body_meta = (
        f"font-family:{FONT_BODY_FAMILY};font-size:{FONT_BODY_COMPACT_PX} !important;"
        f"line-height:1.55 !important;color:{TEXT_MUTED} !important;"
    )
    title_style = (
        f"font-family:{FONT_HEADING};font-size:{FONT_CARD_TITLE_PX} !important;"
        f"line-height:1.55 !important;color:{TEXT_MUTED} !important;"
        f"font-weight:600 !important;margin:0 0 0.4rem;"
    )
    body_style = f"{body_meta}margin:0 0 0.35rem;flex:1;"
    st.html(
        f'<div class="db-card" data-db-font="meta">'
        f'<h4 class="db-card-title" style="{title_style}">{html.escape(src["name"])}</h4>'
        f'<div class="db-card-body" style="{body_style}">{html.escape(src["origin"])}</div>'
        f'<div class="db-card-body" style="{body_style}">'
        f'<b>Raw file</b><br>{html.escape(src["raw_path"])}</div>'
        f'<div class="db-card-body" style="{body_style}">'
        f'<b>Cleaning applied</b><br>{html.escape(src["cleaning"])}</div></div>',
        width="stretch",
    )


def _kpi_card_markup(item: dict) -> str:
    help_text = item.get("help")
    title_attr = f' title="{html.escape(help_text)}"' if help_text else ""
    value = html.escape(str(item["value"]))
    # Inline style is required: Streamlit markdown may strip custom classes from
    # spans, and class-based rules then lose to `.stApp span { color: … }`.
    value_style = (
        f"font-family:{FONT_BODY_FAMILY};color:{ACCENT};font-weight:700;"
        f"font-size:{FONT_KPI_VALUE};line-height:1.2;"
    )
    return (
        f'<div class="db-kpi-card"{title_attr}>'
        f'<div class="db-kpi-label">{html.escape(item["label"])}</div>'
        f'<div class="db-kpi-value">'
        f'<span style="{value_style}">{value}</span>'
        f"</div></div>"
    )


def _kpi_row_html(items: list[dict]) -> str:
    cards = "".join(_kpi_card_markup(item) for item in items)
    return f'<div class="db-kpi-row">{cards}</div>'


def kpi_row(items: list[dict]) -> None:
    """Render KPI stat cards with strong typography and even spacing."""
    cols = st.columns(len(items), gap="small")
    for col, item in zip(cols, items):
        with col:
            st.markdown(_kpi_card_markup(item), unsafe_allow_html=True)


def page_hero(title: str, subtitle: str, *, kpis: list[dict] | None = None, eyebrow: str = "Project Overview") -> None:
    """Home page hero: title, description, and key statistics."""
    kpi_block = f'<div class="db-hero__kpis">{_kpi_row_html(kpis)}</div>' if kpis else ""
    st.html(
        f"""
        <div class="db-hero">
            <div class="db-hero__eyebrow">{html.escape(eyebrow)}</div>
            <h1 class="db-hero__title">{html.escape(title)}</h1>
            <p class="db-hero__subtitle">{html.escape(subtitle)}</p>
            {kpi_block}
        </div>
        """,
        width="stretch",
    )


def nav_option_label(text: str, *, icon: Path | str | None = None) -> str:
    """Build a Streamlit nav/radio label with an optional leading image icon."""
    icon_path = Path(icon) if icon is not None else None
    if icon_path is not None and icon_path.exists():
        return f"![]({_image_data_uri(icon_path)}) {text}"
    return text


def sidebar_brand(title: str, subtitle: str | None = None, *, icon: Path | str | None = None) -> None:
    """Sidebar app title with the same dashboard icon as the home page header."""
    icon_path = Path(icon) if icon is not None else DASHBOARD_ICON
    icon_html = ""
    if icon_path.exists():
        icon_html = f'<img class="db-sidebar-brand__icon" src="{_image_data_uri(icon_path)}" alt="" />'

    st.markdown(
        f'<div class="db-sidebar-brand">'
        f'<div class="db-sidebar-brand__row">{icon_html}'
        f'<div class="db-sidebar-brand__title">{html.escape(title)}</div>'
        f"</div></div>",
        unsafe_allow_html=True,
    )
    if subtitle:
        st.caption(subtitle)


def module_page_header(title: str, subtitle: str, *, icon: Path | str | None = None) -> None:
    """Module page title — plain title + subtitle block (no card), spacing unchanged."""
    icon_path = Path(icon) if icon is not None else None
    if icon_path is not None and icon_path.exists():
        title_html = (
            f'<div class="db-module-header__title-row">'
            f'<img class="db-module-header__icon" src="{_image_data_uri(icon_path)}" alt="" />'
            f'<div class="db-module-header__title-text">{html.escape(title)}</div>'
            f"</div>"
        )
    else:
        title_html = f'<div class="db-module-header__title">{html.escape(title)}</div>'

    st.markdown(
        f'<div class="db-module-header">{title_html}'
        f'<div class="db-module-header__subtitle">{html.escape(subtitle)}</div>'
        f"</div>",
        unsafe_allow_html=True,
    )


def section_heading(text: str) -> None:
    st.markdown(f'<h2 class="db-section-heading">{html.escape(text)}</h2>', unsafe_allow_html=True)


_SEGMENT_VARIANTS: dict[str, tuple[str, str]] = {
    "takeaway": ("💡", "db-insight-header--takeaway"),
    "impact": ("📌", "db-insight-header--impact"),
    "warning": ("⚠️", "db-insight-header--warning"),
    "evidence": ("📊", "db-insight-header--evidence"),
    "tables": ("📋", "db-insight-header--tables"),
    # Home — section tier (Executive Summary, Module Highlights, Dataset Source)
    "executive": ("📊", "db-insight-header--evidence"),
    "highlights": ("🎯", "db-insight-header--takeaway"),
    "dataset": ("📁", "db-insight-header--tables"),
    # Home — subsection tier (same visual weight as module segment labels)
    "objective": ("💡", "db-insight-header--takeaway"),
    "questions": ("❓", "db-insight-header--impact"),
    "findings": ("📊", "db-insight-header--evidence"),
    "recommendations": ("📌", "db-insight-header--impact"),
}


def _segment_label_html(
    text: str,
    variant: str,
    *,
    tier: Literal["section", "segment"] = "segment",
    icon: Path | str | None = None,
    block_class: str | None = None,
    block_style: str | None = None,
    suppress_emoji: bool = False,
) -> str:
    emoji, cls = _SEGMENT_VARIANTS[variant]
    block_cls = "db-insight-block db-insight-block--tier-section" if tier == "section" else "db-insight-block"
    if block_class:
        block_cls += f" {block_class}"
    style_attr = f' style="{block_style}"' if block_style else ""
    icon_path = Path(icon) if icon is not None else None
    text_style = ""
    if block_class and "db-insight-block--home-executive" in block_class:
        text_style = (
            f' style="display:inline-block;border-bottom:2px solid {ACCENT};'
            f'padding-bottom:2px;"'
        )
    if icon_path is not None and icon_path.exists():
        label_inner = (
            f'<img class="db-insight-header__icon" src="{_image_data_uri(icon_path)}" alt="" />'
            f'<span class="db-insight-header__text"{text_style}>{html.escape(text)}</span>'
        )
    elif suppress_emoji:
        label_inner = f'<span class="db-insight-header__text"{text_style}>{html.escape(text)}</span>'
    else:
        label_inner = f"{emoji} {html.escape(text)}"

    return (
        f'<div class="{block_cls}"{style_attr}>'
        f'<div class="db-insight-header {cls}">{label_inner}</div>'
        f"</div>"
    )


def _segment_label(
    text: str,
    variant: str,
    *,
    tier: Literal["section", "segment"] = "segment",
    icon: Path | str | None = None,
    block_class: str | None = None,
    block_style: str | None = None,
    suppress_emoji: bool = False,
) -> None:
    st.markdown(
        _segment_label_html(
            text,
            variant,
            tier=tier,
            icon=icon,
            block_class=block_class,
            block_style=block_style,
            suppress_emoji=suppress_emoji,
        ),
        unsafe_allow_html=True,
    )


def segment_heading(
    text: str,
    *,
    kind: Literal["evidence", "tables"],
    icon: Path | str | None = None,
    block_class: str | None = None,
) -> None:
    """Module section label — matches Key Takeaway / Business Impact header style."""
    _segment_label(text, kind, icon=icon, block_class=block_class)


def home_section_heading(
    text: str,
    *,
    kind: Literal["executive", "highlights", "dataset"],
    icon: Path | str | None = None,
    block_class: str | None = None,
    suppress_emoji: bool = False,
) -> None:
    """Home major section label — segment style at section tier (larger than subsections)."""
    if kind == "highlights":
        icon = None
        suppress_emoji = True
        block_class = block_class or "db-insight-block--home-highlights"
    if kind == "dataset":
        icon = None
        suppress_emoji = True
        block_class = block_class or "db-insight-block--home-dataset"
    _segment_label(
        text,
        kind,
        tier="section",
        icon=icon,
        block_class=block_class,
        suppress_emoji=suppress_emoji,
    )


def home_subsection_heading(
    text: str,
    *,
    kind: Literal["objective", "questions", "findings", "recommendations"],
    icon: Path | str | None = None,
    block_class: str | None = None,
    block_style: str | None = None,
) -> None:
    """Home subsection label — same tier as module Key Takeaway / Business Impact labels."""
    _segment_label(text, kind, icon=icon, block_class=block_class, block_style=block_style)


def subsection_heading(text: str) -> None:
    st.markdown(f'<h4 class="db-subsection-heading">{html.escape(text)}</h4>', unsafe_allow_html=True)


def business_question(
    text: str,
    *,
    icon: Path | str | None = None,
    body_align: Literal["center", "left"] = "center",
) -> None:
    icon_path = Path(icon) if icon is not None else BUSINESS_QUESTIONS_ICON
    box_class = "db-question-box"
    if body_align == "left":
        box_class += " db-question-box--body-left"
    if icon_path.exists():
        label_html = (
            f'<div class="db-question-box__label">'
            f'<img class="db-question-box__icon" src="{_image_data_uri(icon_path)}" alt="" />'
            f'<div class="db-question-box__label-text">Business Question</div>'
            f"</div>"
        )
    else:
        label_html = '<div class="db-question-box__label">🎯 Business Question</div>'

    st.markdown(
        f"""
        <div class="{box_class}">
            {label_html}
            <div class="db-question-box__text">{html.escape(text)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def insight_card(key_takeaway: str, business_impact: list[str], notes: list[str]) -> None:
    """The Insight Card: Key Takeaway -> Business Impact -> Interpretation Notes."""
    _segment_label(
        "Key Takeaway",
        "recommendations",
        icon=BUSINESS_QUESTION_ICON,
    )
    st.html(
        f'<div class="db-surface-card">{_surface_content_html(key_takeaway)}</div>',
        width="stretch",
    )

    _segment_label("Business Impact", "impact", block_class="db-insight-block--follows-card")
    st.html(
        f'<div class="db-surface-card">{_surface_list_html(business_impact)}</div>',
        width="stretch",
    )

    _segment_label("Interpretation Notes", "warning", block_class="db-insight-block--follows-card")
    st.html(
        f'<div class="db-surface-card db-surface-card--warning">{_surface_list_html(notes)}</div>',
        width="stretch",
    )


def section_tag(label: str) -> None:
    st.markdown(f'<span class="db-section-tag">{label}</span>', unsafe_allow_html=True)


def module_highlight_card(tag: str, title: str, takeaway: str) -> None:
    st.html(
        f"""
        <div class="db-module-card" data-db-layout="v5" style="{_MODULE_CARD_STYLE}">
            <span class="db-tag" style="{_MODULE_TAG_STYLE}">{html.escape(tag)}</span>
            <div class="db-module-title" style="{_MODULE_TITLE_STYLE}">{html.escape(title)}</div>
            <div class="db-module-takeaway" style="{_MODULE_TAKEAWAY_STYLE}">{_surface_content_html(takeaway)}</div>
        </div>
        """,
        width="stretch",
    )


def data_table(df: pd.DataFrame, caption: str | None = None, stretch: bool = True) -> None:
    st.dataframe(df, width="stretch" if stretch else "content", hide_index=True)
    if caption:
        st.markdown(f'<p class="db-caption">{caption}</p>', unsafe_allow_html=True)


def static_figure(rel_path: str, caption: str, expanded: bool = False) -> None:
    """Show the original report figure (already generated, not regenerated) inside an expander."""
    with st.expander(f"🖼️ View Original Report Figure — {caption}", expanded=expanded):
        img_path = FIGURES_DIR / rel_path
        if img_path.exists():
            st.image(str(img_path), caption=caption, width="stretch")
        else:
            st.warning(f"Figure not found: {rel_path}")


def _flaticon_attribution_html() -> str:
    icon_links = " · ".join(
        f'<a href="{html.escape(c["url"])}" target="_blank" rel="noopener noreferrer">'
        f'{html.escape(c["label"])}</a>'
        for c in FLATICON_CREDITS
    )
    seen_authors: set[str] = set()
    author_links: list[str] = []
    for credit in FLATICON_CREDITS:
        author = credit["author"]
        if author in seen_authors:
            continue
        seen_authors.add(author)
        author_links.append(
            f'<a href="{html.escape(credit["url"])}" target="_blank" rel="noopener noreferrer">'
            f"{html.escape(author)}</a>"
        )
    authors = " · ".join(author_links)
    return (
        f'<div class="db-footer-attribution">'
        f"Icons (Flaticon): {icon_links}<br>"
        f'<div class="db-footer-attribution__authors">Icon authors: {authors}</div>'
        f"</div>"
    )


def footer(project: str, dataset: str, technology: str, repo: str | None = None) -> None:
    repo_line = (
        f' <a href="{html.escape(repo)}" target="_blank" rel="noopener noreferrer">GitHub Repository</a>'
        if repo
        else ""
    )
    # Inline styles required: Streamlit markdown span rules override class-based footer labels.
    label_style = (
        f"font-family:{FONT_BODY_FAMILY};font-weight:400;font-size:{FONT_BODY_COMPACT_PX};"
        f"color:{TEXT_MUTED};letter-spacing:0.01em;"
    )
    line_style = (
        f"font-family:{FONT_BODY_FAMILY};font-size:{FONT_BODY_COMPACT_PX};"
        f"color:{TEXT_MUTED};line-height:1.6;margin:0;"
    )
    st.html(
        f"""
        <div class="db-footer">
            <div class="db-footer__meta">
                <p class="db-footer__line" style="{line_style}">
                    <span class="db-footer__label" style="{label_style}">Project:</span>
                    {html.escape(project)}{repo_line}
                </p>
                <p class="db-footer__line" style="{line_style}">
                    <span class="db-footer__label" style="{label_style}">Dataset:</span>
                    {html.escape(dataset)}
                </p>
                <p class="db-footer__line" style="{line_style}">
                    <span class="db-footer__label" style="{label_style}">Technology:</span>
                    {html.escape(technology)}
                </p>
            </div>
            {_flaticon_attribution_html()}
        </div>
        """,
        width="stretch",
    )


def finalize_bar_chart(fig, bar_colors: list[str] | str):
    """Apply bar geometry and force fill colors as the last chart step."""
    fig.update_layout(
        bargap=CHART_BAR_GAP,
        bargroupgap=CHART_BAR_GROUP_GAP,
    )
    fig.update_traces(
        selector=dict(type="bar"),
        width=CHART_BAR_WIDTH,
        cliponaxis=False,
        marker=dict(
            color=bar_colors,
            cornerradius=CHART_BAR_CORNER_RADIUS,
            line=dict(width=0),
        ),
    )
    return fig


def style_bar_chart(fig, bar_colors: list[str] | str | None = None):
    """Backward-compatible alias for bar geometry + optional color lock-in."""
    if bar_colors is None:
        for trace in fig.data:
            if getattr(trace, "type", None) != "bar":
                continue
            colors = trace.marker.color if trace.marker and trace.marker.color is not None else ACCENT
            bar_colors = colors
            break
        else:
            return fig
    return finalize_bar_chart(fig, bar_colors)


def _feature_category_col(df: pd.DataFrame) -> str:
    for col in df.columns:
        if col not in (
            "rank",
            "count",
            "percentage",
            "yes",
            "subscription_rate",
            "contribution_to_yes",
            "small_sample",
        ):
            return col
    return df.columns[0]


def build_conversion_rate_bar(df: pd.DataFrame, feature_name: str, overall_rate: float):
    """Module 1 conversion-rate bar chart."""
    import plotly.graph_objects as go

    cat_col = _feature_category_col(df)
    d = df.sort_values("subscription_rate", ascending=False)
    bar_colors = small_sample_colors(d, base_color=ACCENT)
    fig = go.Figure(
        data=[
            go.Bar(
                x=d[cat_col],
                y=d["subscription_rate"],
                text=d["subscription_rate"].map(lambda v: f"{v:.1%}"),
                textposition="outside",
                customdata=d[["count", "percentage", "subscription_rate"]].values,
                hovertemplate=(
                    f"<b>{feature_name}: %{{x}}</b><br>"
                    "Count (n): %{customdata[0]}<br>"
                    "Share of dataset: %{customdata[1]:.2f}%<br>"
                    "Subscription Rate: %{customdata[2]:.2%}<extra></extra>"
                ),
                marker=dict(color=bar_colors),
            )
        ]
    )
    fig.update_xaxes(type="category", tickmode="array", tickvals=d[cat_col].tolist(), ticktext=small_sample_labels(d, cat_col))
    fig.add_hline(
        y=overall_rate,
        line_dash="dash",
        line_color=CHART_NEUTRAL,
        line_width=CHART_REFERENCE_LINE_WIDTH,
        annotation_text=f"Overall rate {overall_rate:.2%}",
        annotation_position="top right",
    )
    fig.update_layout(
        title=f"Subscription Rate by {feature_name}",
        yaxis_title="Subscription Rate",
        yaxis_tickformat=".0%",
        xaxis_title=feature_name,
        height=420,
    )
    apply_plotly_theme(fig)
    return finalize_bar_chart(fig, bar_colors)


def build_contribution_bar(df: pd.DataFrame, feature_name: str):
    """Module 1 contribution bar chart."""
    import plotly.graph_objects as go

    cat_col = _feature_category_col(df)
    d = df.sort_values("contribution_to_yes", ascending=False)
    bar_colors = small_sample_colors(d, base_color=ACCENT_TEAL)
    fig = go.Figure(
        data=[
            go.Bar(
                x=d[cat_col],
                y=d["contribution_to_yes"],
                text=d["contribution_to_yes"].map(lambda v: f"{v:.1%}"),
                textposition="outside",
                customdata=d[["count", "percentage"]].values,
                hovertemplate=(
                    f"<b>{feature_name}: %{{x}}</b><br>"
                    "Count (n): %{customdata[0]}<br>"
                    "Share of dataset: %{customdata[1]:.2f}%<br>"
                    "Contribution to total subscribers: %{y:.2%}<extra></extra>"
                ),
                marker=dict(color=bar_colors),
            )
        ]
    )
    fig.update_xaxes(type="category", tickmode="array", tickvals=d[cat_col].tolist(), ticktext=small_sample_labels(d, cat_col))
    fig.update_layout(
        title=f"Contribution to Total Subscribers — {feature_name}",
        yaxis_title="Contribution to Subscribers (yes)",
        yaxis_tickformat=".0%",
        xaxis_title=feature_name,
        height=420,
    )
    apply_plotly_theme(fig)
    return finalize_bar_chart(fig, bar_colors)


def build_subscription_rate_bar(
    df: pd.DataFrame,
    cat_col: str,
    title: str,
    x_title: str,
    overall_rate: float,
    extra_cols: list[str] | None = None,
):
    """Module 2 subscription-rate bar chart."""
    import plotly.graph_objects as go

    extra_cols = extra_cols or []
    custom = ["count", "percentage", "subscription_rate", "small_sample"] + extra_cols
    bar_colors = small_sample_colors(df, base_color=ACCENT)
    hover = (
        f"<b>%{{x}}</b><br>Count (n): %{{customdata[0]}}<br>"
        "Share of dataset: %{customdata[1]:.2f}%<br>"
        "Subscription Rate: %{customdata[2]:.2%}<br>"
        "Small Sample (n<100): %{customdata[3]}"
    )
    for i, col in enumerate(extra_cols, start=4):
        hover += f"<br>{col.replace('_', ' ').title()}: %{{customdata[{i}]}}"
    hover += "<extra></extra>"
    fig = go.Figure(
        data=[
            go.Bar(
                x=df[cat_col],
                y=df["subscription_rate"],
                text=df["subscription_rate"].map(lambda v: f"{v:.1%}"),
                textposition="outside",
                customdata=df[custom].values,
                hovertemplate=hover,
                marker=dict(color=bar_colors),
            )
        ]
    )
    fig.update_xaxes(type="category", tickmode="array", tickvals=df[cat_col].tolist(), ticktext=small_sample_labels(df, cat_col))
    fig.add_hline(
        y=overall_rate,
        line_dash="dash",
        line_color=CHART_NEUTRAL,
        line_width=CHART_REFERENCE_LINE_WIDTH,
        annotation_text=f"Overall rate {overall_rate:.2%}",
        annotation_position="top right",
    )
    fig.update_layout(title=title, xaxis_title=x_title, yaxis_title="Subscription Rate", yaxis_tickformat=".0%", height=420)
    apply_plotly_theme(fig)
    return finalize_bar_chart(fig, bar_colors)


def build_correlation_bar_chart(df: pd.DataFrame):
    """Module 3 horizontal correlation bar chart."""
    import plotly.graph_objects as go

    ranked = df.sort_values("correlation_with_subscription", key=lambda s: s.abs(), ascending=True)
    bar_colors = ACCENT
    fig = go.Figure(
        data=[
            go.Bar(
                x=ranked["correlation_with_subscription"],
                y=ranked["variable"],
                orientation="h",
                text=ranked["correlation_with_subscription"].map(lambda v: f"{v:.3f}"),
                textposition="outside",
                customdata=ranked[["rank"]].values,
                hovertemplate=(
                    "<b>%{y}</b><br>Correlation with subscription: %{x:.3f}<br>"
                    "Rank (by |r|): #%{customdata[0]}<extra></extra>"
                ),
                marker=dict(color=bar_colors),
            )
        ]
    )
    fig.add_vline(x=0, line_color=CHART_NEUTRAL, line_width=CHART_REFERENCE_LINE_WIDTH)
    fig.update_layout(
        title="Correlation with Subscription (Pearson r)",
        xaxis_title="Correlation coefficient",
        yaxis_title="",
        height=420,
    )
    apply_plotly_theme(fig)
    return finalize_bar_chart(fig, bar_colors)


def _line_marker(color: str, *, emphasis: bool = False) -> dict:
    size = CHART_LINE_MARKER_SIZE_EMPHASIS if emphasis else CHART_LINE_MARKER_SIZE
    return dict(size=size, color=color, line=dict(width=1, color="#FFFFFF"))


def _normalize_series(series: pd.Series) -> pd.Series:
    return (series - series.min()) / (series.max() - series.min())


def finalize_line_chart(fig, trace_colors: dict[str, str] | None = None):
    """Apply shared line styling and lock trace colors for Streamlit."""
    trace_colors = trace_colors or {}

    fig.update_layout(
        margin=dict(l=48, r=48, t=72, b=110),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.25,
            xanchor="center",
            x=0.5,
            font=dict(family=CHART_FONT, size=11, color=TEXT_MUTED),
            itemsizing="constant",
            tracegroupgap=10,
        ),
        hovermode="x unified",
        uirevision="dashboard-line-v3",
    )
    fig.update_xaxes(showgrid=True, gridcolor=CHART_GRID, gridwidth=1, zeroline=False)

    if getattr(fig.layout, "yaxis2", None) and fig.layout.yaxis2.overlaying:
        fig.update_layout(
            yaxis2=dict(
                tickfont=dict(family=CHART_FONT, size=12, color=TEXT_MUTED),
                title=dict(font=dict(family=CHART_FONT, size=12, color=TEXT_MUTED)),
                showgrid=False,
                zeroline=False,
            )
        )

    for name, color in trace_colors.items():
        fig.update_traces(
            selector=dict(name=name, type="scatter"),
            mode="lines+markers",
            line=dict(color=color, width=CHART_LINE_WIDTH),
            marker=_line_marker(color),
            hoverlabel=dict(
                bgcolor=BG_CARD,
                bordercolor=BORDER,
                font=dict(family=CHART_FONT, size=12, color=TEXT_MAIN),
            ),
        )

    fig.update_traces(
        selector=dict(name=SUBSCRIPTION_RATE_TRACE_NAME, type="scatter"),
        mode="lines+markers",
        line=dict(
            color=CHART_SUBSCRIPTION_LINE_COLOR,
            width=CHART_LINE_WIDTH_PRIMARY,
            dash=CHART_SUBSCRIPTION_LINE_DASH,
        ),
        marker=_line_marker(CHART_SUBSCRIPTION_LINE_COLOR, emphasis=True),
        hoverlabel=dict(
            bgcolor=BG_CARD,
            bordercolor=BORDER,
            font=dict(family=CHART_FONT, size=12, color=TEXT_MAIN),
        ),
    )
    return fig


def build_macro_trend_chart(df: pd.DataFrame):
    """Module 3 macro indicators (normalized) vs subscription rate."""
    import plotly.graph_objects as go

    series_map = {
        "emp.var.rate (normalized)": "emp_var_rate",
        "euribor3m (normalized)": "euribor3m",
        "nr.employed (normalized)": "nr_employed",
    }
    trace_colors = dict(zip(series_map.keys(), CHART_MACRO_LINE_COLORS))
    fig = go.Figure()
    for label, col in series_map.items():
        color = trace_colors[label]
        fig.add_trace(
            go.Scatter(
                x=df["month"],
                y=_normalize_series(df[col]),
                name=label,
                mode="lines+markers",
                line=dict(color=color, width=CHART_LINE_WIDTH),
                marker=_line_marker(color),
                customdata=df[[col]].values,
                hovertemplate=(
                    f"<b>%{{x}}</b><br>{label}: %{{y:.2f}} (scaled)<br>"
                    "Actual value: %{customdata[0]:.3f}<extra></extra>"
                ),
            )
        )
    fig.add_trace(
        go.Scatter(
            x=df["month"],
            y=df["subscription_rate"],
            name=SUBSCRIPTION_RATE_TRACE_NAME,
            mode="lines+markers",
            yaxis="y2",
            line=dict(
                color=CHART_SUBSCRIPTION_LINE_COLOR,
                width=CHART_LINE_WIDTH_PRIMARY,
                dash=CHART_SUBSCRIPTION_LINE_DASH,
            ),
            marker=_line_marker(CHART_SUBSCRIPTION_LINE_COLOR, emphasis=True),
            hovertemplate="<b>%{x}</b><br>Subscription Rate: %{y:.2%}<extra></extra>",
        )
    )
    fig.update_layout(
        title="Macro Trend vs Subscription Rate (Normalized emp.var.rate / euribor3m / nr.employed)",
        xaxis_title="Month",
        yaxis=dict(title="Normalized Macro Value (0-1 scale)"),
        yaxis2=dict(title="Subscription Rate", overlaying="y", side="right", tickformat=".0%"),
        height=480,
    )
    fig.update_xaxes(type="category", categoryarray=df["month"].tolist())
    apply_plotly_theme(fig)
    return finalize_line_chart(fig, trace_colors=trace_colors)


def build_dual_axis_metric_chart(df: pd.DataFrame, value_col: str, value_label: str, title: str):
    """Module 3 dual-axis line chart for a macro metric vs subscription rate."""
    import plotly.graph_objects as go

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["month"],
            y=df[value_col],
            name=value_label,
            mode="lines+markers",
            line=dict(color=ACCENT, width=CHART_LINE_WIDTH),
            marker=_line_marker(ACCENT),
            hovertemplate=f"<b>%{{x}}</b><br>{value_label}: %{{y:.3f}}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df["month"],
            y=df["subscription_rate"],
            name=SUBSCRIPTION_RATE_TRACE_NAME,
            mode="lines+markers",
            yaxis="y2",
            line=dict(
                color=CHART_SUBSCRIPTION_LINE_COLOR,
                width=CHART_LINE_WIDTH_PRIMARY,
                dash=CHART_SUBSCRIPTION_LINE_DASH,
            ),
            marker=_line_marker(CHART_SUBSCRIPTION_LINE_COLOR, emphasis=True),
            customdata=df[["count", "yes"]].values,
            hovertemplate=(
                "<b>%{x}</b><br>Subscription Rate: %{y:.2%}<br>"
                "Contacts (n): %{customdata[0]}<br>Subscribers: %{customdata[1]}<extra></extra>"
            ),
        )
    )
    fig.update_layout(
        title=title,
        xaxis_title="Month",
        yaxis=dict(title=value_label),
        yaxis2=dict(title="Subscription Rate", overlaying="y", side="right", tickformat=".0%"),
        height=460,
    )
    fig.update_xaxes(type="category", categoryarray=df["month"].tolist())
    apply_plotly_theme(fig)
    return finalize_line_chart(fig, trace_colors={value_label: ACCENT})


def build_month_volume_rate_chart(df: pd.DataFrame):
    """Module 2 monthly campaign volume (bar) with subscription rate (line)."""
    import plotly.graph_objects as go

    fig = go.Figure()
    fig.add_bar(
        x=df["month"],
        y=df["count"],
        name="Campaign Volume (n)",
        marker_color=CHART_BAR_VOLUME_COLOR,
        customdata=df[["percentage"]].values,
        hovertemplate="<b>%{x}</b><br>Volume (n): %{y}<br>Share of dataset: %{customdata[0]:.2f}%<extra></extra>",
    )
    fig.add_trace(
        go.Scatter(
            x=df["month"],
            y=df["subscription_rate"],
            name=SUBSCRIPTION_RATE_TRACE_NAME,
            mode="lines+markers",
            yaxis="y2",
            line=dict(
                color=CHART_SUBSCRIPTION_LINE_COLOR,
                width=CHART_LINE_WIDTH_PRIMARY,
                dash=CHART_SUBSCRIPTION_LINE_DASH,
            ),
            marker=_line_marker(CHART_SUBSCRIPTION_LINE_COLOR, emphasis=True),
            customdata=df[["yes"]].values,
            hovertemplate=(
                "<b>%{x}</b><br>Subscription Rate: %{y:.2%}<br>"
                "Subscribers (yes): %{customdata[0]}<extra></extra>"
            ),
        )
    )
    fig.update_layout(
        title="Monthly Campaign Volume and Subscription Rate",
        xaxis_title="Month",
        yaxis=dict(title="Campaign Volume (n)"),
        yaxis2=dict(title="Subscription Rate", overlaying="y", side="right", tickformat=".0%"),
        height=440,
    )
    fig.update_xaxes(type="category", categoryarray=df["month"].tolist())
    apply_plotly_theme(fig)
    finalize_bar_chart(fig, CHART_BAR_VOLUME_COLOR)
    return finalize_line_chart(fig)


def finalize_heatmap_chart(fig):
    """Apply shared heatmap styling and lock the diverging colorscale."""
    fig.update_layout(
        margin=dict(l=56, r=40, t=72, b=56),
        uirevision="dashboard-heatmap-v1",
    )
    fig.update_traces(
        selector=dict(type="heatmap"),
        colorscale=CHART_HEATMAP_COLORSCALE,
        zmin=CHART_HEATMAP_ZMIN,
        zmax=CHART_HEATMAP_ZMAX,
        xgap=1,
        ygap=1,
        hoverlabel=dict(
            bgcolor=BG_CARD,
            bordercolor=BORDER,
            font=dict(family=CHART_FONT, size=12, color=TEXT_MAIN),
        ),
        colorbar=dict(
            title=dict(text="Correlation", font=dict(family=CHART_FONT, size=12, color=TEXT_MUTED)),
            tickfont=dict(family=CHART_FONT, size=11, color=TEXT_MUTED),
            len=0.72,
            thickness=14,
            outlinewidth=0,
            tickformat=".1f",
        ),
    )
    fig.update_xaxes(
        showgrid=False,
        tickangle=-25,
        tickfont=dict(family=CHART_FONT, size=11, color=TEXT_MUTED),
        automargin=True,
    )
    fig.update_yaxes(
        showgrid=False,
        tickfont=dict(family=CHART_FONT, size=11, color=TEXT_MUTED),
        automargin=True,
    )
    return fig


def build_correlation_heatmap(corr: pd.DataFrame):
    """Module 3 correlation matrix heatmap with a muted diverging palette."""
    import plotly.graph_objects as go

    text_values = [[f"{value:.2f}" for value in row] for row in corr.values]
    fig = go.Figure(
        data=[
            go.Heatmap(
                z=corr.values,
                x=corr.columns.tolist(),
                y=corr.index.tolist(),
                text=text_values,
                texttemplate="%{text}",
                textfont=dict(family=CHART_FONT, size=11, color=TEXT_MAIN),
                colorscale=CHART_HEATMAP_COLORSCALE,
                zmin=CHART_HEATMAP_ZMIN,
                zmax=CHART_HEATMAP_ZMAX,
                xgap=1,
                ygap=1,
                hovertemplate="%{x} × %{y}<br>Correlation: %{z:.3f}<extra></extra>",
                colorbar=dict(
                    title=dict(text="Correlation", font=dict(family=CHART_FONT, size=12, color=TEXT_MUTED)),
                    tickfont=dict(family=CHART_FONT, size=11, color=TEXT_MUTED),
                    len=0.72,
                    thickness=14,
                    outlinewidth=0,
                    tickformat=".1f",
                ),
            )
        ]
    )
    fig.update_layout(
        title="Correlation Heatmap — Macroeconomic Variables + Subscription",
        xaxis_title="",
        yaxis_title="",
        height=480,
    )
    apply_plotly_theme(fig)
    return finalize_heatmap_chart(fig)


def finalize_quadrant_chart(fig):
    """Apply shared quadrant scatter styling and lock trace colors for Streamlit."""
    legend_items = sum(
        1
        for trace in fig.data
        if getattr(trace, "type", None) == "scatter"
        and trace.showlegend is not False
        and trace.name
    )

    if legend_items >= 5:
        bottom_margin = 168
        legend_y = -0.24
        legend_cfg = dict(
            orientation="h",
            yanchor="top",
            y=legend_y,
            xanchor="center",
            x=0.5,
            font=dict(family=CHART_FONT, size=10, color=TEXT_MUTED),
            itemsizing="constant",
            tracegroupgap=12,
            entrywidth=90,
        )
        chart_height = 680
        chart_margin = dict(l=96, r=48, t=104, b=bottom_margin)
    else:
        bottom_margin = 148
        legend_y = -0.18
        legend_cfg = dict(
            orientation="h",
            yanchor="top",
            y=legend_y,
            xanchor="center",
            x=0.5,
            font=dict(family=CHART_FONT, size=10, color=TEXT_MUTED),
            itemsizing="constant",
            tracegroupgap=16,
        )
        chart_height = 640
        chart_margin = dict(l=96, r=48, t=104, b=bottom_margin)

    fig.update_layout(
        height=chart_height,
        margin=chart_margin,
        legend=legend_cfg,
        uirevision="dashboard-quadrant-v8",
    )
    fig.update_xaxes(showgrid=True, gridcolor=CHART_GRID, gridwidth=1, zeroline=False, automargin=True)
    fig.update_yaxes(showgrid=True, gridcolor=CHART_GRID, gridwidth=1, zeroline=False, automargin=True)

    for trace in fig.data:
        if getattr(trace, "type", None) != "scatter":
            continue
        if trace.name == SMALL_SAMPLE_LEGEND_LABEL:
            sizes = trace.marker.size
            trace.update(
                marker=dict(
                    symbol="circle-open",
                    size=sizes,
                    color=SMALL_SAMPLE_RING_COLOR,
                    line=dict(color=SMALL_SAMPLE_RING_COLOR, width=3),
                ),
                hoverinfo="skip",
            )
            continue
        if trace.name not in CHART_QUADRANT_COLORS_BY_LEGEND:
            continue
        color = CHART_QUADRANT_COLORS_BY_LEGEND[trace.name]
        sizes = trace.marker.size
        trace.update(
            cliponaxis=False,
            marker=dict(
                color=color,
                size=sizes,
                opacity=0.9,
                line=dict(width=1.5, color="#FFFFFF"),
            ),
            hoverlabel=dict(
                bgcolor=BG_CARD,
                bordercolor=BORDER,
                font=dict(family=CHART_FONT, size=12, color=TEXT_MAIN),
            ),
        )
    return fig


def apply_plotly_theme(fig):
    """Shared Plotly styling for every chart in every module.

    The legend is anchored *below* the plot area (not above, next to the
    title) so multi-series charts (e.g. Quadrant Analysis, Macro Trend) never
    overlap their own title - this legend position/margin is identical
    across Module 1 / 2 / 3 so charts feel consistent app-wide.
    """
    fig.update_layout(
        template="plotly_white",
        colorway=PLOTLY_COLORWAY,
        font=dict(family=CHART_FONT, size=13, color=TEXT_MAIN),
        plot_bgcolor="white",
        paper_bgcolor="white",
        autosize=True,
        margin=dict(l=40, r=24, t=72, b=96),
        hoverlabel=dict(
            bgcolor=BG_CARD,
            bordercolor=BORDER,
            font=dict(family=CHART_FONT, size=12, color=TEXT_MAIN),
        ),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.22,
            xanchor="center",
            x=0.5,
            font=dict(family=CHART_FONT, size=12, color=TEXT_MUTED),
        ),
        title=dict(
            y=0.97,
            yanchor="top",
            automargin=True,
            font=dict(family=CHART_FONT, size=15, color=ACCENT_DARK),
        ),
    )
    fig.update_xaxes(
        showgrid=False,
        showline=True,
        linecolor=BORDER,
        title=dict(font=dict(family=CHART_FONT, size=12, color=TEXT_MUTED)),
        tickfont=dict(family=CHART_FONT, size=12, color=TEXT_MUTED),
        automargin=True,
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor=CHART_GRID,
        gridwidth=1,
        zeroline=False,
        title=dict(font=dict(family=CHART_FONT, size=12, color=TEXT_MUTED)),
        tickfont=dict(family=CHART_FONT, size=12, color=TEXT_MUTED),
        automargin=True,
    )
    fig.update_annotations(font=dict(family=CHART_FONT, size=11, color=TEXT_MUTED))
    return fig


def _prepare_plotly_figure_for_display(fig) -> None:
    """Lock custom colors and detach Streamlit's global Plotly template."""
    fig.update_layout(template="plotly_white", autosize=True)

    macro_line_colors = {
        "emp.var.rate (normalized)": CHART_MACRO_LINE_COLORS[0],
        "euribor3m (normalized)": CHART_MACRO_LINE_COLORS[1],
        "nr.employed (normalized)": CHART_MACRO_LINE_COLORS[2],
    }

    for trace in fig.data:
        trace_type = getattr(trace, "type", None)
        if trace_type != "scatter":
            continue
        name = trace.name or ""
        if name in CHART_QUADRANT_COLORS_BY_LEGEND:
            color = CHART_QUADRANT_COLORS_BY_LEGEND[name]
            sizes = trace.marker.size if trace.marker and trace.marker.size is not None else None
            trace.update(
                marker=dict(
                    color=color,
                    size=sizes,
                    opacity=0.9,
                    line=dict(width=1.5, color="#FFFFFF"),
                )
            )
        elif name == SUBSCRIPTION_RATE_TRACE_NAME:
            trace.update(
                mode="lines+markers",
                line=dict(
                    color=CHART_SUBSCRIPTION_LINE_COLOR,
                    width=CHART_LINE_WIDTH_PRIMARY,
                    dash=CHART_SUBSCRIPTION_LINE_DASH,
                ),
                marker=_line_marker(CHART_SUBSCRIPTION_LINE_COLOR, emphasis=True),
            )
        elif name in macro_line_colors:
            color = macro_line_colors[name]
            trace.update(
                mode="lines+markers",
                line=dict(color=color, width=CHART_LINE_WIDTH),
                marker=_line_marker(color),
            )
        elif name == "Campaign Volume (n)":
            continue
        elif getattr(trace, "mode", "") and "lines" in trace.mode and name not in {
            SMALL_SAMPLE_LEGEND_LABEL,
            SUBSCRIPTION_RATE_TRACE_NAME,
        }:
            trace.update(
                line=dict(color=ACCENT, width=CHART_LINE_WIDTH),
                marker=_line_marker(ACCENT),
            )


def render_plotly_chart(fig, *, key: str | None = None) -> None:
    """Render Plotly with locked colors; native Streamlit chart avoids iframe clipping."""
    _prepare_plotly_figure_for_display(fig)
    st.plotly_chart(fig, width="stretch", theme=None, key=key)
