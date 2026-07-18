"""Shared utilities for Bank Marketing EDA (load, clean, save figures/reports)."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Sequence

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from eda.config import (
    DATA_PATH,
    FIGURES_DIR,
    REPORTS_EDA_DIR,
    TARGET_COL,
    UNKNOWN_LABEL,
)

sns.set_theme(style="whitegrid", context="notebook")


def load_data(path: Path | str | None = None) -> pd.DataFrame:
    """Load the bank marketing dataset (semicolon-separated)."""
    data_path = Path(path) if path is not None else DATA_PATH
    df = pd.read_csv(data_path, sep=";")
    return df


def remove_exact_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """Drop exact duplicate rows (technical error only); keep first occurrence."""
    return df.drop_duplicates(keep="first").reset_index(drop=True)


def ensure_cleaned(df: pd.DataFrame | None = None) -> pd.DataFrame:
    """Load data if needed, then return the exact-duplicate-cleaned frame."""
    if df is None:
        df = load_data()
    return remove_exact_duplicates(df)


def write_summary_report(
    module_path: Path | str,
    title: str,
    observation: Sequence[str],
    key_statistics: Sequence[str],
    notable_patterns: Sequence[str],
) -> Path:
    """Write a unified summary report markdown file under reports/eda/."""
    module_path = Path(module_path)
    REPORTS_EDA_DIR.mkdir(parents=True, exist_ok=True)
    out_path = REPORTS_EDA_DIR / f"{module_path.stem}_summary.md"
    sections = [
        ("Observation", observation),
        ("Key Statistics", key_statistics),
        ("Notable Patterns", notable_patterns),
    ]
    lines = [f"# {title}", ""]
    for heading, items in sections:
        lines.append(f"## {heading}")
        for item in items:
            lines.append(f"- {item}")
        lines.append("")
    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"[saved] {out_path}")
    return out_path


def ensure_figures_dir(subdir: str | None = None) -> Path:
    """Create and return the figures output directory."""
    out_dir = FIGURES_DIR if subdir is None else FIGURES_DIR / subdir
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir


def print_section(title: str) -> None:
    """Print a section header to stdout."""
    line = "=" * 72
    print(f"\n{line}\n{title}\n{line}")


def print_subsection(title: str) -> None:
    """Print a subsection header to stdout."""
    print(f"\n--- {title} ---")


def save_fig(fig: plt.Figure, name: str, subdir: str | None = None) -> Path:
    """Save a matplotlib figure and close it."""
    out_dir = ensure_figures_dir(subdir)
    path = out_dir / f"{name}.png"
    fig.savefig(path, dpi=120, bbox_inches="tight")
    plt.close(fig)
    print(f"[saved] {path}")
    return path


def numeric_columns(df: pd.DataFrame) -> list[str]:
    return df.select_dtypes(include="number").columns.tolist()


def categorical_columns(df: pd.DataFrame) -> list[str]:
    return df.select_dtypes(include=["object", "category", "bool"]).columns.tolist()


def add_target_binary(df: pd.DataFrame, target_col: str = TARGET_COL) -> pd.DataFrame:
    """Return a copy with binary target column `y_binary` (1=yes, 0=no)."""
    out = df.copy()
    out["y_binary"] = (out[target_col] == "yes").astype(int)
    return out


def subscription_rate(
    df: pd.DataFrame,
    by: str | Sequence[str],
    target_col: str = TARGET_COL,
) -> pd.DataFrame:
    """Compute subscription counts and rates by one or more columns."""
    grouped = (
        df.groupby(list(by) if isinstance(by, (list, tuple)) else [by], observed=False)
        .agg(
            count=(target_col, "size"),
            yes=(target_col, lambda s: (s == "yes").sum()),
        )
        .reset_index()
    )
    grouped["no"] = grouped["count"] - grouped["yes"]
    grouped["subscription_rate"] = grouped["yes"] / grouped["count"]
    return grouped.sort_values("subscription_rate", ascending=False)


def plot_count(
    df: pd.DataFrame,
    column: str,
    *,
    hue: str | None = None,
    order: Sequence[str] | None = None,
    title: str | None = None,
    figsize: tuple[float, float] = (10, 5),
    rotate_xticks: int = 0,
) -> plt.Figure:
    """Bar count plot for a categorical column."""
    fig, ax = plt.subplots(figsize=figsize)
    sns.countplot(data=df, x=column, hue=hue, order=order, ax=ax)
    ax.set_title(title or f"Count of {column}")
    if rotate_xticks:
        ax.tick_params(axis="x", rotation=rotate_xticks)
    fig.tight_layout()
    return fig


def plot_histogram(
    df: pd.DataFrame,
    column: str,
    *,
    hue: str | None = None,
    bins: int = 30,
    title: str | None = None,
    figsize: tuple[float, float] = (10, 5),
) -> plt.Figure:
    """Histogram for a numeric column."""
    fig, ax = plt.subplots(figsize=figsize)
    sns.histplot(data=df, x=column, hue=hue, bins=bins, kde=True, ax=ax)
    ax.set_title(title or f"Distribution of {column}")
    fig.tight_layout()
    return fig


def plot_boxplot(
    df: pd.DataFrame,
    column: str,
    *,
    by: str | None = None,
    title: str | None = None,
    figsize: tuple[float, float] = (10, 5),
) -> plt.Figure:
    """Box plot for a numeric column, optionally split by a categorical column."""
    fig, ax = plt.subplots(figsize=figsize)
    if by is None:
        sns.boxplot(data=df, y=column, ax=ax)
    else:
        sns.boxplot(data=df, x=by, y=column, ax=ax)
        ax.tick_params(axis="x", rotation=30)
    ax.set_title(title or f"Box plot of {column}" + (f" by {by}" if by else ""))
    fig.tight_layout()
    return fig


def plot_rate_bar(
    rate_df: pd.DataFrame,
    category_col: str,
    *,
    rate_col: str = "subscription_rate",
    title: str | None = None,
    figsize: tuple[float, float] = (10, 5),
    rotate_xticks: int = 30,
    order: Sequence[str] | None = None,
) -> plt.Figure:
    """Bar plot of subscription rate by category."""
    plot_df = rate_df.copy()
    if order is not None:
        plot_df[category_col] = pd.Categorical(
            plot_df[category_col], categories=order, ordered=True
        )
        plot_df = plot_df.sort_values(category_col)

    fig, ax = plt.subplots(figsize=figsize)
    sns.barplot(data=plot_df, x=category_col, y=rate_col, ax=ax)
    ax.set_title(title or f"Subscription rate by {category_col}")
    ax.set_ylabel("Subscription rate")
    ax.set_ylim(0, min(1.0, plot_df[rate_col].max() * 1.2 + 0.01))
    if rotate_xticks:
        ax.tick_params(axis="x", rotation=rotate_xticks)
    fig.tight_layout()
    return fig


def plot_correlation_heatmap(
    df: pd.DataFrame,
    columns: Iterable[str] | None = None,
    *,
    title: str = "Correlation heatmap",
    figsize: tuple[float, float] = (10, 8),
) -> plt.Figure:
    """Correlation heatmap for numeric columns."""
    cols = list(columns) if columns is not None else numeric_columns(df)
    corr = df[cols].corr(numeric_only=True)
    fig, ax = plt.subplots(figsize=figsize)
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", center=0, ax=ax)
    ax.set_title(title)
    fig.tight_layout()
    return fig


def describe_numeric(df: pd.DataFrame, columns: Sequence[str] | None = None) -> pd.DataFrame:
    """Descriptive statistics for numeric columns."""
    cols = list(columns) if columns is not None else numeric_columns(df)
    return df[cols].describe().T


def value_counts_table(
    df: pd.DataFrame,
    column: str,
    *,
    normalize: bool = True,
) -> pd.DataFrame:
    """Frequency table for a categorical column."""
    counts = df[column].value_counts(dropna=False)
    table = pd.DataFrame({"count": counts})
    if normalize:
        table["proportion"] = counts / counts.sum()
    return table


def unknown_summary(
    df: pd.DataFrame,
    columns: Sequence[str] | None = None,
    unknown_label: str = UNKNOWN_LABEL,
) -> pd.DataFrame:
    """Count and proportion of 'unknown' values per column."""
    cols = list(columns) if columns is not None else categorical_columns(df)
    rows = []
    for col in cols:
        if col not in df.columns:
            continue
        n_unknown = (df[col] == unknown_label).sum()
        rows.append(
            {
                "column": col,
                "unknown_count": int(n_unknown),
                "unknown_rate": n_unknown / len(df),
            }
        )
    return pd.DataFrame(rows).sort_values("unknown_rate", ascending=False)


def outlier_summary(
    df: pd.DataFrame,
    columns: Sequence[str] | None = None,
    iqr_multiplier: float = 1.5,
) -> pd.DataFrame:
    """IQR-based outlier counts for numeric columns."""
    cols = list(columns) if columns is not None else numeric_columns(df)
    rows = []
    for col in cols:
        series = df[col]
        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1
        lower = q1 - iqr_multiplier * iqr
        upper = q3 + iqr_multiplier * iqr
        n_out = ((series < lower) | (series > upper)).sum()
        rows.append(
            {
                "column": col,
                "q1": q1,
                "q3": q3,
                "lower_bound": lower,
                "upper_bound": upper,
                "outlier_count": int(n_out),
                "outlier_rate": n_out / len(df),
            }
        )
    return pd.DataFrame(rows)


def explore_categorical_feature(
    df: pd.DataFrame,
    column: str,
    *,
    target_col: str = TARGET_COL,
    order: Sequence[str] | None = None,
    subdir: str = "feature_exploration",
    prefix: str = "",
) -> None:
    """Print tables and save count / rate plots for a categorical feature."""
    print_subsection(column)
    print(value_counts_table(df, column).to_string())
    rates = subscription_rate(df, column, target_col=target_col)
    print(rates.to_string(index=False))

    fig = plot_count(
        df,
        column,
        hue=target_col,
        order=order,
        title=f"{column} by target",
        rotate_xticks=30,
    )
    save_fig(fig, f"{prefix}{column}_count_by_target", subdir=subdir)

    fig = plot_rate_bar(
        rates,
        column,
        title=f"Subscription rate by {column}",
        order=order,
    )
    save_fig(fig, f"{prefix}{column}_subscription_rate", subdir=subdir)


def explore_numeric_feature(
    df: pd.DataFrame,
    column: str,
    *,
    target_col: str = TARGET_COL,
    bins: int = 30,
    subdir: str = "feature_exploration",
    prefix: str = "",
) -> None:
    """Print stats and save histogram / box plots for a numeric feature."""
    print_subsection(column)
    print(df[column].describe().to_string())
    print(df.groupby(target_col)[column].describe().to_string())

    fig = plot_histogram(
        df,
        column,
        hue=target_col,
        bins=bins,
        title=f"{column} distribution by target",
    )
    save_fig(fig, f"{prefix}{column}_hist_by_target", subdir=subdir)

    fig = plot_boxplot(
        df,
        column,
        by=target_col,
        title=f"{column} by target",
    )
    save_fig(fig, f"{prefix}{column}_box_by_target", subdir=subdir)
