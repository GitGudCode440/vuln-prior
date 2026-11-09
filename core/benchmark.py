"""Timing / memory measurement and greedy-vs-DP comparison."""
from __future__ import annotations

import statistics
import time
import tracemalloc
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

from .generator import generate_synthetic
from .greedy import greedy_select
from .knapsack import TableTooLargeError, knapsack_select
from .models import AlgorithmResult, Vulnerability

Algo = Callable[[List[Vulnerability], int], AlgorithmResult]


def run_timed(
    fn: Algo,
    vulns: List[Vulnerability],
    budget: int,
    repeats: int = 5,
    measure_memory: bool = True,
) -> AlgorithmResult:
    """Median wall time over `repeats` runs; peak memory from one extra run
    (separate so tracemalloc overhead does not distort the timings)."""
    times: List[float] = []
    result = None
    for _ in range(max(1, repeats)):
        t0 = time.perf_counter()
        result = fn(vulns, budget)
        times.append((time.perf_counter() - t0) * 1000.0)
    result.time_ms = statistics.median(times)

    if measure_memory:
        already = tracemalloc.is_tracing()
        if already:
            tracemalloc.reset_peak()
        else:
            tracemalloc.start()
        fn(vulns, budget)
        _, peak = tracemalloc.get_traced_memory()
        if not already:
            tracemalloc.stop()
        result.peak_memory_kb = peak / 1024.0
    return result


@dataclass
class Comparison:
    greedy: AlgorithmResult
    dp: Optional[AlgorithmResult]
    dp_error: Optional[str] = None
    gap_pct: float = 0.0               # (DP - Greedy) / DP * 100
    only_greedy: List[str] = field(default_factory=list)
    only_dp: List[str] = field(default_factory=list)
    both: List[str] = field(default_factory=list)


def compare(vulns: List[Vulnerability], budget: int, repeats: int = 5) -> Comparison:
    greedy = run_timed(greedy_select, vulns, budget, repeats)
    try:
        dp = run_timed(knapsack_select, vulns, budget, repeats)
    except TableTooLargeError as e:
        return Comparison(greedy=greedy, dp=None, dp_error=str(e))

    g_ids, d_ids = set(greedy.selected_ids), set(dp.selected_ids)
    gap = 0.0
    if dp.total_risk_reduction > 0:
        gap = (dp.total_risk_reduction - greedy.total_risk_reduction) / dp.total_risk_reduction * 100
    return Comparison(
        greedy=greedy,
        dp=dp,
        gap_pct=max(gap, 0.0),
        only_greedy=sorted(g_ids - d_ids),
        only_dp=sorted(d_ids - g_ids),
        both=sorted(g_ids & d_ids),
    )


def scaling_experiment(
    configs: List[tuple], seed: int = 42, repeats: int = 3
) -> List[Dict[str, Optional[float]]]:
    """For each (n, B): time both algorithms on synthetic data (no memory run).
    DP time is None when the table would exceed the size limit."""
    rows: List[Dict[str, Optional[float]]] = []
    for n, budget in configs:
        data = generate_synthetic(n, seed)
        g = run_timed(greedy_select, data, budget, repeats, measure_memory=False)
        try:
            d = run_timed(knapsack_select, data, budget, repeats, measure_memory=False)
            dp_ms = d.time_ms
        except TableTooLargeError:
            dp_ms = None
        rows.append({"n": n, "budget": budget, "greedy_ms": g.time_ms, "dp_ms": dp_ms})
    return rows
