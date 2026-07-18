"""Module 3 - Market Environment data, transcribed from module3_market_environment_analysis_summary.md.

All numbers are copied as-is from the already-completed analysis report.
"""

from __future__ import annotations

import pandas as pd

BUSINESS_QUESTION = (
    "Are macroeconomic conditions associated with subscription outcomes, and should market "
    "environment be considered when planning telephone marketing strategy?"
)

KEY_TAKEAWAY = (
    "Macroeconomic conditions show observed statistical associations with subscription "
    "outcomes. `nr.employed` has the largest absolute correlation with subscription "
    "(r=-0.3547), followed by `euribor3m` (r=-0.3077) and `emp.var.rate` (r=-0.2983). "
    "`cons.price.idx` is weaker (r=-0.1361), and `cons.conf.idx` is the weakest macro "
    "indicator in this dataset (r=0.0548)."
)

BUSINESS_IMPACT = [
    "Market Environment should be considered as <b>background context</b> when planning "
    "campaigns and evaluating performance, especially when comparing results across months.",
    "`nr.employed`, `euribor3m`, and `emp.var.rate` provide the most useful macroeconomic reference "
    "indicators for monitoring market conditions and interpreting campaign performance across "
    "different months.",
    "When campaign performance differs noticeably across months, Market Environment provides useful "
    "explanatory context alongside campaign execution.",
    "Macroeconomic indicators should complement Customer Targeting (Module 1) and Campaign Strategy "
    "(Module 2) findings rather than replace them in business decision-making.",
]

INTERPRETATION_NOTES = [
    "Correlation does not imply causation — these are statistical associations only, not evidence "
    "that macroeconomic changes directly cause subscription behavior.",
    "Macroeconomic variables are highly correlated with calendar month: customers contacted in the "
    "same period share the same market environment, so calendar month, campaign timing, and "
    "macroeconomic context cannot be cleanly separated in this descriptive analysis.",
    "Results should be interpreted as trend associations over one campaign period, not generalized "
    "to all market environments or economic cycles.",
    "Several macro indicators are highly correlated with each other (`emp.var.rate` & `euribor3m` "
    "r=0.972; `euribor3m` & `nr.employed` r=0.945; `emp.var.rate` & `nr.employed` r=0.907). No "
    "single macroeconomic indicator should be interpreted as an independent business driver.",
]

# ---------------------------------------------------------------------------
# Supporting tables
# ---------------------------------------------------------------------------

MACRO_SUMMARY_TABLE = pd.DataFrame(
    [
        {"variable": "emp.var.rate", "count": 41176, "mean": 0.0819, "median": 1.1000, "std": 1.5709, "min": -3.4000, "max": 1.4000},
        {"variable": "cons.price.idx", "count": 41176, "mean": 93.5757, "median": 93.7490, "std": 0.5788, "min": 92.2010, "max": 94.7670},
        {"variable": "cons.conf.idx", "count": 41176, "mean": -40.5029, "median": -41.8000, "std": 4.6279, "min": -50.8000, "max": -26.9000},
        {"variable": "euribor3m", "count": 41176, "mean": 3.6213, "median": 4.8570, "std": 1.7344, "min": 0.6340, "max": 5.0450},
        {"variable": "nr.employed", "count": 41176, "mean": 5167.0349, "median": 5191.0000, "std": 72.2514, "min": 4963.6000, "max": 5228.1000},
    ]
)

MACRO_BY_SUBSCRIPTION_TABLE = pd.DataFrame(
    [
        {"variable": "emp.var.rate", "mean_yes": -1.2331, "mean_no": 0.2489, "mean_diff": -1.4820, "median_yes": -1.8000, "median_no": 1.1000},
        {"variable": "cons.price.idx", "mean_yes": 93.3546, "mean_no": 93.6038, "mean_diff": -0.2492, "median_yes": 93.2000, "median_no": 93.9180},
        {"variable": "cons.conf.idx", "mean_yes": -39.7911, "mean_no": -40.5932, "mean_diff": 0.8021, "median_yes": -40.4000, "median_no": -41.8000},
        {"variable": "euribor3m", "mean_yes": 2.1234, "mean_no": 3.8115, "mean_diff": -1.6881, "median_yes": 1.2660, "median_no": 4.8570},
        {"variable": "nr.employed", "mean_yes": 5095.1201, "mean_no": 5176.1657, "mean_diff": -81.0456, "median_yes": 5099.1000, "median_no": 5195.8000},
    ]
)

