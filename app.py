"""Bank Marketing Strategy Dashboard — Streamlit entry point.

Business decision-support dashboard built entirely on top of already-completed
analysis (Module 1 / 2 / 3 summary reports + Executive Summary). This app does
not run any new EDA and does not recompute or change any existing statistic;
it only reorganizes and re-presents those results for non-technical audiences.
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import streamlit as st

import plotly.io as pio

from dashboard.components import DASHBOARD_ICON, footer, sidebar_brand
from dashboard.data import home_content as hc
from dashboard.navigation import reset_scroll_if_page_changed, resolve_current_page
from dashboard.theme import inject_css
from dashboard.views import home, module1, module2, module3

# Streamlit sets pio.templates.default = "streamlit" on import, which embeds
# placeholder colors (#000001…) that the frontend replaces with theme colors.
# Override so scatter/line charts keep our explicit trace colors when theme=None.
pio.templates.default = "plotly_white"

st.set_page_config(
    page_title="Bank Marketing Strategy Dashboard",
    page_icon=str(DASHBOARD_ICON),
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()

_VIEW_MODULES = {
    "home": home,
    "module1": module1,
    "module2": module2,
    "module3": module3,
}

with st.sidebar:
    sidebar_brand("Bank Marketing", "Strategy Decision-Support Dashboard", icon=DASHBOARD_ICON)
    st.markdown("### Navigation")

    # This is the ONLY widget that controls top-level page navigation. The
    # sidebar intentionally stops here (Home / Module 1 / 2 / 3) - chart-group
    # switching within a module lives exclusively in the tabs at the top of
    # that module's "Supporting Evidence" section (identical across all three
    # modules), so there is only one control per concern instead of two
    # widgets for the same thing.
    selected_page = resolve_current_page()

# Reset scroll to top only when the active top-level page actually changed
# (not on in-page interactions like tab clicks).
reset_scroll_if_page_changed(selected_page)

importlib.reload(_VIEW_MODULES[selected_page])
_VIEW_MODULES[selected_page].render()

if selected_page != "home":
    footer(**hc.FOOTER)
