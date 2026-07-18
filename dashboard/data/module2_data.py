"""Module 2 - Campaign Strategy data, transcribed from module2_campaign_strategy_summary.md.

All numbers are copied as-is from the already-completed analysis report.
"""

from __future__ import annotations

import pandas as pd

BUSINESS_QUESTION = (
    "Which telephone marketing strategies and historical campaign characteristics are associated "
    "with higher term deposit subscription rates?"
)

KEY_TAKEAWAY = (
    "Contact Method, Campaign Frequency, and prior campaign engagement show some of the clearest "
    "observed differences among campaign-related variables. `cellular` contact (14.74%) has a "
    "higher observed subscription rate than `telephone` (5.23%); subscription rate declines as "
    "repeat contacts increase; and customers with a prior successful outcome (`poutcome=success`) "
    "show an observed subscription rate of 65.11%, far above the 11.27% baseline. Among previously "
    "contacted customers, the `pdays 0–7 day` group has the highest observed rate (65.76%). Timing "
    "shows high-rate but low-volume months (March, September, October, December) contrasted with "
    "the high-volume, low-rate month of May."
)

BUSINESS_IMPACT = [
    "<b>Contact Method:</b> The observed results support considering greater use of `cellular` contact, "
    "where operationally feasible, because it shows a substantially higher observed subscription rate "
    "in this dataset (14.74% vs 5.23% for `telephone`).",
    "<b>Previous campaign history:</b> Prior positive engagement may serve as a practical follow-up "
    "prioritization signal rather than a predictive score (`poutcome=success` at 65.11%, "
    "`previous>=1` at 26.65%, `pdays!=999` at 63.83%).",
    "<b>Follow-up Timing:</b> Among previously contacted customers (`pdays != 999`), the "
    "`0–7 day` group shows the highest observed subscription rate (65.76%, n=1,177) and accounts for "
    "most of the contacted-only day-range sample. The 15+ day group is a small sample (n=62) and "
    "should be read cautiously.",
    "<b>Campaign Frequency:</b> Observed subscription rate declines as repeat contacts increase — "
    "from 13.04% (1 contact) to 5.49% (6+ contacts). This pattern suggests diminishing returns from "
    "repeated contact in this dataset.",
    "<b>Month / Week:</b> Month-level rate and volume may be read together for calendar planning — March "
    "(50.55% rate, n=546) is high-rate/low-volume while May (6.44% rate, n=13,767) is high-volume/"
    "low-rate. Weekday differences are comparatively modest (9.95%–12.11%). Campaign planning should "
    "balance observed conversion rate with campaign volume rather than optimizing either metric in "
    "isolation.",
]

INTERPRETATION_NOTES = [
    "These findings reflect descriptive statistical associations only — prior success, Previous Contact, or "
    "`cellular` contact should not be interpreted as causing subscription without further controlled analysis.",
    "Small-sample groups should be interpreted cautiously. For example, `previous >= 3` (n=310) and "
    "the `pdays` `15+` day group (n=62) represent limited observations.",
    "`duration` was intentionally excluded because it is only known after a call ends and would not be "
    "available when planning customer contact in advance. Including it would introduce information "
    "unavailable at decision time.",
    "High-rate, low-volume Month values should not be treated as automatically scalable campaign windows.",
]

# ---------------------------------------------------------------------------
# Supporting tables
# ---------------------------------------------------------------------------

CONTACT_TABLE = pd.DataFrame(
    [
        {"contact": "cellular", "count": 26135, "percentage": 63.47, "yes": 3852, "subscription_rate": 0.1474, "rate_rank": 1, "small_sample": "No"},
        {"contact": "telephone", "count": 15041, "percentage": 36.53, "yes": 787, "subscription_rate": 0.0523, "rate_rank": 2, "small_sample": "No"},
    ]
)

POUTCOME_TABLE = pd.DataFrame(
    [
        {"poutcome": "success", "count": 1373, "percentage": 3.33, "yes": 894, "subscription_rate": 0.6511, "rate_rank": 1, "contribution_to_yes": 0.1927, "small_sample": "No"},
        {"poutcome": "failure", "count": 4252, "percentage": 10.33, "yes": 605, "subscription_rate": 0.1423, "rate_rank": 2, "contribution_to_yes": 0.1304, "small_sample": "No"},
        {"poutcome": "nonexistent", "count": 35551, "percentage": 86.34, "yes": 3140, "subscription_rate": 0.0883, "rate_rank": 3, "contribution_to_yes": 0.6769, "small_sample": "No"},
    ]
)

