"""Module 1 - Customer Profile data, transcribed from module1_customer_profile_summary.md.

All numbers below are copied as-is from the already-completed analysis report.
No statistic here is recalculated from the raw dataset.
"""

from __future__ import annotations

import pandas as pd

BUSINESS_QUESTION = "Which customer characteristics are associated with a higher subscription rate for term deposits?"

KEY_TAKEAWAY = (
    "Customer characteristics show observed associations with term deposit subscription, with "
    "`job` exhibiting the widest category-level subscription-rate spread (0.2453) and `personal loan` the "
    "narrowest (0.0053). The most business-useful view comes from combining conversion rate, "
    "group size, contribution to subscribers, and quadrant placement — not conversion rate alone. "
    "`age` differs only slightly between subscribers and non-subscribers (~1 year), so it should not "
    "be used as a primary customer-targeting differentiator."
)

BUSINESS_IMPACT = [
    "<b>High-potential segments</b> combine above-average observed subscription rates with sufficient sample "
    "support, making them suitable candidates for customer-targeting prioritization. Representative "
    "examples include `student` and `retired` (`job`), `university.degree` (`education`), and `single` (`marital`).",
    "<b>High-impact segments</b> contribute a substantial share of total subscribers because of their scale, "
    "even when their observed subscription rates are close to the overall baseline. Representative "
    "examples include `admin.` (`job`) and `married` (`marital`). These segments are important when the "
    "objective is maximizing overall subscriber volume rather than identifying the highest-converting "
    "customer groups.",
    "<b>Stable reference features</b> show relatively little differentiation across categories and therefore "
    "provide limited value as primary customer-targeting variables. `personal loan` (rate spread 0.0053), "
    "`housing`, and `age` all show relatively small observed differences in this module. These are "
    "best used as baseline references when interpreting stronger differentiating signals from `job`, "
    "`education`, or `marital` status.",
    "Customer Targeting findings should be interpreted together with Campaign Strategy (Module 2) and "
    "Market Environment (Module 3) to support balanced telephone marketing decisions.",
]

INTERPRETATION_NOTES = [
    "High conversion rate does not necessarily imply high business impact — a small high-rate group "
    "(e.g. `student`, n=875) contributes far fewer total subscribers than a large near-baseline group "
    "(e.g. `married`, n=24,921).",
    "Small sample sizes should be interpreted cautiously: `marital=unknown` (n=80), "
    "`education=illiterate` (n=18), and `default=yes` (n=3) are flagged as small-sample categories.",
    "These are descriptive statistical associations only — this module provides customer-targeting "
    "decision support that can inform segmentation and prioritization discussions. It does not establish "
    "causal effects and should not be treated as a predictive scoring model.",
]

# ---------------------------------------------------------------------------
# Supporting Tables (Table 3-8 in the report; each already includes count,
# percentage, subscription_rate and contribution_to_yes).
# ---------------------------------------------------------------------------

AGE_SUMMARY = pd.DataFrame(
    [
        {"Group": "Overall", "Count": 41176, "Mean Age": 40.02, "Median Age": 38.0, "Std Dev": 10.42, "Min": 17, "Max": 98},
        {"Group": "Subscribed (yes)", "Count": 4639, "Mean Age": 40.91, "Median Age": 37.0, "Std Dev": 13.84, "Min": 17, "Max": 98},
        {"Group": "Not Subscribed (no)", "Count": 36537, "Mean Age": 39.91, "Median Age": 38.0, "Std Dev": 9.90, "Min": 17, "Max": 95},
    ]
)

