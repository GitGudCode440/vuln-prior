"""Shared styling and small UI helpers for VulnPrior."""
from html import escape

import streamlit as st

GREEDY_COLOR = "#E08A00"
DP_COLOR = "#0B7A75"

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,700&family=Public+Sans:wght@400;500;600&display=swap');

:root {
  --ink: #0F2A3D;
  --muted: #566775;
  --line: #D3DCE3;
  --greedy: #E08A00;
  --dp: #0B7A75;
}
html, body, .stApp, [data-testid="stSidebar"] {
  font-family: 'Public Sans', system-ui, -apple-system, 'Segoe UI', sans-serif;
}
h1, h2, h3, h4 {
  font-family: 'Bricolage Grotesque', 'Public Sans', system-ui, sans-serif !important;
  color: var(--ink);
  letter-spacing: -0.01em;
}
.block-container { padding-top: 5rem; max-width: 1180px; }
footer { visibility: hidden; }

/* ---- hero ---- */
.vp-hero {
  display: grid; grid-template-columns: 1.05fr 1fr; gap: 2.5rem;
  align-items: center; padding: 0.5rem 0 1.4rem 0;
}
.vp-hero h1 { font-size: 3.4rem; line-height: 1.02; margin: 0 0 0.9rem 0; font-weight: 700; }
.vp-lead { font-size: 1.12rem; line-height: 1.55; color: var(--ink); max-width: 33rem; margin: 0 0 0.7rem 0; }
.vp-sub { font-size: 0.95rem; color: var(--muted); max-width: 33rem; margin: 0; }

