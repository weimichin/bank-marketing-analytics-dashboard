"""Compatibility entry point for older launch commands.

Prefer the repository root:

    uv run streamlit run app.py
"""

from __future__ import annotations

import runpy
from pathlib import Path

runpy.run_path(
    str(Path(__file__).resolve().parents[1] / "app.py"),
    run_name="__main__",
)
