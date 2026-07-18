from __future__ import annotations

import importlib

import streamlit as st

from dashboard.components import (
    SUPPORTING_EVIDENCE_ICON,
    SUPPORTING_TABLES_ICON,
    SMALL_SAMPLE_CAPTION,
    data_table,
    module_page_header,
    segment_heading,
    static_figure,
)
from dashboard.data import module2_data as m2
from dashboard.navigation import evidence_tabs_key

MODULE_KEY = "module2"


def render() -> None:
    import dashboard.components as components
    import dashboard.theme as theme

    importlib.reload(theme)
    importlib.reload(m2)
    importlib.reload(components)

    module_page_header("Module 2 — How to Engage", "Campaign Strategy Evaluation")

    components.business_question(m2.BUSINESS_QUESTION, body_align="left")

    components.insight_card(m2.KEY_TAKEAWAY, m2.BUSINESS_IMPACT, m2.INTERPRETATION_NOTES)

    segment_heading("Supporting Evidence", kind="evidence", icon=SUPPORTING_EVIDENCE_ICON)
    st.caption(
        "Charts follow the analytical workflow used in the completed analysis report: Contact Method, "
        "Previous Campaign Outcome, Previous Contacts, Campaign Frequency, Pdays, and Month / Week. "
        "Click a tab below to switch chart group."
    )
    st.caption(SMALL_SAMPLE_CAPTION)

    group_tabs = st.tabs(m2.CHART_GROUPS, key=evidence_tabs_key(MODULE_KEY), on_change="rerun")

    with group_tabs[0]:
        components.render_plotly_chart(
            components.build_subscription_rate_bar(
                m2.CONTACT_TABLE, "contact", "Subscription Rate by Contact Method", "Contact Method", m2.OVERALL_RATE
            ),
            key="m2_contact",
        )
        static_figure(m2.FIGURES["1. Contact Method"], "Subscription Rate by Contact Method")

    with group_tabs[1]:
        components.render_plotly_chart(
            components.build_subscription_rate_bar(
                m2.POUTCOME_TABLE,
                "poutcome",
                "Subscription Rate by Previous Campaign Outcome",
                "Previous Outcome (poutcome)",
                m2.OVERALL_RATE,
                extra_cols=["contribution_to_yes"],
            ),
            key="m2_poutcome",
        )
        static_figure(m2.FIGURES["2. Previous Campaign Outcome"], "Subscription Rate by Previous Campaign Outcome")

    with group_tabs[2]:
        c1, c2 = st.tabs(["By Count (0 / 1 / 2 / 3+)", "Simplified (0 vs >=1)"])
        with c1:
            components.render_plotly_chart(
                components.build_subscription_rate_bar(
                    m2.PREVIOUS_TABLE,
                    "previous_group",
                    "Subscription Rate by Previous Contact Count",
                    "Previous Contacts",
                    m2.OVERALL_RATE,
                ),
                key="m2_previous_count",
            )
        with c2:
            components.render_plotly_chart(
                components.build_subscription_rate_bar(
                    m2.PREVIOUS_BINARY_TABLE,
                    "previous_binary",
                    "Subscription Rate: Previous = 0 vs >=1",
                    "Previous Contacts (binary)",
                    m2.OVERALL_RATE,
                ),
                key="m2_previous_binary",
            )
        static_figure(m2.FIGURES["3. Previous Contacts"], "Subscription Rate by Previous Contact Count")

    with group_tabs[3]:
        components.render_plotly_chart(
            components.build_subscription_rate_bar(
                m2.CAMPAIGN_FREQ_TABLE,
                "campaign_group",
                "Subscription Rate by Campaign Frequency (This Campaign)",
                "Contacts in Current Campaign",
                m2.OVERALL_RATE,
            ),
            key="m2_campaign_freq",
        )
        static_figure(m2.FIGURES["4. Campaign Frequency"], "Subscription Rate by Campaign Frequency")

    with group_tabs[4]:
        p1, p2 = st.tabs(["Contacted vs Not Contacted", "Day-Range (Contacted Only)"])
        with p1:
            components.render_plotly_chart(
                components.build_subscription_rate_bar(
                    m2.PDAYS_STATUS_TABLE,
                    "pdays_contact_status",
                    "Subscription Rate: Pdays Contact Status",
                    "Pdays Contact Status",
                    m2.OVERALL_RATE,
                ),
                key="m2_pdays_status",
            )
        with p2:
            components.render_plotly_chart(
                components.build_subscription_rate_bar(
                    m2.PDAYS_RANGE_TABLE,
                    "pdays_days_group",
                    "Subscription Rate by Days Since Previous Contact",
                    "Days Since Previous Contact",
                    m2.OVERALL_RATE,
                ),
                key="m2_pdays_range",
            )
        static_figure(m2.FIGURES["5. Pdays"], "Pdays: Contact Status and Day-Range Distribution")

    with group_tabs[5]:
        mo, wk = st.tabs(["Monthly Volume & Rate", "Weekday"])
        with mo:
            components.render_plotly_chart(
                components.build_month_volume_rate_chart(m2.MONTH_TABLE),
                key="m2_month_volume_rate",
            )
            static_figure(m2.FIGURES["6. Month / Week"], "Monthly Campaign Volume and Subscription Rate")
        with wk:
            components.render_plotly_chart(
                components.build_subscription_rate_bar(
                    m2.WEEKDAY_TABLE, "day_of_week", "Subscription Rate by Weekday", "Day of Week", m2.OVERALL_RATE
                ),
                key="m2_weekday",
            )
            static_figure(m2.WEEKDAY_FIGURE, "Subscription Rate by Weekday")

    segment_heading(
        "Supporting Tables",
        kind="tables",
        icon=SUPPORTING_TABLES_ICON,
        block_class="db-insight-block--m2-supporting-tables",
    )
    table_tabs = st.tabs(list(m2.SUPPORTING_TABLES.keys()))
    for tab, name in zip(table_tabs, m2.SUPPORTING_TABLES.keys()):
        with tab:
            data_table(m2.SUPPORTING_TABLES[name], caption=f"Source: Module 2 Summary Report — Table for {name}.")
