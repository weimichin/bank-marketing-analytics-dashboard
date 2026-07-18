"""EDA step 5: two-way interactions and relationships with subscription."""

from __future__ import annotations

from pathlib import Path

from eda.config import NUMERIC_COLS, TARGET_COL, MACRO_COLS
from eda.utils import (
    add_target_binary,
    ensure_cleaned,
    plot_correlation_heatmap,
    print_section,
    print_subsection,
    save_fig,
    subscription_rate,
    write_summary_report,
)

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

MODULE_PATH = Path(__file__)
SUBDIR = "interaction_analysis"


def numeric_target_correlation(df: pd.DataFrame) -> pd.Series:
    print_subsection("Numeric features vs target (point-biserial / Pearson)")
    data = add_target_binary(df)
    cols = [c for c in NUMERIC_COLS if c in data.columns]
    corr = data[cols + ["y_binary"]].corr(numeric_only=True)["y_binary"].drop("y_binary")
    corr = corr.sort_values(key=abs, ascending=False)
    print(corr.to_string())

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(x=corr.values, y=corr.index, ax=ax)
    ax.set_title("Correlation with target (y_binary)")
    ax.set_xlabel("correlation")
    save_fig(fig, "numeric_target_correlation", subdir=SUBDIR)
    return corr


def numeric_feature_correlations(df: pd.DataFrame) -> pd.DataFrame:
    print_subsection("Numeric feature correlation matrix")
    corr = df[NUMERIC_COLS].corr(numeric_only=True)
    fig = plot_correlation_heatmap(
        df,
        NUMERIC_COLS,
        title="Numeric feature correlations",
        figsize=(11, 9),
    )
    save_fig(fig, "numeric_correlation_matrix", subdir=SUBDIR)
    return corr


def categorical_pair_rates(
    df: pd.DataFrame,
    col_a: str,
    col_b: str,
    *,
    top_n: int | None = None,
) -> pd.DataFrame:
    rates = subscription_rate(df, [col_a, col_b])
    if top_n is not None:
        rates = rates.head(top_n)
    print(rates.to_string(index=False))
    return rates


def plot_two_way_heatmap(
    df: pd.DataFrame,
    row_col: str,
    col_col: str,
    *,
    name: str,
    figsize: tuple[float, float] = (10, 6),
) -> None:
    data = add_target_binary(df)
    pivot = data.pivot_table(
        index=row_col,
        columns=col_col,
        values="y_binary",
        aggfunc="mean",
        observed=False,
    )
    fig, ax = plt.subplots(figsize=figsize)
    sns.heatmap(pivot, annot=True, fmt=".2f", cmap="YlOrRd", ax=ax)
    ax.set_title(f"Subscription rate: {row_col} x {col_col}")
    save_fig(fig, name, subdir=SUBDIR)


def demographic_interactions(df: pd.DataFrame) -> pd.DataFrame:
    print_subsection("Demographic interactions")
    print("job x marital")
    job_marital = categorical_pair_rates(df, "job", "marital", top_n=20)
    plot_two_way_heatmap(df, "job", "marital", name="job_x_marital_rate", figsize=(8, 8))

    print("education x marital")
    categorical_pair_rates(df, "education", "marital")
    plot_two_way_heatmap(
        df, "education", "marital", name="education_x_marital_rate", figsize=(8, 6)
    )

    print("job x education (top combinations)")
    categorical_pair_rates(df, "job", "education", top_n=20)
    return job_marital


def financial_interactions(df: pd.DataFrame) -> pd.DataFrame:
    print_subsection("Financial interactions")
    print("housing x loan")
    housing_loan = categorical_pair_rates(df, "housing", "loan")
    plot_two_way_heatmap(df, "housing", "loan", name="housing_x_loan_rate", figsize=(6, 4))

    print("default x housing")
    categorical_pair_rates(df, "default", "housing")
    plot_two_way_heatmap(
        df, "default", "housing", name="default_x_housing_rate", figsize=(6, 4)
    )
    return housing_loan


def marketing_interactions(df: pd.DataFrame) -> pd.DataFrame:
    print_subsection("Marketing interactions")
    print("contact x poutcome")
    contact_poutcome = categorical_pair_rates(df, "contact", "poutcome")
    plot_two_way_heatmap(
        df, "contact", "poutcome", name="contact_x_poutcome_rate", figsize=(6, 4)
    )

    print("contact x month")
    categorical_pair_rates(df, "contact", "month", top_n=20)
    plot_two_way_heatmap(
        df, "contact", "month", name="contact_x_month_rate", figsize=(10, 4)
    )

    data = add_target_binary(df)
    print_subsection("duration vs campaign by target")
    sample = data.sample(n=min(4000, len(data)), random_state=42)
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.scatterplot(
        data=sample,
        x="campaign",
        y="duration",
        hue=TARGET_COL,
        alpha=0.4,
        ax=ax,
    )
    ax.set_title("duration vs campaign by target (sample)")
    save_fig(fig, "duration_vs_campaign", subdir=SUBDIR)
    return contact_poutcome


