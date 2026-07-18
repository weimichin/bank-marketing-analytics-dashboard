# Project structure

```
.
├── app.py                 # Streamlit dashboard entry point
├── requirements.txt       # pip-compatible dependencies
├── pyproject.toml         # uv project metadata + lockfile companion
├── assets/                # README / portfolio screenshots
├── dashboard/             # Streamlit UI (views, theme, components, static KPIs)
│   └── assets/            # In-app icons
├── analysis/              # Reproducible EDA + Module 1–3 analysis scripts
│   ├── main.py            # Run full EDA pipeline
│   ├── eda/               # Shared EDA package
│   └── module*.py         # Business-module analyses
├── data/                  # Raw Bank Marketing CSV files
├── images/                # Generated charts used by reports + dashboard
├── reports/               # Executive / module / EDA markdown summaries
└── docs/                  # Extra documentation
```

## Quick start

```bash
uv sync
uv run streamlit run app.py
```

Re-run EDA (optional; dashboard uses precomputed results):

```bash
uv run python analysis/main.py
```
