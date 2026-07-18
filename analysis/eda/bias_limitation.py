"""EDA step 6: sample-size caveats, bias checks, and analysis limitations."""

from __future__ import annotations

from pathlib import Path

from eda.config import (
    CATEGORICAL_COLS,
    DEMOGRAPHIC_COLS,
    MONTH_ORDER,
    PDAYS_NO_CONTACT,
    TARGET_COL,
    UNKNOWN_LABEL,
)
from eda.utils import (
    add_target_binary,
    ensure_cleaned,
    plot_count,
    plot_histogram,
    print_section,
    print_subsection,
    save_fig,
    subscription_rate,
    unknown_summary,
    value_counts_table,
    write_summary_report,
)

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

MODULE_PATH = Path(__file__)
SUBDIR = "bias_limitation"


def check_class_imbalance_bias(df: pd.DataFrame) -> pd.DataFrame:
    print_subsection("Class imbalance")
    table = value_counts_table(df, TARGET_COL)
    print(table.to_string())
    fig = plot_count(df, TARGET_COL, title="Target imbalance", figsize=(6, 4))
    save_fig(fig, "class_imbalance", subdir=SUBDIR)
    return table


def check_duration_leakage(df: pd.DataFrame) -> dict[str, float | int]:
    print_subsection("Duration leakage risk")
    print(
        "Note from dataset docs: duration is known only after the call; "
        "duration=0 implies y='no'."
    )
    duration_zero = df[df["duration"] == 0]
    print(f"rows with duration==0: {len(duration_zero)}")
    if len(duration_zero) > 0:
        print(value_counts_table(duration_zero, TARGET_COL).to_string())

    data = add_target_binary(df)
    corr = float(data[["duration", "y_binary"]].corr().iloc[0, 1])
    print(f"corr(duration, y_binary): {corr:.4f}")

    bins = pd.qcut(df["duration"], q=10, duplicates="drop")
    rate_by_bin = (
        data.assign(duration_bin=bins)
        .groupby("duration_bin", observed=False)["y_binary"]
        .agg(["count", "mean"])
        .rename(columns={"mean": "subscription_rate"})
    )
    print(rate_by_bin.to_string())

    fig = plot_histogram(
        df,
        "duration",
        hue=TARGET_COL,
        bins=40,
        title="Duration vs target (leakage check)",
    )
    save_fig(fig, "duration_leakage", subdir=SUBDIR)
    return {
        "duration_zero_rows": len(duration_zero),
        "duration_target_corr": corr,
        "duration_bin_min_rate": float(rate_by_bin["subscription_rate"].min()),
        "duration_bin_max_rate": float(rate_by_bin["subscription_rate"].max()),
    }


def check_unknown_bias(df: pd.DataFrame) -> pd.DataFrame:
    print_subsection("Unknown-value representation bias")
    summary = unknown_summary(df, CATEGORICAL_COLS)
    print(summary.to_string(index=False))

    for col in ["job", "marital", "education", "default", "housing", "loan"]:
        rates = subscription_rate(df, col)
        unknown_row = rates[rates[col] == UNKNOWN_LABEL]
        known_rate = rates.loc[rates[col] != UNKNOWN_LABEL, "subscription_rate"]
        print(f"\n{col}:")
        print(rates.to_string(index=False))
        if not unknown_row.empty and len(known_rate) > 0:
            print(
                f"unknown_rate={unknown_row['subscription_rate'].iloc[0]:.4f}, "
                f"known_mean_rate={known_rate.mean():.4f}"
            )
    return summary


def check_demographic_representation(df: pd.DataFrame) -> None:
    print_subsection("Demographic representation")
    for col in ["job", "marital", "education"]:
        table = value_counts_table(df, col)
        print(f"\n{col}")
        print(table.to_string())
        fig = plot_count(
            df,
            col,
            title=f"Representation: {col}",
            rotate_xticks=30,
            figsize=(10, 4),
        )
        save_fig(fig, f"representation_{col}", subdir=SUBDIR)

    print_subsection("Age representation")
    print(df["age"].describe().to_string())
    fig = plot_histogram(df, "age", bins=30, title="Age representation")
    save_fig(fig, "representation_age", subdir=SUBDIR)


