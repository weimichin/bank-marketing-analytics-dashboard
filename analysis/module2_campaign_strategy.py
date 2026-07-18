"""
Module 2 - Campaign Strategy Evaluation
=========================================

NOTE ON FILE NAME: the implementation plan / prompt referred to this file as
`module1_customer_profile.py`, but all content (business question, data
used, tables, figures) describes Module 2 - Campaign Strategy Evaluation.
`module1_customer_profile.py` already exists as a separate, completed
deliverable for Module 1 (Customer Profile Analysis). To avoid overwriting
that file, this module is saved as `module2_campaign_strategy.py`, following
the same naming convention (moduleN_<topic>.py).

Business Question
------------------
Which telephone marketing strategies and historical campaign characteristics
are associated with higher term deposit subscription rates?

Analysis Goal
-------------
Evaluate historical telephone campaign performance. This module is
descriptive and comparative ONLY - it does not infer causal effects and does
NOT include any predictive modeling.

Scope
-----
Only the following columns are analyzed:
    contact, campaign, previous, pdays, poutcome, month, day_of_week, y
`duration` is explicitly EXCLUDED (see "Duration Exclusion" below). Customer
characteristics and macroeconomic conditions are out of scope for this
module and are analyzed separately in other modules.

Data Source (confirm before analysis)
--------------------------------------
This project ships two RAW dataset files (neither is de-duplicated):
    - data/bank-additional/bank-additional-full.csv  (full dataset, 41,188 rows)
    - data/bank-additional/bank-additional.csv       (10% sample, 4,119 rows)

There is no separately-saved "cleaned" CSV file in this project. Every EDA
module in this codebase (see eda/data_cleaning.py, eda/utils.py
`ensure_cleaned`, and module1_customer_profile.py) defines the "cleaned
dataset" as:

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

Duration Exclusion
-------------------
`duration` (last-call duration in seconds) is NOT included anywhere in this
module. It is only known after a call ends, so it cannot support evaluating
campaign strategy before or during customer contact, and including it would
cause data leakage. It is dropped during column selection in
data_preprocessing() and never reappears in any table or figure below.

Standalone usage
-----------------
    uv run python module2_campaign_strategy.py
    (or) python module2_campaign_strategy.py

This script has no dependency on any other file in this project (e.g. the
`eda` package, or module1_customer_profile.py) and can be run independently,
provided pandas, numpy, matplotlib, and seaborn are installed.

Structure
---------
    load_data()               - locate & load the raw CSV, confirm its path
    data_preprocessing()      - remove exact duplicates, select columns
                                 (excluding duration), verify dtypes
    analysis()                - descriptive stats (campaign/previous only; pdays
                                 is a sentinel-dominated field and is instead
                                 broken down separately as contacted-vs-not plus
                                 actual-day stats for pdays != 999), frequency
                                 tables, subscription-rate tables, grouped
                                 categories, small-sample flags, ranking
    visualization()           - Figures 1-7 (saved as PNG files; Figure 4 covers
                                 pdays contacted-vs-not (left) plus a coarse
                                 day-range distribution & subscription rate on a
                                 dual y-axis (right, 0-7/8-14/15+, pdays != 999
                                 only), Figure 6 combines monthly volume and
                                 subscription rate on a dual y-axis)
    generate_summary_report() - Markdown report (Observation / Key Statistics /
                                 Notable Patterns + supporting data tables)
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
FIGURES_DIR = PROJECT_ROOT / "images" / "module2_campaign_strategy"
REPORT_PATH = PROJECT_ROOT / "reports" / "module2_campaign_strategy_summary.md"

TARGET_COL = "y"
NUMERIC_COLS = ["campaign", "previous", "pdays"]
# Table 1 excludes `pdays`: 999 is a sentinel category (not previously contacted),
# not an actual day count, so mean/median/quartile statistics over it are not
# meaningful. See Table 5 (contacted vs not contacted) and Table 5b (actual day
# statistics, pdays != 999 only) for the interpretable pdays breakdowns.
TABLE1_COLS = ["campaign", "previous"]
CONTACT_COL = "contact"
POUTCOME_COL = "poutcome"
TIME_COLS = ["month", "day_of_week"]
EXCLUDED_COL = "duration"
REQUIRED_COLS = ["contact", "campaign", "previous", "pdays", "poutcome", "month", "day_of_week", "y"]

SMALL_SAMPLE_THRESHOLD = 100
PDAYS_SENTINEL = 999

MONTH_ORDER = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
DAY_ORDER = ["mon", "tue", "wed", "thu", "fri"]

CAMPAIGN_GROUP_ORDER = ["1", "2", "3", "4", "5", "6+"]
PREVIOUS_GROUP_ORDER = ["0", "1", "2", "3+"]
PREVIOUS_BINARY_ORDER = ["0", ">=1"]
PDAYS_NOT_CONTACTED_LABEL = "Previously Not Contacted (pdays = 999)"
PDAYS_CONTACTED_LABEL = "Previously Contacted (pdays != 999)"
PDAYS_CONTACT_STATUS_ORDER = [PDAYS_NOT_CONTACTED_LABEL, PDAYS_CONTACTED_LABEL]
PDAYS_DAYS_GROUP_ORDER = ["0-7", "8-14", "15+"]
POUTCOME_ORDER = ["success", "failure", "nonexistent"]

TABLE_TITLES = {
    "contact": "Table 2 - Contact Method Summary",
    "campaign_group": "Table 3 - Campaign Frequency Summary",
    "previous_group": "Table 4 - Previous Contact Summary",
    "previous_binary": "Table 4b - Previous Contact Summary (Simplified: 0 vs >=1)",
    "pdays_contact_status": "Table 5 - Pdays: Contacted vs Not Contacted Summary",
    "pdays_days": "Table 5b - Pdays Distribution (Previously Contacted Only, actual days)",
    "pdays_days_group": "Table 5c - Pdays Day-Range Summary (Previously Contacted Only)",
    "poutcome": "Table 6 - Previous Campaign Outcome Summary (incl. Contribution to Positive Class)",
    "month": "Table 7 - Monthly Campaign Summary",
    "day_of_week": "Table 8 - Weekday Campaign Summary",
}

FIGURE_FILES = [
    ("figure1_subscription_rate_by_contact.png", "Figure 1 - Subscription Rate by Contact Method"),
    ("figure2_subscription_rate_by_campaign_frequency.png", "Figure 2 - Subscription Rate by Campaign Frequency"),
    ("figure3_subscription_rate_by_previous_count.png", "Figure 3 - Subscription Rate by Previous Contact Count"),
    ("figure4_subscription_rate_by_pdays_group.png", "Figure 4 - Pdays: Contact Status, and Day-Range Distribution & Subscription Rate"),
    ("figure5_subscription_rate_by_poutcome.png", "Figure 5 - Subscription Rate by Previous Campaign Outcome"),
    ("figure6_monthly_volume_and_rate.png", "Figure 6 - Monthly Campaign Volume and Subscription Rate (dual axis)"),
    ("figure7_subscription_rate_by_weekday.png", "Figure 7 - Subscription Rate by Weekday"),
]


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
    """Produce the cleaned, analysis-ready DataFrame for Module 2.

    Steps (per Module 2 Implementation Plan):
        1. Remove exact duplicate rows (all columns identical), keep first
           occurrence -> this is the "cleaned dataset".
        2. Select only the 8 required columns; `duration` is explicitly
           EXCLUDED (data leakage - only known after a call ends).
        3. Verify data types (campaign/previous/pdays numeric, remaining
           columns categorical). No type conversion is applied unless a
           mismatch is found.
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

    # --- Step 1: select required columns (duration excluded) ---
    if EXCLUDED_COL in df_clean_full.columns:
        print(
            f"\n[Column Selection] Excluding `{EXCLUDED_COL}` (data leakage: only known "
            "after a call ends; not suitable for evaluating campaign strategy)."
        )

    missing_cols = [c for c in REQUIRED_COLS if c not in df_clean_full.columns]
    if missing_cols:
        raise KeyError(f"Required columns missing from cleaned dataset: {missing_cols}")

    df = df_clean_full[REQUIRED_COLS].copy()
    print(f"[Column Selection] Selected columns: {REQUIRED_COLS}")
    print(f"[Column Selection] Resulting shape: {df.shape[0]} rows x {df.shape[1]} columns")
    assert EXCLUDED_COL not in df.columns, "duration must not appear in the analysis-ready DataFrame"

    # --- Step 2: verify data types ---
    print("\n[Dtype Verification]")
    dtype_rows = []
    for col in REQUIRED_COLS:
        expected_numeric = col in NUMERIC_COLS
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
        print(f"  - {col:<12} dtype={str(df[col].dtype):<10} expected={expected_label:<12} [{status}]")

    dtype_df = pd.DataFrame(dtype_rows)
    mismatches = dtype_df[dtype_df["status"] == "MISMATCH"]
    if not mismatches.empty:
        print(
            f"[Dtype Verification] WARNING: {len(mismatches)} column(s) do not match the "
            "expected role. No automatic type conversion is applied (per plan constraints)."
        )
    else:
        print("[Dtype Verification] All columns match their expected role. No conversion needed.")

    # --- Informational note: pdays sentinel is a valid category, not missing ---
    n_sentinel = int((df["pdays"] == PDAYS_SENTINEL).sum())
    print(
        f"[Category Note] `pdays` = {PDAYS_SENTINEL} for {n_sentinel} rows "
        f"({n_sentinel / len(df):.2%}) - a valid category meaning the customer was not "
        "contacted in a previous campaign, not a missing value."
    )
    n_nonexistent = int((df[POUTCOME_COL] == "nonexistent").sum())
    print(
        f"[Category Note] `poutcome` = 'nonexistent' for {n_nonexistent} rows "
        f"({n_nonexistent / len(df):.2%}) - consistent with the `pdays` sentinel above "
        "(no previous campaign contact)."
    )

    prep_info: dict[str, Any] = {
        "raw_path": str(RAW_DATA_PATH),
        "n_before_dedup": n_before,
        "n_exact_duplicates_removed": n_exact_duplicates,
        "n_after_dedup": n_after,
        "n_final": len(df),
        "dtype_report": dtype_df,
        "excluded_col": EXCLUDED_COL,
    }
    return df, prep_info


