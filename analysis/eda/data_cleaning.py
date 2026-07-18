"""Data cleaning: remove exact duplicate rows only."""

from __future__ import annotations

import pandas as pd

from eda.utils import load_data, print_section, print_subsection


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Remove exact duplicate rows (all columns identical), keep first occurrence.

    Only technical-error cleaning is applied. No imputation, outlier handling,
    encoding, column changes, or feature engineering.
    """
    print_section("Data Cleaning: Exact Duplicate Rows")

    n_rows_before, n_cols_before = df.shape
    print_subsection("Before cleaning")
    print(f"rows: {n_rows_before}")
    print(f"columns: {n_cols_before}")

    # Rows belonging to any exact-duplicate group (including the first occurrence)
    n_duplicate_rows_incl_first = int(df.duplicated(keep=False).sum())
    # Rows that will be removed when keeping the first occurrence of each group
    n_rows_to_remove = int(df.duplicated(keep="first").sum())

    print_subsection("Exact duplicate summary")
    print(
        "exact_duplicate_rows_incl_first "
        f"(all rows in duplicate groups): {n_duplicate_rows_incl_first}"
    )
    print(
        "rows_to_remove "
        f"(after keep='first'): {n_rows_to_remove}"
    )

    cleaned = df.drop_duplicates(keep="first").reset_index(drop=True)

    n_rows_after, n_cols_after = cleaned.shape
    n_removed = n_rows_before - n_rows_after

    print_subsection("After cleaning")
    print(f"rows: {n_rows_after}")
    print(f"columns: {n_cols_after}")
    print(f"rows_removed: {n_removed}")

    return cleaned


def run(df: pd.DataFrame | None = None) -> pd.DataFrame:
    """Load data (if needed), clean exact duplicates, and return cleaned frame."""
    if df is None:
        df = load_data()
    return clean_data(df)


if __name__ == "__main__":
    run()
