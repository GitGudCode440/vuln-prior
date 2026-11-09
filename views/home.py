"""Home page: what VulnPrior is, why two methods, and a live demo."""
import streamlit as st

from core.greedy import greedy_select
from core.knapsack import knapsack_select
from core.models import Vulnerability
from ui import bar_row, budget_bar, html

PRIORITIZER = "views/prioritizer.py"

# The classic example where the greedy rule of thumb is not optimal
DEMO = [
    Vulnerability("A", "Fix A", 8.0, 4, 10, 60),
    Vulnerability("B", "Fix B", 8.0, 4, 20, 100),
    Vulnerability("C", "Fix C", 8.0, 4, 30, 120),
]


def picks(result) -> str:
    return " and ".join(result.selected_ids) if result.selected else "nothing"


# ------------------------------------------------------------------ hero
left, right = st.columns([1.05, 1], gap="large", vertical_alignment="center")

with left:
    html(
        """
<div class="vp-home-h1">VulnPrior</div>
<div class="vp-tagline">Fix the right vulnerabilities first.</div>
<p class="vp-lead">You almost never have the time or money to fix everything.
VulnPrior chooses which fixes to make so you remove the most risk without going over your budget.</p>
<p class="vp-sub">It compares a quick rule of thumb (Greedy) with a method that is guaranteed to find
the best answer (Dynamic Programming), and shows you exactly where and why they differ.</p>
"""
    )
    st.write("")
    if st.button("Open the prioritizer", type="primary", key="hero_cta"):
        st.switch_page(PRIORITIZER)

with right:
    with st.container(border=True):
        html('<p class="vp-demo-title">Try it yourself</p>')
        html(
            """<p class="vp-demo-note">Three fixes. A costs 10 and removes 60 risk, B costs 20 and removes 100,
            C costs 30 and removes 120. Drag the budget and watch where Greedy falls behind.</p>"""
        )
        demo_budget = st.slider("Budget", 0, 60, 50, key="home_demo_budget")

        if demo_budget == 0:
            st.info("With a budget of 0 nothing can be fixed. Drag the slider up.")
        else:
            g = greedy_select(DEMO, demo_budget)
            d = knapsack_select(DEMO, demo_budget)
            html(
                bar_row(f"Greedy picks {picks(g)}", f"risk removed: {g.total_risk_reduction:,.0f}")
                + budget_bar(g, "greedy", demo_budget)
            )
            html(
                bar_row(f"Dynamic programming picks {picks(d)}", f"risk removed: {d.total_risk_reduction:,.0f}")
                + budget_bar(d, "dp", demo_budget)
            )
            gap = d.total_risk_reduction - g.total_risk_reduction
            if gap > 1e-9:
                st.warning(f"Greedy removes {gap:,.0f} less risk than the best possible answer at this budget.")
            else:
                st.success("Both methods agree at this budget. Try 40 or 50 to see them split.")

# ------------------------------------------------------------------ two methods
html('<div class="vp-section-title">Two methods, one question</div>')
html(
    """<p class="vp-section-sub">Both answer the same question: which fixes should we do with the budget we have?
    They trade speed against certainty.</p>"""
)
m1, m2 = st.columns(2, gap="large")
with m1:
    html(
        """
<div class="vp-method greedy">
<span class="vp-tag greedy">Greedy</span>
<h3>Fast rule of thumb</h3>
<p class="kicker">Best value for money first.</p>
<ul>
<li>Works out risk removed per unit of cost for every fix.</li>
<li>Sorts from best value to worst.</li>
<li>Takes each fix that still fits in the budget.</li>
</ul>
<div class="meta"><b>Fast</b>, but can miss the best combination. Time grows like O(n log n).</div>
</div>
"""
    )
with m2:
    html(
        """
<div class="vp-method dp">
<span class="vp-tag dp">Dynamic programming</span>
<h3>Best possible answer</h3>
<p class="kicker">Checks every budget level, step by step.</p>
<ul>
<li>Builds a table of the best result for every budget up to yours.</li>
<li>Decides for each fix whether including it improves the total.</li>
<li>Traces back through the table to list the chosen fixes.</li>
</ul>
<div class="meta"><b>Always optimal</b>, but slower and heavier. Time and memory grow like O(n × budget).</div>
</div>
"""
    )

# ------------------------------------------------------------------ steps
html('<div class="vp-section-title">What happens when you use it</div>')
st.write("")
s1, s2, s3 = st.columns(3, gap="large")
with s1:
    html(
        """<div class="vp-step"><b>1. Load fixes and a budget</b>
        <p>Use the built-in sample, upload a CSV, or generate random data. Then enter how much you can spend.</p></div>"""
    )
with s2:
    html(
        """<div class="vp-step"><b>2. Records are checked</b>
        <p>Every record is validated. Bad ones are rejected and listed with the reason, so nothing wrong sneaks in.</p></div>"""
    )
with s3:
    html(
        """<div class="vp-step"><b>3. Both methods run</b>
        <p>You see the chosen fixes, cost, risk removed, speed and memory for each, with a plain-English verdict.</p></div>"""
    )

# ------------------------------------------------------------------ features
html('<div class="vp-section-title">What is inside</div>')
f1, f2 = st.columns(2, gap="large")
with f1:
    html(
        """
<div class="vp-feature"><b>Strict input checking</b><p>Missing fields, negative costs, out-of-range scores and duplicate ids are rejected with a clear reason.</p></div>
<div class="vp-feature"><b>Edge-case files</b><p>Ready-made files for zero budget, empty input, unaffordable fixes, free fixes and ties.</p></div>
"""
    )
with f2:
    html(
        """
<div class="vp-feature"><b>Time and memory measured</b><p>Each method is timed over several runs, and its peak memory is recorded separately.</p></div>
<div class="vp-feature"><b>Scaling experiments</b><p>Watch both methods slow down as the number of fixes or the budget grows.</p></div>
"""
    )

# ------------------------------------------------------------------ team
html('<div class="vp-section-title">The team</div>')
html(
    """<p class="vp-section-sub">CT-363 Design and Analysis of Algorithms, complex computing problem.
    Department of Computer Science and Information Systems, NED University of Engineering and Technology.</p>"""
)
html(
    """
<div class="vp-team">
<div class="vp-person"><b>Mustafa Ahmed Siddiqui</b><span>CT-24261</span></div>
<div class="vp-person"><b>Wasif Ahmed Soomro</b><span>CT-24269</span></div>
<div class="vp-person"><b>Muhammad Mahad Hashmi</b><span>CT-24287</span></div>
<div class="vp-person"><b>Muhammad Zaid Khan</b><span>CT-24300</span></div>
</div>
"""
)

st.write("")
st.write("")
if st.button("Open the prioritizer", type="primary", key="bottom_cta"):
    st.switch_page(PRIORITIZER)
