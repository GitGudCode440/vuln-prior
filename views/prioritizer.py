"""Prioritizer page: load fixes, set a budget, compare Greedy vs dynamic programming."""
from pathlib import Path

import pandas as pd
import streamlit as st

from core.benchmark import compare, scaling_experiment
from core.generator import generate_synthetic, suggest_budget
from core.models import ValidationReport
from core.validator import load_csv, missing_columns, parse_budget, validate_records
from ui import DP_COLOR, GREEDY_COLOR, bar_row, budget_bar, html

ROOT = Path(__file__).resolve().parent.parent
SAMPLE = ROOT / "data" / "sample.csv"
EDGE_DIR = ROOT / "data" / "edge_cases"

# Suggested budgets that demonstrate each edge-case file
EDGE_BUDGET_HINTS = {
    "greedy_fails": 50,
    "all_unaffordable": 50,
    "free_fixes": 15,
    "ties": 30,
    "invalid_rows": 30,
    "empty": 100,
}

st.markdown("## Prioritizer")
st.caption("Load your fixes and a budget in the sidebar, then read the results in the tabs below.")

with st.expander("How to use VulnPrior", expanded=True):
    s1, s2, s3 = st.columns(3)
    with s1:
        html(
            """<div class="vp-step"><b>1. Choose your data</b>
            <p>Open the sidebar on the left. The built-in sample is already loaded, so you can explore right away.
            You can also upload your own CSV or generate random data.</p></div>"""
        )
    with s2:
        html(
            """<div class="vp-step"><b>2. Set your budget</b>
            <p>Enter a whole number in the same unit as your fix costs, for example engineer-hours.
            A suggested budget is filled in for you.</p></div>"""
        )
    with s3:
        html(
            """<div class="vp-step"><b>3. Read the results</b>
            <p>Use the tabs below. Start with Comparison to see which method wins,
            then open Greedy or Dynamic programming to see the exact fixes each one picked.</p></div>"""
        )
    st.markdown("")
    st.markdown(
        "**What each tab shows**\n\n"
        "- **Your data:** the records that were read, and any that were rejected, with the reason.\n"
        "- **Greedy:** the fixes chosen by the fast rule of thumb (best risk reduction per unit cost first).\n"
        "- **Dynamic programming:** the fixes chosen by the exact method that finds the best possible total.\n"
        "- **Comparison:** both results side by side, with a plain-English verdict, speed, memory and charts.\n"
        "- **Scaling:** an experiment showing how each method slows down as the problem grows."
    )

with st.expander("What do these terms mean?"):
    st.markdown(
        "- **Severity:** how serious the weakness is, from 0 to 10 (like a CVSS score).\n"
        "- **Asset importance:** how much the affected system matters to the organization, from 1 to 5.\n"
        "- **Cost:** what the fix takes to implement, as a whole number such as engineer-hours.\n"
        "- **Risk reduction:** how much risk disappears once the fix is applied. Bigger is better.\n"
        "- **Ratio:** risk reduction divided by cost, which is the value you get per unit spent. Greedy sorts by this.\n"
        "- **Budget:** the total cost you can afford. The chosen fixes can never add up to more than this.\n"
        "- **Optimality gap:** how much less risk Greedy removes compared with the best possible answer, as a percentage.\n"
        "- **Risk score:** severity × asset importance. Shown for reference only, it does not change the results."
    )


# ------------------------------------------------------------------ helpers
def vulns_to_df(vulns) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "id": v.id,
                "name": v.name,
                "severity": v.severity,
                "asset_importance": v.asset_importance,
                "risk_score (sev×imp)": round(v.risk_score, 1),
                "cost": v.cost,
                "risk_reduction": v.risk_reduction,
                "ratio (rr/cost)": "∞ (free)" if v.cost == 0 and v.risk_reduction > 0 else round(v.ratio, 3),
            }
            for v in vulns
        ]
    )


def result_metrics(r):
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Fixes selected", len(r.selected))
    c2.metric("Total cost", f"{r.total_cost:,}", help=f"Budget: {r.budget:,}")
    c3.metric("Risk reduction", f"{r.total_risk_reduction:,.1f}")
    c4.metric("Budget used", f"{r.utilization_pct:.1f}%", help=f"Remaining: {r.remaining_budget:,}")