# ---------------------------------------------------------------------------
# analysis
# ---------------------------------------------------------------------------
def _build_group_table(df: pd.DataFrame, col: str, order: list[str]) -> pd.DataFrame:
    """Build a count / percentage / subscription-rate table for `col`,
    preserving `order` (calendar / natural / logical order - NOT sorted by
    subscription rate). A separate `rate_rank` column reports the
    subscription-rate ranking (Ranking Analysis requirement) without
    reordering the table itself. Zero-count categories (e.g. empty pdays
    bins) are kept and shown with subscription_rate = NaN rather than
    causing a division error.
    """
    tmp = df.copy()
    tmp[col] = pd.Categorical(tmp[col], categories=order, ordered=True)
    grouped = (
        tmp.groupby(col, observed=False)
        .agg(count=(TARGET_COL, "size"), yes=(TARGET_COL, lambda s: (s == "yes").sum()))
        .reset_index()
    )
    grouped["percentage"] = grouped["count"] / len(df) * 100
    grouped["subscription_rate"] = np.where(
        grouped["count"] > 0, grouped["yes"] / grouped["count"], np.nan
    )
    grouped["small_sample_flag"] = grouped["count"] < SMALL_SAMPLE_THRESHOLD
    grouped["rate_rank"] = grouped["subscription_rate"].rank(ascending=False, method="min")
    return grouped


