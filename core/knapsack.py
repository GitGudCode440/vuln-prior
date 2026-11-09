"""Optimal 0/1 knapsack via dynamic programming (full table + backtracking)."""
from __future__ import annotations

from typing import List

import numpy as np

from .models import AlgorithmResult, Vulnerability, check_budget

# 25M float64 cells ~ 200 MB. Above this the app warns instead of freezing.
DEFAULT_MAX_CELLS = 25_000_000


class TableTooLargeError(Exception):
    def __init__(self, n: int, capacity: int, cells: int, limit: int):
        self.n, self.capacity, self.cells, self.limit = n, capacity, cells, limit
        super().__init__(
            f"DP table would need {cells:,} cells (n={n:,}, budget={capacity:,}); "
            f"limit is {limit:,}. Reduce the budget or number of fixes."
        )


def estimate_cells(n: int, budget: int) -> int:
    return (n + 1) * (budget + 1)


def knapsack_select(
    vulns: List[Vulnerability], budget: int, max_cells: int = DEFAULT_MAX_CELLS
) -> AlgorithmResult:
    """O(nB) time and O(nB) space.

    dp[i][w] = best risk reduction using the first i fixes with budget w
        cost_i > w : dp[i][w] = dp[i-1][w]
        otherwise  : dp[i][w] = max(dp[i-1][w], dp[i-1][w-cost_i] + rr_i)
    Backtrack from dp[n][cap]: if dp[i][w] != dp[i-1][w], fix i was chosen.
    """
    check_budget(budget)

    items = [v for v in vulns if v.cost <= budget and v.risk_reduction > 0]
    if not items:
        return AlgorithmResult.from_selection("Dynamic Programming", [], budget)

    # No need for columns beyond the total cost of all candidates.
    cap = min(budget, sum(v.cost for v in items))
    n = len(items)
    cells = estimate_cells(n, cap)
    if cells > max_cells:
        raise TableTooLargeError(n, cap, cells, max_cells)

    dp = np.zeros((n + 1, cap + 1), dtype=np.float64)
    for i, v in enumerate(items, start=1):
        prev, cur = dp[i - 1], dp[i]
        cur[:] = prev
        c = v.cost  # c <= cap is guaranteed by construction (also works for c = 0)
        cur[c:] = np.maximum(prev[c:], prev[: cap + 1 - c] + v.risk_reduction)

    chosen: List[Vulnerability] = []
    w = cap
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i - 1][w]:
            chosen.append(items[i - 1])
            w -= items[i - 1].cost
    chosen.reverse()

    return AlgorithmResult.from_selection("Dynamic Programming", chosen, budget)