JOB_TABLE = pd.DataFrame(
    [
        {"rank": 1, "job": "student", "count": 875, "percentage": 2.13, "yes": 275, "subscription_rate": 0.3143, "contribution_to_yes": 0.0593, "small_sample": "No"},
        {"rank": 2, "job": "retired", "count": 1718, "percentage": 4.17, "yes": 434, "subscription_rate": 0.2526, "contribution_to_yes": 0.0936, "small_sample": "No"},
        {"rank": 3, "job": "unemployed", "count": 1014, "percentage": 2.46, "yes": 144, "subscription_rate": 0.1420, "contribution_to_yes": 0.0310, "small_sample": "No"},
        {"rank": 4, "job": "admin.", "count": 10419, "percentage": 25.30, "yes": 1351, "subscription_rate": 0.1297, "contribution_to_yes": 0.2912, "small_sample": "No"},
        {"rank": 5, "job": "management", "count": 2924, "percentage": 7.10, "yes": 328, "subscription_rate": 0.1122, "contribution_to_yes": 0.0707, "small_sample": "No"},
        {"rank": 6, "job": "unknown", "count": 330, "percentage": 0.80, "yes": 37, "subscription_rate": 0.1121, "contribution_to_yes": 0.0080, "small_sample": "No"},
        {"rank": 7, "job": "technician", "count": 6739, "percentage": 16.37, "yes": 730, "subscription_rate": 0.1083, "contribution_to_yes": 0.1574, "small_sample": "No"},
        {"rank": 8, "job": "self-employed", "count": 1421, "percentage": 3.45, "yes": 149, "subscription_rate": 0.1049, "contribution_to_yes": 0.0321, "small_sample": "No"},
        {"rank": 9, "job": "housemaid", "count": 1060, "percentage": 2.57, "yes": 106, "subscription_rate": 0.1000, "contribution_to_yes": 0.0228, "small_sample": "No"},
        {"rank": 10, "job": "entrepreneur", "count": 1456, "percentage": 3.54, "yes": 124, "subscription_rate": 0.0852, "contribution_to_yes": 0.0267, "small_sample": "No"},
        {"rank": 11, "job": "services", "count": 3967, "percentage": 9.63, "yes": 323, "subscription_rate": 0.0814, "contribution_to_yes": 0.0696, "small_sample": "No"},
        {"rank": 12, "job": "blue-collar", "count": 9253, "percentage": 22.47, "yes": 638, "subscription_rate": 0.0690, "contribution_to_yes": 0.1375, "small_sample": "No"},
    ]
)

MARITAL_TABLE = pd.DataFrame(
    [
        {"rank": 1, "marital": "unknown", "count": 80, "percentage": 0.19, "yes": 12, "subscription_rate": 0.1500, "contribution_to_yes": 0.0026, "small_sample": "Yes"},
        {"rank": 2, "marital": "single", "count": 11564, "percentage": 28.08, "yes": 1620, "subscription_rate": 0.1401, "contribution_to_yes": 0.3492, "small_sample": "No"},
        {"rank": 3, "marital": "divorced", "count": 4611, "percentage": 11.20, "yes": 476, "subscription_rate": 0.1032, "contribution_to_yes": 0.1026, "small_sample": "No"},
        {"rank": 4, "marital": "married", "count": 24921, "percentage": 60.52, "yes": 2531, "subscription_rate": 0.1016, "contribution_to_yes": 0.5456, "small_sample": "No"},
    ]
)

EDUCATION_TABLE = pd.DataFrame(
    [
        {"rank": 1, "education": "illiterate", "count": 18, "percentage": 0.04, "yes": 4, "subscription_rate": 0.2222, "contribution_to_yes": 0.0009, "small_sample": "Yes"},
        {"rank": 2, "education": "unknown", "count": 1730, "percentage": 4.20, "yes": 251, "subscription_rate": 0.1451, "contribution_to_yes": 0.0541, "small_sample": "No"},
        {"rank": 3, "education": "university.degree", "count": 12164, "percentage": 29.54, "yes": 1669, "subscription_rate": 0.1372, "contribution_to_yes": 0.3598, "small_sample": "No"},
        {"rank": 4, "education": "professional.course", "count": 5240, "percentage": 12.73, "yes": 595, "subscription_rate": 0.1135, "contribution_to_yes": 0.1283, "small_sample": "No"},
        {"rank": 5, "education": "high.school", "count": 9512, "percentage": 23.10, "yes": 1031, "subscription_rate": 0.1084, "contribution_to_yes": 0.2222, "small_sample": "No"},
        {"rank": 6, "education": "basic.4y", "count": 4176, "percentage": 10.14, "yes": 428, "subscription_rate": 0.1025, "contribution_to_yes": 0.0923, "small_sample": "No"},
        {"rank": 7, "education": "basic.6y", "count": 2291, "percentage": 5.56, "yes": 188, "subscription_rate": 0.0821, "contribution_to_yes": 0.0405, "small_sample": "No"},
        {"rank": 8, "education": "basic.9y", "count": 6045, "percentage": 14.68, "yes": 473, "subscription_rate": 0.0782, "contribution_to_yes": 0.1020, "small_sample": "No"},
    ]
)