def result_table(r):
    if not r.selected:
        st.info("No fixes were selected.")
        return
    st.dataframe(vulns_to_df(r.selected), width="stretch", hide_index=True)


# ------------------------------------------------------------------ sidebar
with st.sidebar:
    st.header("1. Choose your data")
    source = st.radio(
        "Where should the fixes come from?",
        ["Built-in sample", "Upload CSV", "Edge-case file", "Synthetic generator"],
        help="Built-in sample: 22 realistic fixes. Edge-case file: small files that test unusual situations. "
        "Synthetic generator: random data you can make as large as you like.",
    )

    report = ValidationReport()
    default_budget = 0
    source_key = source
    header_problem = None

    if source == "Built-in sample":
        st.caption("22 example vulnerabilities, ready to use.")
        records, cols = load_csv(SAMPLE)
        header_problem = missing_columns(cols)
        report = validate_records(records)
        default_budget = suggest_budget(report.valid)

    elif source == "Upload CSV":
        st.caption("Your file needs these columns: id, name, severity, asset_importance, cost, risk_reduction.")
        if SAMPLE.exists():
            st.download_button(
                "Download a CSV template",
                data=SAMPLE.read_text(encoding="utf-8"),
                file_name="vulnprior_template.csv",
                mime="text/csv",
            )
        up = st.file_uploader("Choose a CSV file", type="csv")
        if up is not None:
            records, cols = load_csv(up)
            header_problem = missing_columns(cols) if cols else []
            report = validate_records(records)
            default_budget = suggest_budget(report.valid)
            source_key = f"upload:{up.name}:{up.size}"

    elif source == "Edge-case file":
        st.caption("Small files built to test unusual situations. A matching budget is filled in for you.")
        files = sorted(p.stem for p in EDGE_DIR.glob("*.csv"))
        name = st.selectbox("File", files)
        records, cols = load_csv(EDGE_DIR / f"{name}.csv")
        header_problem = missing_columns(cols) if cols else []
        report = validate_records(records)
        default_budget = EDGE_BUDGET_HINTS.get(name, suggest_budget(report.valid))
        source_key = f"edge:{name}"

    else:
        st.caption("Random fixes. The same seed always gives the same data.")
        n = st.number_input("Number of fixes", 1, 5000, 100, step=10)
        seed = st.number_input("Random seed", 0, 10**6, 42)
        report = ValidationReport(valid=generate_synthetic(int(n), int(seed)))
        default_budget = suggest_budget(report.valid)
        source_key = f"synthetic:{n}:{seed}"

    st.header("2. Set your budget")
    budget_in = st.number_input(
        "Budget (whole number)",
        min_value=0,
        value=int(default_budget),
        step=1,
        key=f"budget_{source_key}",
        help="Use the same unit as the fix costs. The suggested value is 40% of the total cost of all fixes.",
    )
    st.caption("Results update as soon as you change anything here.")

try:
    budget = parse_budget(budget_in)
except ValueError as e:
    st.error(str(e))
    st.stop()

# ------------------------------------------------------------------ tabs
tab_data, tab_greedy, tab_dp, tab_cmp, tab_scale = st.tabs(
    ["Your data", "Greedy", "Dynamic programming", "Comparison", "Scaling"]
)

with tab_data:
    st.caption("Every record is checked before it is used. Rejected records are listed with the reason, so you can fix and re-upload them.")
    if header_problem:
        st.error(f"Your file is missing these required columns: {', '.join(header_problem)}. Add them and upload again.")
    if source == "Upload CSV" and not report.total and not header_problem:
        st.info("No file yet. Choose a CSV in the sidebar, or download the template to see the expected format.")
    c1, c2, c3 = st.columns(3)
    c1.metric("Records read", report.total)
    c2.metric("Valid", len(report.valid))
    c3.metric("Rejected", len(report.rejected))

    if report.valid:
        st.subheader("Valid records")
        st.dataframe(vulns_to_df(report.valid), width="stretch", hide_index=True)
    if report.rejected:
        st.subheader("Rejected records")
        st.dataframe(
            pd.DataFrame(
                [
                    {"row": r.row_number, **{k: v for k, v in r.raw.items()}, "reason": "; ".join(r.reasons)}
                    for r in report.rejected
                ]
            ),
            width="stretch",
            hide_index=True,
        )

