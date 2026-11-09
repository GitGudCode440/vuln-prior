"""Data classes shared across VulnPrior."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

REQUIRED_FIELDS = (
    "id",
    "name",
    "severity",          # CVSS-style score, 0-10
    "asset_importance",  # integer 1-5
    "cost",              # non-negative integer (e.g. engineer-hours)
    "risk_reduction",    # non-negative number
)


@dataclass(frozen=True)
class Vulnerability:
    """One candidate remediation fix (a validated record)."""

    id: str
    name: str
    severity: float
    asset_importance: int
    cost: int
    risk_reduction: float

    @property
    def risk_score(self) -> float:
        """Reference score (severity x importance). Display only."""
        return self.severity * self.asset_importance

    @property
    def ratio(self) -> float:
        """Risk reduction per unit cost (inf for free fixes with benefit)."""
        if self.cost == 0:
            return float("inf") if self.risk_reduction > 0 else 0.0
        return self.risk_reduction / self.cost


@dataclass
class RejectedRecord:
    """A raw record that failed validation, with human-readable reasons."""

    row_number: int  # 1-based position among the data rows
    raw: Dict[str, Any]
    reasons: List[str]


@dataclass
class ValidationReport:
    valid: List[Vulnerability] = field(default_factory=list)
    rejected: List[RejectedRecord] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.valid) + len(self.rejected)


@dataclass
class AlgorithmResult:
    """Outcome of running one algorithm on one dataset and budget."""

    algorithm: str
    selected: List[Vulnerability]
    budget: int
    total_cost: int
    total_risk_reduction: float
    remaining_budget: int
    utilization_pct: float
    time_ms: float = 0.0
    peak_memory_kb: float = 0.0

    @property
    def selected_ids(self) -> List[str]:
        return [v.id for v in self.selected]

    @classmethod
    def from_selection(
        cls, algorithm: str, selected: List[Vulnerability], budget: int
    ) -> "AlgorithmResult":
        total_cost = sum(v.cost for v in selected)
        total_rr = sum(v.risk_reduction for v in selected)
        util = (total_cost / budget * 100.0) if budget > 0 else 0.0
        return cls(
            algorithm=algorithm,
            selected=list(selected),
            budget=budget,
            total_cost=total_cost,
            total_risk_reduction=total_rr,
            remaining_budget=budget - total_cost,
            utilization_pct=util,
        )


def check_budget(budget: int) -> None:
    """Shared guard used by both algorithms."""
    if isinstance(budget, bool) or not isinstance(budget, int) or budget < 0:
        raise ValueError("Budget must be a non-negative integer.")