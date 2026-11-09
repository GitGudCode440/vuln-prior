import itertools
import random

import pytest

from core.benchmark import compare
from core.generator import generate_synthetic
from core.greedy import greedy_select
from core.knapsack import TableTooLargeError, knapsack_select
from core.models import Vulnerability
from core.validator import load_csv, validate_records


def V(id, cost, rr):
    return Vulnerability(id=id, name=id, severity=5.0, asset_importance=3, cost=cost, risk_reduction=rr)


def brute_force(vulns, budget):
    best = 0.0
    for r in range(len(vulns) + 1):
        for combo in itertools.combinations(vulns, r):
            if sum(v.cost for v in combo) <= budget:
                best = max(best, sum(v.risk_reduction for v in combo))
    return best


def load_edge(name):
    recs, _ = load_csv(f"data/edge_cases/{name}.csv")
    return validate_records(recs).valid


# ---- the classic example where greedy is suboptimal ----
def test_greedy_fails_example():
    items = [V("A", 10, 60), V("B", 20, 100), V("C", 30, 120)]
    g, d = greedy_select(items, 50), knapsack_select(items, 50)
    assert g.total_risk_reduction == 160 and set(g.selected_ids) == {"A", "B"}
    assert d.total_risk_reduction == 220 and set(d.selected_ids) == {"B", "C"}


def test_greedy_fails_csv():
    items = load_edge("greedy_fails")
    c = compare(items, 50, repeats=1)
    assert c.dp.total_risk_reduction > c.greedy.total_risk_reduction
    assert c.gap_pct == pytest.approx((220 - 160) / 220 * 100)
    assert c.only_dp == ["C"] and c.only_greedy == ["A"]


# ---- invariants on random inputs ----
@pytest.mark.parametrize("seed", range(40))
def test_random_small_inputs(seed):
    rng = random.Random(seed)
    items = [V(f"i{k}", rng.randint(0, 15), rng.randint(0, 40)) for k in range(rng.randint(0, 10))]
    budget = rng.randint(0, 60)
    g, d = greedy_select(items, budget), knapsack_select(items, budget)
    assert g.total_cost <= budget and d.total_cost <= budget
    assert d.total_risk_reduction == pytest.approx(brute_force(items, budget))
    assert d.total_risk_reduction >= g.total_risk_reduction - 1e-9
    assert len(set(g.selected_ids)) == len(g.selected_ids)
    assert len(set(d.selected_ids)) == len(d.selected_ids)


def test_synthetic_dp_beats_or_ties_greedy():
    data = generate_synthetic(200, seed=7)
    budget = 1500
    g, d = greedy_select(data, budget), knapsack_select(data, budget)
    assert d.total_cost <= budget and g.total_cost <= budget
    assert d.total_risk_reduction >= g.total_risk_reduction - 1e-9


# ---- edge cases ----
@pytest.mark.parametrize("algo", [greedy_select, knapsack_select])
def test_zero_budget(algo):
    r = algo(load_edge("ties"), 0)
    assert r.selected == [] and r.total_cost == 0 and r.utilization_pct == 0.0


@pytest.mark.parametrize("algo", [greedy_select, knapsack_select])
def test_zero_budget_still_takes_free_fixes(algo):
    r = algo(load_edge("free_fixes"), 0)
    assert set(r.selected_ids) == {"F1", "F2"} and r.total_risk_reduction == 25


@pytest.mark.parametrize("algo", [greedy_select, knapsack_select])
def test_empty_input(algo):
    r = algo([], 100)
    assert r.selected == [] and r.total_risk_reduction == 0


@pytest.mark.parametrize("algo", [greedy_select, knapsack_select])
def test_all_unaffordable(algo):
    r = algo(load_edge("all_unaffordable"), 50)
    assert r.selected == [] and r.remaining_budget == 50


@pytest.mark.parametrize("algo", [greedy_select, knapsack_select])
def test_free_fixes(algo):
    r = algo(load_edge("free_fixes"), 15)
    assert set(r.selected_ids) == {"F1", "F2", "F3", "F4"}  # F5 has no benefit
    assert r.total_cost == 15 and r.total_risk_reduction == 57


def test_ties_are_deterministic_and_equal_value():
    items = load_edge("ties")
    g1, g2 = greedy_select(items, 30), greedy_select(list(reversed(items)), 30)
    assert g1.selected_ids == g2.selected_ids or set(g1.selected_ids) == set(g2.selected_ids)
    assert g1.total_risk_reduction == knapsack_select(items, 30).total_risk_reduction == 60


def test_budget_exactly_equals_total_cost():
    items = [V("a", 5, 10), V("b", 5, 10)]
    assert knapsack_select(items, 10).total_cost == 10
    assert greedy_select(items, 10).total_cost == 10


def test_bad_budget_raises():
    for bad in (-1, 2.5, True):
        with pytest.raises(ValueError):
            greedy_select([], bad)
        with pytest.raises(ValueError):
            knapsack_select([], bad)


def test_dp_table_limit():
    items = [V(f"i{k}", 100, 5) for k in range(50)]
    with pytest.raises(TableTooLargeError):
        knapsack_select(items, 10_000, max_cells=1000)
    c = compare(items, 10_000, repeats=1)  # default limit is fine here
    assert c.dp is not None
