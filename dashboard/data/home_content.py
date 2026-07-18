"""Content reused verbatim (in substance) from executive_summary.md.

Nothing here is a new calculation - text is transcribed / lightly reformatted
from the completed Executive Summary so it can be rendered as dashboard
cards instead of a flat Markdown document.
"""

from __future__ import annotations

PROJECT_OBJECTIVE = (
    "This project analyzes the Bank Marketing dataset to understand which **customer**, **campaign**, and "
    "**macroeconomic** factors are associated with term deposit subscription.\n\n"
    "The cleaned dataset contains 41,176 observations (after removing 12 exact duplicate rows), "
    "with an overall subscription rate of 11.27%.\n\n"
    "⚠️ *The analysis is descriptive and business-oriented — it does not build predictive models, "
    "estimate causal effects, or introduce new scoring rules.*"
)

BUSINESS_QUESTIONS = [
    "Which customer characteristics are associated with higher term deposit subscription rates?",
    "Which telephone marketing strategies and historical campaign characteristics are associated "
    "with higher subscription rates?",
    "Are macroeconomic conditions associated with subscription outcomes, and should market "
    "environment be considered when planning telephone marketing strategy?",
]

KEY_FINDINGS = {
    "1. Customer Targeting": [
        "Customer characteristics show observed differences in subscription rates, with `job` "
        "showing the widest category-level spread and `personal loan` showing the narrowest spread in this "
        "analysis. `personal loan` status alone provides comparatively little differentiation in observed "
        "subscription rates.",
        "Customer-targeting signals are most useful when conversion rate, group size, contribution to "
        "subscribers, and quadrant placement are read together. `student`, `retired`, `single`, "
        "and `university.degree` customers are notable segments for prioritization "
        "discussion, subject to scale and sample-size context.",
        "Some large groups (e.g. `admin.`, `married`) contribute heavily to total subscribers even "
        "when their conversion rate is not the highest, simply because of their scale.",
        "`age` differences are modest — subscribers are only about one year older on average than "
        "non-subscribers, so `age` should not be treated as a primary customer-targeting differentiator "
        "by itself.",
        "Small-sample categories such as `marital=unknown`, `education=illiterate`, and "
        "`default=yes` should be interpreted cautiously and should not drive business decisions.",
    ],
    "2. Campaign Strategy": [
        "Contact Method shows one of the clearest observed differences in observed subscription rates: `cellular` contacts "
        "had a higher rate than `telephone` contacts in this dataset.",
        "Lower Campaign Frequency is associated with better outcomes — customers contacted once show "
        "the highest subscription rate, while 6+ contacts show the lowest rate.",
        "Prior campaign engagement is one of the more clearly differentiated campaign signals in "
        "this dataset. "
        "`previous >= 1`, `pdays != 999`, and especially `poutcome = success` show substantially "
        "higher observed subscription rates than customers with no prior campaign contact. "
        "Among previously contacted customers, follow-up within 0–7 days shows the highest observed "
        "subscription rate, suggesting timely follow-up may be worth consideration in campaign planning.",
        "Timing matters but should be read with volume — March has the highest subscription rate, "
        "while May has the largest campaign volume but the lowest rate. Weekday differences are modest.",
        "These findings are associations only; prior success, Previous Contact, or `cellular` contact "
        "should not be interpreted as causing subscription without further controlled analysis.",
    ],
    "3. Market Environment": [
        "Macroeconomic conditions show an observed statistical association with subscription "
        "outcomes. The largest absolute macro-related correlation with subscription is "
        "`nr.employed`, followed by `euribor3m` and `emp.var.rate`.",
        "`cons.price.idx` has a weaker association, and `cons.conf.idx` is the weakest macro "
        "indicator in this module.",
        "Market Environment should be considered as planning context when evaluating telephone "
        "marketing performance, especially when comparing results across months or market conditions.",
        "Macroeconomic indicators should not be used as the only decision basis — several indicators "
        "are highly correlated with each other, and macro variables are closely tied to `month`.",
        "The analysis does not support causal claims — it shows market conditions and subscription "
        "rates moved together during this campaign period, not that macro changes caused behavior.",
    ],
}

BUSINESS_RECOMMENDATIONS = [
    "Customer Targeting, Campaign Strategy, and Market Environment findings may be interpreted together "
    "when planning campaigns. Customer Targeting prioritization should not rely on a single variable such "
    "as `age`, `loan` status, or one high-rate category.",
    "Campaign review may focus on Contact Method and Campaign Frequency. The findings support "
    "prioritizing review of Contact Method and Campaign Frequency, including the use of `cellular` "
    "contact and avoiding excessive repeated contacts.",
    "Prior engagement may serve as a practical follow-up signal. Customers with previous positive campaign "
    "outcomes or recent prior contact show substantially higher observed subscription rates, but this "
    "should be used as a prioritization guide rather than a predictive score.",
    "Balance conversion rate with customer volume. High conversion alone should not determine "
    "customer-targeting prioritization. Contribution to subscribers and customer volume should also "
    "be considered because small segments may contribute relatively few subscribers.",
    "Market Environment context may be included in performance evaluation. Month-to-month campaign results "
    "should be assessed alongside market indicators, while clearly separating statistical association from "
    "causation.",
]

