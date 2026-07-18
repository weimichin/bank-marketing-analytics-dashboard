from __future__ import annotations

import importlib

import streamlit as st

from dashboard.components import (
    SUPPORTING_EVIDENCE_ICON,
    SUPPORTING_TABLES_ICON,
    SMALL_SAMPLE_CAPTION,
    SMALL_SAMPLE_RING_CAPTION,
    business_question,
    data_table,
    module_page_header,
    segment_heading,
    static_figure,
)
from dashboard.data import module1_data as m1
from dashboard.navigation import evidence_tabs_key

CHART_GROUPS = ["Conversion Rate", "Contribution to Subscribers", "Quadrant Analysis"]
MODULE_KEY = "module1"

# View-layer display labels (tab text). Internal data keys stay "Loan".
FEATURE_DISPLAY_LABELS = {
    "Loan": "Personal Loan",
}


def _feature_tab_labels(feature_keys) -> list[str]:
    return [FEATURE_DISPLAY_LABELS.get(key, key) for key in feature_keys]


def _feature_display_name(feature_key: str) -> str:
    return FEATURE_DISPLAY_LABELS.get(feature_key, feature_key)


def render() -> None:
    import dashboard.components as components
    import dashboard.theme as theme

    importlib.reload(theme)
    importlib.reload(m1)
    importlib.reload(components)

    module_page_header("Module 1 — Who to Target", "Customer Targeting Analysis")

    business_question(m1.BUSINESS_QUESTION)

    components.insight_card(m1.KEY_TAKEAWAY, m1.BUSINESS_IMPACT, m1.INTERPRETATION_NOTES)

    segment_heading("Supporting Evidence", kind="evidence", icon=SUPPORTING_EVIDENCE_ICON)
    st.caption(
        "Charts follow the analytical workflow used in the completed analysis report: conversion rate, "
        "contribution to subscribers, and quadrant analysis by customer characteristic. "
        "Click a tab below to switch chart group."
    )

    group_tabs = st.tabs(CHART_GROUPS, key=evidence_tabs_key(MODULE_KEY), on_change="rerun")

    with group_tabs[0]:
        st.markdown("Subscription rate by customer characteristic. Dashed line = overall subscription rate (11.27%).")
        st.caption(SMALL_SAMPLE_CAPTION)
        conversion_features = list(m1.CONVERSION_FIGURES.keys())
        feature_tabs = st.tabs(_feature_tab_labels(conversion_features), key="m1_conversion_features", on_change="rerun")
        for tab, feature in zip(feature_tabs, conversion_features):
            with tab:
                display_name = _feature_display_name(feature)
                components.render_plotly_chart(
                    components.build_conversion_rate_bar(m1.CHART_TABLES[feature], display_name, m1.OVERALL_RATE),
                    key=f"m1_conv_{feature}",
                )
                static_figure(m1.CONVERSION_FIGURES[feature], f"Subscription Rate by {display_name}")

    with group_tabs[1]:
        st.markdown(
            "**Contribution** shows the share of all 4,639 subscribers represented by each category. It "
            "answers the question, \"Which categories contribute the largest share of subscribers?\". "
            "**Conversion Rate** (previous tab) instead "
            "answers \"how likely is someone *in* this category to subscribe?\". A category can be high "
            "on one and low on the other — e.g. a small category can convert very well but still "
            "contribute few total subscribers, while a large near-average category can contribute many."
        )
        st.caption(SMALL_SAMPLE_CAPTION)
        contribution_features = list(m1.CONTRIBUTION_FIGURES.keys())
        feature_tabs = st.tabs(_feature_tab_labels(contribution_features), key="m1_contribution_features", on_change="rerun")
        for tab, feature in zip(feature_tabs, contribution_features):
            with tab:
                display_name = _feature_display_name(feature)
                components.render_plotly_chart(
                    components.build_contribution_bar(m1.CHART_TABLES[feature], display_name),
                    key=f"m1_contrib_{feature}",
                )
                static_figure(m1.CONTRIBUTION_FIGURES[feature], f"Contribution to Positive Class by {display_name}")

    with group_tabs[2]:
        st.markdown(
            "X-axis = Conversion Rate, Y-axis = Contribution to Total Subscribers. Reference lines = feature-level mean. "
            "Q1 = High Conversion + High Contribution, Q2 = High Conversion + Low Contribution, "
            "Q3 = Low Conversion + High Contribution, Q4 = Low Conversion + Low Contribution. "
            "Quadrants are interpreted within each feature rather than across different customer characteristics."
        )
        st.caption(SMALL_SAMPLE_RING_CAPTION)
        quadrant_features = list(m1.QUADRANT_TABLES.keys())
        feature_tabs = st.tabs(_feature_tab_labels(quadrant_features), key="m1_quadrant_features", on_change="rerun")
        for tab, feature in zip(feature_tabs, quadrant_features):
            with tab:
                display_name = _feature_display_name(feature)
                df, refs = m1.QUADRANT_TABLES[feature]
                components.render_plotly_chart(
                    components.build_quadrant_chart(df, refs, display_name),
                    key=f"m1_quadrant_{feature}",
                )
                static_figure(m1.QUADRANT_FIGURES[feature], f"Quadrant Analysis — {display_name}")

    segment_heading("Supporting Tables", kind="tables", icon=SUPPORTING_TABLES_ICON)
    st.caption("Switch between customer variables to inspect the underlying figures.")
    table_names = list(m1.SUPPORTING_TABLES.keys())
    table_tabs = st.tabs(_feature_tab_labels(table_names), key="m1_supporting_tables", on_change="rerun")
    for tab, name in zip(table_tabs, table_names):
        with tab:
            display_name = _feature_display_name(name)
            data_table(m1.SUPPORTING_TABLES[name], caption=f"Source: Module 1 Summary Report — Table for {display_name}.")