def analysis(df: pd.DataFrame) -> dict[str, Any]:
    """Compute all descriptive statistics, frequency tables, subscription-rate
    tables, small-sample flags, and rankings required by the Module 2 plan."""
    print("\n" + "=" * 78)
    print("STEP 2: Analysis")
    print("=" * 78)

    results: dict[str, Any] = {}
    n_obs = len(df)
    n_yes = int((df[TARGET_COL] == "yes").sum())
    overall_rate = n_yes / n_obs

    # ---- Table 1: Campaign Summary Statistics (campaign / previous) ----
    def _numeric_stats(s: pd.Series) -> dict[str, float]:
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

    table1 = pd.DataFrame({col: _numeric_stats(df[col]) for col in TABLE1_COLS}).T
    print("\n[Table 1] Campaign Summary Statistics (campaign / previous)")
    print(table1.to_string())
    print(
        f"[Note] `pdays` is excluded from Table 1: {PDAYS_SENTINEL} is a sentinel category "
        "(customer not previously contacted), not an actual day count, so mean/median/quartile "
        "statistics over it would not be meaningful. See Table 5 (contacted vs not contacted) "
        "and Table 5b (actual day statistics, pdays != 999 only) for the interpretable breakdowns."
    )

    # ---- Derived grouping columns (analysis-only; do not mutate the returned df) ----
    work = df.copy()
    work["campaign_group"] = work["campaign"].apply(lambda x: str(x) if x < 6 else "6+")
    work["previous_group"] = work["previous"].apply(lambda x: str(x) if x < 3 else "3+")
    work["previous_binary"] = work["previous"].apply(lambda x: "0" if x == 0 else ">=1")

    # `pdays` = 999 is a distinct category ("previously not contacted"), never a
    # numeric day count. It is analyzed as its own group and is NEVER combined
    # with actual day values in the same grouped chart/table.
    work["pdays_contact_status"] = np.where(
        work["pdays"] == PDAYS_SENTINEL, PDAYS_NOT_CONTACTED_LABEL, PDAYS_CONTACTED_LABEL
    )

    # ---- Table 2: Contact Method Summary ----
    contact_order = sorted(work[CONTACT_COL].unique())
    table_contact = _build_group_table(work, CONTACT_COL, contact_order)
    print(f"\n[{TABLE_TITLES['contact']}]")
    print(table_contact.to_string(index=False))

    # ---- Table 3: Campaign Frequency Summary ----
    campaign_order = [c for c in CAMPAIGN_GROUP_ORDER if c in work["campaign_group"].unique()]
    table_campaign = _build_group_table(work, "campaign_group", campaign_order)
    print(f"\n[{TABLE_TITLES['campaign_group']}]")
    print(table_campaign.to_string(index=False))

    # ---- Table 4: Previous Contact Summary ----
    previous_order = [c for c in PREVIOUS_GROUP_ORDER if c in work["previous_group"].unique()]
    table_previous = _build_group_table(work, "previous_group", previous_order)
    print(f"\n[{TABLE_TITLES['previous_group']}]")
    print(table_previous.to_string(index=False))
    for cat in ["2", "3+"]:
        if cat in table_previous["previous_group"].astype(str).values:
            n_cat = int(table_previous.loc[table_previous["previous_group"] == cat, "count"].iloc[0])
            print(f"[Note] `previous`={cat} has a comparatively small sample (n={n_cat}) relative to 0/1.")

    # ---- Table 4b: Previous Contact Summary (simplified 0 vs >=1) ----
    previous_binary_order = [c for c in PREVIOUS_BINARY_ORDER if c in work["previous_binary"].unique()]
    table_previous_binary = _build_group_table(work, "previous_binary", previous_binary_order)
    print(f"\n[{TABLE_TITLES['previous_binary']}]")
    print(table_previous_binary.to_string(index=False))

    # ---- Table 5: Pdays - Contacted vs Not Contacted Summary ----
    # pdays=999 ("previously not contacted") is kept fully separate from actual
    # day values here - this table only compares the two top-level groups.
    pdays_status_order = [c for c in PDAYS_CONTACT_STATUS_ORDER if c in work["pdays_contact_status"].unique()]
    table_pdays_status = _build_group_table(work, "pdays_contact_status", pdays_status_order)
    print(f"\n[{TABLE_TITLES['pdays_contact_status']}]")
    print(table_pdays_status.to_string(index=False))

    # ---- Table 5b: Pdays distribution among previously-contacted customers only ----
    # Analyzed strictly on the pdays != 999 subset (actual day values only).
    df_contacted = work.loc[work["pdays"] != PDAYS_SENTINEL]
    n_contacted = len(df_contacted)
    pdays_days_stats = _numeric_stats(df_contacted["pdays"])
    table_pdays_days = pd.DataFrame({"pdays (previously contacted only)": pdays_days_stats}).T
    print(f"\n[{TABLE_TITLES['pdays_days']}]")
    print(table_pdays_days.to_string())
    print(
        f"[Note] Actual `pdays` values are only observed for {n_contacted} previously-contacted "
        f"rows (pdays != {PDAYS_SENTINEL}), ranging {int(pdays_days_stats['min'])}-"
        f"{int(pdays_days_stats['max'])} days and concentrated well below 30 days; see Table 5c "
        "and Figure 4 (right panel) for a coarse day-range breakdown."
    )
    n_previous_ge1 = int((work["previous"] >= 1).sum())
    if n_previous_ge1 != n_contacted:
        print(
            f"[Note] `previous`>=1 ({n_previous_ge1} rows) is NOT identical to `pdays`!=999 "
            f"({n_contacted} rows) in this dataset; the pdays day-value analysis above uses "
            "pdays != 999 as the denominator, since that is the field being analyzed."
        )

    # ---- Table 5c: Pdays day-range summary (previously contacted only) ----
    # Coarse, fixed day-range grouping (0-7 / 8-14 / 15+) used ONLY to pair a
    # subscription-rate comparison with the contact-day distribution (Figure 4,
    # right panel) with more stable per-group sample sizes than fine-grained
    # bins. Small-sample groups are flagged via the same convention as every
    # other table in this module (`small_sample_flag`, count < threshold).
    def _pdays_days_group(x: int) -> str:
        if x <= 7:
            return "0-7"
        if x <= 14:
            return "8-14"
        return "15+"

    df_contacted = df_contacted.copy()
    df_contacted["pdays_days_group"] = df_contacted["pdays"].apply(_pdays_days_group)
    pdays_days_group_order = [c for c in PDAYS_DAYS_GROUP_ORDER if c in df_contacted["pdays_days_group"].unique()]
    table_pdays_days_group = _build_group_table(df_contacted, "pdays_days_group", pdays_days_group_order)
    print(f"\n[{TABLE_TITLES['pdays_days_group']}]")
    print(table_pdays_days_group.to_string(index=False))
    n_small_pdays_days_group = int(table_pdays_days_group["small_sample_flag"].sum())
    if n_small_pdays_days_group:
        small_groups = table_pdays_days_group.loc[table_pdays_days_group["small_sample_flag"], "pdays_days_group"].tolist()
        print(
            f"[Note] Day-range group(s) {small_groups} have count < {SMALL_SAMPLE_THRESHOLD} "
            "(small sample); their subscription rates should be interpreted with caution."
        )

    # ---- Table 6: Previous Campaign Outcome Summary (+ contribution to positive class) ----
    poutcome_order = [c for c in POUTCOME_ORDER if c in work[POUTCOME_COL].unique()]
    table_poutcome = _build_group_table(work, POUTCOME_COL, poutcome_order)
    table_poutcome["contribution_to_yes"] = table_poutcome["yes"] / n_yes
    print(f"\n[{TABLE_TITLES['poutcome']}]")
    print(table_poutcome.to_string(index=False))

    # ---- Table 7: Monthly Campaign Summary (calendar order) ----
    month_order = [m for m in MONTH_ORDER if m in work["month"].unique()]
    table_month = _build_group_table(work, "month", month_order)
    print(f"\n[{TABLE_TITLES['month']}]")
    print(table_month.to_string(index=False))

    # ---- Table 8: Weekday Campaign Summary (natural order) ----
    day_order = [d for d in DAY_ORDER if d in work["day_of_week"].unique()]
    table_day = _build_group_table(work, "day_of_week", day_order)
    print(f"\n[{TABLE_TITLES['day_of_week']}]")
    print(table_day.to_string(index=False))

    results.update(
        {
            "n_obs": n_obs,
            "n_yes": n_yes,
            "overall_rate": overall_rate,
            "table1_campaign_summary": table1,
            "table_contact": table_contact,
            "table_campaign_group": table_campaign,
            "table_previous_group": table_previous,
            "table_previous_binary": table_previous_binary,
            "table_pdays_status": table_pdays_status,
            "table_pdays_days": table_pdays_days,
            "table_pdays_days_group": table_pdays_days_group,
            "n_pdays_contacted": n_contacted,
            "table_poutcome": table_poutcome,
            "table_month": table_month,
            "table_day": table_day,
        }
    )
    return results