DEFAULT_TABLE = pd.DataFrame(
    [
        {"rank": 1, "default": "no", "count": 32577, "percentage": 79.12, "yes": 4196, "subscription_rate": 0.1288, "contribution_to_yes": 0.9045, "small_sample": "No"},
        {"rank": 2, "default": "unknown", "count": 8596, "percentage": 20.88, "yes": 443, "subscription_rate": 0.0515, "contribution_to_yes": 0.0955, "small_sample": "No"},
        {"rank": 3, "default": "yes", "count": 3, "percentage": 0.01, "yes": 0, "subscription_rate": 0.0000, "contribution_to_yes": 0.0000, "small_sample": "Yes"},
    ]
)

HOUSING_TABLE = pd.DataFrame(
    [
        {"rank": 1, "housing": "yes", "count": 21571, "percentage": 52.39, "yes": 2507, "subscription_rate": 0.1162, "contribution_to_yes": 0.5404, "small_sample": "No"},
        {"rank": 2, "housing": "no", "count": 18615, "percentage": 45.21, "yes": 2025, "subscription_rate": 0.1088, "contribution_to_yes": 0.4365, "small_sample": "No"},
        {"rank": 3, "housing": "unknown", "count": 990, "percentage": 2.40, "yes": 107, "subscription_rate": 0.1081, "contribution_to_yes": 0.0231, "small_sample": "No"},
    ]
)

LOAN_TABLE = pd.DataFrame(
    [
        {"rank": 1, "loan": "no", "count": 33938, "percentage": 82.42, "yes": 3849, "subscription_rate": 0.1134, "contribution_to_yes": 0.8297, "small_sample": "No"},
        {"rank": 2, "loan": "yes", "count": 6248, "percentage": 15.17, "yes": 683, "subscription_rate": 0.1093, "contribution_to_yes": 0.1472, "small_sample": "No"},
        {"rank": 3, "loan": "unknown", "count": 990, "percentage": 2.40, "yes": 107, "subscription_rate": 0.1081, "contribution_to_yes": 0.0231, "small_sample": "No"},
    ]
)

# Internal feature keys (match dataset / report tables). Display labels for tabs/UI only.
FEATURE_LABELS = {
    "Age": "Age",
    "Job": "Job",
    "Education": "Education",
    "Marital": "Marital",
    "Default": "Default",
    "Housing": "Housing",
    "Loan": "Personal Loan",
}

CHART_TABLES = {
    "Job": JOB_TABLE,
    "Marital": MARITAL_TABLE,
    "Education": EDUCATION_TABLE,
    "Default": DEFAULT_TABLE,
    "Housing": HOUSING_TABLE,
    "Loan": LOAN_TABLE,
}

SUPPORTING_TABLES = {
    "Age": AGE_SUMMARY,
    "Job": JOB_TABLE,
    "Education": EDUCATION_TABLE,
    "Marital": MARITAL_TABLE,
    "Default": DEFAULT_TABLE,
    "Housing": HOUSING_TABLE,
    "Loan": LOAN_TABLE,
}

# ---------------------------------------------------------------------------
# Quadrant tables (X = subscription_rate, Y = contribution_to_yes)
# ---------------------------------------------------------------------------

