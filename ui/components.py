"""
Reusable UI components for NextHire.
All HTML is rendered via st.markdown with unsafe_allow_html.
Content injected into HTML is escaped to prevent XSS.
"""

import html
from typing import Dict, List, Optional

import streamlit as st

from ui.styles import probability_bar_html, probability_color


def _e(text: str) -> str:
    """HTML-escape a string before injecting into markup."""
    return html.escape(str(text or ""))


def render_navbar(current_page: str = "home") -> None:
    """Top navigation bar."""
    st.markdown(
        f"""
        <div style="
            display: flex; align-items: center; justify-content: space-between;
            padding: 1rem 0 2rem; border-bottom: 1px solid rgba(108,99,255,0.15);
            margin-bottom: 2.5rem;
        ">
            <div style="
                font-family: 'Syne', sans-serif; font-size: 1.4rem;
                font-weight: 800; color: #eeeef5; letter-spacing: -0.03em;
            ">
                Next<span style="color:#6c63ff;">Hire</span>
            </div>
            <div style="
                font-family: 'DM Mono', monospace; font-size: 0.72rem;
                color: #555570; text-transform: uppercase; letter-spacing: 0.12em;
            ">
                Predictive Job Analytics
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def stat_card(label: str, value: str, subtitle: str = "") -> str:
    """Returns HTML for a single stat card."""
    subtitle_html = f'<div style="color:#8888aa; font-size:0.8rem; margin-top:0.2rem;">{_e(subtitle)}</div>' if subtitle else ""
    return f"""
    <div class="nh-card" style="text-align:center;">
        <div class="nh-stat-label">{_e(label)}</div>
        <div class="nh-stat-value" style="margin:0.3rem 0;">{_e(value)}</div>
        {subtitle_html}
    </div>
    """


def job_card(job: Dict, index: int) -> None:
    """Renders a single job result card."""
    prob = job.get("probability", 0.0)
    prob_pct = job.get("probability_pct", "N/A")
    color = probability_color(prob)
    tier = _e(job.get("tier_label", ""))
    title = _e(job.get("title", "Unknown Role"))
    company = _e(job.get("company", "Unknown Company"))
    location = _e(job.get("location", ""))
    url = _e(job.get("url", "#"))
    salary_min = job.get("salary_min")
    salary_max = job.get("salary_max")
    match_pct = f"{job.get('match_score', 0) * 100:.0f}%"

    salary_html = ""
    if salary_min or salary_max:
        lo = f"${salary_min:,.0f}" if salary_min else ""
        hi = f"${salary_max:,.0f}" if salary_max else ""
        salary_range = f"{lo} – {hi}" if lo and hi else (lo or hi)
        salary_html = f'<span class="nh-badge nh-badge-purple">{_e(salary_range)}</span>'

    bar_html = probability_bar_html(prob)

    st.markdown(
        f"""
        <div class="nh-card" style="margin-bottom:1rem;">
            <div style="display:flex; align-items:flex-start; justify-content:space-between; gap:1rem;">
                <div style="flex:1; min-width:0;">
                    <div style="
                        font-family:'Syne',sans-serif; font-size:1.05rem;
                        font-weight:700; color:#eeeef5; margin-bottom:0.25rem;
                        white-space:nowrap; overflow:hidden; text-overflow:ellipsis;
                    ">{title}</div>
                    <div style="color:#8888aa; font-size:0.875rem; margin-bottom:0.6rem;">
                        {company}
                        {"&nbsp;&nbsp;·&nbsp;&nbsp;" + location if location else ""}
                    </div>
                    <div style="display:flex; gap:0.5rem; flex-wrap:wrap; align-items:center;">
                        <span class="nh-badge nh-badge-purple">{tier}</span>
                        {salary_html}
                        <span style="font-family:'DM Mono',monospace; font-size:0.72rem; color:#555570;">
                            Skill match: {match_pct}
                        </span>
                    </div>
                </div>
                <div style="text-align:right; min-width:100px; flex-shrink:0;">
                    <div class="nh-stat-label" style="margin-bottom:0.2rem;">Match chance</div>
                    <div style="
                        font-family:'Syne',sans-serif; font-weight:800;
                        font-size:1.6rem; line-height:1;
                        color:{'#22d3a0' if color == 'green' else '#f59e0b' if color == 'amber' else '#ef4444'};
                    ">{_e(prob_pct)}</div>
                    {bar_html}
                </div>
            </div>
            <div style="margin-top:1rem; padding-top:0.75rem; border-top:1px solid rgba(108,99,255,0.1);">
                <a href="{url}" target="_blank" rel="noopener noreferrer" style="
                    font-family:'Syne',sans-serif; font-size:0.82rem; font-weight:600;
                    color:#6c63ff; text-decoration:none; letter-spacing:0.02em;
                ">Apply Now →</a>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def empty_state(message: str, icon: str = "◌") -> None:
    st.markdown(
        f"""
        <div style="
            text-align:center; padding:4rem 2rem;
            color:#555570; font-family:'DM Mono',monospace; font-size:0.85rem;
        ">
            <div style="font-size:2.5rem; margin-bottom:1rem; opacity:0.4;">{icon}</div>
            {_e(message)}
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_header(title: str, subtitle: str = "") -> None:
    sub_html = f'<p style="color:#8888aa; font-size:0.9rem; margin:0.3rem 0 0;">{_e(subtitle)}</p>' if subtitle else ""
    st.markdown(
        f"""
        <div style="margin-bottom:1.5rem;">
            <h2 style="
                font-family:'Syne',sans-serif; font-weight:700;
                font-size:1.5rem; color:#eeeef5; margin:0;
            ">{_e(title)}</h2>
            {sub_html}
        </div>
        """,
        unsafe_allow_html=True,
    )