def check_temporal_coverage(df: pd.DataFrame) -> pd.DataFrame:
    print_subsection("Temporal coverage / seasonality concentration")
    month_order = [m for m in MONTH_ORDER if m in df["month"].unique()]
    month_table = value_counts_table(df, "month").reindex(month_order)
    print(month_table.to_string())

    rates = subscription_rate(df, "month")
    rates["month"] = pd.Categorical(rates["month"], categories=month_order, ordered=True)
    rates = rates.sort_values("month")
    print(rates.to_string(index=False))

    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    sns.countplot(data=df, x="month", order=month_order, ax=axes[0])
    axes[0].set_title("Contact volume by month")
    sns.barplot(data=rates, x="month", y="subscription_rate", order=month_order, ax=axes[1])
    axes[1].set_title("Subscription rate by month")
    fig.tight_layout()
    save_fig(fig, "temporal_coverage", subdir=SUBDIR)
    return month_table


def check_previous_campaign_bias(df: pd.DataFrame) -> dict[str, float]:
    print_subsection("Previous-campaign / pdays encoding limitations")
    sentinel_rate = float((df["pdays"] == PDAYS_NO_CONTACT).mean())
    print(f"pdays sentinel ({PDAYS_NO_CONTACT}) rate: {sentinel_rate:.4f}")
    print(value_counts_table(df, "poutcome").to_string())

    rates = subscription_rate(df, "poutcome")
    print(rates.to_string(index=False))

    contacted = df[df["pdays"] != PDAYS_NO_CONTACT]
    contacted_share = len(contacted) / len(df)
    print(f"previously contacted share: {contacted_share:.4f}")
    if len(contacted) > 0:
        print(value_counts_table(contacted, TARGET_COL).to_string())
    return {
        "pdays_sentinel_rate": sentinel_rate,
        "previously_contacted_share": contacted_share,
    }


def check_contact_channel_bias(df: pd.DataFrame) -> pd.DataFrame:
    print_subsection("Contact channel coverage")
    table = value_counts_table(df, "contact")
    print(table.to_string())
    print(subscription_rate(df, "contact").to_string(index=False))

    print("\ncontact x month volume")
    ct = pd.crosstab(df["month"], df["contact"], normalize="index")
    month_order = [m for m in MONTH_ORDER if m in df["month"].unique()]
    ct = ct.reindex(month_order)
    print(ct.to_string())

    fig, ax = plt.subplots(figsize=(10, 4))
    ct.plot(kind="bar", stacked=True, ax=ax)
    ax.set_title("Contact channel mix by month")
    ax.set_ylabel("proportion")
    ax.tick_params(axis="x", rotation=0)
    fig.tight_layout()
    save_fig(fig, "contact_channel_mix", subdir=SUBDIR)
    return table


def check_macro_granularity_limitation(df: pd.DataFrame) -> dict[str, float | int]:
    print_subsection("Macro feature granularity limitation")
    macro_cols = [
        "emp.var.rate",
        "cons.price.idx",
        "cons.conf.idx",
        "euribor3m",
        "nr.employed",
    ]
    for col in macro_cols:
        nunique = df[col].nunique()
        print(f"{col}: nunique={nunique}")

    # Macro values are shared across many clients (national indicators)
    combo_nunique = df[macro_cols].drop_duplicates().shape[0]
    rows_per_combo = len(df) / combo_nunique
    print(f"unique macro-context combinations: {combo_nunique}")
    print(f"rows per unique macro combo (mean): {rows_per_combo:.1f}")
    return {
        "macro_combo_nunique": combo_nunique,
        "rows_per_macro_combo": rows_per_combo,
    }


def check_selection_limitation(df: pd.DataFrame) -> dict[str, int]:
    print_subsection("Selection / population limitation")
    print(
        "Dataset contains clients contacted by a bank telemarketing campaign; "
        "it is not a random sample of the general population."
    )
    n_yes = int((df[TARGET_COL] == "yes").sum())
    print(f"total contacted clients (rows): {len(df)}")
    print(f"positive outcomes (y=yes): {n_yes}")
    print(f"campaign contacts per client (campaign) describe:")
    print(df["campaign"].describe().to_string())
    return {"n_rows": len(df), "n_yes": n_yes}


