from __future__ import annotations

import importlib

import pandas as pd
import streamlit as st

from dashboard.components import (
    SUPPORTING_EVIDENCE_ICON,
    SUPPORTING_TABLES_ICON,
    data_table,
    module_page_header,
    segment_heading,
    static_figure,
)
from dashboard.data import module3_data as m3
from dashboard.navigation import evidence_tabs_key

MODULE_KEY = "module3"


def _correlation_heatmap_matrix() -> pd.DataFrame:
    corr = m3.CORRELATION_MATRIX.copy()
    sub_corr = m3.CORR_WITH_SUBSCRIPTION_TABLE.set_index("variable")["correlation_with_subscription"]
    corr["subscription"] = sub_corr.reindex(corr.index)
    sub_row = sub_corr.reindex(corr.columns[:-1]).to_dict()
    sub_row["subscription"] = 1.0
    corr.loc["subscription"] = pd.Series(sub_row)
    return corr


def render() -> None:
    import dashboard.components as components
    import dashboard.theme as theme

    importlib.reload(theme)
    importlib.reload(m3)
    importlib.reload(components)

    module_page_header("Module 3 — Market Environment", "Market Environment Analysis")

    components.business_question(m3.BUSINESS_QUESTION, body_align="left")

    components.insight_card(m3.KEY_TAKEAWAY, m3.BUSINESS_IMPACT, m3.INTERPRETATION_NOTES)

    segment_heading("Supporting Evidence", kind="evidence", icon=SUPPORTING_EVIDENCE_ICON)
    st.caption(
        "Charts follow the analytical workflow used in the completed analysis report: macro indicator "
        "summaries, correlation analysis, and Month-level subscription trends. "
        "Click a tab below to switch chart group."
    )

    group_tabs = st.tabs(m3.CHART_GROUPS, key=evidence_tabs_key(MODULE_KEY), on_change="rerun")

    with group_tabs[0]:
        components.render_plotly_chart(
            components.build_macro_trend_chart(m3.MONTHLY_MARKET_TABLE),
            key="m3_macro_trend",
        )
        static_figure(m3.FIGURES["1. Macro Trend"], "Macro Trend vs Subscription")

    with group_tabs[1]:
        components.render_plotly_chart(
            components.build_dual_axis_metric_chart(
                m3.MONTHLY_MARKET_TABLE,
                "cons_price_idx",
                "Consumer Price Index",
                "Consumer Price Index vs Subscription Rate",
            ),
            key="m3_consumer_price",
        )
        static_figure(m3.FIGURES["2. Consumer Price"], "Consumer Price Index vs Subscription Rate")

    with group_tabs[2]:
        components.render_plotly_chart(
            components.build_dual_axis_metric_chart(
                m3.MONTHLY_MARKET_TABLE,
                "cons_conf_idx",
                "Consumer Confidence Index",
                "Consumer Confidence Index vs Subscription Rate",
            ),
            key="m3_consumer_confidence",
        )
        static_figure(m3.FIGURES["3. Consumer Confidence"], "Consumer Confidence Index vs Subscription Rate")

    with group_tabs[3]:
        components.render_plotly_chart(
            components.build_correlation_heatmap(_correlation_heatmap_matrix()),
            key="m3_correlation_heatmap",
        )
        static_figure(m3.FIGURES["4. Correlation Heatmap"], "Correlation Heatmap")

    with group_tabs[4]:
        components.render_plotly_chart(
            components.build_correlation_bar_chart(m3.CORR_WITH_SUBSCRIPTION_TABLE),
            key="m3_correlation_bar",
        )
        static_figure(m3.FIGURES["5. Correlation Bar"], "Correlation with Subscription")

    with group_tabs[5]:
        st.markdown(
            "Distribution quartiles are not part of the tabulated summary results, so the original "
            "report figure is shown directly below rather than being re-derived."
        )
        static_figure(m3.FIGURES["6. Boxplots"], "Macro Variable Boxplots by Subscription Status", expanded=True)
        data_table(m3.MACRO_BY_SUBSCRIPTION_TABLE, caption="Mean / median comparison (Yes vs No) — Module 3 Summary Report, Table 2.")

    segment_heading("Supporting Tables", kind="tables", icon=SUPPORTING_TABLES_ICON)
    table_tabs = st.tabs(list(m3.SUPPORTING_TABLES.keys()))
    for tab, name in zip(table_tabs, m3.SUPPORTING_TABLES.keys()):
        with tab:
            data_table(m3.SUPPORTING_TABLES[name], caption=f"Source: Module 3 Summary Report — Table for {name}.")
