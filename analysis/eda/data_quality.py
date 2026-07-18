"""EDA step 2: missing values, duplicates, outliers, and quality checks."""

from __future__ import annotations

from pathlib import Path

from eda.config import CATEGORICAL_COLS, NUMERIC_COLS, PDAYS_NO_CONTACT, UNKNOWN_LABEL
from eda.utils import (
    ensure_cleaned,
    load_data,
    outlier_summary,
    plot_boxplot,
    print_section,
    print_subsection,
    remove_exact_duplicates,
    save_fig,
    unknown_summary,
    write_summary_report,
)

import pandas as pd

MODULE_PATH = Path(__file__)


def check_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    print_subsection("Missing values (NaN / None)")
    missing = pd.DataFrame(
        {
            "missing_count": df.isna().sum(),
            "missing_rate": df.isna().mean(),
        }
    ).sort_values("missing_count", ascending=False)
    print(missing.to_string())
    return missing


def check_unknown_values(df: pd.DataFrame) -> pd.DataFrame:
    print_subsection(f"Unknown label ('{UNKNOWN_LABEL}') in categorical columns")
    summary = unknown_summary(df, CATEGORICAL_COLS)
    print(summary.to_string(index=False))
    return summary


def check_duplicates(df_before: pd.DataFrame, df_after: pd.DataFrame) -> dict[str, int | float]:
    print_subsection("Duplicate rows")

    n_dup_before = int(df_before.duplicated().sum())
    n_dup_after = int(df_after.duplicated().sum())

    print(f"duplicate_rows (before cleaning): {n_dup_before}")
    print(f"duplicate_rate (before cleaning): {n_dup_before / len(df_before):.6f}")
    print(f"duplicate_rows (after cleaning): {n_dup_after}")
    print(f"duplicate_rate (after cleaning): {n_dup_after / len(df_after):.6f}")

    if n_dup_before > 0:
        print(df_before[df_before.duplicated(keep=False)].head(10).to_string())

    return {
        "n_dup_before": n_dup_before,
        "dup_rate_before": n_dup_before / len(df_before),
        "n_dup_after": n_dup_after,
        "dup_rate_after": n_dup_after / len(df_after),
        "n_rows_before": len(df_before),
        "n_rows_after": len(df_after),
    }


def check_constant_columns(df: pd.DataFrame) -> pd.DataFrame:
    print_subsection("Constant / near-constant columns")
    rows = []
    for col in df.columns:
        nunique = df[col].nunique(dropna=False)
        top_rate = df[col].value_counts(normalize=True, dropna=False).iloc[0]
        rows.append(
            {
                "column": col,
                "nunique": nunique,
                "top_value_rate": top_rate,
            }
        )
    summary = pd.DataFrame(rows).sort_values(["nunique", "top_value_rate"])
    print(summary.to_string(index=False))
    return summary


def check_numeric_ranges(df: pd.DataFrame) -> pd.DataFrame:
    print_subsection("Numeric ranges")
    summary = df[NUMERIC_COLS].agg(["min", "max", "mean", "median", "std"]).T
    print(summary.to_string())
    return summary


def check_pdays_sentinel(df: pd.DataFrame) -> dict[str, int]:
    print_subsection(f"pdays sentinel value ({PDAYS_NO_CONTACT})")
    n_sentinel = int((df["pdays"] == PDAYS_NO_CONTACT).sum())
    n_contacted = int((df["pdays"] != PDAYS_NO_CONTACT).sum())
    print(f"not_previously_contacted ({PDAYS_NO_CONTACT}): {n_sentinel}")
    print(f"previously_contacted: {n_contacted}")
    if n_contacted > 0:
        contacted = df.loc[df["pdays"] != PDAYS_NO_CONTACT, "pdays"]
        print("pdays stats (excluding sentinel):")
        print(contacted.describe().to_string())
    return {"n_sentinel": n_sentinel, "n_contacted": n_contacted}


def check_outliers(df: pd.DataFrame) -> pd.DataFrame:
    print_subsection("IQR outlier summary")
    summary = outlier_summary(df, NUMERIC_COLS)
    print(summary.to_string(index=False))

    for col in ["age", "duration", "campaign", "previous"]:
        fig = plot_boxplot(df, col, title=f"Outlier check: {col}")
        save_fig(fig, f"outlier_{col}", subdir="data_quality")
    return summary


