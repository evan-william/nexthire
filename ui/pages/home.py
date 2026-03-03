"""
Home page: CV upload, career preferences, and search trigger.
"""

import streamlit as st

from config.settings import CONTRACT_TYPES, WORK_MODES, config
from core.cv_parser import parse_cv
from ui.components import render_navbar, section_header


def render() -> None:
    render_navbar("home")

    # Hero section
    st.markdown(
        """
        <div style="text-align:center; padding:2rem 0 3rem;">
            <div style="
                font-family:'DM Mono',monospace; font-size:0.72rem;
                color:#6c63ff; text-transform:uppercase; letter-spacing:0.18em;
                margin-bottom:1rem;
            ">Predictive Career Analytics</div>
            <h1 style="
                font-family:'Syne',sans-serif; font-weight:800;
                font-size:clamp(2.2rem, 5vw, 3.4rem);
                color:#eeeef5; line-height:1.1; margin:0 0 1rem;
                letter-spacing:-0.03em;
            ">Find Jobs You'll<br><span style='color:#6c63ff;'>Actually Get</span></h1>
            <p style="
                color:#8888aa; font-size:1rem; max-width:520px;
                margin:0 auto; line-height:1.7;
            ">
                Upload your CV and let our probability engine score every listing
                against your profile — weighted by company competitiveness and role fit.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Upload + Preferences ──────────────────────────────────────────────────
    col_upload, col_spacer, col_prefs = st.columns([5, 1, 5])

    with col_upload:
        section_header("Upload CV", "PDF or DOCX · max 5 MB")
        uploaded = st.file_uploader(
            label="Drop your CV here",
            type=["pdf", "docx"],
            label_visibility="collapsed",
            key="cv_upload",
        )

        if uploaded:
            file_bytes = uploaded.read()
            try:
                cv_text = parse_cv(file_bytes, uploaded.name)
                st.session_state.cv_text = cv_text
                st.session_state.cv_filename = uploaded.name
                word_count = len(cv_text.split())
                st.markdown(
                    f"""
                    <div style="
                        margin-top:0.75rem; padding:0.75rem 1rem;
                        background:rgba(34,211,160,0.08);
                        border:1px solid rgba(34,211,160,0.25);
                        border-radius:8px; font-size:0.82rem;
                        font-family:'DM Mono',monospace; color:#22d3a0;
                    ">
                        ✓ Parsed &nbsp;·&nbsp; {uploaded.name} &nbsp;·&nbsp; ~{word_count} words
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            except (ValueError, RuntimeError) as exc:
                st.error(str(exc))
                st.session_state.cv_text = None

    with col_prefs:
        section_header("Search Preferences")

        keywords = st.text_input(
            "Job title or keywords",
            placeholder="e.g. Data Scientist, Backend Engineer",
            key="pref_keywords",
        )
        location = st.text_input(
            "Location",
            placeholder="e.g. London, Remote, New York",
            key="pref_location",
        )

        col_mode, col_contract = st.columns(2)
        with col_mode:
            work_mode = st.selectbox("Work mode", WORK_MODES, key="pref_work_mode")
        with col_contract:
            contract = st.selectbox("Contract", CONTRACT_TYPES, key="pref_contract")

        country_map = {
            "United States": "us",
            "United Kingdom": "gb",
            "Australia": "au",
            "Canada": "ca",
            "Germany": "de",
            "France": "fr",
            "India": "in",
            "Singapore": "sg",
            "Indonesia": "id",
        }
        country_label = st.selectbox("Country", list(country_map.keys()), key="pref_country")

    st.markdown("<div style='margin-top:2rem;'></div>", unsafe_allow_html=True)

    # ── Search button ─────────────────────────────────────────────────────────
    _, btn_col, _ = st.columns([3, 2, 3])
    with btn_col:
        search_clicked = st.button(
            "Analyze & Find Jobs",
            type="primary",
            use_container_width=True,
            key="search_btn",
        )

    if search_clicked:
        _handle_search(keywords, location, work_mode, contract, country_map[country_label])

    # ── How it works ──────────────────────────────────────────────────────────
    st.markdown("<div style='margin-top:4rem;'></div>", unsafe_allow_html=True)
    _render_how_it_works()


def _handle_search(
    keywords: str,
    location: str,
    work_mode: str,
    contract: str,
    country: str,
) -> None:
    if not st.session_state.get("cv_text"):
        st.warning("Please upload your CV before searching.")
        return
    if not keywords.strip():
        st.warning("Enter at least one keyword or job title.")
        return

    st.session_state.preferences = {
        "keywords": keywords.strip(),
        "location": location.strip(),
        "work_mode": work_mode,
        "contract": contract,
        "country": country,
    }

    with st.spinner("Fetching and scoring jobs…"):
        try:
            from core.job_fetcher import fetch_jobs
            from core.probability_engine import rank_jobs

            jobs = fetch_jobs(
                keywords=keywords,
                location=location,
                country=country,
                contract_type=contract,
                work_mode=work_mode,
                max_results=config.DEFAULT_RESULTS_COUNT,
            )

            if not jobs:
                st.warning("No jobs found. Try different keywords or location.")
                return

            ranked = rank_jobs(st.session_state.cv_text, jobs)
            st.session_state.job_results = ranked
            st.session_state.search_done = True
            st.session_state.page = "results"
            st.rerun()

        except ConnectionError as exc:
            st.error(f"Search failed: {exc}")
        except Exception as exc:
            st.error(f"An unexpected error occurred: {exc}")


def _render_how_it_works() -> None:
    st.markdown(
        """
        <div style="border-top:1px solid rgba(108,99,255,0.12); padding-top:3rem;">
            <div style="
                font-family:'DM Mono',monospace; font-size:0.68rem;
                color:#555570; text-transform:uppercase; letter-spacing:0.14em;
                text-align:center; margin-bottom:2rem;
            ">How it works</div>
            <div style="display:grid; grid-template-columns:repeat(3,1fr); gap:1.5rem; max-width:800px; margin:0 auto;">
        """,
        unsafe_allow_html=True,
    )

    steps = [
        ("01", "Upload", "Your CV is parsed locally. No data is stored after your session ends."),
        ("02", "Aggregate", "Jobs are fetched from live APIs and ranked against your profile using semantic NLP."),
        ("03", "Prioritize", "Each listing gets a probability score weighted by company competitiveness."),
    ]

    for num, title, desc in steps:
        st.markdown(
            f"""
            <div class="nh-card" style="text-align:center;">
                <div style="
                    font-family:'DM Mono',monospace; font-size:0.68rem;
                    color:#6c63ff; letter-spacing:0.12em; margin-bottom:0.5rem;
                ">{num}</div>
                <div style="
                    font-family:'Syne',sans-serif; font-weight:700;
                    font-size:1rem; color:#eeeef5; margin-bottom:0.5rem;
                ">{title}</div>
                <div style="color:#8888aa; font-size:0.82rem; line-height:1.6;">{desc}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("</div></div>", unsafe_allow_html=True)
