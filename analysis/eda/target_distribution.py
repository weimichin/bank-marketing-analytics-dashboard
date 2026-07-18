"""EDA step 3: subscription target (y) class balance and distribution charts."""

from __future__ import annotations

from pathlib import Path

from eda.config import TARGET_COL
from eda.utils import (
    ensure_cleaned,
    plot_count,
    print_section,
    print_subsection,
    save_fig,
    value_counts_table,
    write_summary_report,
)

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

MODULE_PATH = Path(__file__)


def summarize_target(df: pd.DataFrame, target_col: str = TARGET_COL) -> pd.DataFrame:
    print_subsection("Target value counts")
    table = value_counts_table(df, target_col)
    print(table.to_string())
    return table


def plot_target_distribution(
    df: pd.DataFrame,
    target_col: str = TARGET_COL,
) -> None:
    print_subsection("Target distribution plots")
    fig = plot_count(df, target_col, title="Target class counts", figsize=(6, 4))
    save_fig(fig, "target_count", subdir="target_distribution")

    counts = df[target_col].value_counts()
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(
        counts.values,
        labels=counts.index,
        autopct="%1.1f%%",
        startangle=90,
        colors=sns.color_palette("pastel"),
    )
    ax.set_title("Target class proportion")
    save_fig(fig, "target_pie", subdir="target_distribution")


def summarize_imbalance(df: pd.DataFrame, target_col: str = TARGET_COL) -> dict[str, float | int | str]:
    print_subsection("Class imbalance metrics")
    counts = df[target_col].value_counts()
    majority = int(counts.max())
    minority = int(counts.min())
    ratio = majority / minority if minority > 0 else float("inf")
    metrics = {
        "majority_class": str(counts.idxmax()),
        "majority_count": majority,
        "minority_class": str(counts.idxmin()),
        "minority_count": minority,
        "imbalance_ratio": ratio,
        "minority_rate": minority / len(df),
    }
    print(f"majority_class: {metrics['majority_class']} ({majority})")
    print(f"minority_class: {metrics['minority_class']} ({minority})")
    print(f"imbalance_ratio (majority/minority): {ratio:.3f}")
    print(f"minority_rate: {metrics['minority_rate']:.4f}")
    return metrics


def write_summary(df: pd.DataFrame, table: pd.DataFrame, metrics: dict) -> Path:
    yes_count = int(table.loc["yes", "count"]) if "yes" in table.index else 0
    no_count = int(table.loc["no", "count"]) if "no" in table.index else 0
    yes_prop = float(table.loc["yes", "proportion"]) if "yes" in table.index else 0.0
    no_prop = float(table.loc["no", "proportion"]) if "no" in table.index else 0.0

    observation = [
        f"Target analysis uses the cleaned dataset with {len(df)} rows.",
        f"Target column `{TARGET_COL}` has two classes: yes and no.",
        f"Class `no` accounts for {no_count} rows; class `yes` accounts for {yes_count} rows.",
        "Count and pie charts are saved under images/target_distribution.",
    ]
    key_statistics = [
        f"y=no: count={no_count}, proportion={no_prop:.4f}.",
        f"y=yes: count={yes_count}, proportion={yes_prop:.4f}.",
        f"Majority class: {metrics['majority_class']} ({metrics['majority_count']}).",
        f"Minority class: {metrics['minority_class']} ({metrics['minority_count']}).",
        f"Imbalance ratio (majority/minority): {metrics['imbalance_ratio']:.3f}; minority rate: {metrics['minority_rate']:.4f}.",
    ]
    notable_patterns = [
        f"The majority class is `{metrics['majority_class']}` and the minority class is `{metrics['minority_class']}`.",
        f"Minority class share is {metrics['minority_rate']:.2%} of all cleaned rows.",
        f"Majority class is approximately {metrics['imbalance_ratio']:.2f} times the minority class count.",
    ]
    return write_summary_report(
        MODULE_PATH,
        "Target Distribution Summary Report",
        observation,
        key_statistics,
        notable_patterns,
    )


def run(df: pd.DataFrame | None = None) -> pd.DataFrame:
    """Run Target Distribution EDA on data after exact-duplicate removal."""
    print_section("3. Target Distribution")
    df = ensure_cleaned(df)

    table = summarize_target(df)
    metrics = summarize_imbalance(df)
    plot_target_distribution(df)
    write_summary(df, table, metrics)
    return df


if __name__ == "__main__":
    run()