QUADRANT_TABLES = {
    "Job": (
        pd.DataFrame(
            [
                {"category": "student", "count": 875, "subscription_rate": 0.3143, "contribution_to_yes": 0.0593, "small_sample": "No", "quadrant": "Q2: High Conversion + Low Contribution"},
                {"category": "retired", "count": 1718, "subscription_rate": 0.2526, "contribution_to_yes": 0.0936, "small_sample": "No", "quadrant": "Q1: High Conversion + High Contribution"},
                {"category": "unemployed", "count": 1014, "subscription_rate": 0.1420, "contribution_to_yes": 0.0310, "small_sample": "No", "quadrant": "Q2: High Conversion + Low Contribution"},
                {"category": "admin.", "count": 10419, "subscription_rate": 0.1297, "contribution_to_yes": 0.2912, "small_sample": "No", "quadrant": "Q3: Low Conversion + High Contribution"},
                {"category": "management", "count": 2924, "subscription_rate": 0.1122, "contribution_to_yes": 0.0707, "small_sample": "No", "quadrant": "Q4: Low Conversion + Low Contribution"},
                {"category": "unknown", "count": 330, "subscription_rate": 0.1121, "contribution_to_yes": 0.0080, "small_sample": "No", "quadrant": "Q4: Low Conversion + Low Contribution"},
                {"category": "technician", "count": 6739, "subscription_rate": 0.1083, "contribution_to_yes": 0.1574, "small_sample": "No", "quadrant": "Q3: Low Conversion + High Contribution"},
                {"category": "self-employed", "count": 1421, "subscription_rate": 0.1049, "contribution_to_yes": 0.0321, "small_sample": "No", "quadrant": "Q4: Low Conversion + Low Contribution"},
                {"category": "housemaid", "count": 1060, "subscription_rate": 0.1000, "contribution_to_yes": 0.0228, "small_sample": "No", "quadrant": "Q4: Low Conversion + Low Contribution"},
                {"category": "entrepreneur", "count": 1456, "subscription_rate": 0.0852, "contribution_to_yes": 0.0267, "small_sample": "No", "quadrant": "Q4: Low Conversion + Low Contribution"},
                {"category": "services", "count": 3967, "subscription_rate": 0.0814, "contribution_to_yes": 0.0696, "small_sample": "No", "quadrant": "Q4: Low Conversion + Low Contribution"},
                {"category": "blue-collar", "count": 9253, "subscription_rate": 0.0690, "contribution_to_yes": 0.1375, "small_sample": "No", "quadrant": "Q3: Low Conversion + High Contribution"},
            ]
        ),
        {"mean_rate": 0.1343, "mean_contribution": 0.0833},
    ),
    "Education": (
        pd.DataFrame(
            [
                {"category": "illiterate", "count": 18, "subscription_rate": 0.2222, "contribution_to_yes": 0.0009, "small_sample": "Yes", "quadrant": "Q2: High Conversion + Low Contribution"},
                {"category": "unknown", "count": 1730, "subscription_rate": 0.1451, "contribution_to_yes": 0.0541, "small_sample": "No", "quadrant": "Q2: High Conversion + Low Contribution"},
                {"category": "university.degree", "count": 12164, "subscription_rate": 0.1372, "contribution_to_yes": 0.3598, "small_sample": "No", "quadrant": "Q1: High Conversion + High Contribution"},
                {"category": "professional.course", "count": 5240, "subscription_rate": 0.1135, "contribution_to_yes": 0.1283, "small_sample": "No", "quadrant": "Q3: Low Conversion + High Contribution"},
                {"category": "high.school", "count": 9512, "subscription_rate": 0.1084, "contribution_to_yes": 0.2222, "small_sample": "No", "quadrant": "Q3: Low Conversion + High Contribution"},
                {"category": "basic.4y", "count": 4176, "subscription_rate": 0.1025, "contribution_to_yes": 0.0923, "small_sample": "No", "quadrant": "Q4: Low Conversion + Low Contribution"},
                {"category": "basic.6y", "count": 2291, "subscription_rate": 0.0821, "contribution_to_yes": 0.0405, "small_sample": "No", "quadrant": "Q4: Low Conversion + Low Contribution"},
                {"category": "basic.9y", "count": 6045, "subscription_rate": 0.0782, "contribution_to_yes": 0.1020, "small_sample": "No", "quadrant": "Q4: Low Conversion + Low Contribution"},
            ]
        ),
        {"mean_rate": 0.1237, "mean_contribution": 0.1250},
    ),
    "Marital": (
        pd.DataFrame(
            [
                {"category": "unknown", "count": 80, "subscription_rate": 0.1500, "contribution_to_yes": 0.0026, "small_sample": "Yes", "quadrant": "Q2: High Conversion + Low Contribution"},
                {"category": "single", "count": 11564, "subscription_rate": 0.1401, "contribution_to_yes": 0.3492, "small_sample": "No", "quadrant": "Q1: High Conversion + High Contribution"},
                {"category": "divorced", "count": 4611, "subscription_rate": 0.1032, "contribution_to_yes": 0.1026, "small_sample": "No", "quadrant": "Q4: Low Conversion + Low Contribution"},
                {"category": "married", "count": 24921, "subscription_rate": 0.1016, "contribution_to_yes": 0.5456, "small_sample": "No", "quadrant": "Q3: Low Conversion + High Contribution"},
            ]
        ),
        {"mean_rate": 0.1237, "mean_contribution": 0.2500},
    ),
    "Housing": (
        pd.DataFrame(
            [
                {"category": "yes", "count": 21571, "subscription_rate": 0.1162, "contribution_to_yes": 0.5404, "small_sample": "No", "quadrant": "Q1: High Conversion + High Contribution"},
                {"category": "no", "count": 18615, "subscription_rate": 0.1088, "contribution_to_yes": 0.4365, "small_sample": "No", "quadrant": "Q3: Low Conversion + High Contribution"},
                {"category": "unknown", "count": 990, "subscription_rate": 0.1081, "contribution_to_yes": 0.0231, "small_sample": "No", "quadrant": "Q4: Low Conversion + Low Contribution"},
            ]
        ),
        {"mean_rate": 0.1110, "mean_contribution": 0.3333},
    ),
    "Loan": (
        pd.DataFrame(
            [
                {"category": "no", "count": 33938, "subscription_rate": 0.1134, "contribution_to_yes": 0.8297, "small_sample": "No", "quadrant": "Q1: High Conversion + High Contribution"},
                {"category": "yes", "count": 6248, "subscription_rate": 0.1093, "contribution_to_yes": 0.1472, "small_sample": "No", "quadrant": "Q4: Low Conversion + Low Contribution"},
                {"category": "unknown", "count": 990, "subscription_rate": 0.1081, "contribution_to_yes": 0.0231, "small_sample": "No", "quadrant": "Q4: Low Conversion + Low Contribution"},
            ]
        ),
        {"mean_rate": 0.1103, "mean_contribution": 0.3333},
    ),
}