LIMITATIONS = [
    "The project is based on observational data — the analysis identifies associations, not causal effects.",
    "The target class is imbalanced: only 11.27% of observations subscribed, so rates and segment "
    "comparisons should be interpreted with class imbalance in mind.",
    "Some categories or subgroups have relatively small sample sizes, so their observed conversion "
    "rates should be interpreted cautiously.",
    "Campaign variables such as `previous`, `pdays`, and `poutcome` are highly imbalanced; most "
    "customers had no prior campaign contact.",
    "Macroeconomic variables are closely tied to `month`, and several macro indicators are highly "
    "correlated with each other, limiting the ability to isolate any single macro variable's effect.",
]

KPI_CARDS = [
    {"label": "Dataset", "value": "Bank Marketing", "help": "bank-additional-full.csv — UCI Bank Marketing dataset, Portuguese bank telemarketing campaigns"},
    {"label": "Observations", "value": "41,176", "help": "After removing 12 exact duplicate rows (41,188 raw rows -> 41,176 cleaned)"},
    {"label": "Subscription Rate", "value": "11.27%", "help": "4,639 subscribers (y=yes) out of 41,176 cleaned observations"},
    {"label": "Business Questions", "value": "3", "help": "Customer Targeting · Campaign Strategy · Market Environment"},
    {"label": "Technology", "value": "Python", "help": "Pandas · Plotly · Streamlit — descriptive analytics dashboard"},
]

MODULE_HIGHLIGHTS = [
    {
        "tag": "Module 1",
        "title": "Who to Target — Customer Targeting",
        "takeaway": "`job`, `education`, and `marital` show the clearest subscription-rate differences; "
        "`student`, `retired`, `single`, and `university.degree` are notable segments for prioritization "
        "discussion, subject to scale and sample-size context.",
    },
    {
        "tag": "Module 2",
        "title": "How to Engage — Campaign Strategy",
        "takeaway": "Contact Method (`cellular`), lower Campaign Frequency, and prior positive `poutcome` are "
        "among the clearest observed campaign signals associated with higher subscription rates.",
    },
    {
        "tag": "Module 3",
        "title": "Market Environment",
        "takeaway": "Macroeconomic conditions — especially `nr.employed`, `euribor3m`, and `emp.var.rate` — move "
        "together with subscription rate and should be used as planning context, not a standalone explanation.",
    },
]

DATASET_SOURCE = {
    "name": "Bank Marketing Dataset (bank-additional-full.csv)",
    "origin": "UCI Machine Learning Repository — direct marketing campaigns (phone calls) of a Portuguese "
    "banking institution.",
    "raw_path": "data/bank-additional/bank-additional-full.csv",
    "cleaning": "12 exact duplicate rows removed (41,188 raw rows -> 41,176 analyzed observations). "
    "No other transformation, imputation, or feature engineering was applied.",
}

FOOTER = {
    "project": "Bank Marketing Analytics Dashboard",
    "dataset": "Bank Marketing Dataset (UCI)",
    "technology": "Python · Pandas · Plotly · Streamlit",
    "repo": None,
}

# Flaticon attribution (free license) — label links to icon set; authors deduplicated in footer.
FLATICON_CREDITS = [
    {"label": "Results", "url": "https://www.flaticon.com/free-icons/results", "author": "redempticon"},
    {"label": "Summary", "url": "https://www.flaticon.com/free-icons/summary", "author": "Canticons"},
    {"label": "Define", "url": "https://www.flaticon.com/free-icons/define", "author": "VectorPortal"},
    {"label": "Find", "url": "https://www.flaticon.com/free-icons/find", "author": "IconMarketPK"},
    {"label": "Introduction", "url": "https://www.flaticon.com/free-icons/introduction", "author": "Freepik"},
    {"label": "Target (Freepik)", "url": "https://www.flaticon.com/free-icons/target", "author": "Freepik"},
    {"label": "Home", "url": "https://www.flaticon.com/free-icons/home", "author": "Ihdizein"},
    {"label": "Contact", "url": "https://www.flaticon.com/free-icons/contact", "author": "meaicon"},
    {"label": "Target (Cap Cool)", "url": "https://www.flaticon.com/free-icons/target", "author": "Cap Cool"},
    {"label": "Data table", "url": "https://www.flaticon.com/free-icons/data-table", "author": "Iconise"},
    {"label": "Research", "url": "https://www.flaticon.com/free-icons/reseach", "author": "the best icon"},
]