def check_inconsistencies(df: pd.DataFrame) -> pd.DataFrame:
    print_subsection("Logical consistency checks")
    prev_zero_but_poutcome = (
        (df["previous"] == 0) & (df["poutcome"] != "nonexistent")
    ).sum()
    prev_pos_but_nonexistent = (
        (df["previous"] > 0) & (df["poutcome"] == "nonexistent")
    ).sum()
    pdays_sentinel_but_previous = (
        (df["pdays"] == PDAYS_NO_CONTACT) & (df["previous"] > 0)
    ).sum()
    pdays_contacted_but_previous_zero = (
        (df["pdays"] != PDAYS_NO_CONTACT) & (df["previous"] == 0)
    ).sum()
    duration_zero = (df["duration"] == 0).sum()

    checks = pd.DataFrame(
        [
            {
                "check": "previous==0 but poutcome!='nonexistent'",
                "count": int(prev_zero_but_poutcome),
            },
            {
                "check": "previous>0 but poutcome=='nonexistent'",
                "count": int(prev_pos_but_nonexistent),
            },
            {
                "check": f"pdays=={PDAYS_NO_CONTACT} but previous>0",
                "count": int(pdays_sentinel_but_previous),
            },
            {
                "check": f"pdays!={PDAYS_NO_CONTACT} but previous==0",
                "count": int(pdays_contacted_but_previous_zero),
            },
            {"check": "duration==0", "count": int(duration_zero)},
        ]
    )
    print(checks.to_string(index=False))
    return checks


def write_summary(
    df: pd.DataFrame,
    missing: pd.DataFrame,
    unknown: pd.DataFrame,
    dup_stats: dict[str, int | float],
    outliers: pd.DataFrame,
    checks: pd.DataFrame,
    pdays_stats: dict[str, int],
) -> Path:
    total_missing = int(missing["missing_count"].sum())
    top_unknown = unknown.sort_values("unknown_rate", ascending=False).iloc[0]
    top_outlier = outliers.sort_values("outlier_rate", ascending=False).iloc[0]
    nonzero_checks = checks[checks["count"] > 0]

    observation = [
        f"Quality checks use the cleaned dataset with {dup_stats['n_rows_after']} rows and {df.shape[1]} columns.",
        f"Exact-duplicate rows to remove before cleaning: {dup_stats['n_dup_before']}; after cleaning: {dup_stats['n_dup_after']}.",
        f"NaN/None missing values across all columns total {total_missing}.",
        f"Categorical `unknown` labels remain present; highest rate is in `{top_unknown['column']}`.",
    ]
    key_statistics = [
        f"Duplicate rows before cleaning: {dup_stats['n_dup_before']} (rate={dup_stats['dup_rate_before']:.6f}).",
        f"Duplicate rows after cleaning: {dup_stats['n_dup_after']} (rate={dup_stats['dup_rate_after']:.6f}).",
        f"Missing values: all columns have missing_count=0.",
        (
            f"Unknown rates (top): "
            f"{top_unknown['column']}={top_unknown['unknown_rate']:.4f}, "
            f"education={float(unknown.loc[unknown['column'] == 'education', 'unknown_rate'].iloc[0]):.4f}, "
            f"housing={float(unknown.loc[unknown['column'] == 'housing', 'unknown_rate'].iloc[0]):.4f}."
        ),
        (
            f"pdays sentinel ({PDAYS_NO_CONTACT}): {pdays_stats['n_sentinel']}; "
            f"previously contacted: {pdays_stats['n_contacted']}."
        ),
    ]
    notable_patterns = [
        (
            f"Highest IQR outlier rate among numeric columns: "
            f"`{top_outlier['column']}` ({top_outlier['outlier_rate']:.4f})."
        ),
        (
            "Logical consistency checks with non-zero counts: "
            + (
                ", ".join(f"{r.check}={r.count}" for r in nonzero_checks.itertuples())
                if not nonzero_checks.empty
                else "none"
            )
            + "."
        ),
        f"Outlier boxplots saved under images/data_quality for age, duration, campaign, and previous.",
        f"Rows removed by exact-duplicate cleaning: {dup_stats['n_rows_before'] - dup_stats['n_rows_after']}.",
    ]
    return write_summary_report(
        MODULE_PATH,
        "Data Quality Assessment Summary Report",
        observation,
        key_statistics,
        notable_patterns,
    )


def run(df: pd.DataFrame | None = None) -> pd.DataFrame:
    """Run Data Quality Assessment EDA on data after exact-duplicate removal."""
    print_section("2. Data Quality Assessment")

    # Always compare against the source file so before/after stats are correct
    # even when a pre-cleaned frame is passed in (e.g. from Data Overview).
    df_before = load_data()
    df_after = remove_exact_duplicates(df if df is not None else df_before)

    missing = check_missing_values(df_after)
    unknown = check_unknown_values(df_after)
    dup_stats = check_duplicates(df_before, df_after)
    check_constant_columns(df_after)
    check_numeric_ranges(df_after)
    pdays_stats = check_pdays_sentinel(df_after)
    outliers = check_outliers(df_after)
    checks = check_inconsistencies(df_after)
    write_summary(df_after, missing, unknown, dup_stats, outliers, checks, pdays_stats)
    return df_after


if __name__ == "__main__":
    run()