QUADRANT_FIGURES = {
    "Job": "module1_customer_profile/quadrant_job.png",
    "Education": "module1_customer_profile/quadrant_education.png",
    "Marital": "module1_customer_profile/quadrant_marital.png",
    "Housing": "module1_customer_profile/quadrant_housing.png",
    "Loan": "module1_customer_profile/quadrant_loan.png",
}

CONVERSION_FIGURES = {
    "Job": "module1_customer_profile/figure3_subscription_rate_by_job.png",
    "Marital": "module1_customer_profile/figure4_subscription_rate_by_marital.png",
    "Education": "module1_customer_profile/figure5_subscription_rate_by_education.png",
    "Default": "module1_customer_profile/figure6_subscription_rate_by_default.png",
    "Housing": "module1_customer_profile/figure7_subscription_rate_by_housing.png",
    "Loan": "module1_customer_profile/figure8_subscription_rate_by_loan.png",
}

CONTRIBUTION_FIGURES = {
    "Job": "module1_customer_profile/contribution_by_job.png",
    "Marital": "module1_customer_profile/contribution_by_marital.png",
    "Education": "module1_customer_profile/contribution_by_education.png",
    "Default": "module1_customer_profile/contribution_by_default.png",
    "Housing": "module1_customer_profile/contribution_by_housing.png",
    "Loan": "module1_customer_profile/contribution_by_loan.png",
}

AGE_FIGURES = {
    "Age Distribution": "module1_customer_profile/figure1_age_distribution_histogram.png",
    "Age Boxplot by Subscription": "module1_customer_profile/figure2_age_boxplot_by_subscription_status.png",
}

OVERALL_RATE = 0.1127
