"""About page."""

import streamlit as st
from ui.components import render_navbar


def render() -> None:
    render_navbar("about")
    st.markdown(
        """
        <div style="max-width:640px; margin:0 auto; padding:2rem 0;">
            <h1 style="font-family:'Syne',sans-serif; font-weight:800; font-size:2rem; color:#eeeef5;">
                About NextHire
            </h1>
            <p style="color:#8888aa; line-height:1.8;">
                NextHire is an open-source predictive job analytics platform. It aggregates live
                job listings and scores each one against your CV using semantic NLP, weighted by
                real-world company competitiveness data.
            </p>
            <h3 style="font-family:'Syne',sans-serif; color:#eeeef5; margin-top:2rem;">Privacy</h3>
            <p style="color:#8888aa; line-height:1.8;">
                Your CV is processed entirely in-memory during your session.
                No personal data is written to disk or transmitted to third parties beyond the job search API.
                Session data is discarded when you close the tab.
            </p>
            <h3 style="font-family:'Syne',sans-serif; color:#eeeef5; margin-top:2rem;">Tech stack</h3>
            <p style="color:#8888aa; line-height:1.8;">
                Streamlit · scikit-learn · PyMuPDF · python-docx · SQLite · Adzuna API
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("← Back", type="secondary"):
        st.session_state.page = "home"
        st.rerun()