MONTHLY_MARKET_TABLE = pd.DataFrame(
    [
        {"month": "mar", "count": 546, "yes": 276, "subscription_rate": 0.5055, "emp_var_rate": -1.8000, "cons_price_idx": 93.0973, "cons_conf_idx": -42.6505, "euribor3m": 1.1627, "nr_employed": 5055.3901},
        {"month": "apr", "count": 2631, "yes": 539, "subscription_rate": 0.2049, "emp_var_rate": -1.8000, "cons_price_idx": 93.1196, "cons_conf_idx": -46.2733, "euribor3m": 1.3610, "nr_employed": 5093.1214},
        {"month": "may", "count": 13767, "yes": 886, "subscription_rate": 0.0644, "emp_var_rate": -0.1649, "cons_price_idx": 93.5289, "cons_conf_idx": -40.5792, "euribor3m": 3.2937, "nr_employed": 5149.5222},
        {"month": "jun", "count": 5318, "yes": 559, "subscription_rate": 0.1051, "emp_var_rate": 0.6884, "cons_price_idx": 94.2454, "cons_conf_idx": -41.5794, "euribor3m": 4.2569, "nr_employed": 5197.4932},
        {"month": "jul", "count": 7169, "yes": 648, "subscription_rate": 0.0904, "emp_var_rate": 1.1594, "cons_price_idx": 93.8951, "cons_conf_idx": -42.3712, "euribor3m": 4.6860, "nr_employed": 5214.0900},
        {"month": "aug", "count": 6176, "yes": 655, "subscription_rate": 0.1061, "emp_var_rate": 0.7469, "cons_price_idx": 93.3110, "cons_conf_idx": -35.5970, "euribor3m": 4.3004, "nr_employed": 5200.2393},
        {"month": "sep", "count": 570, "yes": 256, "subscription_rate": 0.4491, "emp_var_rate": -2.1774, "cons_price_idx": 93.3465, "cons_conf_idx": -33.8932, "euribor3m": 0.8348, "nr_employed": 4988.8479},
        {"month": "oct", "count": 717, "yes": 315, "subscription_rate": 0.4393, "emp_var_rate": -2.4372, "cons_price_idx": 93.1761, "cons_conf_idx": -34.5916, "euribor3m": 1.2008, "nr_employed": 5018.8257},
        {"month": "nov", "count": 4100, "yes": 416, "subscription_rate": 0.1015, "emp_var_rate": -0.4186, "cons_price_idx": 93.2009, "cons_conf_idx": -41.2386, "euribor3m": 3.7230, "nr_employed": 5173.0257},
        {"month": "dec", "count": 182, "yes": 89, "subscription_rate": 0.4890, "emp_var_rate": -2.8462, "cons_price_idx": 92.7154, "cons_conf_idx": -33.7088, "euribor3m": 0.8653, "nr_employed": 5031.8956},
    ]
)

CORRELATION_MATRIX = pd.DataFrame(
    [
        {"variable": "emp.var.rate", "emp.var.rate": 1.0000, "cons.price.idx": 0.7753, "cons.conf.idx": 0.1963, "euribor3m": 0.9722, "nr.employed": 0.9069},
        {"variable": "cons.price.idx", "emp.var.rate": 0.7753, "cons.price.idx": 1.0000, "cons.conf.idx": 0.0592, "euribor3m": 0.6882, "nr.employed": 0.5219},
        {"variable": "cons.conf.idx", "emp.var.rate": 0.1963, "cons.price.idx": 0.0592, "cons.conf.idx": 1.0000, "euribor3m": 0.2779, "nr.employed": 0.1007},
        {"variable": "euribor3m", "emp.var.rate": 0.9722, "cons.price.idx": 0.6882, "cons.conf.idx": 0.2779, "euribor3m": 1.0000, "nr.employed": 0.9451},
        {"variable": "nr.employed", "emp.var.rate": 0.9069, "cons.price.idx": 0.5219, "cons.conf.idx": 0.1007, "euribor3m": 0.9451, "nr.employed": 1.0000},
    ]
).set_index("variable")

CORR_WITH_SUBSCRIPTION_TABLE = pd.DataFrame(
    [
        {"rank": 1, "variable": "nr.employed", "correlation_with_subscription": -0.3547},
        {"rank": 2, "variable": "euribor3m", "correlation_with_subscription": -0.3077},
        {"rank": 3, "variable": "emp.var.rate", "correlation_with_subscription": -0.2983},
        {"rank": 4, "variable": "cons.price.idx", "correlation_with_subscription": -0.1361},
        {"rank": 5, "variable": "cons.conf.idx", "correlation_with_subscription": 0.0548},
    ]
)

HIGH_CORR_PAIRS_TABLE = pd.DataFrame(
    [
        {"variable_1": "emp.var.rate", "variable_2": "euribor3m", "correlation": 0.9722},
        {"variable_1": "euribor3m", "variable_2": "nr.employed", "correlation": 0.9451},
        {"variable_1": "emp.var.rate", "variable_2": "nr.employed", "correlation": 0.9069},
    ]
)

SUPPORTING_TABLES = {
    "Macro Summary Stats": MACRO_SUMMARY_TABLE,
    "Macro by Subscription": MACRO_BY_SUBSCRIPTION_TABLE,
    "Monthly Market Summary": MONTHLY_MARKET_TABLE,
    "Correlation with Subscription": CORR_WITH_SUBSCRIPTION_TABLE,
    "High Correlation Pairs": HIGH_CORR_PAIRS_TABLE,
}

# ---------------------------------------------------------------------------
# Chart groups in the module's analysis-flow order.
# ---------------------------------------------------------------------------

CHART_GROUPS = [
    "1. Macro Trend",
    "2. Consumer Price",
    "3. Consumer Confidence",
    "4. Correlation Heatmap",
    "5. Correlation Bar",
    "6. Boxplots",
]

FIGURES = {
    "1. Macro Trend": "module3_market_environment_analysis/figure2_macro_trend_vs_subscription.png",
    "2. Consumer Price": "module3_market_environment_analysis/figure3_consumer_price_vs_subscription.png",
    "3. Consumer Confidence": "module3_market_environment_analysis/figure4_consumer_confidence_vs_subscription.png",
    "4. Correlation Heatmap": "module3_market_environment_analysis/figure5_correlation_heatmap.png",
    "5. Correlation Bar": "module3_market_environment_analysis/figure6_correlation_with_subscription.png",
    "6. Boxplots": "module3_market_environment_analysis/figure1_macro_boxplots_by_subscription.png",
}

OVERALL_RATE = 0.1127
