"""EDA step 4: univariate exploration across demographic, financial, and campaign features."""

from __future__ import annotations

from pathlib import Path

from eda.config import (
    DAY_ORDER,
    DEMOGRAPHIC_COLS,
    EDUCATION_ORDER,
    FINANCIAL_COLS,
    MACRO_COLS,
    MARKETING_COLS,
    MONTH_ORDER,
    PDAYS_NO_CONTACT,
    TARGET_COL,
    TIME_COLS,
)
from eda.utils import (
    describe_numeric,
    ensure_cleaned,
    explore_categorical_feature,
    explore_numeric_feature,
    plot_correlation_heatmap,
    plot_histogram,
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
SUBDIR = "feature_exploration"


def explore_demographics(df: pd.DataFrame) -> None:
    """(1) Demographics: age, job, marital, education."""
    print_subsection("4.(1) Demographics")
    print(f"columns: {DEMOGRAPHIC_COLS}")

    explore_numeric_feature(df, "age", subdir=SUBDIR, prefix="demo_")

    explore_categorical_feature(
        df, "job", order=sorted(df["job"].unique()), subdir=SUBDIR, prefix="demo_"
    )
    explore_categorical_feature(
        df,
        "marital",
        order=sorted(df["marital"].unique()),
        subdir=SUBDIR,
        prefix="demo_",
    )
    explore_categorical_feature(
        df,
        "education",
        order=[e for e in EDUCATION_ORDER if e in df["education"].unique()],
        subdir=SUBDIR,
        prefix="demo_",
    )

    print_subsection("age by job")
    print(df.groupby("job")["age"].describe().to_string())
    fig, ax = plt.subplots(figsize=(12, 5))
    sns.boxplot(data=df, x="job", y="age", ax=ax)
    ax.tick_params(axis="x", rotation=30)
    ax.set_title("Age by job")
    save_fig(fig, "demo_age_by_job", subdir=SUBDIR)


def explore_financial(df: pd.DataFrame) -> None:
    """(2) Financial Features: default, housing, loan."""
    print_subsection("4.(2) Financial Features")
    print(f"columns: {FINANCIAL_COLS}")

    for col in FINANCIAL_COLS:
        explore_categorical_feature(df, col, subdir=SUBDIR, prefix="fin_")

    print_subsection("Financial feature combinations")
    combo = (
        df.groupby(FINANCIAL_COLS, observed=False)[TARGET_COL]
        .value_counts()
        .unstack(fill_value=0)
    )
    combo["total"] = combo.sum(axis=1)
    if "yes" in combo.columns:
        combo["subscription_rate"] = combo["yes"] / combo["total"]
    print(combo.sort_values("total", ascending=False).to_string())

    fig, axes = plt.subplots(1, 3, figsize=(14, 4))
    for ax, col in zip(axes, FINANCIAL_COLS):
        sns.countplot(data=df, x=col, hue=TARGET_COL, ax=ax)
        ax.set_title(col)
    fig.suptitle("Financial features by target")
    fig.tight_layout()
    save_fig(fig, "fin_features_overview", subdir=SUBDIR)


def explore_marketing(df: pd.DataFrame) -> None:
    """(3) Marketing Behavior: contact, duration, campaign, pdays, previous, poutcome."""
    print_subsection("4.(3) Marketing Behavior")
    print(f"columns: {MARKETING_COLS}")

    explore_categorical_feature(df, "contact", subdir=SUBDIR, prefix="mkt_")
    explore_categorical_feature(df, "poutcome", subdir=SUBDIR, prefix="mkt_")

    for col in ["duration", "campaign", "previous"]:
        explore_numeric_feature(df, col, subdir=SUBDIR, prefix="mkt_")

    print_subsection("pdays (with / without sentinel)")
    print(df["pdays"].describe().to_string())
    contacted = df[df["pdays"] != PDAYS_NO_CONTACT]
    print(f"previously contacted rows: {len(contacted)}")
    if len(contacted) > 0:
        print(contacted["pdays"].describe().to_string())
        fig = plot_histogram(
            contacted,
            "pdays",
            hue=TARGET_COL,
            bins=30,
            title="pdays (excluding 999) by target",
        )
        save_fig(fig, "mkt_pdays_contacted_hist", subdir=SUBDIR)

    df_flag = df.copy()
    df_flag["previously_contacted"] = (df_flag["pdays"] != PDAYS_NO_CONTACT).map(
        {True: "yes", False: "no"}
    )
    explore_categorical_feature(
        df_flag,
        "previously_contacted",
        subdir=SUBDIR,
        prefix="mkt_",
    )

    print_subsection("campaign vs previous")
    print(describe_numeric(df, ["campaign", "previous", "duration"]).to_string())


def explore_time(df: pd.DataFrame) -> None:
    """(4) Time Analysis: month, day_of_week."""
    print_subsection("4.(4) Time Analysis")
    print(f"columns: {TIME_COLS}")

    month_order = [m for m in MONTH_ORDER if m in df["month"].unique()]
    day_order = [d for d in DAY_ORDER if d in df["day_of_week"].unique()]

    explore_categorical_feature(
        df, "month", order=month_order, subdir=SUBDIR, prefix="time_"
    )
    explore_categorical_feature(
        df, "day_of_week", order=day_order, subdir=SUBDIR, prefix="time_"
    )

    print_subsection("month x day_of_week subscription rate")
    pivot = (
        df.assign(y_binary=(df[TARGET_COL] == "yes").astype(int))
        .pivot_table(
            index="month",
            columns="day_of_week",
            values="y_binary",
            aggfunc="mean",
            observed=False,
        )
        .reindex(index=month_order, columns=day_order)
    )
    print(pivot.to_string())

    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(pivot, annot=True, fmt=".2f", cmap="YlGnBu", ax=ax)
    ax.set_title("Subscription rate: month x day_of_week")
    save_fig(fig, "time_month_day_heatmap", subdir=SUBDIR)

    month_counts = (
        df["month"]
        .value_counts()
        .reindex(month_order)
        .rename_axis("month")
        .reset_index(name="count")
    )
    fig, ax = plt.subplots(figsize=(10, 4))
    sns.barplot(data=month_counts, x="month", y="count", ax=ax, order=month_order)
    ax.set_title("Contact volume by month")
    save_fig(fig, "time_month_volume", subdir=SUBDIR)


def explore_macro(df: pd.DataFrame) -> None:
    """(5) Macroeconomic Context."""
    print_subsection("4.(5) Macroeconomic Context")
    print(f"columns: {MACRO_COLS}")
    print(describe_numeric(df, MACRO_COLS).to_string())

    for col in MACRO_COLS:
        explore_numeric_feature(df, col, bins=20, subdir=SUBDIR, prefix="macro_")

    fig = plot_correlation_heatmap(
        df,
        MACRO_COLS,
        title="Macroeconomic features correlation",
        figsize=(8, 6),
    )
    save_fig(fig, "macro_correlation", subdir=SUBDIR)

    print_subsection("Macro indicators by target")
    print(df.groupby(TARGET_COL)[MACRO_COLS].mean().to_string())

    # Pairwise relationships among macro features (sample for speed)
    sample = df[MACRO_COLS + [TARGET_COL]].sample(
        n=min(3000, len(df)), random_state=42
    )
    g = sns.pairplot(sample, hue=TARGET_COL, corner=True, plot_kws={"alpha": 0.4, "s": 12})
    g.figure.suptitle("Macro features pairplot (sample)", y=1.02)
    save_fig(g.figure, "macro_pairplot", subdir=SUBDIR)


def write_summary(df: pd.DataFrame) -> Path:
    age_mean = df["age"].mean()
    age_median = df["age"].median()
    top_job = df["job"].value_counts().index[0]
    top_job_share = df["job"].value_counts(normalize=True).iloc[0]
    job_rates = subscription_rate(df, "job")
    job_rate_max = job_rates.iloc[0]
    job_rate_min = job_rates.iloc[-1]
    poutcome_rates = subscription_rate(df, "poutcome")
    contact_rates = subscription_rate(df, "contact")
    month_counts = df["month"].value_counts()
    month_rates = subscription_rate(df, "month")
    prev_contacted = (df["pdays"] != PDAYS_NO_CONTACT).mean()
    macro_by_y = df.groupby(TARGET_COL)[MACRO_COLS].mean()

    observation = [
        f"Feature exploration uses the cleaned dataset with {len(df)} rows.",
        f"Explored groups: Demographics, Financial Features, Marketing Behavior, Time Analysis, Macroeconomic Context.",
        f"Age mean is {age_mean:.2f} and median is {age_median:.1f}.",
        f"Most frequent job category is `{top_job}` ({top_job_share:.2%} of rows).",
    ]
    key_statistics = [
        f"Job subscription rate range: {job_rate_min['job']}={job_rate_min['subscription_rate']:.4f} to {job_rate_max['job']}={job_rate_max['subscription_rate']:.4f}.",
        f"poutcome rates: "
        + ", ".join(
            f"{r.poutcome}={r.subscription_rate:.4f} (n={r.count})"
            for r in poutcome_rates.itertuples()
        )
        + ".",
        f"contact rates: "
        + ", ".join(
            f"{r.contact}={r.subscription_rate:.4f} (n={r.count})"
            for r in contact_rates.itertuples()
        )
        + ".",
        f"Highest-volume month: {month_counts.index[0]} (n={month_counts.iloc[0]}); "
        f"highest subscription-rate month: {month_rates.iloc[0]['month']} "
        f"(rate={month_rates.iloc[0]['subscription_rate']:.4f}).",
        f"Previously contacted share (pdays != {PDAYS_NO_CONTACT}): {prev_contacted:.4f}.",
    ]
    notable_patterns = [
        f"Duration mean by target: "
        f"no={df.loc[df[TARGET_COL] == 'no', 'duration'].mean():.1f}, "
        f"yes={df.loc[df[TARGET_COL] == 'yes', 'duration'].mean():.1f}.",
        f"Mean euribor3m by target: "
        f"no={macro_by_y.loc['no', 'euribor3m']:.3f}, "
        f"yes={macro_by_y.loc['yes', 'euribor3m']:.3f}.",
        f"Mean nr.employed by target: "
        f"no={macro_by_y.loc['no', 'nr.employed']:.1f}, "
        f"yes={macro_by_y.loc['yes', 'nr.employed']:.1f}.",
        "Figures are saved under images/feature_exploration for all five feature groups.",
    ]
    return write_summary_report(
        MODULE_PATH,
        "Feature Exploration Summary Report",
        observation,
        key_statistics,
        notable_patterns,
    )


def run(df: pd.DataFrame | None = None) -> pd.DataFrame:
    """Run Feature Exploration EDA on data after exact-duplicate removal."""
    print_section("4. Feature Exploration")
    df = ensure_cleaned(df)

    explore_demographics(df)
    explore_financial(df)
    explore_marketing(df)
    explore_time(df)
    explore_macro(df)
    write_summary(df)
    return df


if __name__ == "__main__":
    run()
