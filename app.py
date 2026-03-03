"""
NextHire - AI-Powered Job Match Probability Platform
Entry point: orchestrates page routing and session state.
"""

import streamlit as st
from ui.styles import inject_global_styles
from ui.pages import home, results, about


def setup_page() -> None:
    st.set_page_config(
        page_title="NextHire",
        page_icon="assets/favicon.png",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    inject_global_styles()


def init_session() -> None:
    defaults = {
        "page": "home",
        "cv_text": None,
        "cv_filename": None,
        "job_results": None,
        "preferences": {},
        "search_done": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def route() -> None:
    page = st.session_state.get("page", "home")
    if page == "home":
        home.render()
    elif page == "results":
        results.render()
    elif page == "about":
        about.render()
    else:
        st.session_state.page = "home"
        home.render()


def main() -> None:
    setup_page()
    init_session()
    route()


if __name__ == "__main__":
    main()
