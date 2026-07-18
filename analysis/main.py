"""Run all Bank Marketing EDA modules in order.

Entry point for the exploratory analysis pipeline. Adds this directory to
sys.path so the local `eda` package can be imported, then executes each EDA
step and writes figures under `images/` and summaries under `reports/eda/`.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Allow `import eda` when running: uv run python analysis/main.py
sys.path.insert(0, str(Path(__file__).resolve().parent))

import matplotlib

matplotlib.use("Agg")

from eda import (
    bias_limitation,
    data_overview,
    data_quality,
    feature_exploration,
    interaction_analysis,
    target_distribution,
)
from eda.utils import ensure_figures_dir, load_data, print_section


EDA_STEPS = [
    ("Data Overview", data_overview.run),
    ("Data Quality Assessment", data_quality.run),
    ("Target Distribution", target_distribution.run),
    ("Feature Exploration", feature_exploration.run),
    ("Interaction Analysis", interaction_analysis.run),
    ("Bias & Limitation Checks", bias_limitation.run),
]


def run_all() -> None:
    print_section("Bank Marketing EDA Pipeline")
    ensure_figures_dir()
    df = load_data()
    print(f"Loaded data: {df.shape[0]} rows x {df.shape[1]} columns")

    for name, step in EDA_STEPS:
        print(f"\n>>> Running: {name}")
        df = step(df)

    print_section("EDA pipeline completed")
    print("Figures saved under: images/")


if __name__ == "__main__":
    run_all()
