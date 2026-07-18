"""Shared configuration for Bank Marketing EDA (paths and column groups)."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

# analysis/eda/config.py -> project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "bank-additional" / "bank-additional-full.csv"
NAMES_PATH = PROJECT_ROOT / "data" / "bank-additional" / "bank-additional-names.txt"
FIGURES_DIR = PROJECT_ROOT / "images"
REPORTS_EDA_DIR = PROJECT_ROOT / "reports" / "eda"

TARGET_COL = "y"
UNKNOWN_LABEL = "unknown"
PDAYS_NO_CONTACT = 999

DEMOGRAPHIC_COLS = ["age", "job", "marital", "education"]
FINANCIAL_COLS = ["default", "housing", "loan"]
MARKETING_COLS = [
    "contact",
    "duration",
    "campaign",
    "pdays",
    "previous",
    "poutcome",
]
TIME_COLS = ["month", "day_of_week"]
MACRO_COLS = [
    "emp.var.rate",
    "cons.price.idx",
    "cons.conf.idx",
    "euribor3m",
    "nr.employed",
]

NUMERIC_COLS = [
    "age",
    "duration",
    "campaign",
    "pdays",
    "previous",
    "emp.var.rate",
    "cons.price.idx",
    "cons.conf.idx",
    "euribor3m",
    "nr.employed",
]

CATEGORICAL_COLS = [
    "job",
    "marital",
    "education",
    "default",
    "housing",
    "loan",
    "contact",
    "month",
    "day_of_week",
    "poutcome",
]

MONTH_ORDER = [
    "jan",
    "feb",
    "mar",
    "apr",
    "may",
    "jun",
    "jul",
    "aug",
    "sep",
    "oct",
    "nov",
    "dec",
]
DAY_ORDER = ["mon", "tue", "wed", "thu", "fri"]
EDUCATION_ORDER = [
    "illiterate",
    "basic.4y",
    "basic.6y",
    "basic.9y",
    "high.school",
    "professional.course",
    "university.degree",
    "unknown",
]

FEATURE_GROUPS = {
    "Demographics": DEMOGRAPHIC_COLS,
    "Financial Features": FINANCIAL_COLS,
    "Marketing Behavior": MARKETING_COLS,
    "Time Analysis": TIME_COLS,
    "Macroeconomic Context": MACRO_COLS,
}
