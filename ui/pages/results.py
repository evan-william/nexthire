"""
Results page: displays ranked job listings with probability scores and filters.
"""

from typing import List, Dict
import streamlit as st

from ui.components import (
    empty_state,
    job_card,
    render_navbar,
    section_header,
    stat_card,
)
from core.semantic_matcher import extract_skills


def render() -> None:
    render_navbar("results")

    jobs: List[Dict] = st.session_state.get("job_results", [])
    prefs = st.session_state.get("preferences", {})
    cv_text = st.session_state.get("cv_text", "")

    if not jobs:
        empty_state("No results yet. Go back and run a search.", "◌")
        if st.button("← Back to Search", type="secondary"):
            st.session_state.page = "home"
            st.rerun()
        return

    # ── Summary stats ─────────────────────────────────────────────────────────
    high_prob = [j for j in jobs if j.get("probability", 0) >= 0.65]
    avg_prob = sum(j.get("probability", 0) for j in jobs) / len(jobs)
    top_score = jobs[0].get("probability", 0) if jobs else 0

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(stat_card("Total Jobs", str(len(jobs)), prefs.get("keywords", "")), unsafe_allow_html=True)
    with col2:
        st.markdown(stat_card("Strong Matches", str(len(high_prob)), "≥ 65% match chance"), unsafe_allow_html=True)
    with col3:
        st.markdown(stat_card("Avg Match", f"{avg_prob*100:.0f}%", "Across all listings"), unsafe_allow_html=True)
    with col4:
        st.markdown(stat_card("Top Score", f"{top_score*100:.0f}%", jobs[0].get("company", "") if jobs else ""), unsafe_allow_html=True)

    st.markdown("<div style='margin:1.5rem 0;'></div>", unsafe_allow_html=True)

    # ── Skills detected from CV ────────────────────────────────────────────────
    if cv_text:
        skills = extract_skills(cv_text)
        if skills:
            badges = "".join(
                f'<span class="nh-badge nh-badge-purple" style="margin:0.2rem;">{s}</span>'
                for s in skills[:12]
            )
            st.markdown(
                f"""
                <div style="margin-bottom:1.5rem;">
                    <div class="nh-stat-label" style="margin-bottom:0.5rem;">Skills detected from your CV</div>
                    <div>{badges}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # ── Filter bar ────────────────────────────────────────────────────────────
    col_filter, col_sort, col_back = st.columns([3, 3, 2])
    with col_filter:
        min_prob = st.slider(
            "Min match chance",
            min_value=0,
            max_value=100,
            value=0,
            step=5,
            format="%d%%",
            key="filter_min_prob",
        )
    with col_sort:
        sort_by = st.selectbox(
            "Sort by",
            ["Match chance (high → low)", "Match chance (low → high)", "Skill match"],
            key="sort_by",
        )
    with col_back:
        st.markdown("<div style='margin-top:1.6rem;'></div>", unsafe_allow_html=True)
        if st.button("← New Search", type="secondary", use_container_width=True):
            st.session_state.page = "home"
            st.session_state.job_results = None
            st.rerun()

    # ── Apply filters + sorting ───────────────────────────────────────────────
    filtered = [j for j in jobs if j.get("probability", 0) * 100 >= min_prob]

    if sort_by == "Match chance (low → high)":
        filtered = sorted(filtered, key=lambda j: j.get("probability", 0))
    elif sort_by == "Skill match":
        filtered = sorted(filtered, key=lambda j: j.get("match_score", 0), reverse=True)

    st.markdown("<div style='margin-top:1rem;'></div>", unsafe_allow_html=True)
    section_header(
        f"{len(filtered)} Listings",
        f"Filtered from {len(jobs)} total · sorted by {sort_by.split(' (')[0].lower()}",
    )

    # ── Job cards ─────────────────────────────────────────────────────────────
    if not filtered:
        empty_state(f"No jobs match the {min_prob}%+ filter. Lower the threshold.", "◌")
    else:
        for i, job in enumerate(filtered):
            job_card(job, i)