def check_rare_category_instability(df: pd.DataFrame) -> list[str]:
    print_subsection("Rare category instability")
    rare_items: list[str] = []
    for col in DEMOGRAPHIC_COLS:
        if col == "age":
            continue
        rates = subscription_rate(df, col)
        rare = rates[rates["count"] < 100]
        print(f"\n{col}: categories with count < 100")
        if rare.empty:
            print("(none)")
        else:
            print(rare.to_string(index=False))
            for row in rare.itertuples():
                rare_items.append(
                    f"{col}={getattr(row, col)} (n={int(row.count)}, "
                    f"rate={row.subscription_rate:.4f})"
                )
    return rare_items


def write_summary(
    df: pd.DataFrame,
    target_table: pd.DataFrame,
    duration_stats: dict[str, float | int],
    unknown: pd.DataFrame,
    month_table: pd.DataFrame,
    prev_stats: dict[str, float],
    contact_table: pd.DataFrame,
    macro_stats: dict[str, float | int],
    selection_stats: dict[str, int],
    rare_items: list[str],
) -> Path:
    yes_prop = float(target_table.loc["yes", "proportion"])
    no_prop = float(target_table.loc["no", "proportion"])
    top_unknown = unknown.sort_values("unknown_rate", ascending=False).iloc[0]
    top_month = month_table["count"].idxmax()
    top_month_share = float(month_table.loc[top_month, "proportion"])
    top_contact = contact_table["count"].idxmax()
    top_contact_share = float(contact_table.loc[top_contact, "proportion"])

    observation = [
        f"Bias and limitation checks use the cleaned dataset with {selection_stats['n_rows']} rows.",
        f"Target class proportions: no={no_prop:.4f}, yes={yes_prop:.4f}.",
        f"Duration has correlation {duration_stats['duration_target_corr']:.4f} with y_binary; duration==0 rows: {duration_stats['duration_zero_rows']}.",
        "Dataset documentation notes duration is known only after the call.",
    ]
    key_statistics = [
        f"Unknown label highest rate: {top_unknown['column']}={top_unknown['unknown_rate']:.4f} (count={int(top_unknown['unknown_count'])}).",
        f"pdays sentinel rate: {prev_stats['pdays_sentinel_rate']:.4f}; previously contacted share: {prev_stats['previously_contacted_share']:.4f}.",
        f"Highest-volume month: {top_month} (share={top_month_share:.4f}).",
        f"Dominant contact channel: {top_contact} (share={top_contact_share:.4f}).",
        (
            f"Macro unique combinations: {macro_stats['macro_combo_nunique']}; "
            f"mean rows per combination: {macro_stats['rows_per_macro_combo']:.1f}."
        ),
    ]
    notable_patterns = [
        (
            f"Duration decile subscription rates range from "
            f"{duration_stats['duration_bin_min_rate']:.4f} to "
            f"{duration_stats['duration_bin_max_rate']:.4f}."
        ),
        f"Positive outcomes (y=yes): {selection_stats['n_yes']} of {selection_stats['n_rows']}.",
        (
            "Demographic categories with count < 100: "
            + (", ".join(rare_items) if rare_items else "none")
            + "."
        ),
        "Figures are saved under images/bias_limitation.",
    ]
    return write_summary_report(
        MODULE_PATH,
        "Bias & Limitation Checks Summary Report",
        observation,
        key_statistics,
        notable_patterns,
    )


def run(df: pd.DataFrame | None = None) -> pd.DataFrame:
    """Run Bias & Limitation Checks EDA on data after exact-duplicate removal."""
    print_section("6. Bias & Limitation Checks")
    df = ensure_cleaned(df)

    target_table = check_class_imbalance_bias(df)
    duration_stats = check_duration_leakage(df)
    unknown = check_unknown_bias(df)
    check_demographic_representation(df)
    month_table = check_temporal_coverage(df)
    prev_stats = check_previous_campaign_bias(df)
    contact_table = check_contact_channel_bias(df)
    macro_stats = check_macro_granularity_limitation(df)
    selection_stats = check_selection_limitation(df)
    rare_items = check_rare_category_instability(df)
    write_summary(
        df,
        target_table,
        duration_stats,
        unknown,
        month_table,
        prev_stats,
        contact_table,
        macro_stats,
        selection_stats,
        rare_items,
    )
    return df


if __name__ == "__main__":
    run()
