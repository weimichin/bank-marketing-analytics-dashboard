"""Single source of truth for dashboard navigation + scroll behavior.

Design notes (why this module exists):

- Streamlit widgets that use a ``key=`` persist their value in
  ``st.session_state`` across reruns. Once that key exists, passing
  ``index=`` / ``value=`` again on the next run is silently ignored by
  Streamlit — only a *pre-write* to ``st.session_state[key]`` (before the
  widget is instantiated) can change a keyed widget's value. The previous
  implementation tried to drive the sidebar radio from a separate
  ``nav_page`` variable, which is exactly the pattern Streamlit ignores —
  that is why some buttons appeared to "do nothing".
- All programmatic navigation (Home page buttons, and any future entry
  point) must go through the single ``goto()`` helper below so there is
  only one way to change page, instead of mixing ad-hoc
  ``st.session_state`` writes with ``st.rerun()`` in individual pages.
- Scroll position is reset only when the *top-level page* actually changes
  (Home <-> Module 1/2/3), not on every rerun (e.g. in-module tab clicks),
  so in-page interactions do not unexpectedly jerk the viewport.
- Chart-group switching within a module (Module 1/2/3's "Supporting
  Evidence" section) is owned entirely by that module's own tab bar
  (``st.tabs(..., key=evidence_tabs_key(module_key))``). There is
  deliberately no sidebar equivalent - a single control per concern avoids
  both "jumps to the wrong place" bugs and duplicate switching UI.
"""

from __future__ import annotations

import streamlit as st

from dashboard.components import HOME_NAV_ICON, MODULE2_NAV_ICON, MODULE_HIGHLIGHTS_ICON, nav_option_label

_NAV_LABELS: dict[str, str] = {
    "module3": "🌐 Module 3 — Market Environment",
}


def nav_items() -> dict[str, str]:
    """Sidebar navigation labels. Home, Module 1, and Module 2 use custom image icons."""
    return {
        "home": nav_option_label("Home", icon=HOME_NAV_ICON),
        "module1": nav_option_label("Module 1 — Who to Target", icon=MODULE_HIGHLIGHTS_ICON),
        "module2": nav_option_label("Module 2 — How to Engage", icon=MODULE2_NAV_ICON),
        **_NAV_LABELS,
    }


def _label_to_key() -> dict[str, str]:
    items = nav_items()
    return {label: key for key, label in items.items()}

_RADIO_KEY = "nav_radio"
_PENDING_KEY = "_pending_nav_target"
_LAST_PAGE_KEY = "_last_rendered_page"
_FORCE_SCROLL_KEY = "_force_scroll_reset"


def goto(page_key: str) -> None:
    """The one and only way to programmatically change page (e.g. from a button).

    Direct user clicks on the sidebar radio itself do not need this - they are
    handled natively by the widget. This is only for buttons / links elsewhere
    in the app that need to jump to a different top-level page.
    """
    items = nav_items()
    if page_key not in items:
        raise ValueError(f"Unknown page key: {page_key}")
    st.session_state[_PENDING_KEY] = page_key
    st.session_state[_FORCE_SCROLL_KEY] = True
    st.rerun()


def resolve_current_page() -> str:
    """Apply any pending programmatic navigation, then render the sidebar radio.

    Must be called once, inside the sidebar, before anything else that
    depends on "which page is active".
    """
    pending = st.session_state.pop(_PENDING_KEY, None)
    items = nav_items()
    label_to_key = _label_to_key()
    if pending is not None:
        # Pre-write the widget's own state BEFORE it is instantiated below -
        # this is the only way Streamlit allows a keyed widget's value to be
        # changed programmatically.
        st.session_state[_RADIO_KEY] = items[pending]

    selected_label = st.radio(
        "Go to",
        options=list(items.values()),
        label_visibility="collapsed",
        key=_RADIO_KEY,
    )
    return label_to_key[selected_label]


def evidence_tabs_key(module_key: str) -> str:
    """Session-state key for a module's Supporting Evidence tab bar.

    This is the single source of truth for "which chart group is active" in
    a module. Chart-group switching lives *only* in this tab bar (rendered
    at the top of each module's Supporting Evidence section) - there is no
    duplicate switching control in the sidebar, so there is exactly one way
    to change chart group per module, identical across Module 1 / 2 / 3.
    """
    return f"evidence_tabs_{module_key}"


def reset_scroll_if_page_changed(page_key: str) -> None:
    """Scroll the browser viewport back to top whenever the active page changes."""
    force_scroll = st.session_state.pop(_FORCE_SCROLL_KEY, False)
    if not force_scroll and st.session_state.get(_LAST_PAGE_KEY) == page_key:
        return
    st.session_state[_LAST_PAGE_KEY] = page_key
    st.iframe(
        f"""
        <script>
        // nav-scroll-reset: {page_key}
        (function() {{
            function scrollAppToTop() {{
                try {{
                    var doc = window.parent.document;
                    var candidates = [
                        doc.querySelector('[data-testid="stMain"]'),
                        doc.querySelector('section.main'),
                        doc.querySelector('[data-testid="stAppViewContainer"]'),
                        doc.querySelector('.main'),
                        doc.documentElement,
                        doc.body
                    ];
                    candidates.forEach(function(el) {{
                        if (el) {{
                            el.scrollTop = 0;
                            el.scrollLeft = 0;
                        }}
                    }});
                    window.parent.scrollTo({{top: 0, left: 0, behavior: 'instant'}});
                    if (window.parent.frames) {{
                        for (var i = 0; i < window.parent.frames.length; i += 1) {{
                            try {{
                                window.parent.frames[i].scrollTo(0, 0);
                            }} catch (e) {{}}
                        }}
                    }}
                }} catch (e) {{ /* no-op: best-effort scroll reset */ }}
            }}
            scrollAppToTop();
            setTimeout(scrollAppToTop, 60);
            setTimeout(scrollAppToTop, 250);
            setTimeout(scrollAppToTop, 600);
        }})();
        </script>
        """,
        height=1,
    )