# Friendly messages for degenerate inputs
if not report.valid:
    for t in (tab_greedy, tab_dp, tab_cmp):
        with t:
            st.info("There are no valid fixes to prioritize yet. Check the data source, or correct the rejected rows in the Your data tab.")
else:
    affordable = [v for v in report.valid if v.cost <= budget and v.risk_reduction > 0]
    notice = None
    if budget == 0 and affordable:
        notice = "The budget is 0, so only free fixes (cost 0) can be selected."
    elif budget == 0:
        notice = "The budget is 0, so no fixes can be selected. Raise it in the sidebar."
    elif not affordable:
        notice = "Every fix costs more than your budget (or has no benefit), so nothing can be selected. Raise the budget in the sidebar."

    cmp = compare(report.valid, budget)
    g, d = cmp.greedy, cmp.dp

    with tab_greedy:
        html('<span class="vp-tag greedy">Greedy</span>')
        st.subheader("Fast rule of thumb")
        st.caption(
            "Sorts fixes by risk reduction per unit cost and takes each one that still fits. "
            "Very fast, but not always the best. Time grows like O(n log n)."
        )
        if notice:
            st.warning(notice)
        result_metrics(g)
        result_table(g)

    with tab_dp:
        html('<span class="vp-tag dp">Dynamic programming</span>')
        st.subheader("Best possible answer")
        st.caption(
            "Tries every combination in an organized way (0/1 knapsack) and is guaranteed to find the most risk reduction "
            "for the budget. Slower, and its time and memory grow like O(n × budget)."
        )
        if cmp.dp_error:
            st.error(cmp.dp_error)
        else:
            if notice:
                st.warning(notice)
            result_metrics(d)
            result_table(d)

    with tab_cmp:
        st.caption("Both methods ran on the same fixes and the same budget.")
        if cmp.dp_error:
            st.error(cmp.dp_error)
            st.caption("Greedy still ran. See its tab for the result.")
        else:
            if notice:
                st.warning(notice)

            # Plain-English verdict
            diff = d.total_risk_reduction - g.total_risk_reduction
            if cmp.gap_pct > 1e-9:
                line = (
                    f"Greedy is not optimal here. Dynamic programming removes <b>{diff:,.1f}</b> more risk "
                    f"(Greedy reaches {100 - cmp.gap_pct:.1f}% of the best possible total)."
                )
            else:
                line = "Greedy found the best possible answer on this input, so the fast method was good enough here."
            if g.time_ms > 0 and d.time_ms / g.time_ms >= 1.5:
                speed = f" Dynamic programming took about {d.time_ms / g.time_ms:,.0f}× as long as Greedy."
            else:
                speed = " Both ran in a similar amount of time on this small input."
            html(
                f'<div class="vp-verdict">With a budget of <b>{budget:,}</b>, Greedy removes <b>{g.total_risk_reduction:,.1f}</b> '
                f"risk and dynamic programming removes <b>{d.total_risk_reduction:,.1f}</b>. {line}{speed}</div>"
            )

            m1, m2, m3 = st.columns(3)
            m1.metric("Greedy risk reduction", f"{g.total_risk_reduction:,.1f}")
            m2.metric("Dynamic programming (optimal)", f"{d.total_risk_reduction:,.1f}")
            m3.metric("Optimality gap", f"{cmp.gap_pct:.2f}%", help="(DP − Greedy) / DP × 100. 0% means Greedy matched the best answer.")

            total_rr = sum(v.risk_reduction for v in report.valid)

            def col(r):
                return [
                    len(r.selected), r.total_cost, r.remaining_budget, round(r.utilization_pct, 1),
                    round(r.total_risk_reduction, 1),
                    round(r.total_risk_reduction / total_rr * 100, 1) if total_rr else 0.0,
                    round(r.time_ms, 4), round(r.peak_memory_kb, 1),
                ]

            st.subheader("Side by side")
            st.dataframe(
                pd.DataFrame(
                    {"Greedy": col(g), "Dynamic programming": col(d)},
                    index=[
                        "Fixes selected", "Total cost", "Remaining budget", "Budget used (%)",
                        "Risk reduction", "Share of all risk covered (%)",
                        "Time, median (ms)", "Peak memory (KB)",
                    ],
                ),
                width="stretch",
            )

            st.subheader("Where the picks differ")
            dc1, dc2, dc3 = st.columns(3)
            dc1.markdown("**Both pick**")
            dc1.write(", ".join(cmp.both) or "None")
            dc2.markdown("**Only Greedy picks**")
            dc2.write(", ".join(cmp.only_greedy) or "None")
            dc3.markdown("**Only dynamic programming picks**")
            dc3.write(", ".join(cmp.only_dp) or "None")

            if budget > 0 and (g.selected or d.selected):
                st.subheader("Budget at a glance")
                st.caption(
                    "Each block is one fix, sized by its cost. Hatched space is budget left unused. "
                    "Hover a block to see which fix it is."
                )
                html(
                    bar_row("Greedy", f"risk removed: {g.total_risk_reduction:,.1f}")
                    + budget_bar(g, "greedy", budget)
                    + bar_row("Dynamic programming", f"risk removed: {d.total_risk_reduction:,.1f}")
                    + budget_bar(d, "dp", budget)
                )

            st.subheader("Charts")
            colors = [GREEDY_COLOR, DP_COLOR]

            def chart_df(a, b):
                return pd.DataFrame({"Greedy": [a], "Dynamic programming": [b]}, index=[""])

            ch1, ch2 = st.columns(2)
            ch1.caption("Total risk reduction (higher is better)")
            ch1.bar_chart(chart_df(g.total_risk_reduction, d.total_risk_reduction), color=colors)
            ch2.caption("Total cost used")
            ch2.bar_chart(chart_df(g.total_cost, d.total_cost), color=colors)
            ch3, ch4 = st.columns(2)
            ch3.caption("Execution time in ms (lower is better)")
            ch3.bar_chart(chart_df(g.time_ms, d.time_ms), color=colors)
            ch4.caption("Peak memory in KB (lower is better)")
            ch4.bar_chart(chart_df(g.peak_memory_kb, d.peak_memory_kb), color=colors)

