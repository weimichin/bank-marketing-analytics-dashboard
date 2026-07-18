"""
Module 1 - Customer Profile Analysis
=====================================

Business Question
------------------
Which customer characteristics are associated with a higher subscription
rate for term deposits?

Analysis Goal
-------------
Describe the relationship between customer demographic / financial
characteristics and term deposit subscription. This module is descriptive
and comparative ONLY - it does not attempt to establish causal relationships
and does NOT include any predictive modeling.

Scope
-----
Only the following columns are analyzed:
    age, job, marital, education, default, housing, loan, y
Campaign behavior and macroeconomic conditions are out of scope for this
module and are analyzed separately in other modules.

Data Source (confirm before analysis)
--------------------------------------
This project ships two RAW dataset files (neither is de-duplicated):
    - data/bank-additional/bank-additional-full.csv  (full dataset, 41,188 rows)
    - data/bank-additional/bank-additional.csv       (10% sample, 4,119 rows)

There is no separately-saved "cleaned" CSV file in this project. Every EDA
module in this codebase (see eda/data_cleaning.py and eda/utils.py
`ensure_cleaned`) defines the "cleaned dataset" as:

    the FULL dataset (bank-additional-full.csv) with exact duplicate rows
    (all columns identical) removed, keeping the first occurrence.

This script follows the exact same, project-wide definition:
    1. load_data() loads bank-additional-full.csv (the RAW file) and prints
       its full path so the source is explicit before any analysis runs.
    2. data_preprocessing() immediately removes exact duplicate rows. This
       de-duplicated DataFrame is the "cleaned dataset".
    3. All statistics, tables, and figures produced below (analysis() and
       visualization()) use ONLY the cleaned dataset. The raw dataset itself
       is never analyzed directly.

Standalone usage
-----------------
    uv run python module1_customer_profile.py
    (or) python module1_customer_profile.py

This script has no dependency on any other file in this project (e.g. the
`eda` package) and can be run independently, provided pandas, numpy,
matplotlib, and seaborn are installed.

Structure
---------
    load_data()               - locate & load the raw CSV, confirm its path
    data_preprocessing()      - remove exact duplicates, select columns, verify dtypes
    analysis()                - descriptive stats, frequency tables, subscription
                                 rates, small-sample flags, ranking, and (additive)
                                 positive-class contribution + quadrant segmentation
                                 per category
    segmentation_synthesis()  - (additive, rule-based only) synthesizes High-potential /
                                 High-impact / Stable segments from the tables above;
                                 no EDA recalculation, no groupby, no ML/prediction
    visualization()           - Figures 1-8 (saved as PNG files), plus additive
                                 "contribution to positive class" bar charts and
                                 quadrant-analysis scatter plots
    generate_summary_report() - Markdown report (Observation / Key Statistics /
                                 Notable Patterns + Positive Class Contribution
                                 Analysis + Quadrant Analysis Observations + Final
                                 Segmentation Synthesis sections + supporting data tables)

Positive Class Contribution Analysis (additive section)
---------------------------------------------------------
For every categorical feature (job, marital, education, default, housing, loan),
in addition to the existing conversion rate (subscription_rate) and group size
(count) - both computed exactly as before and left unmodified - a new column
`contribution_to_yes` is added:

    contribution_to_yes = (count of y=yes within the category) / (total count of
    y=yes in the cleaned dataset)

This new metric is also presented as its own ranking (sorted by contribution,
descending) in the "Positive Class Contribution Analysis" report section, with
one bar chart per feature, without reordering the original conversion-rate
ranking used elsewhere in this script.

Quadrant Analysis (additive section, categorical feature segmentation)
--------------------------------------------------------------------------
For job, education, marital, housing, and loan, categories are plotted on:
    X-axis: Conversion Rate (subscription_rate)
    Y-axis: Contribution to Total Positive Class (contribution_to_yes)
Reference lines are drawn at the MEAN conversion rate and MEAN contribution
across that feature's own categories, splitting each scatter plot into 4
quadrants:
    Q1: High Conversion Rate + High Contribution
    Q2: High Conversion Rate + Low Contribution
    Q3: Low Conversion Rate  + High Contribution
    Q4: Low Conversion Rate  + Low Contribution
This reuses the already-computed subscription_rate / contribution_to_yes
values as-is (no recalculation, no ML/prediction) and does not alter the
existing EDA structure, table order, or prior sections.

Final Segmentation Synthesis (additive section, rule-based only)
----------------------------------------------------------------------
segmentation_synthesis() synthesizes three segment types purely by reading,
filtering, and re-labeling the already-computed tables above (category_tables,
contribution_tables, quadrant_tables). It performs NO new groupby, NO EDA
recalculation, and NO ML/prediction/scoring:
    1. High-potential segments : quadrant Q1/Q2 (conversion rate >= feature
       mean) AND a reasonable sample (count >= SMALL_SAMPLE_THRESHOLD).
    2. High-impact segments     : top contribution_rank (<= 2) per feature
       AND a large sample (count >= SMALL_SAMPLE_THRESHOLD).
    3. Stable segments          : the majority (largest-count) category per
       feature whose subscription_rate is close to the overall baseline rate
       (within STABLE_RATE_TOLERANCE), checked across all 6 categorical
       features so the pattern is not tied to a single variable.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

sns.set_theme(style="whitegrid", context="notebook")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DATA_PATH = PROJECT_ROOT / "data" / "bank-additional" / "bank-additional-full.csv"
FIGURES_DIR = PROJECT_ROOT / "images" / "module1_customer_profile"
REPORT_PATH = PROJECT_ROOT / "reports" / "module1_customer_profile_summary.md"

TARGET_COL = "y"
AGE_COL = "age"
DEMOGRAPHIC_CAT_COLS = ["job", "marital", "education"]
FINANCIAL_CAT_COLS = ["default", "housing", "loan"]
CATEGORICAL_COLS = DEMOGRAPHIC_CAT_COLS + FINANCIAL_CAT_COLS
REQUIRED_COLS = ["age", "job", "marital", "education", "default", "housing", "loan", "y"]

SMALL_SAMPLE_THRESHOLD = 100
AGE_BIN_WIDTH = 5  # years; identical bin width used across overall / by-status comparisons

TABLE_TITLES = {
    "job": "Table 3 - Job Subscription Summary",
    "marital": "Table 4 - Marital Subscription Summary",
    "education": "Table 5 - Education Subscription Summary",
    "default": "Table 6 - Default Subscription Summary",
    "housing": "Table 7 - Housing Loan Subscription Summary",
    "loan": "Table 8 - Personal Loan Subscription Summary",
}

# New (additive) section: Positive Class Contribution Analysis.
# contribution_to_yes = (count of y=yes within the category) / (total count of y=yes overall).
# This does NOT change how conversion rate (subscription_rate) or group size (count) are
# computed above; it only adds one extra, independently-computed column/section.
CONTRIBUTION_TABLE_TITLES = {
    "job": "Contribution Table - Job",
    "marital": "Contribution Table - Marital Status",
    "education": "Contribution Table - Education",
    "default": "Contribution Table - Default",
    "housing": "Contribution Table - Housing Loan",
    "loan": "Contribution Table - Personal Loan",
}

FIGURE_FILES = [
    ("figure1_age_distribution_histogram.png", "Figure 1 - Age Distribution Histogram (Overall & by Subscription Status)"),
    ("figure2_age_boxplot_by_subscription_status.png", "Figure 2 - Age Boxplot by Subscription Status"),
    ("figure3_subscription_rate_by_job.png", "Figure 3 - Subscription Rate by Job"),
    ("figure4_subscription_rate_by_marital.png", "Figure 4 - Subscription Rate by Marital Status"),
    ("figure5_subscription_rate_by_education.png", "Figure 5 - Subscription Rate by Education"),
    ("figure6_subscription_rate_by_default.png", "Figure 6 - Subscription Rate by Default Status"),
    ("figure7_subscription_rate_by_housing.png", "Figure 7 - Subscription Rate by Housing Loan"),
    ("figure8_subscription_rate_by_loan.png", "Figure 8 - Subscription Rate by Personal Loan"),
]

CONTRIBUTION_FIGURE_FILES = [
    ("contribution_by_job.png", "Contribution to Positive Class (yes) by Job"),
    ("contribution_by_marital.png", "Contribution to Positive Class (yes) by Marital Status"),
    ("contribution_by_education.png", "Contribution to Positive Class (yes) by Education"),
    ("contribution_by_default.png", "Contribution to Positive Class (yes) by Default Status"),
    ("contribution_by_housing.png", "Contribution to Positive Class (yes) by Housing Loan"),
    ("contribution_by_loan.png", "Contribution to Positive Class (yes) by Personal Loan"),
]

# New (additive) section: Quadrant Analysis for categorical feature segmentation.
# X-axis = conversion rate (subscription_rate); Y-axis = contribution_to_yes.
# Reference lines = mean of each axis across that feature's own categories.
# NOTE: `default` is intentionally excluded (not requested for quadrant analysis).
QUADRANT_VARS = ["job", "education", "marital", "housing", "loan"]

QUADRANT_VAR_LABELS = {
    "job": "Job",
    "education": "Education",
    "marital": "Marital Status",
    "housing": "Housing Loan",
    "loan": "Personal Loan",
}

QUADRANT_TABLE_TITLES = {col: f"Quadrant Table - {label}" for col, label in QUADRANT_VAR_LABELS.items()}

QUADRANT_FIGURE_FILES = [
    (f"quadrant_{col}.png", f"Quadrant Analysis - {label}") for col, label in QUADRANT_VAR_LABELS.items()
]

Q1_LABEL = "Q1: High Conversion + High Contribution"
Q2_LABEL = "Q2: High Conversion + Low Contribution"
Q3_LABEL = "Q3: Low Conversion + High Contribution"
Q4_LABEL = "Q4: Low Conversion + Low Contribution"
QUADRANT_ORDER = [Q1_LABEL, Q2_LABEL, Q3_LABEL, Q4_LABEL]
QUADRANT_COLORS = {
    Q1_LABEL: "#2ca02c",
    Q2_LABEL: "#1f77b4",
    Q3_LABEL: "#ff7f0e",
    Q4_LABEL: "#d62728",
}


def _quadrant_label(rate: float, contribution: float, rate_ref: float, contrib_ref: float) -> str:
    """Assign a category to one of the 4 quadrants based on reference lines.

    Ties (value exactly equal to the reference) are treated as "high" (>=),
    consistent with a single, deterministic tie-breaking rule.
    """
    if rate >= rate_ref and contribution >= contrib_ref:
        return Q1_LABEL
    if rate >= rate_ref and contribution < contrib_ref:
        return Q2_LABEL
    if rate < rate_ref and contribution >= contrib_ref:
        return Q3_LABEL
    return Q4_LABEL


# New (additive) section: Final Segmentation Synthesis.
# These are rule-based SYNTHESIS thresholds applied to values already computed in
# analysis() (subscription_rate, count, contribution_to_yes, contribution_rank,
# quadrant, small_sample_flag). They do NOT trigger any new groupby or EDA metric
# recalculation; no ML / prediction / scoring is used anywhere in this synthesis.
HIGH_IMPACT_CONTRIBUTION_TOP_N = 2  # top-N by the already-computed contribution_rank
STABLE_RATE_TOLERANCE = 0.03  # +/- band around the already-computed overall_rate


# ---------------------------------------------------------------------------
# load_data
# ---------------------------------------------------------------------------
def load_data(path: Path | str | None = None) -> pd.DataFrame:
    """Load the raw Bank Marketing dataset and confirm the source file path.

    NOTE: this returns the RAW data as-is. Exact-duplicate cleaning happens
    in `data_preprocessing()`, which is the ONLY function that produces the
    "cleaned dataset" used for analysis, per project-wide convention.
    """
    data_path = Path(path) if path is not None else RAW_DATA_PATH

    print("=" * 78)
    print("STEP 0: Confirm Data Source")
    print("=" * 78)
    print(f"[Data Source] File path : {data_path}")

    if not data_path.exists():
        raise FileNotFoundError(f"Raw dataset not found at: {data_path}")

    df_raw = pd.read_csv(data_path, sep=";")
    print(f"[Data Source] Raw shape : {df_raw.shape[0]} rows x {df_raw.shape[1]} columns")
    print(
        "[Data Source] This is the RAW file. Exact duplicate rows are removed in "
        "data_preprocessing() BEFORE any analysis; only the resulting CLEANED "
        "dataset is used for statistics, tables, and figures below."
    )
    return df_raw


# ---------------------------------------------------------------------------
# data_preprocessing
# ---------------------------------------------------------------------------
def data_preprocessing(df_raw: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Produce the cleaned, analysis-ready DataFrame for Module 1.

    Steps (per Module 1 Implementation Plan):
        1. Remove exact duplicate rows (all columns identical), keep first
           occurrence -> this is the "cleaned dataset".
        2. Select only the 8 required columns.
        3. Verify data types (age numeric, remaining columns categorical).
           No type conversion is applied unless a mismatch is found.
    """
    print("\n" + "=" * 78)
    print("STEP 1: Data Preprocessing")
    print("=" * 78)

    # --- Step: remove exact duplicates (defines the cleaned dataset) ---
    n_before = len(df_raw)
    n_exact_duplicates = int(df_raw.duplicated(keep="first").sum())
    df_clean_full = df_raw.drop_duplicates(keep="first").reset_index(drop=True)
    n_after = len(df_clean_full)

    print("\n[Cleaning] Exact-duplicate removal (keep first occurrence)")
    print(f"  rows before : {n_before}")
    print(f"  duplicates removed : {n_exact_duplicates}")
    print(f"  rows after (= cleaned dataset) : {n_after}")

    # --- Step 1: select required columns ---
    missing_cols = [c for c in REQUIRED_COLS if c not in df_clean_full.columns]
    if missing_cols:
        raise KeyError(f"Required columns missing from cleaned dataset: {missing_cols}")

    df = df_clean_full[REQUIRED_COLS].copy()
    print(f"\n[Column Selection] columns: {REQUIRED_COLS}")
    print(f"[Column Selection] resulting shape: {df.shape[0]} rows x {df.shape[1]} columns")

    # --- Step 2: verify data types ---
    print("\n[Dtype Verification]")
    dtype_rows = []
    for col in REQUIRED_COLS:
        expected_numeric = col == AGE_COL
        is_numeric = pd.api.types.is_numeric_dtype(df[col])
        status = "OK" if is_numeric == expected_numeric else "MISMATCH"
        dtype_rows.append(
            {
                "column": col,
                "dtype": str(df[col].dtype),
                "expected_role": "numeric" if expected_numeric else "categorical",
                "status": status,
            }
        )
        expected_label = "numeric" if expected_numeric else "categorical"
        print(f"  - {col:<10} dtype={str(df[col].dtype):<10} expected={expected_label:<12} [{status}]")

    dtype_df = pd.DataFrame(dtype_rows)
    mismatches = dtype_df[dtype_df["status"] == "MISMATCH"]
    if not mismatches.empty:
        print(
            f"[Dtype Verification] WARNING: {len(mismatches)} column(s) do not match the "
            "expected role. No automatic type conversion is applied (per plan constraints)."
        )
    else:
        print("[Dtype Verification] All columns match their expected role. No conversion needed.")

    # --- Informational note: valid 'unknown' categories are retained ---
    for col in CATEGORICAL_COLS:
        if df[col].dtype == object:
            n_unknown = int((df[col] == "unknown").sum())
            if n_unknown > 0:
                print(
                    f"[Category Note] `{col}` contains {n_unknown} 'unknown' values "
                    "(a valid recorded response, retained as-is; not treated as missing)."
                )

    prep_info: dict[str, Any] = {
        "raw_path": str(RAW_DATA_PATH),
        "n_before_dedup": n_before,
        "n_exact_duplicates_removed": n_exact_duplicates,
        "n_after_dedup": n_after,
        "n_final": len(df),
        "dtype_report": dtype_df,
    }
    return df, prep_info


