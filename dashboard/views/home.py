from __future__ import annotations

import importlib

import streamlit as st

import dashboard.components
import dashboard.data.home_content as hc
import dashboard.theme as theme

from dashboard.theme import SPACE_SEGMENT_LABEL_BOTTOM, SPACE_SEGMENT_TOP

from dashboard.navigation import goto

# Display titles are defined here (view layer) so Module Highlights always
# matches the dashboard terminology, independent of any stale module cache.
MODULE_HIGHLIGHT_TITLES = {
    "Module 1": "Who to Target — Customer Targeting",
    "Module 2": "How to Engage — Campaign Strategy",
    "Module 3": "Market Environment",
}


def render() -> None:
    importlib.reload(hc)
    importlib.reload(theme)
    importlib.reload(dashboard.components)
    components = dashboard.components

    theme.inject_home_card_css()

    components.module_page_header(
        "Bank Marketing Strategy Dashboard",
        "Business decision support for telephone term-deposit marketing.",
        icon=components.DASHBOARD_ICON,
    )
    components.kpi_row(hc.KPI_CARDS)

    st.divider()

    components.home_section_heading(
        "Executive Summary",
        kind="executive",
        block_class="db-insight-block--home-executive",
        suppress_emoji=True,
    )

    components.home_subsection_heading(
        "Project Objective",
        kind="objective",
        icon=components.PROJECT_OBJECTIVE_ICON,
        block_class="db-insight-block--home-objective",
    )
    st.markdown(hc.PROJECT_OBJECTIVE)

    components.home_subsection_heading(
        "Three Business Questions",
        kind="questions",
        icon=components.BUSINESS_QUESTIONS_ICON,
        block_class="db-insight-block--home-questions",
    )
    q_cols = st.columns(3, vertical_alignment="top")
    titles = ["Who to Target", "How to Engage", "Market Environment"]
    for col, number, title, question in zip(q_cols, (1, 2, 3), titles, hc.BUSINESS_QUESTIONS):
        with col:
            components.business_question_card(title, question, number=number)

    components.home_subsection_heading(
        "Key Findings",
        kind="findings",
        icon=components.KEY_FINDINGS_ICON,
        block_class="db-insight-block--home-findings",
    )
    tabs = st.tabs(list(hc.KEY_FINDINGS.keys()))
    for tab, (_, points) in zip(tabs, hc.KEY_FINDINGS.items()):
        with tab:
            for p in points:
                st.markdown(f"- {p}")

    components.home_subsection_heading(
        "Business Recommendations",
        kind="recommendations",
        icon=components.EXECUTIVE_SUMMARY_ICON,
        block_class="db-insight-block--home-recommendations",
        block_style=(
            f"margin:{SPACE_SEGMENT_TOP} 0 {SPACE_SEGMENT_LABEL_BOTTOM} !important;"
        ),
    )
    for rec in hc.BUSINESS_RECOMMENDATIONS:
        st.markdown(f"- {rec}")

    with st.expander("⚠️ Project-Level Limitations"):
        for lim in hc.LIMITATIONS:
            st.markdown(f"- {lim}")

    st.divider()

    components.home_section_heading("Module Highlights", kind="highlights")
    m_cols = st.columns(3, vertical_alignment="top")
    page_keys = ["module1", "module2", "module3"]
    for col, module, page_key in zip(m_cols, hc.MODULE_HIGHLIGHTS, page_keys):
        with col:
            title = MODULE_HIGHLIGHT_TITLES.get(module["tag"], module["title"])
            components.module_highlight_card(module["tag"], title, module["takeaway"])
            if st.button(f"View {module['tag']} →", key=f"goto_{page_key}", width="stretch"):
                goto(page_key)

    st.divider()

    components.home_section_heading("Dataset Source", kind="dataset")
    components.dataset_source_card(hc.DATASET_SOURCE)

    components.footer(**hc.FOOTER)