/* ---- the live example in the hero ---- */
.vp-demo { background: #fff; border: 1px solid var(--line); border-radius: 8px; padding: 1.1rem 1.2rem 1.2rem 1.2rem; }
.vp-demo-title { font-family: 'Bricolage Grotesque', sans-serif; font-weight: 700; font-size: 1.05rem; color: var(--ink); margin: 0 0 0.2rem 0; }
.vp-demo-note { font-size: 0.85rem; color: var(--muted); margin: 0 0 0.9rem 0; }
.vp-row-label { display: flex; justify-content: space-between; font-size: 0.88rem; font-weight: 600; color: var(--ink); margin: 0.7rem 0 0.3rem 0; }
.vp-row-label span:last-child { font-weight: 500; color: var(--muted); }
.vp-bar { display: flex; height: 2.3rem; border-radius: 5px; overflow: hidden; border: 1px solid var(--line); }
.vp-seg { display: flex; align-items: center; justify-content: center; color: #fff; font-weight: 600; font-size: 0.82rem; border-right: 2px solid #fff; }
.vp-seg:last-child { border-right: none; }
.vp-seg.greedy { background: var(--greedy); }
.vp-seg.dp { background: var(--dp); }
.vp-seg.unused {
  color: var(--muted); font-weight: 500;
  background: repeating-linear-gradient(135deg, #eef2f5, #eef2f5 6px, #e1e8ed 6px, #e1e8ed 12px);
}

/* ---- how-to steps ---- */
.vp-step { border-top: 3px solid var(--ink); padding-top: 0.6rem; }
.vp-step b { font-family: 'Bricolage Grotesque', sans-serif; font-size: 1.05rem; color: var(--ink); }
.vp-step p { margin: 0.3rem 0 0 0; font-size: 0.93rem; line-height: 1.5; color: #2a4254; }

/* ---- algorithm tags and verdict ---- */
.vp-tag { display: inline-block; padding: 0.15rem 0.65rem; border-radius: 999px; color: #fff; font-weight: 600; font-size: 0.82rem; margin-bottom: 0.4rem; }
.vp-tag.greedy { background: var(--greedy); }
.vp-tag.dp { background: var(--dp); }
.vp-verdict { background: #fff; border: 1px solid var(--line); border-left: 5px solid var(--ink); border-radius: 6px; padding: 0.9rem 1.1rem; margin: 0.4rem 0 1rem 0; font-size: 1rem; line-height: 1.55; color: var(--ink); }

/* ---- Streamlit widgets ---- */
[data-testid="stMetric"] { background: #fff; border: 1px solid var(--line); border-left: 4px solid var(--ink); border-radius: 6px; padding: 0.7rem 0.95rem; }
[data-testid="stMetricLabel"] p { color: var(--muted); font-size: 0.85rem; }
button[data-baseweb="tab"] p { font-weight: 600; font-size: 0.98rem; }
[data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 { font-size: 1.15rem; }
.vp-foot { margin-top: 2.5rem; padding-top: 0.9rem; border-top: 1px solid var(--line); font-size: 0.82rem; color: var(--muted); }

@media (max-width: 860px) {
  .vp-hero { grid-template-columns: 1fr; gap: 1.2rem; }
  .vp-hero h1 { font-size: 2.6rem; }
}


/* ---- page polish ---- */
.stApp {
  background-image: radial-gradient(#DAE2E8 1px, transparent 1px);
  background-size: 22px 22px;
}
.vp-tagline { font-family: 'Bricolage Grotesque', 'Public Sans', sans-serif; font-weight: 500; font-size: 1.6rem; line-height: 1.25; color: var(--ink); margin: 0 0 0.9rem 0; max-width: 30rem; }
.vp-home-h1 { font-family: 'Bricolage Grotesque', sans-serif; font-size: 4.2rem; line-height: 0.98; font-weight: 700; color: var(--ink); margin: 0.2rem 0 0.7rem 0; letter-spacing: -0.02em; }
.vp-section-title { font-family: 'Bricolage Grotesque', sans-serif; font-size: 1.7rem; font-weight: 700; color: var(--ink); margin: 2.6rem 0 0.3rem 0; }
.vp-section-sub { color: var(--muted); font-size: 0.98rem; margin: 0 0 1.1rem 0; max-width: 40rem; }

/* ---- the two method cards ---- */
.vp-method { background: #fff; border: 1px solid var(--line); border-radius: 8px; padding: 1.1rem 1.25rem 1.2rem 1.25rem; height: 100%; }
.vp-method.greedy { border-top: 6px solid var(--greedy); }
.vp-method.dp { border-top: 6px solid var(--dp); }
.vp-method h3 { margin: 0 0 0.15rem 0; font-size: 1.3rem; }
.vp-method .kicker { color: var(--muted); font-size: 0.9rem; margin: 0 0 0.7rem 0; }
.vp-method ul { margin: 0 0 0.8rem 1.1rem; padding: 0; font-size: 0.95rem; line-height: 1.55; color: #2a4254; }
.vp-method .meta { border-top: 1px solid var(--line); padding-top: 0.6rem; font-size: 0.88rem; color: var(--muted); }
.vp-method .meta b { color: var(--ink); }

/* ---- feature list ---- */
.vp-feature { padding: 0.7rem 0; border-bottom: 1px solid var(--line); }
.vp-feature b { color: var(--ink); font-size: 1rem; }
.vp-feature p { margin: 0.15rem 0 0 0; font-size: 0.93rem; color: var(--muted); line-height: 1.5; }

/* ---- team ---- */
.vp-team { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; }
.vp-person { border-left: 3px solid var(--ink); padding-left: 0.8rem; }
.vp-person b { display: block; color: var(--ink); font-size: 0.98rem; }
.vp-person span { color: var(--muted); font-size: 0.85rem; }
@media (max-width: 860px) {
  .vp-home-h1 { font-size: 3rem; }
  .vp-team { grid-template-columns: 1fr 1fr; }
}

/* ---- motion: one page-load sequence, plus motion that answers a click or drag ---- */
@keyframes vp-rise { from { opacity: 0; transform: translateY(14px); } to { opacity: 1; transform: translateY(0); } }
@keyframes vp-grow { from { transform: scaleX(0); opacity: 0.2; } to { transform: scaleX(1); opacity: 1; } }
.vp-home-h1, .vp-tagline, .vp-lead, .vp-sub { animation: vp-rise 0.7s cubic-bezier(0.2, 0.7, 0.2, 1) backwards; }
.vp-tagline { animation-delay: 0.12s; }
.vp-lead { animation-delay: 0.24s; }
.vp-sub { animation-delay: 0.36s; }
.vp-seg { transform-origin: left center; animation: vp-grow 0.55s cubic-bezier(0.2, 0.7, 0.2, 1) backwards; transition: width 0.45s ease, filter 0.15s ease; }
.vp-seg:hover { filter: brightness(1.12); }
.vp-bar-wrap { margin-bottom: 1rem; }
.vp-seg { white-space: nowrap; overflow: hidden; }
.stButton button[kind="primary"] { transition: transform 0.15s ease, box-shadow 0.15s ease; }
.stButton button[kind="primary"]:hover { transform: translateY(-2px); box-shadow: 0 6px 14px rgba(11, 122, 117, 0.28); }
@media (prefers-reduced-motion: reduce) {
  .vp-home-h1, .vp-tagline, .vp-lead, .vp-sub, .vp-seg { animation: none !important; transition: none !important; }
  .stButton button[kind="primary"] { transition: none !important; }
  .stButton button[kind="primary"]:hover { transform: none; }
}
</style>
"""


def html(block: str) -> None:
    """Render an HTML snippet (lines are stripped so Markdown never treats them as code)."""
    st.markdown(" ".join(line.strip() for line in block.splitlines() if line.strip()), unsafe_allow_html=True)


def inject_css() -> None:
    html(CSS)


def footer() -> None:
    html(
        """<div class="vp-foot">CT-363 Design and Analysis of Algorithms, NED University of Engineering and Technology.
        VulnPrior is for defensive remediation planning and uses synthetic or authorized data only.</div>"""
    )


def budget_bar(result, css_class: str, budget: int) -> str:
    """HTML for one bar: each chosen fix is a block sized by its cost, plus any unused budget.

    Blocks grow in one after another. Hover a block to see the fix's details.
    """
    segs = []
    for i, v in enumerate(result.selected):
        width = v.cost / budget * 100
        if width >= 12:
            label = f"{escape(v.id)} ({v.cost})"
        elif width >= 5:
            label = escape(v.id)
        else:
            label = ""
        tip = escape(f"{v.id}: {v.name} | cost {v.cost} | risk reduction {v.risk_reduction:g}", quote=True)
        segs.append(
            f'<div class="vp-seg {css_class}" title="{tip}" '
            f'style="width:{max(width, 0.6):.2f}%;min-width:3px;animation-delay:{i * 0.06:.2f}s">{label}</div>'
        )
    if result.remaining_budget > 0:
        unused_pct = result.remaining_budget / budget * 100
        unused_label = f"{result.remaining_budget:,} unused" if unused_pct >= 9 else ""
        segs.append(
            f'<div class="vp-seg unused" title="{result.remaining_budget:,} budget unused" '
            f'style="width:{unused_pct:.2f}%;animation-delay:{len(result.selected) * 0.06:.2f}s">{unused_label}</div>'
        )
    return f'<div class="vp-bar-wrap"><div class="vp-bar">{"".join(segs)}</div></div>'


def bar_row(label: str, value_text: str) -> str:
    return f'<div class="vp-row-label"><span>{escape(label)}</span><span>{escape(value_text)}</span></div>'
