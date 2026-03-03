"""
CSS injection for NextHire's custom UI.
Hides Streamlit chrome and applies the design system.
"""

import streamlit as st


GLOBAL_CSS = """
<style>
/* ── Import typefaces ─────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Syne:wght@400;600;700;800&family=Inter:wght@300;400;500&display=swap');

/* ── Hide Streamlit chrome ───────────────────────────── */
#MainMenu, header, footer,
[data-testid="stSidebar"],
[data-testid="collapsedControl"],
.stDeployButton { display: none !important; }

/* ── Design tokens ───────────────────────────────────── */
:root {
    --bg-base:       #080810;
    --bg-surface:    #0f0f1a;
    --bg-card:       #14141f;
    --bg-card-hover: #1a1a28;
    --border:        rgba(108, 99, 255, 0.15);
    --border-bright: rgba(108, 99, 255, 0.50);
    --accent:        #6c63ff;
    --accent-dim:    rgba(108, 99, 255, 0.12);
    --accent-glow:   rgba(108, 99, 255, 0.35);
    --green:         #22d3a0;
    --amber:         #f59e0b;
    --red:           #ef4444;
    --text-primary:  #eeeef5;
    --text-secondary:#8888aa;
    --text-dim:      #555570;
    --radius-sm:     6px;
    --radius-md:     12px;
    --radius-lg:     20px;
    --font-display:  'Syne', sans-serif;
    --font-body:     'Inter', sans-serif;
    --font-mono:     'DM Mono', monospace;
    --transition:    0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

/* ── Base ────────────────────────────────────────────── */
html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg-base) !important;
    color: var(--text-primary) !important;
    font-family: var(--font-body) !important;
}

[data-testid="block-container"] {
    padding: 2rem 3rem !important;
    max-width: 1200px;
    margin: 0 auto;
}

/* ── Typography ──────────────────────────────────────── */
h1, h2, h3 {
    font-family: var(--font-display) !important;
    letter-spacing: -0.02em;
}

/* ── Inputs ──────────────────────────────────────────── */
[data-testid="stSelectbox"] > div > div,
[data-testid="stTextInput"] > div > div > input {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text-primary) !important;
    font-family: var(--font-body) !important;
    transition: border-color var(--transition) !important;
}

[data-testid="stSelectbox"] > div > div:hover,
[data-testid="stTextInput"] > div > div > input:focus {
    border-color: var(--border-bright) !important;
}

/* ── File uploader ───────────────────────────────────── */
[data-testid="stFileUploader"] {
    background: var(--bg-card) !important;
    border: 1.5px dashed var(--border-bright) !important;
    border-radius: var(--radius-md) !important;
    transition: all var(--transition) !important;
}

[data-testid="stFileUploader"]:hover {
    border-color: var(--accent) !important;
    background: var(--accent-dim) !important;
}

/* ── Primary button ──────────────────────────────────── */
[data-testid="stButton"] > button[kind="primary"] {
    background: var(--accent) !important;
    color: #fff !important;
    border: none !important;
    border-radius: var(--radius-sm) !important;
    font-family: var(--font-display) !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    padding: 0.65rem 2rem !important;
    transition: all var(--transition) !important;
    box-shadow: 0 0 20px var(--accent-glow) !important;
}

[data-testid="stButton"] > button[kind="primary"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 0 32px var(--accent-glow) !important;
}

/* ── Secondary button ────────────────────────────────── */
[data-testid="stButton"] > button[kind="secondary"] {
    background: transparent !important;
    color: var(--text-secondary) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    font-family: var(--font-body) !important;
    transition: all var(--transition) !important;
}

[data-testid="stButton"] > button[kind="secondary"]:hover {
    border-color: var(--border-bright) !important;
    color: var(--text-primary) !important;
}

/* ── Progress bar ────────────────────────────────────── */
[data-testid="stProgress"] > div > div {
    background: var(--accent) !important;
}

/* ── Divider ─────────────────────────────────────────── */
hr { border-color: var(--border) !important; }

/* ── Scrollbar ───────────────────────────────────────── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg-base); }
::-webkit-scrollbar-thumb { background: var(--border-bright); border-radius: 3px; }

/* ── Custom components ───────────────────────────────── */
.nh-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: 1.5rem;
    transition: all var(--transition);
}

.nh-card:hover {
    border-color: var(--border-bright);
    background: var(--bg-card-hover);
    transform: translateY(-2px);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
}

.nh-badge {
    display: inline-block;
    font-family: var(--font-mono);
    font-size: 0.72rem;
    padding: 0.2rem 0.6rem;
    border-radius: 4px;
    border: 1px solid;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}

.nh-badge-green  { color: var(--green); border-color: rgba(34,211,160,0.3); background: rgba(34,211,160,0.08); }
.nh-badge-amber  { color: var(--amber); border-color: rgba(245,158,11,0.3); background: rgba(245,158,11,0.08); }
.nh-badge-red    { color: var(--red);   border-color: rgba(239,68,68,0.3);  background: rgba(239,68,68,0.08); }
.nh-badge-purple { color: var(--accent); border-color: var(--border-bright); background: var(--accent-dim); }

.nh-prob-bar-wrap {
    background: rgba(255,255,255,0.06);
    border-radius: 4px;
    height: 6px;
    overflow: hidden;
    margin: 0.4rem 0;
}

.nh-prob-bar {
    height: 100%;
    border-radius: 4px;
    transition: width 0.6s ease;
}

.nh-stat-label {
    font-family: var(--font-mono);
    font-size: 0.68rem;
    color: var(--text-dim);
    text-transform: uppercase;
    letter-spacing: 0.1em;
}

.nh-stat-value {
    font-family: var(--font-display);
    font-size: 1.8rem;
    font-weight: 700;
    color: var(--text-primary);
    line-height: 1.1;
}
</style>
"""


def inject_global_styles() -> None:
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


def probability_color(probability: float) -> str:
    """Return CSS class suffix based on probability threshold."""
    if probability >= 0.65:
        return "green"
    elif probability >= 0.40:
        return "amber"
    return "red"


def probability_bar_html(probability: float) -> str:
    """Render an inline probability bar as HTML."""
    pct = probability * 100
    color = probability_color(probability)
    color_map = {"green": "#22d3a0", "amber": "#f59e0b", "red": "#ef4444"}
    hex_color = color_map[color]
    return f"""
    <div class="nh-prob-bar-wrap">
        <div class="nh-prob-bar" style="width:{pct:.1f}%; background:{hex_color};"></div>
    </div>
    """