# ---------------------------------------------------------------------------
# visualization
# ---------------------------------------------------------------------------
def visualization(results: dict[str, Any]) -> list[Path]:
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

    def _bar_colors(flags: pd.Series) -> list[str]:
        return ["#d62728" if flag else "#1f77b4" for flag in flags]

    # ---- Figure 1: Subscription Rate by Contact Method (horizontal bar) ----
    t = results["table_contact"]
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.barh(t[CONTACT_COL].astype(str), t["subscription_rate"], color=_bar_colors(t["small_sample_flag"]))
    for y_pos, (rate, count) in enumerate(zip(t["subscription_rate"], t["count"])):
        ax.text(rate + 0.003, y_pos, f"n={count}", va="center", fontsize=8)
    ax.set_xlabel("Subscription Rate")
    ax.set_xlim(0, min(1.0, t["subscription_rate"].max() * 1.25 + 0.02))
    ax.set_title(f"Figure 1: Subscription Rate by Contact Method\n(red bar = small sample, n < {SMALL_SAMPLE_THRESHOLD})")
    fig.tight_layout()
    _save(fig, "figure1_subscription_rate_by_contact")

    # ---- Figure 2: Subscription Rate by Campaign Frequency (vertical bar) ----
    t = results["table_campaign_group"]
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(t["campaign_group"].astype(str), t["subscription_rate"], color=_bar_colors(t["small_sample_flag"]))
    for x_pos, (rate, count) in enumerate(zip(t["subscription_rate"], t["count"])):
        ax.text(x_pos, (rate or 0) + 0.005, f"n={count}", ha="center", fontsize=8)
    ax.set_xlabel("Campaign Frequency (contacts this campaign)")
    ax.set_ylabel("Subscription Rate")
    ax.set_title(f"Figure 2: Subscription Rate by Campaign Frequency\n(red bar = small sample, n < {SMALL_SAMPLE_THRESHOLD})")
    fig.tight_layout()
    _save(fig, "figure2_subscription_rate_by_campaign_frequency")

    # ---- Figure 3: Subscription Rate by Previous Contact Count (vertical bar) ----
    t = results["table_previous_group"]
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(t["previous_group"].astype(str), t["subscription_rate"], color=_bar_colors(t["small_sample_flag"]))
    for x_pos, (rate, count) in enumerate(zip(t["subscription_rate"], t["count"])):
        ax.text(x_pos, (rate or 0) + 0.01, f"n={count}", ha="center", fontsize=8)
    ax.set_xlabel("Previous Contacts (before this campaign)")
    ax.set_ylabel("Subscription Rate")
    ax.set_title(f"Figure 3: Subscription Rate by Previous Contact Count\n(red bar = small sample, n < {SMALL_SAMPLE_THRESHOLD})")
    fig.tight_layout()
    _save(fig, "figure3_subscription_rate_by_previous_count")

    # ---- Figure 4: Pdays - Contacted vs Not Contacted (left) + Contact-Day ----
    # Distribution for previously-contacted customers only (right). pdays=999
    # is NEVER combined with actual day values in the same panel/chart.
    t_status = results["table_pdays_status"]
    fig, (ax_left, ax_right) = plt.subplots(1, 2, figsize=(13, 5))

    ax_left.bar(
        t_status["pdays_contact_status"].astype(str),
        t_status["subscription_rate"],
        color=_bar_colors(t_status["small_sample_flag"]),
    )
    for x_pos, (rate, count) in enumerate(zip(t_status["subscription_rate"], t_status["count"])):
        ax_left.text(x_pos, (rate or 0) + 0.005, f"n={count}", ha="center", fontsize=8)
    ax_left.set_xlabel("Pdays Contact Status")
    ax_left.set_ylabel("Subscription Rate")
    ax_left.set_title("Subscription Rate:\nPreviously Contacted vs Not Contacted")
    ax_left.tick_params(axis="x", labelrotation=8)

    n_contacted = results["n_pdays_contacted"]
    contacted_overall_rate = t_status.loc[t_status["pdays_contact_status"] == PDAYS_CONTACTED_LABEL, "subscription_rate"].iloc[0]

    t_days = results["table_pdays_days_group"]
    ax_right.bar(
        t_days["pdays_days_group"].astype(str),
        t_days["count"],
        color=_bar_colors(t_days["small_sample_flag"]),
        alpha=0.85,
    )
    ax_right.set_xlabel("Pdays Day Range (previously contacted only)")
    ax_right.set_ylabel("Count")

    ax_rate = ax_right.twinx()
    ax_rate.plot(
        t_days["pdays_days_group"].astype(str), t_days["subscription_rate"], marker="o", color="#ff7f0e",
        label="Subscription rate",
    )
    for flag, x_pos, rate in zip(t_days["small_sample_flag"], range(len(t_days)), t_days["subscription_rate"]):
        if flag:
            ax_rate.scatter([x_pos], [rate], color="#d62728", zorder=5, s=60)
    ax_rate.axhline(
        contacted_overall_rate, color="grey", linestyle="--", linewidth=1,
        label="Previously contacted overall rate",
    )
    ax_rate.set_ylabel("Subscription Rate")
    ax_rate.grid(False)
    ax_rate.legend(loc="upper right", fontsize=8)
    ax_right.set_title(f"Day-Range Distribution & Subscription Rate\n(previously contacted only, n={n_contacted})")

    fig.suptitle(
        f"Figure 4: Pdays - Contact Status (left), Day-Range Distribution & Subscription Rate (right)\n"
        f"(red bar/dot = small sample, n < {SMALL_SAMPLE_THRESHOLD}; day ranges: 0-7 / 8-14 / 15+, pdays=999 excluded from right panel)"
    )
    fig.tight_layout(rect=(0, 0, 1, 0.90))
    _save(fig, "figure4_subscription_rate_by_pdays_group")

    # ---- Figure 5: Subscription Rate by Previous Campaign Outcome (vertical bar) ----
    t = results["table_poutcome"]
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.bar(t[POUTCOME_COL].astype(str), t["subscription_rate"], color=_bar_colors(t["small_sample_flag"]))
    for x_pos, (rate, count) in enumerate(zip(t["subscription_rate"], t["count"])):
        ax.text(x_pos, (rate or 0) + 0.01, f"n={count}", ha="center", fontsize=8)
    ax.set_xlabel("Previous Campaign Outcome")
    ax.set_ylabel("Subscription Rate")
    ax.set_title(f"Figure 5: Subscription Rate by Previous Campaign Outcome\n(red bar = small sample, n < {SMALL_SAMPLE_THRESHOLD})")
    fig.tight_layout()
    _save(fig, "figure5_subscription_rate_by_poutcome")

    # ---- Figure 6: Monthly Campaign Volume + Subscription Rate (dual y-axis) ----
    # Combines the former separate volume bar chart and rate line chart into a
    # single chart, preserving each series' original style (bar / line colors,
    # small-sample markers, overall-rate reference line).
    t = results["table_month"]
    fig, ax_bar = plt.subplots(figsize=(9, 5))
    ax_bar.bar(t["month"].astype(str), t["count"], color=_bar_colors(t["small_sample_flag"]), alpha=0.85)
    ax_bar.set_xlabel("Month")
    ax_bar.set_ylabel("Campaign Count")

    ax_line = ax_bar.twinx()
    ax_line.plot(t["month"].astype(str), t["subscription_rate"], marker="o", color="#ff7f0e", label="Subscription rate")
    for flag, x_pos, rate in zip(t["small_sample_flag"], range(len(t)), t["subscription_rate"]):
        if flag:
            ax_line.scatter([x_pos], [rate], color="#d62728", zorder=5, s=60)
    ax_line.axhline(results["overall_rate"], color="grey", linestyle="--", linewidth=1, label="Overall rate")
    ax_line.set_ylabel("Subscription Rate")
    ax_line.grid(False)
    ax_line.legend(loc="upper right")

    ax_bar.set_title(
        f"Figure 6: Monthly Campaign Volume (bar) and Subscription Rate (line)\n"
        f"(red bar/dot = small sample, n < {SMALL_SAMPLE_THRESHOLD}; dashed line = overall rate)"
    )
    fig.tight_layout()
    _save(fig, "figure6_monthly_volume_and_rate")

    # ---- Figure 7: Subscription Rate by Weekday (vertical bar, natural order) ----
    t = results["table_day"]
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.bar(t["day_of_week"].astype(str), t["subscription_rate"], color=_bar_colors(t["small_sample_flag"]))
    for x_pos, (rate, count) in enumerate(zip(t["subscription_rate"], t["count"])):
        ax.text(x_pos, (rate or 0) + 0.005, f"n={count}", ha="center", fontsize=8)
    ax.set_xlabel("Day of Week")
    ax.set_ylabel("Subscription Rate")
    ax.set_title(f"Figure 7: Subscription Rate by Weekday\n(red bar = small sample, n < {SMALL_SAMPLE_THRESHOLD})")
    fig.tight_layout()
    _save(fig, "figure7_subscription_rate_by_weekday")

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
            display_df[col] = display_df[col].map(lambda v: float_fmt.format(v) if pd.notna(v) else "N/A")

    headers = [str(c) for c in display_df.columns]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for _, row in display_df.iterrows():
        lines.append("| " + " | ".join(str(v) for v in row.tolist()) + " |")
    return "\n".join(lines)


