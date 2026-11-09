"""Greedy heuristic: pick fixes by risk-reduction-per-cost ratio."""
from __future__ import annotations

from typing import List

from .models import AlgorithmResult, Vulnerability, check_budget


def greedy_select(vulns: List[Vulnerability], budget: int) -> AlgorithmResult:
    """O(n log n) time (sorting), O(n) space.

    1. Drop unaffordable fixes (cost > budget) and fixes with no benefit.
    2. Sort by ratio desc; ties -> higher risk_reduction, lower cost, id.
       Free fixes (cost 0, benefit > 0) have an infinite ratio => taken first.
    3. Walk the list; take a fix if it fits, otherwise skip it and continue.
    """
    check_budget(budget)

    candidates = [v for v in vulns if v.cost <= budget and v.risk_reduction > 0]
    ordered = sorted(
        candidates, key=lambda v: (-v.ratio, -v.risk_reduction, v.cost, v.id)
    )

    remaining = budget
    chosen: List[Vulnerability] = []
    for v in ordered:
        if v.cost <= remaining:
            chosen.append(v)
            remaining -= v.cost

    return AlgorithmResult.from_selection("Greedy", chosen, budget)