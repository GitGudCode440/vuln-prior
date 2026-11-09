"""Synthetic data generator (reproducible via seed)."""
from __future__ import annotations

import random
from typing import List

from .models import Vulnerability


def generate_synthetic(n: int, seed: int = 42) -> List[Vulnerability]:
    """Random but realistic fixes.

    cost ~ loosely correlated with severity (critical fixes tend to cost more)
    risk_reduction = severity x importance x effectiveness (0.5-1.0), 1 decimal
    """
    rng = random.Random(seed)
    out: List[Vulnerability] = []
    for i in range(1, n + 1):
        severity = round(rng.uniform(0, 10), 1)
        importance = rng.randint(1, 5)
        cost = max(1, round(rng.uniform(0.5, 1.5) * (severity * 5 + 10)))
        effectiveness = rng.uniform(0.5, 1.0)
        rr = round(severity * importance * effectiveness, 1)
        out.append(
            Vulnerability(
                id=f"S{i:04d}",
                name=f"Synthetic fix {i}",
                severity=severity,
                asset_importance=importance,
                cost=cost,
                risk_reduction=rr,
            )
        )
    return out


def suggest_budget(vulns: List[Vulnerability], fraction: float = 0.4) -> int:
    """A sensible default budget: a fraction of the total cost of all fixes."""
    return int(sum(v.cost for v in vulns) * fraction)