def generate_summary_report(
    results: dict[str, Any],
    prep_info: dict[str, Any],
) -> Path:
    """Write the Markdown summary report (Observation / Key Statistics /
    Notable Patterns), plus a supporting data-table appendix and figure
    gallery, to REPORT_PATH."""
    print("\n" + "=" * 78)
    print("STEP 4: Generate Summary Report")
    print("=" * 78)

    overall_rate = results["overall_rate"]
    n_obs = results["n_obs"]
    n_yes = results["n_yes"]
    table1 = results["table1_campaign_summary"]
    table_contact = results["table_contact"]
    table_campaign = results["table_campaign_group"]
    table_previous = results["table_previous_group"]
    table_previous_binary = results["table_previous_binary"]
    table_pdays_status = results["table_pdays_status"]
    table_pdays_days = results["table_pdays_days"]
    table_pdays_days_group = results["table_pdays_days_group"]
    n_pdays_contacted = results["n_pdays_contacted"]
    table_poutcome = results["table_poutcome"]
    table_month = results["table_month"]
    table_day = results["table_day"]

    # ---- Observation (objective description only) ----
    observation = [
        f"Data source (raw file): `{prep_info['raw_path']}`.",
        (
            f"After removing {prep_info['n_exact_duplicates_removed']} exact duplicate rows "
            f"({prep_info['n_before_dedup']} rows before -> {prep_info['n_after_dedup']} rows after), "
            f"the cleaned dataset used for this module contains {prep_info['n_final']} observations "
            f"and the 8 columns required for campaign strategy analysis: {REQUIRED_COLS}."
        ),
        f"`{prep_info['excluded_col']}` was excluded from this module (data leakage - only known after a call ends).",
        (
            f"Overall term deposit subscription rate is {overall_rate:.4f} "
            f"({n_yes} yes out of {n_obs} observations)."
        ),
        (
            f"`campaign` (contacts made during this campaign) ranges from "
            f"{int(table1.loc['campaign', 'min'])} to {int(table1.loc['campaign', 'max'])}, "
            f"mean={table1.loc['campaign', 'mean']:.2f}, median={table1.loc['campaign', 'median']:.1f}."
        ),
        (
            f"`previous` (contacts before this campaign) ranges from "
            f"{int(table1.loc['previous', 'min'])} to {int(table1.loc['previous', 'max'])}, "
            f"mean={table1.loc['previous', 'mean']:.2f}, median={table1.loc['previous', 'median']:.1f}."
        ),
        (
            f"`pdays` = {PDAYS_SENTINEL} is treated as its own category, \"{PDAYS_NOT_CONTACTED_LABEL}\", "
            f"NOT as a numeric day count. It applies to "
            f"{int(table_pdays_status.loc[table_pdays_status['pdays_contact_status'] == PDAYS_NOT_CONTACTED_LABEL, 'count'].iloc[0])} "
            f"observations ({int(table_pdays_status.loc[table_pdays_status['pdays_contact_status'] == PDAYS_NOT_CONTACTED_LABEL, 'percentage'].iloc[0])}% "
            "of the dataset, rounded); `pdays` is therefore excluded from Table 1's mean/quartile "
            "statistics (see Table 5 and Table 5b for the interpretable breakdowns)."
        ),
        (
            f"For the {n_pdays_contacted} observations previously contacted (`pdays` != {PDAYS_SENTINEL}), "
            f"actual day values range from {int(table_pdays_days.loc['pdays (previously contacted only)', 'min'])} "
            f"to {int(table_pdays_days.loc['pdays (previously contacted only)', 'max'])} days "
            f"(mean={table_pdays_days.loc['pdays (previously contacted only)', 'mean']:.2f}, "
            f"median={table_pdays_days.loc['pdays (previously contacted only)', 'median']:.1f}), "
            "concentrated well below 30 days; see Table 5c and Figure 4 (right panel) for a coarse "
            "day-range (0-7 / 8-14 / 15+) breakdown paired with subscription rate."
        ),
        (
            f"`previous` >= 1 applies to "
            f"{int(table_previous_binary.loc[table_previous_binary['previous_binary'] == '>=1', 'count'].iloc[0])} "
            f"observations, which is NOT identical to the {n_pdays_contacted} observations with `pdays` != {PDAYS_SENTINEL} "
            "in this dataset; the two fields are related but not interchangeable, and each is analyzed on its own terms above."
        ),
        (
            f"`poutcome` = 'nonexistent' accounts for "
            f"{int(table_poutcome.loc[table_poutcome[POUTCOME_COL] == 'nonexistent', 'count'].iloc[0])} observations, "
            f"'failure' for {int(table_poutcome.loc[table_poutcome[POUTCOME_COL] == 'failure', 'count'].iloc[0])}, "
            f"and 'success' for {int(table_poutcome.loc[table_poutcome[POUTCOME_COL] == 'success', 'count'].iloc[0])}."
        ),
    ]

    # ---- Key Statistics ----
    key_statistics = [
        f"Dataset size (cleaned): {n_obs} observations; overall subscription rate: {overall_rate:.4f}.",
    ]
    for col_key, series_col, label in [
        ("table_contact", CONTACT_COL, "Contact method"),
        ("table_campaign_group", "campaign_group", "Campaign frequency"),
        ("table_previous_group", "previous_group", "Previous contact count"),
        ("table_previous_binary", "previous_binary", "Previous contact (simplified: 0 vs >=1)"),
        ("table_pdays_status", "pdays_contact_status", "Pdays contact status"),
        ("table_pdays_days_group", "pdays_days_group", "Pdays day range (previously contacted only)"),
        ("table_poutcome", POUTCOME_COL, "Previous campaign outcome"),
        ("table_month", "month", "Month"),
        ("table_day", "day_of_week", "Weekday"),
    ]:
        t = results[col_key]
        valid = t[t["subscription_rate"].notna()]
        if valid.empty:
            key_statistics.append(f"{label}: no non-empty categories.")
            continue
        top = valid.loc[valid["subscription_rate"].idxmax()]
        bottom = valid.loc[valid["subscription_rate"].idxmin()]
        n_small = int(t["small_sample_flag"].sum())
        key_statistics.append(
            f"{label}: highest subscription rate = `{top[series_col]}` "
            f"({top['subscription_rate']:.4f}, n={int(top['count'])}"
            f"{', small sample' if bool(top['small_sample_flag']) else ''}); "
            f"lowest = `{bottom[series_col]}` ({bottom['subscription_rate']:.4f}, n={int(bottom['count'])}"
            f"{', small sample' if bool(bottom['small_sample_flag']) else ''}); "
            f"{n_small} of {len(t)} categories flagged as small sample (n<{SMALL_SAMPLE_THRESHOLD})."
        )

    key_statistics.append(
        f"Pdays (previously contacted only, n={n_pdays_contacted}): actual day values range "
        f"{int(table_pdays_days.loc['pdays (previously contacted only)', 'min'])}-"
        f"{int(table_pdays_days.loc['pdays (previously contacted only)', 'max'])} days, "
        f"mean={table_pdays_days.loc['pdays (previously contacted only)', 'mean']:.2f}, "
        f"median={table_pdays_days.loc['pdays (previously contacted only)', 'median']:.1f}; "
        "see Table 5c / Figure 4 for the coarse day-range subscription-rate comparison above."
    )
    top_contrib = table_poutcome.loc[table_poutcome["contribution_to_yes"].idxmax()]
    key_statistics.append(
        f"Contribution to total positive class (yes) by `poutcome`: highest is `{top_contrib[POUTCOME_COL]}` "
        f"({top_contrib['contribution_to_yes']:.4f}, i.e. {top_contrib['contribution_to_yes']:.2%} of all "
        f"subscribers, from {int(top_contrib['count'])} observations, "
        f"{top_contrib['count'] / n_obs:.2%} of the dataset)."
    )

    # ---- Notable Patterns (descriptive; no causal language) ----
    n_campaign_6plus = int(table_campaign.loc[table_campaign["campaign_group"] == "6+", "count"].iloc[0]) if "6+" in table_campaign["campaign_group"].astype(str).values else 0
    pct_campaign_6plus = n_campaign_6plus / n_obs * 100
    month_counts_sorted = table_month.sort_values("count", ascending=False)
    top_volume_month = month_counts_sorted.iloc[0]
    month_rate_sorted = table_month[table_month["subscription_rate"].notna()].sort_values(
        "subscription_rate", ascending=False
    )
    top_rate_month = month_rate_sorted.iloc[0]

    n_prev_2 = int(table_previous.loc[table_previous["previous_group"] == "2", "count"].iloc[0]) if "2" in table_previous["previous_group"].astype(str).values else 0
    n_prev_3plus = int(table_previous.loc[table_previous["previous_group"] == "3+", "count"].iloc[0]) if "3+" in table_previous["previous_group"].astype(str).values else 0

    # Sparsity check for the pdays day-range groups (Table 5c): single source of
    # truth is the `small_sample_flag` already computed by `_build_group_table`,
    # objectively reported here without additional interpretation.
    thin_day_groups = [
        f"`{row['pdays_days_group']}` (n={int(row['count'])})"
        for _, row in table_pdays_days_group.loc[table_pdays_days_group["small_sample_flag"]].iterrows()
    ]

    notable_patterns = [
        (
            f"Customers contacted 6 or more times during this campaign represent "
            f"{n_campaign_6plus} observations ({pct_campaign_6plus:.2f}% of the dataset); "
            "this is a small share relative to customers contacted 1-5 times."
        ),
        (
            f"The `previous`, `pdays`, and `poutcome` variables are highly imbalanced: most customers "
            f"have `previous`=0, `pdays`={PDAYS_SENTINEL} (not previously contacted), and "
            "`poutcome`='nonexistent', consistent with each other (no prior campaign contact)."
        ),
        (
            f"Within `previous` (Table 4), the `2` (n={n_prev_2}) and `3+` (n={n_prev_3plus}) categories are "
            "considerably smaller samples than `0` and `1`; their subscription rates are reported but should "
            "be interpreted cautiously given the limited sample size. The simplified `0` vs `>=1` split "
            "(Table 4b) avoids this sparsity by pooling all previously-contacted customers into one group."
        ),
        (
            f"Among previously-contacted customers (`pdays` != {PDAYS_SENTINEL}, n={n_pdays_contacted}), "
            "actual day values are heavily concentrated at low values (median "
            f"{table_pdays_days.loc['pdays (previously contacted only)', 'median']:.1f} days) with a long, "
            "thin tail out to "
            f"{int(table_pdays_days.loc['pdays (previously contacted only)', 'max'])} days. Table 5c / Figure 4 "
            "pair a coarse day-range grouping (0-7 / 8-14 / 15+) with subscription rate for a more stable "
            "comparison than the raw day values would allow. "
            + (
                f"Day-range group(s) {', '.join(thin_day_groups)} have count < {SMALL_SAMPLE_THRESHOLD} "
                "(flagged `small_sample_flag`, shown as a red bar/dot in Figure 4); their subscription rates "
                "should be read with caution rather than compared precisely against the other groups."
                if thin_day_groups
                else "All day-range groups meet the small-sample threshold, supporting a descriptive comparison."
            )
        ),
        (
            f"`poutcome`='success' has {int(table_poutcome.loc[table_poutcome[POUTCOME_COL] == 'success', 'count'].iloc[0])} "
            "observations, a much smaller share than 'nonexistent'; its subscription rate should be read "
            "together with this smaller sample size. Despite its small size, its contribution to the total "
            "positive class is "
            f"{table_poutcome.loc[table_poutcome[POUTCOME_COL] == 'success', 'contribution_to_yes'].iloc[0]:.2%} "
            "(see Table 6), disproportionately high relative to its share of the dataset."
        ),
        (
            f"Campaign volume is not evenly distributed across months: the highest-volume month is "
            f"`{top_volume_month['month']}` (n={int(top_volume_month['count'])}), while the highest "
            f"subscription-rate month is `{top_rate_month['month']}` "
            f"(rate={top_rate_month['subscription_rate']:.4f}, n={int(top_rate_month['count'])}"
            f"{', small sample' if bool(top_rate_month['small_sample_flag']) else ''}). "
            "Month comparisons should consider both rate and volume together (see Figure 6, combined view)."
        ),
        (
            "This module identifies statistical associations between campaign characteristics and "
            "subscription outcomes only; it does not establish whether a particular campaign strategy "
            "directly causes higher subscription rates. Customer characteristics and macroeconomic "
            "conditions are analyzed in separate modules to avoid overlapping interpretation."
        ),
    ]

    # ---- Final Business Summary (synthesis only; no new EDA / no prediction) ----
    cellular_row = table_contact.loc[table_contact[CONTACT_COL] == "cellular"].iloc[0]
    telephone_row = table_contact.loc[table_contact[CONTACT_COL] == "telephone"].iloc[0]
    campaign_1_row = table_campaign.loc[table_campaign["campaign_group"] == "1"].iloc[0]
    campaign_6plus_row = table_campaign.loc[table_campaign["campaign_group"] == "6+"].iloc[0]
    previous_0_row = table_previous_binary.loc[table_previous_binary["previous_binary"] == "0"].iloc[0]
    previous_ge1_row = table_previous_binary.loc[table_previous_binary["previous_binary"] == ">=1"].iloc[0]
    pdays_not_contacted_row = table_pdays_status.loc[
        table_pdays_status["pdays_contact_status"] == PDAYS_NOT_CONTACTED_LABEL
    ].iloc[0]
    pdays_contacted_row = table_pdays_status.loc[
        table_pdays_status["pdays_contact_status"] == PDAYS_CONTACTED_LABEL
    ].iloc[0]
    pdays_0_7_row = table_pdays_days_group.loc[table_pdays_days_group["pdays_days_group"] == "0-7"].iloc[0]
    pdays_15plus_row = table_pdays_days_group.loc[table_pdays_days_group["pdays_days_group"] == "15+"].iloc[0]
    poutcome_success_row = table_poutcome.loc[table_poutcome[POUTCOME_COL] == "success"].iloc[0]
    poutcome_nonexistent_row = table_poutcome.loc[table_poutcome[POUTCOME_COL] == "nonexistent"].iloc[0]
    weekday_top = table_day.loc[table_day["subscription_rate"].idxmax()]
    weekday_bottom = table_day.loc[table_day["subscription_rate"].idxmin()]

    final_key_findings = [
        (
            f"Contact channel matters in the observed data: `cellular` contacts show a higher subscription "
            f"rate ({cellular_row['subscription_rate']:.4f}, n={int(cellular_row['count'])}) than "
            f"`telephone` contacts ({telephone_row['subscription_rate']:.4f}, n={int(telephone_row['count'])})."
        ),
        (
            f"Lower contact frequency during the current campaign is associated with higher observed "
            f"subscription rates: one contact has the highest rate ({campaign_1_row['subscription_rate']:.4f}, "
            f"n={int(campaign_1_row['count'])}), while `6+` contacts has the lowest rate "
            f"({campaign_6plus_row['subscription_rate']:.4f}, n={int(campaign_6plus_row['count'])})."
        ),
        (
            f"Prior campaign engagement is the strongest descriptive signal in this module: customers with "
            f"`previous >= 1` show a higher rate ({previous_ge1_row['subscription_rate']:.4f}, "
            f"n={int(previous_ge1_row['count'])}) than `previous = 0` "
            f"({previous_0_row['subscription_rate']:.4f}, n={int(previous_0_row['count'])}); "
            f"`pdays != {PDAYS_SENTINEL}` also has a higher rate "
            f"({pdays_contacted_row['subscription_rate']:.4f}, n={int(pdays_contacted_row['count'])}) than "
            f"`pdays = {PDAYS_SENTINEL}` ({pdays_not_contacted_row['subscription_rate']:.4f}, "
            f"n={int(pdays_not_contacted_row['count'])})."
        ),
        (
            f"`poutcome = success` has the highest previous-outcome subscription rate "
            f"({poutcome_success_row['subscription_rate']:.4f}, n={int(poutcome_success_row['count'])}) and "
            f"contributes {poutcome_success_row['contribution_to_yes']:.2%} of all positive cases, despite "
            f"representing only {poutcome_success_row['percentage']:.2f}% of observations."
        ),
        (
            f"Timing patterns are uneven: the highest subscription-rate month is `{top_rate_month['month']}` "
            f"({top_rate_month['subscription_rate']:.4f}, n={int(top_rate_month['count'])}), while the "
            f"highest-volume month is `{top_volume_month['month']}` (n={int(top_volume_month['count'])}, "
            f"rate={top_volume_month['subscription_rate']:.4f}). Weekday differences are comparatively modest, "
            f"from `{weekday_bottom['day_of_week']}` ({weekday_bottom['subscription_rate']:.4f}) to "
            f"`{weekday_top['day_of_week']}` ({weekday_top['subscription_rate']:.4f})."
        ),
    ]

    recommended_targeting_insights = [
        (
            "Prioritize `cellular` as the observed contact channel associated with higher subscription rates, "
            "while recognizing that this is a descriptive association and may reflect customer/channel mix."
        ),
        (
            "Use early campaign contacts more carefully: customers contacted once show the strongest observed "
            "rate, whereas repeated `6+` contacts are associated with the lowest rate in this module."
        ),
        (
            "Treat prior positive engagement (`previous >= 1`, `pdays != 999`, and especially "
            "`poutcome = success`) as a business targeting signal for follow-up prioritization, not as a "
            "predictive score."
        ),
        (
            f"For customers with actual previous-contact day values, the `0-7` day group has the highest "
            f"observed rate ({pdays_0_7_row['subscription_rate']:.4f}, n={int(pdays_0_7_row['count'])}); "
            f"the `15+` group is small (n={int(pdays_15plus_row['count'])}) and should be treated as a "
            "cautionary reference rather than a planning rule."
        ),
        (
            "Use month-level results to support campaign calendar planning, balancing rate and volume: months "
            "with high rates are often much lower volume than the main campaign months."
        ),
    ]

    data_limitations = [
        (
            "This module is descriptive EDA only. It does not control for customer profile, macroeconomic "
            "conditions, offer context, or channel assignment effects, and it does not establish causality."
        ),
        (
            f"`pdays`, `previous`, and `poutcome` are highly imbalanced: `pdays = {PDAYS_SENTINEL}` and "
            "`poutcome = nonexistent` dominate the dataset, while the actual `pdays` day-value subset "
            f"contains only {n_pdays_contacted} observations."
        ),
        (
            f"Some high-rate categories have limited sample sizes or concentrated distributions, including "
            f"`previous = 3+` (n={n_prev_3plus}) and the `pdays` `15+` group "
            f"(n={int(pdays_15plus_row['count'])})."
        ),
        (
            "`duration` is intentionally excluded because it is only known after a call ends and would cause "
            "data leakage for pre-contact campaign strategy evaluation."
        ),
        (
            "`previous >= 1` and `pdays != 999` are related but not interchangeable in this dataset, so "
            "business interpretation should keep these fields separate."
        ),
    ]

    decision_supported = [
        (
            "Channel planning can be informed by the observed higher subscription rate for `cellular` versus "
            "`telephone` contacts."
        ),
        (
            "Contact-frequency management can be informed by the declining observed rates from first contact "
            "to high repeated-contact groups (`6+`)."
        ),
        (
            "Follow-up prioritization can use prior campaign engagement as a descriptive signal, especially "
            "`poutcome = success`, `previous >= 1`, and `pdays != 999`."
        ),
        (
            "Campaign calendar review can use the month-level volume/rate contrast to avoid relying only on "
            "volume-heavy months when assessing timing performance."
        ),
    ]

    avoid_overinterpretation = [
        (
            "Do not interpret high rates for prior-success or previously-contacted customers as proof that "
            "previous contact caused subscription; these groups may differ systematically from the broader "
            "population."
        ),
        (
            "Do not treat high-rate low-volume months as automatically scalable campaign windows; monthly "
            "volume is uneven and may reflect campaign design or seasonality outside this module."
        ),
        (
            f"Do not overstate small or sparse groups, including `previous = 3+` and `pdays` `15+` "
            f"(n={int(pdays_15plus_row['count'])})."
        ),
        (
            "Do not use weekday differences as a primary targeting rule; the observed range is narrow compared "
            "with channel, prior-engagement, and month-level differences."
        ),
        (
            "Do not convert these findings into an individual-level prediction or scoring rule without a "
            "separate modeling workflow and validation."
        ),
    ]

    # ---- Assemble Markdown ----
    lines: list[str] = []
    lines.append("# Module 2 - Campaign Strategy Evaluation: Summary Report")
    lines.append("")
    lines.append(
        "*Business question: Which telephone marketing strategies and historical campaign "
        "characteristics are associated with higher term deposit subscription rates?*"
    )
    lines.append("")
    lines.append(
        f"*Data source: `{prep_info['raw_path']}` (raw), cleaned by removing "
        f"{prep_info['n_exact_duplicates_removed']} exact duplicate rows -> "
        f"{prep_info['n_final']} observations analyzed. `{prep_info['excluded_col']}` excluded (data leakage).*"
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
        "*Business question: Which telephone marketing strategies and historical campaign "
        "characteristics are associated with higher term deposit subscription rates?*"
    )
    lines.append("")

    lines.append("### Overall Conclusion")
    lines.extend(f"- {item}" for item in final_key_findings)
    lines.append("")

    lines.append("### Business Implications")
    lines.extend(f"- {item}" for item in recommended_targeting_insights)
    lines.extend(f"- {item}" for item in decision_supported)
    lines.append("")

    lines.append("### Limitations")
    lines.extend(f"- {item}" for item in data_limitations)
    lines.extend(f"- {item}" for item in avoid_overinterpretation)
    lines.append("")

    lines.append("## Appendix: Data Tables")
    lines.append("")
    lines.append("### Table 1 - Campaign Summary Statistics (campaign / previous)")
    lines.append("")
    lines.append(
        f"*Note: `pdays` is excluded from this table. Its value of {PDAYS_SENTINEL} is a sentinel "
        "category (not previously contacted), not an actual day count, so mean/median/quartile "
        "statistics over it would not be meaningful. See Table 5 (contacted vs not contacted) and "
        "Table 5b (actual day statistics, pdays != 999 only) for the interpretable breakdowns.*"
    )
    lines.append("")
    lines.append(_df_to_markdown(table1, index=True))
    lines.append("")

    def _render_table_spec(key: str, title: str, cols: list[str]) -> None:
        lines.append(f"### {title}")
        lines.append("")
        note = (
            "*Displayed in calendar/natural/logical order (not sorted by subscription rate); "
            "`rate_rank` reports the subscription-rate ranking (1 = highest) per the Ranking "
            f"Analysis method. Categories with count < {SMALL_SAMPLE_THRESHOLD} are flagged "
            "`small_sample_flag = Yes`."
        )
        if key == "table_poutcome":
            note += (
                " `contribution_to_yes` = (yes count in this category) / (total yes count across the "
                "whole dataset), i.e. this category's share of all positive-class (subscribed) customers."
            )
        note += "*"
        lines.append(note)
        lines.append("")
        lines.append(_df_to_markdown(results[key][cols]))
        lines.append("")

    table_specs_part1 = [
        ("table_contact", "Table 2 - Contact Method Summary", [CONTACT_COL, "count", "percentage", "yes", "subscription_rate", "rate_rank", "small_sample_flag"]),
        ("table_campaign_group", "Table 3 - Campaign Frequency Summary", ["campaign_group", "count", "percentage", "yes", "subscription_rate", "rate_rank", "small_sample_flag"]),
        ("table_previous_group", "Table 4 - Previous Contact Summary", ["previous_group", "count", "percentage", "yes", "subscription_rate", "rate_rank", "small_sample_flag"]),
        ("table_previous_binary", "Table 4b - Previous Contact Summary (Simplified: 0 vs >=1)", ["previous_binary", "count", "percentage", "yes", "subscription_rate", "rate_rank", "small_sample_flag"]),
        ("table_pdays_status", "Table 5 - Pdays: Contacted vs Not Contacted Summary", ["pdays_contact_status", "count", "percentage", "yes", "subscription_rate", "rate_rank", "small_sample_flag"]),
    ]
    for key, title, cols in table_specs_part1:
        _render_table_spec(key, title, cols)

    lines.append("### Table 5b - Pdays Distribution (Previously Contacted Only, actual days)")
    lines.append("")
    lines.append(
        f"*Descriptive statistics of actual `pdays` day values, computed ONLY on the "
        f"{n_pdays_contacted} rows where `pdays` != {PDAYS_SENTINEL} (pdays = {PDAYS_SENTINEL} is excluded "
        "here since it is not a day count). See Table 5c and Figure 4 (right panel) for a coarse "
        "day-range breakdown of this same subset paired with subscription rate.*"
    )
    lines.append("")
    lines.append(_df_to_markdown(table_pdays_days, index=True))
    lines.append("")

    _render_table_spec(
        "table_pdays_days_group",
        "Table 5c - Pdays Day-Range Summary (Previously Contacted Only)",
        ["pdays_days_group", "count", "percentage", "yes", "subscription_rate", "rate_rank", "small_sample_flag"],
    )

    table_specs_part2 = [
        ("table_poutcome", "Table 6 - Previous Campaign Outcome Summary", [POUTCOME_COL, "count", "percentage", "yes", "subscription_rate", "rate_rank", "contribution_to_yes", "small_sample_flag"]),
        ("table_month", "Table 7 - Monthly Campaign Summary", ["month", "count", "percentage", "yes", "subscription_rate", "rate_rank", "small_sample_flag"]),
        ("table_day", "Table 8 - Weekday Campaign Summary", ["day_of_week", "count", "percentage", "yes", "subscription_rate", "rate_rank", "small_sample_flag"]),
    ]
    for key, title, cols in table_specs_part2:
        _render_table_spec(key, title, cols)

    lines.append("## Figures")
    lines.append("")
    for fname, title in FIGURE_FILES:
        rel_path = f"../images/module2_campaign_strategy/{fname}"
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
    visualization(results)
    report_path = generate_summary_report(results, prep_info)

    print("\n" + "=" * 78)
    print("Module 2 - Campaign Strategy Evaluation: COMPLETE")
    print("=" * 78)
    print(f"Figures saved to : {FIGURES_DIR}")
    print(f"Report saved to  : {report_path}")


if __name__ == "__main__":
    main()