PREVIOUS_TABLE = pd.DataFrame(
    [
        {"previous_group": "0", "count": 35551, "percentage": 86.34, "yes": 3140, "subscription_rate": 0.0883, "rate_rank": 4, "small_sample": "No"},
        {"previous_group": "1", "count": 4561, "percentage": 11.08, "yes": 967, "subscription_rate": 0.2120, "rate_rank": 3, "small_sample": "No"},
        {"previous_group": "2", "count": 754, "percentage": 1.83, "yes": 350, "subscription_rate": 0.4642, "rate_rank": 2, "small_sample": "No"},
        {"previous_group": "3+", "count": 310, "percentage": 0.75, "yes": 182, "subscription_rate": 0.5871, "rate_rank": 1, "small_sample": "No"},
    ]
)

PREVIOUS_BINARY_TABLE = pd.DataFrame(
    [
        {"previous_binary": "0", "count": 35551, "percentage": 86.34, "yes": 3140, "subscription_rate": 0.0883, "rate_rank": 2, "small_sample": "No"},
        {"previous_binary": ">=1", "count": 5625, "percentage": 13.66, "yes": 1499, "subscription_rate": 0.2665, "rate_rank": 1, "small_sample": "No"},
    ]
)

CAMPAIGN_FREQ_TABLE = pd.DataFrame(
    [
        {"campaign_group": "1", "count": 17634, "percentage": 42.83, "yes": 2299, "subscription_rate": 0.1304, "rate_rank": 1, "small_sample": "No"},
        {"campaign_group": "2", "count": 10568, "percentage": 25.67, "yes": 1211, "subscription_rate": 0.1146, "rate_rank": 2, "small_sample": "No"},
        {"campaign_group": "3", "count": 5340, "percentage": 12.97, "yes": 574, "subscription_rate": 0.1075, "rate_rank": 3, "small_sample": "No"},
        {"campaign_group": "4", "count": 2650, "percentage": 6.44, "yes": 249, "subscription_rate": 0.0940, "rate_rank": 4, "small_sample": "No"},
        {"campaign_group": "5", "count": 1599, "percentage": 3.88, "yes": 120, "subscription_rate": 0.0750, "rate_rank": 5, "small_sample": "No"},
        {"campaign_group": "6+", "count": 3385, "percentage": 8.22, "yes": 186, "subscription_rate": 0.0549, "rate_rank": 6, "small_sample": "No"},
    ]
)

PDAYS_STATUS_TABLE = pd.DataFrame(
    [
        {"pdays_contact_status": "Previously Not Contacted (pdays = 999)", "count": 39661, "percentage": 96.32, "yes": 3672, "subscription_rate": 0.0926, "rate_rank": 2, "small_sample": "No"},
        {"pdays_contact_status": "Previously Contacted (pdays != 999)", "count": 1515, "percentage": 3.68, "yes": 967, "subscription_rate": 0.6383, "rate_rank": 1, "small_sample": "No"},
    ]
)

PDAYS_RANGE_TABLE = pd.DataFrame(
    [
        {"pdays_days_group": "0-7", "count": 1177, "percentage": 77.69, "yes": 774, "subscription_rate": 0.6576, "rate_rank": 1, "small_sample": "No"},
        {"pdays_days_group": "8-14", "count": 276, "percentage": 18.22, "yes": 157, "subscription_rate": 0.5688, "rate_rank": 3, "small_sample": "No"},
        {"pdays_days_group": "15+", "count": 62, "percentage": 4.09, "yes": 36, "subscription_rate": 0.5806, "rate_rank": 2, "small_sample": "Yes"},
    ]
)

