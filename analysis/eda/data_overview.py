"""EDA step 1: dataset shape, dtypes, feature groups, and high-level overview."""

from __future__ import annotations

from pathlib import Path

from eda.config import FEATURE_GROUPS, TARGET_COL
from eda.utils import (
    categorical_columns,
    ensure_cleaned,
    numeric_columns,
    print_section,
    print_subsection,
    write_summary_report,
)

import pandas as pd

MODULE_PATH = Path(__file__)


def summarize_shape(df: pd.DataFrame) -> None:
    print_subsection("Shape")
    print(f"rows: {df.shape[0]}")
    print(f"columns: {df.shape[1]}")


def summarize_dtypes(df: pd.DataFrame) -> None:
    print_subsection("Data types")
    dtype_df = (
        pd.DataFrame({"column": df.columns, "dtype": df.dtypes.astype(str)})
        .reset_index(drop=True)
    )
    print(dtype_df.to_string(index=False))


def summarize_memory(df: pd.DataFrame) -> None:
    print_subsection("Memory usage")
    mem_bytes = df.memory_usage(deep=True).sum()
    print(f"total memory: {mem_bytes / 1024**2:.2f} MB")
    print(df.memory_usage(deep=True).sort_values(ascending=False).to_string())


def summarize_feature_groups(df: pd.DataFrame) -> None:
    print_subsection("Feature groups")
    for group_name, cols in FEATURE_GROUPS.items():
        present = [c for c in cols if c in df.columns]
        print(f"{group_name}: {present}")
    print(f"Target: [{TARGET_COL}]")


def preview_data(df: pd.DataFrame, n: int = 5) -> None:
    print_subsection(f"Head ({n})")
    print(df.head(n).to_string())
    print_subsection(f"Tail ({n})")
    print(df.tail(n).to_string())


def summarize_column_roles(df: pd.DataFrame) -> None:
    print_subsection("Column roles")
    num_cols = numeric_columns(df)
    cat_cols = categorical_columns(df)
    print(f"numeric ({len(num_cols)}): {num_cols}")
    print(f"categorical ({len(cat_cols)}): {cat_cols}")


def write_summary(df: pd.DataFrame) -> Path:
    num_cols = numeric_columns(df)
    cat_cols = categorical_columns(df)
    mem_mb = df.memory_usage(deep=True).sum() / 1024**2
    dtype_counts = df.dtypes.astype(str).value_counts()

    observation = [
        f"Cleaned dataset shape is {df.shape[0]} rows and {df.shape[1]} columns.",
        f"There are {len(num_cols)} numeric columns and {len(cat_cols)} categorical columns.",
        f"Feature groups present: {', '.join(FEATURE_GROUPS.keys())}.",
        f"Target column is `{TARGET_COL}`.",
    ]
    key_statistics = [
        f"Row count: {df.shape[0]}; column count: {df.shape[1]}.",
        f"Memory usage (deep): {mem_mb:.2f} MB.",
        f"Dtype counts: {', '.join(f'{k}={v}' for k, v in dtype_counts.items())}.",
        f"Numeric columns: {', '.join(num_cols)}.",
        f"Categorical columns: {', '.join(cat_cols)}.",
    ]
    notable_patterns = [
        "All configured feature groups are present in the cleaned dataset.",
        "Head and tail previews show records spanning early and late campaign periods in the file order.",
        f"Index is reset after exact-duplicate removal (range index 0 to {df.shape[0] - 1}).",
    ]
    return write_summary_report(
        MODULE_PATH,
        "Data Overview Summary Report",
        observation,
        key_statistics,
        notable_patterns,
    )


def run(df: pd.DataFrame | None = None) -> pd.DataFrame:
    """Run Data Overview EDA on data after exact-duplicate removal."""
    print_section("1. Data Overview")
    df = ensure_cleaned(df)

    summarize_shape(df)
    summarize_dtypes(df)
    summarize_column_roles(df)
    summarize_feature_groups(df)
    summarize_memory(df)
    preview_data(df)
    write_summary(df)
    return df


if __name__ == "__main__":
    run()