def time_macro_interactions(df: pd.DataFrame) -> pd.DataFrame:
    print_subsection("Time x Macro interactions")
    data = add_target_binary(df)
    month_macro = (
        data.groupby("month", observed=False)[MACRO_COLS + ["y_binary"]]
        .mean()
        .sort_values("y_binary", ascending=False)
    )
    print(month_macro.to_string())

    fig, ax = plt.subplots(figsize=(10, 5))
    sns.scatterplot(
        data=month_macro.reset_index(),
        x="euribor3m",
        y="y_binary",
        hue="month",
        s=100,
        ax=ax,
    )
    ax.set_title("Monthly mean euribor3m vs subscription rate")
    ax.set_ylabel("subscription rate")
    save_fig(fig, "month_euribor_vs_rate", subdir=SUBDIR)

    fig, ax = plt.subplots(figsize=(10, 5))
    sns.scatterplot(
        data=month_macro.reset_index(),
        x="nr.employed",
        y="y_binary",
        hue="month",
        s=100,
        ax=ax,
    )
    ax.set_title("Monthly mean nr.employed vs subscription rate")
    ax.set_ylabel("subscription rate")
    save_fig(fig, "month_nremployed_vs_rate", subdir=SUBDIR)
    return month_macro


def cross_group_interactions(df: pd.DataFrame) -> pd.DataFrame:
    print_subsection("Cross-group interactions")
    print("job x contact")
    categorical_pair_rates(df, "job", "contact", top_n=20)
    plot_two_way_heatmap(df, "job", "contact", name="job_x_contact_rate", figsize=(6, 8))

    print("age bins x poutcome")
    data = df.copy()
    data["age_bin"] = pd.cut(
        data["age"],
        bins=[0, 25, 35, 45, 55, 65, 100],
        labels=["<=25", "26-35", "36-45", "46-55", "56-65", "65+"],
    )
    age_poutcome = categorical_pair_rates(data, "age_bin", "poutcome")
    plot_two_way_heatmap(
        data, "age_bin", "poutcome", name="agebin_x_poutcome_rate", figsize=(6, 5)
    )
    return age_poutcome


def write_summary(
    df: pd.DataFrame,
    corr: pd.Series,
    feature_corr: pd.DataFrame,
    job_marital: pd.DataFrame,
    contact_poutcome: pd.DataFrame,
    month_macro: pd.DataFrame,
) -> Path:
    top_corr = corr.index[0]
    top_corr_val = float(corr.iloc[0])
    # strongest absolute off-diagonal feature correlation
    fc = feature_corr.copy()
    for i in range(len(fc)):
        fc.iloc[i, i] = float("nan")
    abs_fc = fc.abs()
    max_pair = abs_fc.stack().idxmax()
    max_pair_val = float(fc.loc[max_pair])

    top_job_marital = job_marital.iloc[0]
    top_contact_poutcome = contact_poutcome.sort_values(
        "subscription_rate", ascending=False
    ).iloc[0]
    top_month = month_macro.index[0]
    top_month_rate = float(month_macro.iloc[0]["y_binary"])

    observation = [
        f"Interaction analysis uses the cleaned dataset with {len(df)} rows.",
        "Analyses include numeric-target correlations, numeric feature correlations, and categorical pair subscription rates.",
        "Two-way heatmaps and scatter plots are saved under images/interaction_analysis.",
        f"Strongest absolute correlation with target among numeric features is `{top_corr}` ({top_corr_val:.4f}).",
    ]
    key_statistics = [
        "Numeric correlations with y_binary (top 5 by absolute value): "
        + ", ".join(f"{name}={val:.4f}" for name, val in corr.head(5).items())
        + ".",
        f"Strongest absolute numeric feature pair correlation: {max_pair[0]} vs {max_pair[1]} ({max_pair_val:.4f}).",
        (
            f"Highest job x marital subscription rate in top-20 table: "
            f"{top_job_marital['job']} / {top_job_marital['marital']} "
            f"(rate={top_job_marital['subscription_rate']:.4f}, n={int(top_job_marital['count'])})."
        ),
        (
            f"Highest contact x poutcome subscription rate: "
            f"{top_contact_poutcome['contact']} / {top_contact_poutcome['poutcome']} "
            f"(rate={top_contact_poutcome['subscription_rate']:.4f}, n={int(top_contact_poutcome['count'])})."
        ),
        f"Month with highest mean subscription rate: {top_month} (rate={top_month_rate:.4f}).",
    ]
    notable_patterns = [
        f"Monthly mean euribor3m for highest-rate month ({top_month}): {month_macro.loc[top_month, 'euribor3m']:.3f}.",
        f"Monthly mean nr.employed for highest-rate month ({top_month}): {month_macro.loc[top_month, 'nr.employed']:.1f}.",
        f"Lowest monthly mean subscription rate: {month_macro.index[-1]} ({month_macro.iloc[-1]['y_binary']:.4f}).",
        "Cross-group tables include job x contact and age_bin x poutcome subscription rates.",
    ]
    return write_summary_report(
        MODULE_PATH,
        "Interaction Analysis Summary Report",
        observation,
        key_statistics,
        notable_patterns,
    )


def run(df: pd.DataFrame | None = None) -> pd.DataFrame:
    """Run Interaction Analysis EDA on data after exact-duplicate removal."""
    print_section("5. Interaction Analysis")
    df = ensure_cleaned(df)

    corr = numeric_target_correlation(df)
    feature_corr = numeric_feature_correlations(df)
    job_marital = demographic_interactions(df)
    financial_interactions(df)
    contact_poutcome = marketing_interactions(df)
    month_macro = time_macro_interactions(df)
    cross_group_interactions(df)
    write_summary(df, corr, feature_corr, job_marital, contact_poutcome, month_macro)
    return df


if __name__ == "__main__":
    run()