with tab_scale:
    st.subheader("How each method slows down as the problem grows")
    st.caption(
        "Greedy should grow slowly with the number of fixes (n). Dynamic programming also grows with the budget (B). "
        "These experiments use random data and take a few seconds to run."
    )
    seed_s = st.number_input("Random seed", 0, 10**6, 42, key="scale_seed")

    st.markdown("**Experiment A: more fixes, same budget**")
    fixed_b = st.number_input("Budget (B)", 10, 20000, 2000, step=100)
    if st.button("Run experiment A"):
        ns = [50, 100, 200, 400, 800, 1600]
        with st.spinner("Running experiment A..."):
            rows = scaling_experiment([(n, int(fixed_b)) for n in ns], int(seed_s))
        df = pd.DataFrame(rows).set_index("n")[["greedy_ms", "dp_ms"]]
        df.columns = ["Greedy (ms)", "Dynamic programming (ms)"]
        st.line_chart(df, color=[GREEDY_COLOR, DP_COLOR])
        st.dataframe(df, width="stretch")

    st.markdown("**Experiment B: bigger budget, same number of fixes**")
    fixed_n = st.number_input("Number of fixes (n)", 10, 3000, 300, step=50)
    if st.button("Run experiment B"):
        bs = [500, 1000, 2000, 4000, 8000, 16000]
        with st.spinner("Running experiment B..."):
            rows = scaling_experiment([(int(fixed_n), b) for b in bs], int(seed_s))
        df = pd.DataFrame(rows).set_index("budget")[["greedy_ms", "dp_ms"]]
        df.columns = ["Greedy (ms)", "Dynamic programming (ms)"]
        st.line_chart(df, color=[GREEDY_COLOR, DP_COLOR])
        st.dataframe(df, width="stretch")
        st.caption("A blank dynamic programming value means its table was too large and was skipped.")