# ---------------------------------------------------------------------------
# analysis
# ---------------------------------------------------------------------------
def analysis(df: pd.DataFrame) -> dict[str, Any]:
    """Compute all descriptive statistics, frequency tables, subscription-rate
    tables, small-sample flags, and rankings required by the plan."""
    print("\n" + "=" * 78)
    print("STEP 2: Analysis")
    print("=" * 78)

    results: dict[str, Any] = {}

    # ---- Table 1: Dataset Summary ----
    n_obs = len(df)
    n_yes = int((df[TARGET_COL] == "yes").sum())
    n_no = n_obs - n_yes
    overall_rate = n_yes / n_obs
    table1 = pd.DataFrame(
        [
            {
                "observations": n_obs,
                "subscribed_yes": n_yes,
                "subscribed_no": n_no,
                "subscription_rate": overall_rate,
            }
        ]
    )
    print("\n[Table 1] Dataset Summary")
    print(table1.to_string(index=False))

    # ---- Table 2: Age Summary Statistics (Overall / Yes / No) ----
    def _age_stats(s: pd.Series) -> dict[str, float]:
        return {
            "count": int(s.count()),
            "mean": s.mean(),
            "median": s.median(),
            "std": s.std(),
            "min": s.min(),
            "25%": s.quantile(0.25),
            "50%": s.quantile(0.50),
            "75%": s.quantile(0.75),
            "max": s.max(),
        }

    age_overall = _age_stats(df[AGE_COL])
    age_yes = _age_stats(df.loc[df[TARGET_COL] == "yes", AGE_COL])
    age_no = _age_stats(df.loc[df[TARGET_COL] == "no", AGE_COL])
    table2 = pd.DataFrame({"overall": age_overall, "yes": age_yes, "no": age_no}).T
    print("\n[Table 2] Age Summary Statistics (Overall / Yes / No)")
    print(table2.to_string())

    # ---- Shared age bins: identical bin width for overall vs by-status comparisons ----
    age_min, age_max = df[AGE_COL].min(), df[AGE_COL].max()
    bin_start = int(age_min // AGE_BIN_WIDTH) * AGE_BIN_WIDTH
    bin_end = (int(age_max // AGE_BIN_WIDTH) + 1) * AGE_BIN_WIDTH
    age_bins = np.arange(bin_start, bin_end + AGE_BIN_WIDTH, AGE_BIN_WIDTH)
    print(f"\n[Figure prep] Shared age bin edges (width={AGE_BIN_WIDTH}): {list(age_bins)}")

    # ---- Tables 3-8: frequency + subscription rate + small-sample flag + ranking ----
    # (conversion rate / group size formulas below are UNCHANGED from the original
    # implementation; the only addition is the `contribution_to_yes` column)
    category_tables: dict[str, pd.DataFrame] = {}
    for col in CATEGORICAL_COLS:
        grouped = (
            df.groupby(col, observed=True)
            .agg(count=(TARGET_COL, "size"), yes=(TARGET_COL, lambda s: (s == "yes").sum()))
            .reset_index()
        )
        grouped["percentage"] = grouped["count"] / n_obs * 100
        grouped["subscription_rate"] = grouped["yes"] / grouped["count"]
        grouped["small_sample_flag"] = grouped["count"] < SMALL_SAMPLE_THRESHOLD
        # New metric: contribution to total positive class (yes) = group's yes count / total yes count.
        grouped["contribution_to_yes"] = grouped["yes"] / n_yes
        grouped = grouped.sort_values("subscription_rate", ascending=False).reset_index(drop=True)
        grouped.insert(0, "rank", grouped.index + 1)
        grouped = grouped[
            [
                "rank",
                col,
                "count",
                "percentage",
                "yes",
                "subscription_rate",
                "contribution_to_yes",
                "small_sample_flag",
            ]
        ]
        category_tables[col] = grouped

        print(f"\n[{TABLE_TITLES[col]}]")
        print(grouped.to_string(index=False))

    # ---- New section: Positive Class Contribution Analysis ----
    # Separate ranking (sorted by contribution_to_yes, descending) so the ranking above
    # (sorted by subscription_rate) is left untouched.
    print("\n" + "=" * 78)
    print("STEP 2b: Positive Class Contribution Analysis (new section)")
    print("=" * 78)
    contribution_tables: dict[str, pd.DataFrame] = {}
    for col in CATEGORICAL_COLS:
        contribution_table = category_tables[col][
            [col, "count", "subscription_rate", "contribution_to_yes", "small_sample_flag"]
        ].copy()
        contribution_table = contribution_table.sort_values(
            "contribution_to_yes", ascending=False
        ).reset_index(drop=True)
        contribution_table.insert(0, "contribution_rank", contribution_table.index + 1)
        contribution_tables[col] = contribution_table

        print(f"\n[{CONTRIBUTION_TABLE_TITLES[col]}]")
        print(contribution_table.to_string(index=False))

    # ---- New section: Quadrant Analysis (categorical feature segmentation) ----
    # X-axis: subscription_rate (conversion rate); Y-axis: contribution_to_yes.
    # Both values are reused as-is from category_tables above (NOT recalculated),
    # so the original conversion-rate / group-size / contribution formulas are
    # completely unaffected. Reference lines use the MEAN of each axis, computed
    # independently per feature across that feature's own categories.
    print("\n" + "=" * 78)
    print("STEP 2c: Quadrant Analysis (new section)")
    print("=" * 78)
    quadrant_tables: dict[str, pd.DataFrame] = {}
    quadrant_refs: dict[str, dict[str, float]] = {}
    for col in QUADRANT_VARS:
        t = category_tables[col][
            [col, "count", "subscription_rate", "contribution_to_yes", "small_sample_flag"]
        ].copy()
        rate_ref = float(t["subscription_rate"].mean())
        contrib_ref = float(t["contribution_to_yes"].mean())
        t["quadrant"] = [
            _quadrant_label(rate, contrib, rate_ref, contrib_ref)
            for rate, contrib in zip(t["subscription_rate"], t["contribution_to_yes"])
        ]
        t = t.sort_values("subscription_rate", ascending=False).reset_index(drop=True)
        quadrant_tables[col] = t
        quadrant_refs[col] = {"rate_ref": rate_ref, "contrib_ref": contrib_ref}

        print(
            f"\n[{QUADRANT_TABLE_TITLES[col]}] "
            f"(reference: mean conversion rate={rate_ref:.4f}, mean contribution={contrib_ref:.4f})"
        )
        print(t.to_string(index=False))

    results.update(
        {
            "n_obs": n_obs,
            "n_yes": n_yes,
            "overall_rate": overall_rate,
            "table1_dataset_summary": table1,
            "table2_age_summary": table2,
            "age_bins": age_bins,
            "category_tables": category_tables,
            "contribution_tables": contribution_tables,
            "quadrant_tables": quadrant_tables,
            "quadrant_refs": quadrant_refs,
        }
    )
    return results


# ---------------------------------------------------------------------------
# segmentation_synthesis
# ---------------------------------------------------------------------------
def segmentation_synthesis(results: dict[str, Any]) -> dict[str, pd.DataFrame]:
    """Synthesize High-potential / High-impact / Stable segments purely from
    the already-computed category_tables, contribution_tables, and
    quadrant_tables in `results`.

    IMPORTANT: this performs NO re-computation of any EDA metric, NO new
    groupby, and NO ML / prediction / scoring. It only reads, filters, and
    re-labels values analysis() already produced:
        - subscription_rate, count, percentage  (unchanged, from category_tables)
        - contribution_to_yes, contribution_rank (unchanged, from contribution_tables)
        - quadrant, small_sample_flag            (unchanged, from quadrant_tables)
    """
    print("\n" + "=" * 78)
    print("STEP 2d: Final Segmentation Synthesis (new section)")
    print("=" * 78)

    category_tables = results["category_tables"]
    contribution_tables = results["contribution_tables"]
    quadrant_tables = results["quadrant_tables"]
    quadrant_refs = results["quadrant_refs"]
    n_obs = results["n_obs"]
    overall_rate = float(results["table1_dataset_summary"].iloc[0]["subscription_rate"])

    # ---- 1. High-potential segments: quadrant Q1/Q2 + reasonable sample ----
    # (quadrant_tables only exist for job/education/marital/housing/loan, per
    # the Quadrant Analysis section; `default` is not part of quadrant analysis)
    high_potential_rows = []
    for col, label in QUADRANT_VAR_LABELS.items():
        t = quadrant_tables[col]
        subset = t[t["quadrant"].isin([Q1_LABEL, Q2_LABEL]) & (~t["small_sample_flag"])]
        for _, row in subset.iterrows():
            high_potential_rows.append(
                {
                    "feature": label,
                    "category": row[col],
                    "count": int(row["count"]),
                    "subscription_rate": float(row["subscription_rate"]),
                    "contribution_to_yes": float(row["contribution_to_yes"]),
                    "quadrant": row["quadrant"],
                    "why_included": (
                        f"Conversion rate {row['subscription_rate']:.4f} is at/above the {label} "
                        f"feature mean ({quadrant_refs[col]['rate_ref']:.4f}) [{row['quadrant']}], "
                        f"with sample size n={int(row['count'])} at/above the small-sample "
                        f"threshold (n<{SMALL_SAMPLE_THRESHOLD})."
                    ),
                    "stability": (
                        "Reinforced by both high conversion rate and high contribution (Q1: "
                        "aligned on both axes)."
                        if row["quadrant"] == Q1_LABEL
                        else "High conversion rate only; contribution to total subscribers is "
                        "below this feature's mean (Q2: aligned on one axis only)."
                    ),
                    "risk": (
                        f"Represents {row['count'] / n_obs:.2%} of all cleaned observations; "
                        f"subject to the dataset-wide class imbalance (overall yes rate = {overall_rate:.4f})."
                    ),
                }
            )
    high_potential_df = (
        pd.DataFrame(high_potential_rows)
        .sort_values("subscription_rate", ascending=False)
        .reset_index(drop=True)
    )
    print(f"\n[High-Potential Segments] ({len(high_potential_df)} rows)")
    print(
        high_potential_df[["feature", "category", "count", "subscription_rate", "quadrant"]].to_string(
            index=False
        )
    )

    # ---- 2. High-impact segments: top contribution_rank + large sample ----
    high_impact_rows = []
    for col, title in CONTRIBUTION_TABLE_TITLES.items():
        label = title.replace("Contribution Table - ", "")
        t = contribution_tables[col]
        subset = t[(t["contribution_rank"] <= HIGH_IMPACT_CONTRIBUTION_TOP_N) & (~t["small_sample_flag"])]
        for _, row in subset.iterrows():
            below_baseline = float(row["subscription_rate"]) < overall_rate
            high_impact_rows.append(
                {
                    "feature": label,
                    "category": row[col],
                    "count": int(row["count"]),
                    "contribution_to_yes": float(row["contribution_to_yes"]),
                    "contribution_rank": int(row["contribution_rank"]),
                    "subscription_rate": float(row["subscription_rate"]),
                    "why_included": (
                        f"Ranked #{int(row['contribution_rank'])} of {len(t)} categories by "
                        f"contribution to total subscribers ({row['contribution_to_yes']:.4f} of "
                        f"all y=yes), backed by a large sample (n={int(row['count'])})."
                    ),
                    "stability": (
                        f"Large group size (n={int(row['count'])}) means this contribution share "
                        "is based on a substantial sample rather than a handful of observations."
                    ),
                    "risk": (
                        (
                            f"Conversion rate ({row['subscription_rate']:.4f}) is below the overall "
                            f"baseline ({overall_rate:.4f}); this segment's impact comes mainly from "
                            "group size rather than conversion efficiency."
                        )
                        if below_baseline
                        else "None specific beyond the dataset-wide class imbalance."
                    ),
                }
            )
    high_impact_df = (
        pd.DataFrame(high_impact_rows)
        .sort_values("contribution_to_yes", ascending=False)
        .reset_index(drop=True)
    )
    print(f"\n[High-Impact Segments] ({len(high_impact_df)} rows)")
    print(
        high_impact_df[
            ["feature", "category", "count", "contribution_to_yes", "contribution_rank"]
        ].to_string(index=False)
    )

    # ---- 3. Stable segments: majority category per feature, near-baseline rate ----
    # Checked across ALL 6 categorical features (not just the 5 used for quadrant
    # analysis) so the pattern's cross-feature consistency can be assessed.
    stable_rows = []
    for col in CATEGORICAL_COLS:
        t = category_tables[col]
        majority_row = t.loc[t["count"].idxmax()]
        diff = abs(float(majority_row["subscription_rate"]) - overall_rate)
        if diff <= STABLE_RATE_TOLERANCE:
            stable_rows.append(
                {
                    "feature": col,
                    "category": majority_row[col],
                    "count": int(majority_row["count"]),
                    "percentage": float(majority_row["percentage"]),
                    "subscription_rate": float(majority_row["subscription_rate"]),
                    "diff_from_overall_rate": diff,
                }
            )

    n_stable_features = len(stable_rows)
    for row_dict in stable_rows:
        row_dict["why_included"] = (
            f"Largest category in `{row_dict['feature']}` (n={row_dict['count']}, "
            f"{row_dict['percentage']:.2f}% of observations) with conversion rate "
            f"{row_dict['subscription_rate']:.4f}, within {STABLE_RATE_TOLERANCE:.2f} of the "
            f"overall baseline rate ({overall_rate:.4f})."
        )
        row_dict["stability"] = (
            f"This near-baseline, majority-category pattern recurs in {n_stable_features} of "
            f"{len(CATEGORICAL_COLS)} categorical features analyzed, indicating it is not "
            "dependent on any single variable."
        )
        row_dict["risk"] = (
            "Low sample-size risk given majority status; residual risk is the dataset-wide "
            f"class imbalance (overall yes rate = {overall_rate:.4f}) rather than small-sample noise."
        )

    stable_df = pd.DataFrame(stable_rows).sort_values("diff_from_overall_rate").reset_index(drop=True)
    print(f"\n[Stable Segments] ({len(stable_df)} rows, tolerance=+/-{STABLE_RATE_TOLERANCE})")
    print(
        stable_df[
            ["feature", "category", "count", "percentage", "subscription_rate", "diff_from_overall_rate"]
        ].to_string(index=False)
    )

    return {
        "high_potential": high_potential_df,
        "high_impact": high_impact_df,
        "stable": stable_df,
    }


# ---------------------------------------------------------------------------
# visualization
# ---------------------------------------------------------------------------
def visualization(df: pd.DataFrame, results: dict[str, Any]) -> list[Path]:
    """Generate Figures 1-8 and save them as PNG files under FIGURES_DIR."""
    print("\n" + "=" * 78)
    print("STEP 3: Visualization")
    print("=" * 78)

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    saved_paths: list[Path] = []

    def _save(fig: plt.Figure, name: str) -> None:
        out_path = FIGURES_DIR / f"{name}.png"
        fig.savefig(out_path, dpi=120, bbox_inches="tight")
        plt.close(fig)
        print(f"[saved] {out_path}")
        saved_paths.append(out_path)

    age_bins = results["age_bins"]

    # ---- Figure 1: Age Distribution Histogram (Overall & by Subscription Status) ----
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    sns.histplot(data=df, x=AGE_COL, bins=age_bins, ax=axes[0], color="#4c72b0")
    axes[0].set_title("Overall")
    axes[0].set_xlabel("Age")
    axes[0].set_ylabel("Count")

    sns.histplot(
        data=df,
        x=AGE_COL,
        hue=TARGET_COL,
        bins=age_bins,
        ax=axes[1],
        stat="density",
        common_norm=False,
        element="step",
    )
    axes[1].set_title("By Subscription Status (y)")
    axes[1].set_xlabel("Age")
    axes[1].set_ylabel("Density")

    fig.suptitle(f"Figure 1: Age Distribution Histogram (identical bin width = {AGE_BIN_WIDTH} years)")
    fig.tight_layout()
    _save(fig, "figure1_age_distribution_histogram")

    # ---- Figure 2: Age Boxplot by Subscription Status ----
    fig, ax = plt.subplots(figsize=(7, 5))
    sns.boxplot(data=df, x=TARGET_COL, y=AGE_COL, order=["no", "yes"], ax=ax)
    ax.set_title("Figure 2: Age Boxplot by Subscription Status")
    ax.set_xlabel("Subscription Status (y)")
    ax.set_ylabel("Age")
    fig.tight_layout()
    _save(fig, "figure2_age_boxplot_by_subscription_status")

    # ---- Figures 3-8: Subscription Rate by Category (horizontal bar charts) ----
    figure_specs = [
        ("job", "Figure 3: Subscription Rate by Job"),
        ("marital", "Figure 4: Subscription Rate by Marital Status"),
        ("education", "Figure 5: Subscription Rate by Education"),
        ("default", "Figure 6: Subscription Rate by Default Status"),
        ("housing", "Figure 7: Subscription Rate by Housing Loan"),
        ("loan", "Figure 8: Subscription Rate by Personal Loan"),
    ]
    for idx, (col, title) in enumerate(figure_specs, start=3):
        # ascending order so the highest subscription rate renders at the top of the barh
        table = results["category_tables"][col].sort_values("subscription_rate", ascending=True)
        fig, ax = plt.subplots(figsize=(9, max(3.5, 0.6 * len(table))))
        colors = ["#d62728" if flag else "#1f77b4" for flag in table["small_sample_flag"]]
        ax.barh(table[col].astype(str), table["subscription_rate"], color=colors)
        for y_pos, (rate, count) in enumerate(zip(table["subscription_rate"], table["count"])):
            ax.text(rate + 0.005, y_pos, f"n={count}", va="center", fontsize=8)
        ax.set_xlabel("Subscription Rate")
        ax.set_xlim(0, min(1.0, table["subscription_rate"].max() * 1.25 + 0.03))
        ax.set_title(f"{title}\n(red bar = small sample, n < {SMALL_SAMPLE_THRESHOLD})")
        fig.tight_layout()
        file_stub = FIGURE_FILES[idx - 1][0].replace(".png", "")
        _save(fig, file_stub)

    # ---- New section: Positive Class Contribution figures (additive; existing figures unchanged) ----
    contribution_specs = [
        ("job", "Contribution to Positive Class (yes) by Job"),
        ("marital", "Contribution to Positive Class (yes) by Marital Status"),
        ("education", "Contribution to Positive Class (yes) by Education"),
        ("default", "Contribution to Positive Class (yes) by Default Status"),
        ("housing", "Contribution to Positive Class (yes) by Housing Loan"),
        ("loan", "Contribution to Positive Class (yes) by Personal Loan"),
    ]
    for col, title in contribution_specs:
        # ascending order so the highest contribution renders at the top of the barh
        table = results["contribution_tables"][col].sort_values("contribution_to_yes", ascending=True)
        fig, ax = plt.subplots(figsize=(9, max(3.5, 0.6 * len(table))))
        colors = ["#d62728" if flag else "#2ca02c" for flag in table["small_sample_flag"]]
        ax.barh(table[col].astype(str), table["contribution_to_yes"], color=colors)
        for y_pos, (contrib, count) in enumerate(zip(table["contribution_to_yes"], table["count"])):
            ax.text(contrib + 0.003, y_pos, f"n={count}", va="center", fontsize=8)
        ax.set_xlabel("Contribution to Total Positive Class (yes)")
        ax.set_xlim(0, min(1.0, table["contribution_to_yes"].max() * 1.25 + 0.02))
        ax.set_title(f"{title}\n(red bar = small sample, n < {SMALL_SAMPLE_THRESHOLD})")
        fig.tight_layout()
        _save(fig, f"contribution_by_{col}")

    # ---- New section: Quadrant Analysis scatter plots (additive; existing figures unchanged) ----
    # X-axis: Conversion Rate; Y-axis: Contribution to Total Positive Class (yes).
    # Reference lines (dashed grey) = mean of each axis across that feature's own categories.
    for col, label in QUADRANT_VAR_LABELS.items():
        t = results["quadrant_tables"][col]
        rate_ref = results["quadrant_refs"][col]["rate_ref"]
        contrib_ref = results["quadrant_refs"][col]["contrib_ref"]

        fig, ax = plt.subplots(figsize=(8.5, 7))
        for quadrant_name in QUADRANT_ORDER:
            subset = t[t["quadrant"] == quadrant_name]
            if subset.empty:
                continue
            color = QUADRANT_COLORS[quadrant_name]
            edge_colors = ["black" if flag else color for flag in subset["small_sample_flag"]]
            ax.scatter(
                subset["subscription_rate"],
                subset["contribution_to_yes"],
                s=150,
                color=color,
                edgecolors=edge_colors,
                linewidths=1.8,
                alpha=0.85,
                label=quadrant_name,
            )
            for _, row in subset.iterrows():
                marker = " *" if row["small_sample_flag"] else ""
                ax.annotate(
                    f"{row[col]}{marker}",
                    (row["subscription_rate"], row["contribution_to_yes"]),
                    textcoords="offset points",
                    xytext=(7, 5),
                    fontsize=8,
                )

        ax.axvline(rate_ref, color="grey", linestyle="--", linewidth=1)
        ax.axhline(contrib_ref, color="grey", linestyle="--", linewidth=1)
        ax.set_xlabel("Conversion Rate (subscription_rate)")
        ax.set_ylabel("Contribution to Total Positive Class (yes)")
        ax.set_title(
            f"Quadrant Analysis: {label}\n"
            f"Reference lines = mean conversion rate ({rate_ref:.4f}) & mean contribution ({contrib_ref:.4f})"
        )
        ax.legend(loc="upper left", bbox_to_anchor=(1.02, 1.0), fontsize=8, title="Quadrant", borderaxespad=0)
        ax.margins(x=0.2, y=0.2)
        fig.text(0.01, 0.01, f"* small sample (n < {SMALL_SAMPLE_THRESHOLD})", fontsize=8, color="dimgray")
        fig.tight_layout(rect=(0, 0.02, 1, 1))
        _save(fig, f"quadrant_{col}")

    return saved_paths


# ---------------------------------------------------------------------------
# generate_summary_report
# ---------------------------------------------------------------------------
def _df_to_markdown(df: pd.DataFrame, index: bool = False, float_fmt: str = "{:.4f}") -> str:
    """Render a DataFrame as a GitHub-flavored markdown table without
    relying on the optional `tabulate` dependency."""
    display_df = df.copy()
    if index:
        display_df = display_df.reset_index()
    for col in display_df.columns:
        if pd.api.types.is_bool_dtype(display_df[col]):
            display_df[col] = display_df[col].map(lambda v: "Yes" if v else "No")
        elif pd.api.types.is_float_dtype(display_df[col]):
            display_df[col] = display_df[col].map(lambda v: float_fmt.format(v) if pd.notna(v) else "")

    headers = [str(c) for c in display_df.columns]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for _, row in display_df.iterrows():
        lines.append("| " + " | ".join(str(v) for v in row.tolist()) + " |")
    return "\n".join(lines)


def generate_summary_report(
    df: pd.DataFrame,
    results: dict[str, Any],
    prep_info: dict[str, Any],
    synthesis: dict[str, pd.DataFrame],
) -> Path:
    """Write the Markdown summary report (Observation / Key Statistics /
    Notable Patterns), plus Positive Class Contribution Analysis, Quadrant
    Analysis Observations, Final Segmentation Synthesis, and a supporting
    data-table appendix and figure gallery, to REPORT_PATH."""
    print("\n" + "=" * 78)
    print("STEP 4: Generate Summary Report")
    print("=" * 78)

    table1 = results["table1_dataset_summary"].iloc[0]
    table2 = results["table2_age_summary"]
    category_tables = results["category_tables"]
    overall_rate = float(table1["subscription_rate"])

    age_mean_overall = float(table2.loc["overall", "mean"])
    age_median_overall = float(table2.loc["overall", "median"])
    age_mean_yes = float(table2.loc["yes", "mean"])
    age_mean_no = float(table2.loc["no", "mean"])
    age_mean_diff = abs(age_mean_yes - age_mean_no)

    # ---- Observation (objective description only) ----
    observation = [
        f"Data source (raw file): `{prep_info['raw_path']}`.",
        (
            f"After removing {prep_info['n_exact_duplicates_removed']} exact duplicate rows "
            f"({prep_info['n_before_dedup']} rows before -> {prep_info['n_after_dedup']} rows after), "
            f"the cleaned dataset used for this module contains {prep_info['n_final']} observations "
            f"and the 8 columns required for customer profile analysis: {REQUIRED_COLS}."
        ),
        (
            f"Overall term deposit subscription rate is {table1['subscription_rate']:.4f} "
            f"({int(table1['subscribed_yes'])} yes / {int(table1['subscribed_no'])} no "
            f"out of {int(table1['observations'])} observations)."
        ),
        (
            f"Age (overall) ranges from {int(table2.loc['overall', 'min'])} to {int(table2.loc['overall', 'max'])} years, "
            f"with mean={age_mean_overall:.2f}, median={age_median_overall:.1f}, "
            f"std={float(table2.loc['overall', 'std']):.2f}."
        ),
        (
            f"Mean age is {age_mean_yes:.2f} years for subscribers (y=yes) and {age_mean_no:.2f} years "
            f"for non-subscribers (y=no); the difference between the two means is {age_mean_diff:.2f} years."
        ),
        (
            "Categorical variables `default` and `education` contain a valid `unknown` category. "
            "This represents a recorded response rather than a missing value and was retained as-is."
        ),
    ]

    # ---- Key Statistics ----
    key_statistics = [
        f"Dataset size (cleaned): {int(table1['observations'])} observations.",
        f"Class counts: y=no -> {int(table1['subscribed_no'])}; y=yes -> {int(table1['subscribed_yes'])}.",
        f"Age quartiles (overall): Q1={float(table2.loc['overall','25%']):.1f}, Q2={float(table2.loc['overall','50%']):.1f}, Q3={float(table2.loc['overall','75%']):.1f}.",
    ]
    for col, label in [
        ("job", "Job"),
        ("marital", "Marital status"),
        ("education", "Education"),
        ("default", "Default"),
        ("housing", "Housing loan"),
        ("loan", "Personal loan"),
    ]:
        t = category_tables[col]
        top = t.iloc[0]
        bottom = t.iloc[-1]
        n_small = int(t["small_sample_flag"].sum())
        key_statistics.append(
            f"{label}: highest subscription rate = `{top[col]}` "
            f"({top['subscription_rate']:.4f}, n={int(top['count'])}"
            f"{', small sample' if bool(top['small_sample_flag']) else ''}); "
            f"lowest subscription rate = `{bottom[col]}` "
            f"({bottom['subscription_rate']:.4f}, n={int(bottom['count'])}"
            f"{', small sample' if bool(bottom['small_sample_flag']) else ''}); "
            f"{n_small} of {len(t)} categories flagged as small sample (n<{SMALL_SAMPLE_THRESHOLD})."
        )

    # ---- Notable Patterns (descriptive; no causal language) ----
    small_sample_categories = [
        f"{col}={row[col]}"
        for col in CATEGORICAL_COLS
        for _, row in category_tables[col][category_tables[col]["small_sample_flag"]].iterrows()
    ]
    rate_ranges = {
        col: float(category_tables[col]["subscription_rate"].max() - category_tables[col]["subscription_rate"].min())
        for col in CATEGORICAL_COLS
    }
    widest_var = max(rate_ranges, key=rate_ranges.get)
    narrowest_var = min(rate_ranges, key=rate_ranges.get)

    notable_patterns = [
        (
            f"Subscription-rate range across categories is widest for `{widest_var}` "
            f"({rate_ranges[widest_var]:.4f} between its highest and lowest category) and "
            f"narrowest for `{narrowest_var}` ({rate_ranges[narrowest_var]:.4f}), indicating "
            f"`{widest_var}` shows more variation across categories while `{narrowest_var}` "
            "shows comparatively limited differences."
        ),
        (
            f"Categories with sample size below {SMALL_SAMPLE_THRESHOLD} that require cautious "
            "interpretation: " + (", ".join(small_sample_categories) if small_sample_categories else "none") + "."
        ),
        (
            f"The mean age difference between subscribers and non-subscribers is {age_mean_diff:.2f} years, "
            "which is small relative to the overall age spread. The full distribution (Figure 1) and "
            "boxplot (Figure 2) should be considered rather than relying on the mean alone."
        ),
        (
            "This module evaluates statistical association between customer characteristics and "
            "subscription status only; observed differences do not imply that these characteristics "
            "directly influence subscription decisions. Campaign behavior and macroeconomic conditions "
            "are analyzed in separate modules to avoid overlapping interpretation."
        ),
    ]

    # ---- Business Summary (synthesis only; no new EDA / no prediction) ----
    hp_df = synthesis["high_potential"]
    hi_df = synthesis["high_impact"]
    st_df = synthesis["stable"]

    final_overall_conclusion = [
        (
            "Customer profile variables show observable association with term deposit subscription rates, "
            f"with `{widest_var}` showing the widest category-level subscription-rate spread and "
            f"`{narrowest_var}` showing the narrowest spread in this module."
        ),
        (
            "The strongest business-useful customer-profile signals come from combining conversion rate, "
            "group size, contribution to the positive class, and quadrant placement rather than relying on "
            "conversion rate alone."
        ),
        (
            f"The existing segmentation synthesis identifies {len(hp_df)} high-potential segment(s), "
            f"{len(hi_df)} high-impact segment(s), and {len(st_df)} stable segment(s), using only the "
            "already-computed EDA tables."
        ),
        (
            "Age shows only a small mean difference between subscribers and non-subscribers relative to the "
            "overall age spread, so customer-profile interpretation should rely more on the categorical "
            "patterns and segment synthesis than on age mean alone."
        ),
    ]

    final_business_implications = [
        (
            "High-potential segments can help identify customer categories with above-reference conversion "
            "rates and reasonable sample sizes; these are useful for prioritization discussions, not for "
            "individual-level prediction."
        ),
        (
            "High-impact segments highlight large groups that contribute materially to total subscribers; "
            "these groups are useful when the business goal is subscriber volume rather than only category-level "
            "conversion rate."
        ),
        (
            "Stable segments provide baseline customer groups whose subscription rates sit close to the overall "
            "rate; these are useful for benchmarking and for avoiding overreaction to a single high-rate category."
        ),
        (
            "Customer-profile findings should be combined with campaign strategy (Module 2) and market context "
            "(Module 3) before being used in telephone marketing planning."
        ),
    ]

    final_limitations = [
        (
            "This module is descriptive EDA only: it shows association between customer characteristics and "
            "subscription status, but it does not establish causality or produce a targeting model."
        ),
        (
            f"Some categories are flagged as small samples (n < {SMALL_SAMPLE_THRESHOLD}), so high or low "
            "subscription rates in those groups should not be treated as stable business rules."
        ),
        (
            "Contribution to the positive class is influenced by group size, while conversion rate is influenced "
            "by within-group outcomes; both metrics must be interpreted together."
        ),
        (
            "The segmentation synthesis is rule-based and reuses existing EDA values only; it should not be "
            "treated as a validated scoring framework or prediction workflow."
        ),
    ]

    # ---- Assemble Markdown ----
    lines: list[str] = []
    lines.append("# Module 1 - Customer Profile Analysis: Summary Report")
    lines.append("")
    lines.append(
        "*Business question: Which customer characteristics are associated with a higher "
        "subscription rate for term deposits?*"
    )
    lines.append("")
    lines.append(
        f"*Data source: `{prep_info['raw_path']}` (raw), cleaned by removing "
        f"{prep_info['n_exact_duplicates_removed']} exact duplicate rows -> "
        f"{prep_info['n_final']} observations analyzed.*"
    )
    lines.append("")

    lines.append("## Observation")
    lines.extend(f"- {item}" for item in observation)
    lines.append("")

    lines.append("## Key Statistics")
    lines.extend(f"- {item}" for item in key_statistics)
    lines.append("")

    lines.append("## Notable Patterns")
    lines.extend(f"- {item}" for item in notable_patterns)
    lines.append("")

    lines.append("## Business Summary")
    lines.append("")
    lines.append(
        "*Business question: Which customer characteristics are associated with a higher "
        "subscription rate for term deposits?*"
    )
    lines.append("")

    lines.append("### Overall Conclusion")
    lines.extend(f"- {item}" for item in final_overall_conclusion)
    lines.append("")

    lines.append("### Business Implications")
    lines.extend(f"- {item}" for item in final_business_implications)
    lines.append("")

    lines.append("### Limitations")
    lines.extend(f"- {item}" for item in final_limitations)
    lines.append("")

    # ---- New section: Positive Class Contribution Analysis (additive; does not alter ----
    # ---- the existing conversion-rate ranking / table order above) ----
    contribution_tables = results["contribution_tables"]
    n_yes_total = results["n_yes"]

    contribution_observations = []
    for col, label in [
        ("job", "Job"),
        ("marital", "Marital status"),
        ("education", "Education"),
        ("default", "Default"),
        ("housing", "Housing loan"),
        ("loan", "Personal loan"),
    ]:
        ct = contribution_tables[col]
        top_contrib = ct.iloc[0]
        conv_rank_of_top = int(
            category_tables[col].loc[category_tables[col][col] == top_contrib[col], "rank"].iloc[0]
        )
        contribution_observations.append(
            f"{label}: `{top_contrib[col]}` contributes the largest share of all subscribers "
            f"({top_contrib['contribution_to_yes']:.4f} of {n_yes_total} total y=yes observations, "
            f"n={int(top_contrib['count'])}), while its conversion-rate rank is "
            f"{conv_rank_of_top} of {len(ct)} ({top_contrib['subscription_rate']:.4f})."
        )

    lines.append("## Appendix: Supporting Analysis")
    lines.append("")

    lines.append("### Positive Class Contribution Analysis")
    lines.append("")
    lines.append(
        "*Definition: contribution to positive class = (number of y=yes observations within a "
        "category) / (total number of y=yes observations in the cleaned dataset). This measures "
        "each category's share of all subscribers, which is independent of - and reported "
        "alongside, not in place of - its own conversion rate (subscription rate) and group size.*"
    )
    lines.append("")
    lines.extend(f"- {item}" for item in contribution_observations)
    lines.append("")

    for col, title in CONTRIBUTION_TABLE_TITLES.items():
        lines.append(f"#### {title}")
        lines.append("")
        lines.append(
            "*Sorted by contribution to positive class (descending) - a separate ranking from the "
            f"conversion-rate ranking in the Appendix tables below. small_sample_flag uses the same "
            f"n < {SMALL_SAMPLE_THRESHOLD} rule used throughout this report.*"
        )
        lines.append("")
        lines.append(_df_to_markdown(contribution_tables[col]))
        lines.append("")

    for fname, fig_title in CONTRIBUTION_FIGURE_FILES:
        rel_path = f"../images/module1_customer_profile/{fname}"
        lines.append(f"##### {fig_title}")
        lines.append("")
        lines.append(f"![{fig_title}]({rel_path})")
        lines.append("")

    # ---- New section: Quadrant Analysis Observations (additive; purely descriptive, ----
    # ---- no inference/causal language; does not alter any section above) ----
    quadrant_tables = results["quadrant_tables"]
    quadrant_refs = results["quadrant_refs"]

    lines.append("### Quadrant Analysis Observations")
    lines.append("")
    lines.append(
        "*Quadrant segmentation for job, education, marital, housing, and loan. "
        "X-axis = Conversion Rate (subscription_rate); Y-axis = Contribution to Total "
        "Positive Class (contribution_to_yes). Reference lines = mean of each axis across "
        "that feature's own categories. Q1 = High Conversion + High Contribution; "
        "Q2 = High Conversion + Low Contribution; Q3 = Low Conversion + High Contribution; "
        "Q4 = Low Conversion + Low Contribution. Statements below list category membership "
        "and observed values only; they do not infer cause or predict future behavior.*"
    )
    lines.append("")

    for col, label in QUADRANT_VAR_LABELS.items():
        t = quadrant_tables[col]
        refs = quadrant_refs[col]
        lines.append(
            f"- **{label}** (reference lines: mean conversion rate = {refs['rate_ref']:.4f}, "
            f"mean contribution to positive class = {refs['contrib_ref']:.4f}):"
        )
        for q in QUADRANT_ORDER:
            subset = t[t["quadrant"] == q]
            if subset.empty:
                lines.append(f"  - {q}: none.")
                continue
            items = ", ".join(
                f"`{row[col]}` (rate={row['subscription_rate']:.4f}, "
                f"contribution={row['contribution_to_yes']:.4f}, n={int(row['count'])}"
                + (", small sample" if bool(row["small_sample_flag"]) else "")
                + ")"
                for _, row in subset.iterrows()
            )
            lines.append(f"  - {q}: {items}.")
    lines.append("")

    for col, title in QUADRANT_TABLE_TITLES.items():
        lines.append(f"#### {title}")
        lines.append("")
        lines.append(
            "*Reused conversion rate and contribution values from the tables above (not "
            f"recalculated); sorted by conversion rate (descending). small_sample_flag uses "
            f"the same n < {SMALL_SAMPLE_THRESHOLD} rule used throughout this report.*"
        )
        lines.append("")
        lines.append(_df_to_markdown(quadrant_tables[col]))
        lines.append("")

    for fname, fig_title in QUADRANT_FIGURE_FILES:
        rel_path = f"../images/module1_customer_profile/{fname}"
        lines.append(f"##### {fig_title}")
        lines.append("")
        lines.append(f"![{fig_title}]({rel_path})")
        lines.append("")

    # ---- New section: Final Segmentation Synthesis (additive; rule-based synthesis ----
    # ---- of already-computed values only - no EDA recalculation, no groupby, no ML) ----
    lines.append("### Segmentation Synthesis Details")
    lines.append("")
    lines.append(
        "*This section synthesizes the results already computed above (conversion rate, "
        "group size, contribution to positive class, and quadrant analysis) into three "
        "segment types. No EDA metric is recalculated, no new groupby is performed, and "
        "no ML / prediction / scoring is used - this is a rule-based synthesis of existing "
        "values only.*"
    )
    lines.append("")

    hp_df = synthesis["high_potential"]
    lines.append("#### 1. High-Potential Segments")
    lines.append("")
    lines.append(
        "*Rule: quadrant Q1 or Q2 (conversion rate at/above the feature's own mean) AND a "
        f"reasonable sample size (count >= {SMALL_SAMPLE_THRESHOLD}, i.e. not small_sample_flag). "
        "High conversion + reasonable sample; Q1/Q2 = high conversion rate side of the quadrant "
        "analysis above.*"
    )
    lines.append("")
    lines.append(
        _df_to_markdown(
            hp_df[["feature", "category", "count", "subscription_rate", "contribution_to_yes", "quadrant"]]
        )
    )
    lines.append("")
    for _, row in hp_df.iterrows():
        lines.append(f"- **{row['feature']} = `{row['category']}`**")
        lines.append(f"  - why included: {row['why_included']}")
        lines.append(f"  - stability: {row['stability']}")
        lines.append(f"  - risk: {row['risk']}")
    lines.append("")

    hi_df = synthesis["high_impact"]
    lines.append("#### 2. High-Impact Segments")
    lines.append("")
    lines.append(
        f"*Rule: top {HIGH_IMPACT_CONTRIBUTION_TOP_N} contributor(s) to total subscribers "
        f"(contribution_rank <= {HIGH_IMPACT_CONTRIBUTION_TOP_N}) within each feature AND a "
        f"large sample size (count >= {SMALL_SAMPLE_THRESHOLD}, i.e. not small_sample_flag).*"
    )
    lines.append("")
    lines.append(
        _df_to_markdown(
            hi_df[
                ["feature", "category", "count", "contribution_to_yes", "contribution_rank", "subscription_rate"]
            ]
        )
    )
    lines.append("")
    for _, row in hi_df.iterrows():
        lines.append(f"- **{row['feature']} = `{row['category']}`**")
        lines.append(f"  - why included: {row['why_included']}")
        lines.append(f"  - stability: {row['stability']}")
        lines.append(f"  - risk: {row['risk']}")
    lines.append("")

    st_df = synthesis["stable"]
    lines.append("#### 3. Stable Segments")
    lines.append("")
    lines.append(
        "*Rule: the majority (largest-count) category within a feature whose conversion rate "
        f"is within {STABLE_RATE_TOLERANCE:.2f} of the overall baseline rate ({overall_rate:.4f}) "
        f"- checked across all {len(CATEGORICAL_COLS)} categorical features so the pattern is not "
        "tied to a single variable.*"
    )
    lines.append("")
    lines.append(
        _df_to_markdown(
            st_df[["feature", "category", "count", "percentage", "subscription_rate", "diff_from_overall_rate"]]
        )
    )
    lines.append("")
    for _, row in st_df.iterrows():
        lines.append(f"- **{row['feature']} = `{row['category']}`**")
        lines.append(f"  - why included: {row['why_included']}")
        lines.append(f"  - stability: {row['stability']}")
        lines.append(f"  - risk: {row['risk']}")
    lines.append("")

    lines.append("## Appendix: Data Tables")
    lines.append("")
    lines.append("### Table 1 - Dataset Summary")
    lines.append("")
    lines.append(_df_to_markdown(results["table1_dataset_summary"]))
    lines.append("")
    lines.append("### Table 2 - Age Summary Statistics (Overall / Yes / No)")
    lines.append("")
    lines.append(_df_to_markdown(results["table2_age_summary"], index=True))
    lines.append("")

    for col, title in TABLE_TITLES.items():
        lines.append(f"### {title}")
        lines.append("")
        lines.append(
            f"*Sorted by subscription rate (descending). Categories with count < "
            f"{SMALL_SAMPLE_THRESHOLD} are flagged `small_sample_flag = Yes` and should be "
            "interpreted with caution.*"
        )
        lines.append("")
        lines.append(_df_to_markdown(category_tables[col]))
        lines.append("")

    lines.append("## Figures")
    lines.append("")
    for fname, title in FIGURE_FILES:
        rel_path = f"../images/module1_customer_profile/{fname}"
        lines.append(f"### {title}")
        lines.append("")
        lines.append(f"![{title}]({rel_path})")
        lines.append("")

    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"[saved] {REPORT_PATH}")
    return REPORT_PATH


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main() -> None:
    df_raw = load_data()
    df, prep_info = data_preprocessing(df_raw)
    results = analysis(df)
    synthesis = segmentation_synthesis(results)
    visualization(df, results)
    report_path = generate_summary_report(df, results, prep_info, synthesis)

    print("\n" + "=" * 78)
    print("Module 1 - Customer Profile Analysis: COMPLETE")
    print("=" * 78)
    print(f"Figures saved to : {FIGURES_DIR}")
    print(f"Report saved to  : {report_path}")


if __name__ == "__main__":
    main()