MONTH_TABLE = pd.DataFrame(
    [
        {"month": "mar", "count": 546, "percentage": 1.33, "yes": 276, "subscription_rate": 0.5055, "rate_rank": 1, "small_sample": "No"},
        {"month": "apr", "count": 2631, "percentage": 6.39, "yes": 539, "subscription_rate": 0.2049, "rate_rank": 5, "small_sample": "No"},
        {"month": "may", "count": 13767, "percentage": 33.43, "yes": 886, "subscription_rate": 0.0644, "rate_rank": 10, "small_sample": "No"},
        {"month": "jun", "count": 5318, "percentage": 12.92, "yes": 559, "subscription_rate": 0.1051, "rate_rank": 7, "small_sample": "No"},
        {"month": "jul", "count": 7169, "percentage": 17.41, "yes": 648, "subscription_rate": 0.0904, "rate_rank": 9, "small_sample": "No"},
        {"month": "aug", "count": 6176, "percentage": 15.00, "yes": 655, "subscription_rate": 0.1061, "rate_rank": 6, "small_sample": "No"},
        {"month": "sep", "count": 570, "percentage": 1.38, "yes": 256, "subscription_rate": 0.4491, "rate_rank": 3, "small_sample": "No"},
        {"month": "oct", "count": 717, "percentage": 1.74, "yes": 315, "subscription_rate": 0.4393, "rate_rank": 4, "small_sample": "No"},
        {"month": "nov", "count": 4100, "percentage": 9.96, "yes": 416, "subscription_rate": 0.1015, "rate_rank": 8, "small_sample": "No"},
        {"month": "dec", "count": 182, "percentage": 0.44, "yes": 89, "subscription_rate": 0.4890, "rate_rank": 2, "small_sample": "No"},
    ]
)

WEEKDAY_TABLE = pd.DataFrame(
    [
        {"day_of_week": "mon", "count": 8512, "percentage": 20.67, "yes": 847, "subscription_rate": 0.0995, "rate_rank": 5, "small_sample": "No"},
        {"day_of_week": "tue", "count": 8086, "percentage": 19.64, "yes": 953, "subscription_rate": 0.1179, "rate_rank": 2, "small_sample": "No"},
        {"day_of_week": "wed", "count": 8134, "percentage": 19.75, "yes": 949, "subscription_rate": 0.1167, "rate_rank": 3, "small_sample": "No"},
        {"day_of_week": "thu", "count": 8618, "percentage": 20.93, "yes": 1044, "subscription_rate": 0.1211, "rate_rank": 1, "small_sample": "No"},
        {"day_of_week": "fri", "count": 7826, "percentage": 19.01, "yes": 846, "subscription_rate": 0.1081, "rate_rank": 4, "small_sample": "No"},
    ]
)

SUPPORTING_TABLES = {
    "Contact Method": CONTACT_TABLE,
    "Previous Outcome": POUTCOME_TABLE,
    "Previous Contacts": PREVIOUS_TABLE,
    "Previous Contacts (0 vs >=1)": PREVIOUS_BINARY_TABLE,
    "Campaign Frequency": CAMPAIGN_FREQ_TABLE,
    "Pdays": PDAYS_STATUS_TABLE,
    "Pdays Day-Range": PDAYS_RANGE_TABLE,
    "Month": MONTH_TABLE,
    "Weekday": WEEKDAY_TABLE,
}

# ---------------------------------------------------------------------------
# Chart groups in the report's analysis-flow order.
# ---------------------------------------------------------------------------

CHART_GROUPS = [
    "1. Contact Method",
    "2. Previous Campaign Outcome",
    "3. Previous Contacts",
    "4. Campaign Frequency",
    "5. Pdays",
    "6. Month / Week",
]

FIGURES = {
    "1. Contact Method": "module2_campaign_strategy/figure1_subscription_rate_by_contact.png",
    "2. Previous Campaign Outcome": "module2_campaign_strategy/figure5_subscription_rate_by_poutcome.png",
    "3. Previous Contacts": "module2_campaign_strategy/figure3_subscription_rate_by_previous_count.png",
    "4. Campaign Frequency": "module2_campaign_strategy/figure2_subscription_rate_by_campaign_frequency.png",
    "5. Pdays": "module2_campaign_strategy/figure4_subscription_rate_by_pdays_group.png",
    "6. Month / Week": "module2_campaign_strategy/figure6_monthly_volume_and_rate.png",
}

WEEKDAY_FIGURE = "module2_campaign_strategy/figure7_subscription_rate_by_weekday.png"

OVERALL_RATE = 0.1127
