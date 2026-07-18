"""
Module 3 - Market Environment Analysis
=========================================

Business Question
------------------
How are macroeconomic conditions associated with term deposit subscription,
and should changes in the economic environment be considered when evaluating
telephone marketing performance?

Analysis Goal
-------------
Evaluate whether changes in macroeconomic indicators coincide with
differences in subscription outcomes, and provide market context for
interpreting campaign performance. This module is descriptive and
comparative ONLY - it does not quantify causal effects and does NOT include
any predictive modeling.

Scope
-----
Only the following columns are analyzed:
    emp.var.rate, cons.price.idx, cons.conf.idx, euribor3m, nr.employed,
    month, y
`month` is used only for chronological ordering and trend visualization.
Customer characteristics (Module 1) and campaign execution (Module 2) are
out of scope for this module and are analyzed separately.

Data Source (confirm before analysis)
--------------------------------------
This project ships two RAW dataset files (neither is de-duplicated):
    - data/bank-additional/bank-additional-full.csv  (full dataset, 41,188 rows)
    - data/bank-additional/bank-additional.csv       (10% sample, 4,119 rows)

There is no separately-saved "cleaned" CSV file in this project. Every EDA
module in this codebase (see eda/data_cleaning.py, eda/utils.py
`ensure_cleaned`, module1_customer_profile.py, module2_campaign_strategy.py)
defines the "cleaned dataset" as:

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
    uv run python module3_market_environment_analysis.py
    (or) python module3_market_environment_analysis.py

This script has no dependency on any other file in this project (e.g. the
`eda` package, module1_customer_profile.py, or module2_campaign_strategy.py)
and can be run independently, provided pandas, numpy, matplotlib, and
seaborn are installed.

Structure
---------
    load_data()               - locate & load the raw CSV, confirm its path
    data_preprocessing()      - remove exact duplicates, select columns,
                                 verify dtypes (macro vars numeric, month
                                 categorical)
    analysis()                - descriptive stats for macro variables,
                                 stats by subscription status, monthly market
                                 summary, correlation matrix, correlation
                                 with subscription, high-correlation pairs
    visualization()           - Figures 1-6 (saved as PNG files; Figure 2
                                 overlays normalized emp.var.rate/euribor3m/
                                 nr.employed against monthly subscription rate
                                 on a dual y-axis, Figures 3-4 pair
                                 cons.price.idx / cons.conf.idx against
                                 subscription rate on a dual y-axis, Figure 5
                                 extends the correlation heatmap to include
                                 subscription status)
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
FIGURES_DIR = PROJECT_ROOT / "images" / "module3_market_environment_analysis"
REPORT_PATH = PROJECT_ROOT / "reports" / "module3_market_environment_analysis_summary.md"

TARGET_COL = "y"
MONTH_COL = "month"
MACRO_COLS = ["emp.var.rate", "cons.price.idx", "cons.conf.idx", "euribor3m", "nr.employed"]
REQUIRED_COLS = MACRO_COLS + [MONTH_COL, TARGET_COL]

MONTH_ORDER = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]

HIGH_CORR_THRESHOLD = 0.80

TABLE_TITLES = {
    "table1": "Table 1 - Macroeconomic Summary Statistics",
    "table2": "Table 2 - Macroeconomic Statistics by Subscription Status",
    "table3": "Table 3 - Monthly Market Summary",
    "table4": "Table 4 - Correlation Matrix (Macroeconomic Variables)",
    "table5": "Table 5 - Correlation with Subscription",
    "table6": "Table 6 - Highly Correlated Variable Pairs (|r| >= 0.80)",
}

FIGURE_FILES = [
    ("figure1_macro_boxplots_by_subscription.png", "Figure 1 - Boxplots of Macroeconomic Variables by Subscription Status"),
    ("figure2_macro_trend_vs_subscription.png", "Figure 2 - Macro Trend vs Subscription (Normalized emp.var.rate / euribor3m / nr.employed)"),
    ("figure3_consumer_price_vs_subscription.png", "Figure 3 - Consumer Price Index vs Subscription Rate"),
    ("figure4_consumer_confidence_vs_subscription.png", "Figure 4 - Consumer Confidence Index vs Subscription Rate"),
    ("figure5_correlation_heatmap.png", "Figure 5 - Correlation Heatmap (Macroeconomic Variables + Subscription)"),
    ("figure6_correlation_with_subscription.png", "Figure 6 - Correlation with Subscription"),
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
    """Produce the cleaned, analysis-ready DataFrame for Module 3.

    Steps (per Module 3 Implementation Plan):
        1. Remove exact duplicate rows (all columns identical), keep first
           occurrence -> this is the "cleaned dataset".
        2. Select only the 7 required columns (5 macroeconomic variables +
           month + y).
        3. Verify data types (macro variables numeric, month categorical).
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
    print(f"[Column Selection] Selected columns: {REQUIRED_COLS}")
    print(f"[Column Selection] Resulting shape: {df.shape[0]} rows x {df.shape[1]} columns")

    # --- Step 2: verify data types ---
    print("\n[Dtype Verification]")
    dtype_rows = []
    for col in REQUIRED_COLS:
        expected_numeric = col in MACRO_COLS
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
        print(f"  - {col:<16} dtype={str(df[col].dtype):<10} expected={expected_label:<12} [{status}]")

    dtype_df = pd.DataFrame(dtype_rows)
    mismatches = dtype_df[dtype_df["status"] == "MISMATCH"]
    if not mismatches.empty:
        print(
            f"[Dtype Verification] WARNING: {len(mismatches)} column(s) do not match the "
            "expected role. No automatic type conversion is applied (per plan constraints)."
        )
    else:
        print("[Dtype Verification] All columns match their expected role. No conversion needed.")

    print(
        "\n[Scope Note] All customers contacted during the same period share identical "
        "macroeconomic conditions; these 5 variables describe the shared economic "
        "environment rather than individual customer characteristics."
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


def analysis(df: pd.DataFrame) -> dict[str, Any]:
    """Compute all descriptive statistics, group comparisons, monthly
    aggregation, and correlation analyses required by the Module 3 plan."""
    print("\n" + "=" * 78)
    print("STEP 2: Analysis")
    print("=" * 78)

    results: dict[str, Any] = {}
    n_obs = len(df)
    n_yes = int((df[TARGET_COL] == "yes").sum())
    overall_rate = n_yes / n_obs

    # ---- Table 1: Macroeconomic Summary Statistics ----
    table1 = pd.DataFrame({col: _numeric_stats(df[col]) for col in MACRO_COLS}).T
    print(f"\n[{TABLE_TITLES['table1']}]")
    print(table1.to_string())

    # ---- Table 2: Macroeconomic Statistics by Subscription Status ----
    df_yes = df.loc[df[TARGET_COL] == "yes"]
    df_no = df.loc[df[TARGET_COL] == "no"]
    table2_rows = []
    for col in MACRO_COLS:
        table2_rows.append(
            {
                "variable": col,
                "n_yes": int(df_yes[col].count()),
                "mean_yes": df_yes[col].mean(),
                "median_yes": df_yes[col].median(),
                "std_yes": df_yes[col].std(),
                "n_no": int(df_no[col].count()),
                "mean_no": df_no[col].mean(),
                "median_no": df_no[col].median(),
                "std_no": df_no[col].std(),
                "mean_diff (yes - no)": df_yes[col].mean() - df_no[col].mean(),
            }
        )
    table2 = pd.DataFrame(table2_rows)
    print(f"\n[{TABLE_TITLES['table2']}]")
    print(table2.to_string(index=False))

    # ---- Table 3: Monthly Market Summary (calendar order) ----
    month_order = [m for m in MONTH_ORDER if m in df[MONTH_COL].unique()]
    tmp = df.copy()
    tmp[MONTH_COL] = pd.Categorical(tmp[MONTH_COL], categories=month_order, ordered=True)
    agg_dict = {"count": (TARGET_COL, "size"), "yes": (TARGET_COL, lambda s: (s == "yes").sum())}
    agg_dict.update({col: (col, "mean") for col in MACRO_COLS})
    table3 = tmp.groupby(MONTH_COL, observed=False).agg(**agg_dict).reset_index()
    table3["subscription_rate"] = np.where(table3["count"] > 0, table3["yes"] / table3["count"], np.nan)
    # reorder columns: month, count, yes, subscription_rate, then macro averages
    table3 = table3[[MONTH_COL, "count", "yes", "subscription_rate"] + MACRO_COLS]
    print(f"\n[{TABLE_TITLES['table3']}]")
    print(table3.to_string(index=False))

    # ---- Table 4: Correlation Matrix (macro variables only, Pearson) ----
    table4 = df[MACRO_COLS].corr(method="pearson")
    print(f"\n[{TABLE_TITLES['table4']}]")
    print(table4.to_string())

    # ---- Table 5: Correlation with Subscription (Pearson == point-biserial for binary y) ----
    y_numeric = (df[TARGET_COL] == "yes").astype(int)
    corr_with_y = {col: df[col].corr(y_numeric) for col in MACRO_COLS}
    table5 = pd.DataFrame(
        {"variable": list(corr_with_y.keys()), "correlation_with_subscription": list(corr_with_y.values())}
    )
    table5["abs_correlation"] = table5["correlation_with_subscription"].abs()
    table5 = table5.sort_values("abs_correlation", ascending=False).reset_index(drop=True)
    table5["rank"] = table5.index + 1
    print(f"\n[{TABLE_TITLES['table5']}]")
    print(table5.to_string(index=False))
    print(
        "[Note] Correlation is computed as the Pearson correlation between each macroeconomic "
        "variable and `y` encoded as yes=1 / no=0, which is mathematically equivalent to the "
        "point-biserial correlation coefficient for a binary variable."
    )

    # ---- Table 6: Highly Correlated Variable Pairs (|r| >= 0.80) ----
    pairs = []
    for i, col_i in enumerate(MACRO_COLS):
        for col_j in MACRO_COLS[i + 1 :]:
            r = table4.loc[col_i, col_j]
            if abs(r) >= HIGH_CORR_THRESHOLD:
                pairs.append({"variable_1": col_i, "variable_2": col_j, "correlation": r})
    table6 = pd.DataFrame(pairs, columns=["variable_1", "variable_2", "correlation"])
    if not table6.empty:
        table6["abs_correlation"] = table6["correlation"].abs()
        table6 = table6.sort_values("abs_correlation", ascending=False).drop(columns="abs_correlation").reset_index(drop=True)
    print(f"\n[{TABLE_TITLES['table6']}]")
    if table6.empty:
        print("  (no variable pairs meet the |r| >= 0.80 threshold)")
    else:
        print(table6.to_string(index=False))

    # ---- Extended correlation matrix for Figure 5 (visualization only) ----
    # Combines the already-computed Table 4 (macro-macro) and Table 5
    # (macro-subscription) values into a single 6x6 matrix so the heatmap can
    # show subscription alongside the macro variables. Does NOT change the
    # values reported in Table 4 or Table 5.
    corr_with_y_by_var = table5.set_index("variable")["correlation_with_subscription"]
    heatmap_vars = MACRO_COLS + ["subscription"]
    corr_matrix_with_subscription = pd.DataFrame(index=heatmap_vars, columns=heatmap_vars, dtype=float)
    for row_var in heatmap_vars:
        for col_var in heatmap_vars:
            if row_var == col_var:
                corr_matrix_with_subscription.loc[row_var, col_var] = 1.0
            elif row_var == "subscription":
                corr_matrix_with_subscription.loc[row_var, col_var] = corr_with_y_by_var[col_var]
            elif col_var == "subscription":
                corr_matrix_with_subscription.loc[row_var, col_var] = corr_with_y_by_var[row_var]
            else:
                corr_matrix_with_subscription.loc[row_var, col_var] = table4.loc[row_var, col_var]

    results.update(
        {
            "n_obs": n_obs,
            "n_yes": n_yes,
            "overall_rate": overall_rate,
            "table1": table1,
            "table2": table2,
            "table3": table3,
            "table4": table4,
            "table5": table5,
            "table6": table6,
            "corr_matrix_with_subscription": corr_matrix_with_subscription,
        }
    )
    return results


# ---------------------------------------------------------------------------
# visualization
# ---------------------------------------------------------------------------
def visualization(results: dict[str, Any], df: pd.DataFrame) -> list[Path]:
    """Generate Figures 1-6 and save them as PNG files under FIGURES_DIR."""
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

    # ---- Figure 1: Boxplots of Macroeconomic Variables by Subscription Status ----
    fig, axes = plt.subplots(2, 3, figsize=(15, 9))
    axes = axes.flatten()
    for ax, col in zip(axes, MACRO_COLS):
        sns.boxplot(data=df, x=TARGET_COL, y=col, order=["no", "yes"], ax=ax, hue=TARGET_COL, palette="Set2", legend=False)
        ax.set_xlabel("Subscribed (y)")
        ax.set_ylabel(col)
        ax.set_title(col)
    for ax in axes[len(MACRO_COLS) :]:
        ax.axis("off")
    fig.suptitle("Figure 1: Boxplots of Macroeconomic Variables by Subscription Status")
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    _save(fig, "figure1_macro_boxplots_by_subscription")

    # ---- Figure 2: Macro Trend vs Subscription (dual y-axis) ----
    # Left axis: emp.var.rate / euribor3m / nr.employed monthly averages,
    # standardized using Table 1's overall mean/std (z-score) purely so the
    # three series - which sit on very different scales - can be compared
    # visually on one axis. Right axis: monthly subscription rate (Table 3,
    # unchanged). This chart compares trends only; it draws no causal
    # conclusion.
    t3 = results["table3"]
    table1 = results["table1"]
    trend_cols = ["emp.var.rate", "euribor3m", "nr.employed"]
    trend_colors = {"emp.var.rate": "#1f77b4", "euribor3m": "#2ca02c", "nr.employed": "#9467bd"}
    fig, ax_left = plt.subplots(figsize=(10, 5.5))
    for col in trend_cols:
        z = (t3[col] - table1.loc[col, "mean"]) / table1.loc[col, "std"]
        ax_left.plot(t3[MONTH_COL].astype(str), z, marker="o", color=trend_colors[col], label=f"{col} (normalized)")
    ax_left.set_xlabel("Month")
    ax_left.set_ylabel("Normalized value (z-score)")
    ax_left.axhline(0, color="grey", linewidth=0.8)

    ax_right = ax_left.twinx()
    ax_right.plot(
        t3[MONTH_COL].astype(str), t3["subscription_rate"], marker="s", color="black", linestyle="--",
        label="Subscription rate",
    )
    ax_right.set_ylabel("Subscription Rate")
    ax_right.grid(False)

    handles_left, labels_left = ax_left.get_legend_handles_labels()
    handles_right, labels_right = ax_right.get_legend_handles_labels()
    ax_left.legend(handles_left + handles_right, labels_left + labels_right, loc="upper right", fontsize=8)
    ax_left.set_title(
        "Figure 2: Macro Trend vs Subscription\n"
        "(left axis normalized for comparability; trend comparison only, no causal inference)"
    )
    fig.tight_layout()
    _save(fig, "figure2_macro_trend_vs_subscription")

    # ---- Figure 3: Consumer Price Index vs Subscription Rate (dual y-axis) ----
    fig, ax_left = plt.subplots(figsize=(9, 5))
    ax_left.plot(t3[MONTH_COL].astype(str), t3["cons.price.idx"], marker="o", color="#ff7f0e", label="cons.price.idx")
    ax_left.set_xlabel("Month")
    ax_left.set_ylabel("cons.price.idx (average)")

    ax_right = ax_left.twinx()
    ax_right.plot(
        t3[MONTH_COL].astype(str), t3["subscription_rate"], marker="s", color="black", linestyle="--",
        label="Subscription rate",
    )
    ax_right.set_ylabel("Subscription Rate")
    ax_right.grid(False)

    handles_left, labels_left = ax_left.get_legend_handles_labels()
    handles_right, labels_right = ax_right.get_legend_handles_labels()
    ax_left.legend(handles_left + handles_right, labels_left + labels_right, loc="upper right", fontsize=8)
    ax_left.set_title("Figure 3: Consumer Price Index vs Subscription Rate")
    fig.tight_layout()
    _save(fig, "figure3_consumer_price_vs_subscription")

    # ---- Figure 4: Consumer Confidence Index vs Subscription Rate (dual y-axis) ----
    fig, ax_left = plt.subplots(figsize=(9, 5))
    ax_left.plot(t3[MONTH_COL].astype(str), t3["cons.conf.idx"], marker="o", color="#9467bd", label="cons.conf.idx")
    ax_left.set_xlabel("Month")
    ax_left.set_ylabel("cons.conf.idx (average)")

    ax_right = ax_left.twinx()
    ax_right.plot(
        t3[MONTH_COL].astype(str), t3["subscription_rate"], marker="s", color="black", linestyle="--",
        label="Subscription rate",
    )
    ax_right.set_ylabel("Subscription Rate")
    ax_right.grid(False)

    handles_left, labels_left = ax_left.get_legend_handles_labels()
    handles_right, labels_right = ax_right.get_legend_handles_labels()
    ax_left.legend(handles_left + handles_right, labels_left + labels_right, loc="upper right", fontsize=8)
    ax_left.set_title("Figure 4: Consumer Confidence Index vs Subscription Rate")
    fig.tight_layout()
    _save(fig, "figure4_consumer_confidence_vs_subscription")

    # ---- Figure 5: Correlation Heatmap (macro variables + subscription) ----
    fig, ax = plt.subplots(figsize=(7.5, 6.5))
    sns.heatmap(
        results["corr_matrix_with_subscription"].astype(float), annot=True, fmt=".2f", cmap="coolwarm",
        vmin=-1, vmax=1, square=True, ax=ax,
    )
    ax.set_title("Figure 5: Correlation Heatmap (Macroeconomic Variables + Subscription)")
    fig.tight_layout()
    _save(fig, "figure5_correlation_heatmap")

    # ---- Figure 6: Correlation with Subscription (horizontal bar chart) ----
    t5 = results["table5"].sort_values("abs_correlation", ascending=True)
    fig, ax = plt.subplots(figsize=(8, 4.5))
    colors = ["#d62728" if v < 0 else "#1f77b4" for v in t5["correlation_with_subscription"]]
    ax.barh(t5["variable"], t5["correlation_with_subscription"], color=colors)
    for y_pos, r in enumerate(t5["correlation_with_subscription"]):
        ax.text(r + (0.01 if r >= 0 else -0.01), y_pos, f"{r:.3f}", va="center", ha="left" if r >= 0 else "right", fontsize=8)
    ax.axvline(0, color="black", linewidth=0.8)
    ax.set_xlabel("Correlation with Subscription (y = yes/no)")
    ax.set_title("Figure 6: Correlation with Subscription\n(blue = negative-to-positive as shown; red = negative correlation)")
    fig.tight_layout()
    _save(fig, "figure6_correlation_with_subscription")

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
    table1 = results["table1"]
    table2 = results["table2"]
    table3 = results["table3"]
    table4 = results["table4"]
    table5 = results["table5"]
    table6 = results["table6"]

    # ---- Observation (objective description only) ----
    observation = [
        f"Data source (raw file): `{prep_info['raw_path']}`.",
        (
            f"After removing {prep_info['n_exact_duplicates_removed']} exact duplicate rows "
            f"({prep_info['n_before_dedup']} rows before -> {prep_info['n_after_dedup']} rows after), "
            f"the cleaned dataset used for this module contains {prep_info['n_final']} observations "
            f"and the 7 columns required for market environment analysis: {REQUIRED_COLS}."
        ),
        (
            f"Overall term deposit subscription rate is {overall_rate:.4f} "
            f"({n_yes} yes out of {n_obs} observations)."
        ),
    ]
    for col in MACRO_COLS:
        observation.append(
            f"`{col}` ranges from {table1.loc[col, 'min']:.3f} to {table1.loc[col, 'max']:.3f}, "
            f"mean={table1.loc[col, 'mean']:.3f}, median={table1.loc[col, 'median']:.3f}, "
            f"std={table1.loc[col, 'std']:.3f}."
        )
    observation.append(
        f"The dataset covers {len(table3)} calendar months ({', '.join(table3[MONTH_COL].astype(str))}); "
        "`month` is used only to order observations chronologically."
    )

    # ---- Key Statistics ----
    key_statistics = [
        f"Dataset size (cleaned): {n_obs} observations; overall subscription rate: {overall_rate:.4f}.",
    ]
    for _, row in table2.iterrows():
        key_statistics.append(
            f"`{row['variable']}`: mean (yes) = {row['mean_yes']:.3f} vs mean (no) = {row['mean_no']:.3f} "
            f"(difference = {row['mean_diff (yes - no)']:.3f}); median (yes) = {row['median_yes']:.3f}, "
            f"median (no) = {row['median_no']:.3f}."
        )
    top5 = table5.iloc[0]
    bottom5 = table5.iloc[-1]
    key_statistics.append(
        f"Correlation with subscription: strongest is `{top5['variable']}` "
        f"({top5['correlation_with_subscription']:.4f}); weakest is `{bottom5['variable']}` "
        f"({bottom5['correlation_with_subscription']:.4f})."
    )
    top_volume_month = table3.sort_values("count", ascending=False).iloc[0]
    top_rate_month = table3.sort_values("subscription_rate", ascending=False).iloc[0]
    key_statistics.append(
        f"Monthly campaign volume is highest in `{top_volume_month[MONTH_COL]}` "
        f"(n={int(top_volume_month['count'])}); monthly subscription rate is highest in "
        f"`{top_rate_month[MONTH_COL]}` ({top_rate_month['subscription_rate']:.4f})."
    )
    if not table6.empty:
        pair_strs = [f"`{r['variable_1']}` & `{r['variable_2']}` (r={r['correlation']:.3f})" for _, r in table6.iterrows()]
        key_statistics.append(f"{len(table6)} variable pair(s) meet the |r| >= {HIGH_CORR_THRESHOLD} threshold: {'; '.join(pair_strs)}.")
    else:
        key_statistics.append(f"No variable pairs meet the |r| >= {HIGH_CORR_THRESHOLD} threshold.")

    # ---- Notable Patterns (descriptive; no causal language) ----
    notable_patterns = [
        (
            f"`{top5['variable']}` and `{table5.iloc[1]['variable']}` show relatively stronger (negative) "
            "correlation with subscription than the other macroeconomic variables, while "
            f"`{bottom5['variable']}` shows the weakest association in this dataset."
        ),
        (
            "Several macroeconomic variables move together and carry overlapping information: "
            + (
                "; ".join(
                    f"`{r['variable_1']}` and `{r['variable_2']}` (r={r['correlation']:.3f})"
                    for _, r in table6.iterrows()
                )
                + ". This overlap (multicollinearity) means these variables should be interpreted "
                "collectively rather than ranked independently by importance."
                if not table6.empty
                else "no pair reached the |r| >= 0.80 threshold in this dataset."
            )
        ),
        (
            f"Monthly subscription rate varies more than monthly campaign volume would alone suggest: "
            f"the highest-volume month (`{top_volume_month[MONTH_COL]}`, n={int(top_volume_month['count'])}) "
            f"is not the same as the highest-rate month (`{top_rate_month[MONTH_COL]}`, "
            f"rate={top_rate_month['subscription_rate']:.4f}). Because macroeconomic indicators also vary "
            "by month (see Table 3, Figures 2-4), month-to-month differences in subscription rate may "
            "coincide with concurrent changes in multiple macroeconomic indicators rather than reflecting "
            "an independent monthly effect."
        ),
        (
            "All customers contacted during the same period share identical macroeconomic conditions; "
            "these 5 variables describe the shared economic environment at the time of contact rather "
            "than individual customer characteristics. Observed correlations with subscription therefore "
            "reflect statistical association with the broader market context, not customer-level behavior."
        ),
        (
            "Correlation does not imply causation: the associations reported above (Table 5, Figure 6; "
            "see also Figure 5 for the extended heatmap including subscription) are statistical "
            "associations only. Changes in macroeconomic indicators should not be interpreted as direct "
            "causes of subscription behavior."
        ),
        (
            "The dataset covers a specific campaign period rather than multiple economic cycles, so the "
            "relationships observed here may not generalize to different macroeconomic environments. This "
            "module evaluates association only; it does not evaluate policy effectiveness, estimate "
            "economic impacts, or attribute subscription changes to specific indicators. Customer "
            "characteristics and campaign execution are evaluated separately in Modules 1 and 2."
        ),
    ]

    # ---- Final Business Summary ----
    # This section synthesizes existing Module 3 outputs only: Table 2
    # (Yes/No distribution comparison), Table 3 (monthly trend summary),
    # Table 4/6 (macro correlation / multicollinearity), Table 5 (correlation
    # with subscription), and Figures 1-6. No new analysis, statistics, model,
    # or causal estimate is introduced here.
    final_overall_conclusion = [
        (
            "Overall, macroeconomic conditions show an observable statistical association with term "
            f"deposit subscription; in the existing correlation analysis, `{top5['variable']}` has "
            f"the strongest association with subscription (r={top5['correlation_with_subscription']:.4f}), "
            "and the direction is negative."
        ),
        (
            "`nr.employed`, `euribor3m`, and `emp.var.rate` are the three indicators most worth "
            "monitoring; they show visible differences in the Yes/No distribution comparison and "
            "higher absolute correlations in the correlation bar chart and heatmap."
        ),
        (
            "`cons.price.idx` has a relatively weaker association with subscription, while "
            f"`cons.conf.idx` is the weakest indicator in this module "
            f"(r={bottom5['correlation_with_subscription']:.4f}); it should not be used as the main "
            "basis for judgment."
        ),
        (
            "Trend analysis shows that monthly subscription-rate changes coincide with monthly "
            "movements in multiple macroeconomic indicators; however, these trends only show that "
            "market context and subscription rates moved together, not that macroeconomic conditions "
            "directly caused subscription-rate changes."
        ),
    ]

    final_business_implications = [
        (
            "When planning telephone marketing and evaluating performance, the bank should include "
            "macroeconomic conditions as background context; subscription-rate differences across "
            "months should not be explained only by contact volume or a single campaign execution metric."
        ),
        (
            "`nr.employed`, `euribor3m`, and `emp.var.rate` can be used as reference indicators for "
            "market environment monitoring and performance interpretation, especially when comparing "
            "telephone marketing performance across different months and market states."
        ),
        (
            "When campaign performance differs noticeably across months, market environment can serve "
            "as a supporting explanatory context; when subscription-rate changes move alongside rate "
            "or employment-related indicators, managers should avoid attributing the pattern only to "
            "marketing execution."
        ),
        (
            "Macroeconomic indicators should not be used as the only decision basis; actual list "
            "selection, contact method, contact frequency, and customer characteristics should still "
            "be interpreted together with the results from Module 1 and Module 2."
        ),
    ]

    final_limitations = [
        (
            "Macro variables are highly tied to `month`: customers contacted during the same period "
            "share the same market environment, so this analysis cannot clearly separate month effects, "
            "marketing arrangement effects, and macroeconomic effects."
        ),
        (
            "This module is observational EDA only. It presents distribution differences, correlation "
            "coefficients, and trend consistency; it cannot infer that any macroeconomic indicator has "
            "a causal effect on subscription behavior."
        ),
        (
            "Several macroeconomic indicators are highly correlated with each other, especially "
            + (
                "; ".join(
                    f"`{r['variable_1']}` and `{r['variable_2']}` (r={r['correlation']:.3f})"
                    for _, r in table6.iterrows()
                )
                if not table6.empty
                else "no indicator pairs reach the high-correlation threshold in this dataset"
            )
            + "; therefore, a single indicator should not be interpreted independently as the main driver."
        ),
        (
            "The data covers a specific campaign period rather than multiple full economic cycles; "
            "therefore, the findings are suitable for interpreting market context during this dataset "
            "period and should not be directly generalized to all market environments."
        ),
    ]

    # ---- Assemble Markdown ----
    lines: list[str] = []
    lines.append("# Module 3 - Market Environment Analysis: Summary Report")
    lines.append("")
    lines.append(
        "*Business question: How are macroeconomic conditions associated with term deposit "
        "subscription, and should changes in the economic environment be considered when "
        "evaluating telephone marketing performance?*"
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
        "*Business question: Are macroeconomic conditions associated with term deposit subscription, "
        "and should the bank consider market environment when planning telephone marketing strategy?*"
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

    lines.append("## Appendix: Data Tables")
    lines.append("")

    lines.append(f"### {TABLE_TITLES['table1']}")
    lines.append("")
    lines.append("*Mean / median / standard deviation / min / max / quartiles for each macroeconomic variable, cleaned dataset (n={0}).*".format(n_obs))
    lines.append("")
    lines.append(_df_to_markdown(table1, index=True))
    lines.append("")

    lines.append(f"### {TABLE_TITLES['table2']}")
    lines.append("")
    lines.append(
        "*Mean / median / standard deviation of each macroeconomic variable, computed separately "
        "for subscribed (`y = yes`) and non-subscribed (`y = no`) customers. "
        "`mean_diff (yes - no)` = mean (yes) - mean (no).*"
    )
    lines.append("")
    lines.append(_df_to_markdown(table2))
    lines.append("")

    lines.append(f"### {TABLE_TITLES['table3']}")
    lines.append("")
    lines.append(
        "*Displayed in calendar order. `count` = campaign contacts, `yes` = subscription count, "
        "`subscription_rate` = yes / count; remaining columns are the average macroeconomic value "
        "for that month.*"
    )
    lines.append("")
    lines.append(_df_to_markdown(table3))
    lines.append("")

    lines.append(f"### {TABLE_TITLES['table4']}")
    lines.append("")
    lines.append("*Pearson correlation coefficients among the 5 macroeconomic variables.*")
    lines.append("")
    lines.append(_df_to_markdown(table4, index=True))
    lines.append("")

    lines.append(f"### {TABLE_TITLES['table5']}")
    lines.append("")
    lines.append(
        "*Pearson correlation between each macroeconomic variable and subscription status "
        "(`y` encoded as yes=1 / no=0; equivalent to point-biserial correlation). Sorted by "
        "absolute correlation, descending.*"
    )
    lines.append("")
    lines.append(_df_to_markdown(table5[["rank", "variable", "correlation_with_subscription"]]))
    lines.append("")

    lines.append(f"### {TABLE_TITLES['table6']}")
    lines.append("")
    lines.append(f"*Variable pairs with |correlation| >= {HIGH_CORR_THRESHOLD}, from Table 4, sorted by absolute correlation, descending.*")
    lines.append("")
    if table6.empty:
        lines.append(f"No variable pairs meet the |r| >= {HIGH_CORR_THRESHOLD} threshold.")
    else:
        lines.append(_df_to_markdown(table6))
    lines.append("")

    lines.append("## Figures")
    lines.append("")
    for fname, title in FIGURE_FILES:
        rel_path = f"../images/module3_market_environment_analysis/{fname}"
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
    visualization(results, df)
    report_path = generate_summary_report(results, prep_info)

    print("\n" + "=" * 78)
    print("Module 3 - Market Environment Analysis: COMPLETE")
    print("=" * 78)
    print(f"Figures saved to : {FIGURES_DIR}")
    print(f"Report saved to  : {report_path}")


if __name__ == "__main__":
    main()
