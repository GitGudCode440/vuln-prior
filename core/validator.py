"""Input validation: invalid or incomplete records are rejected with reasons."""
from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

from .models import REQUIRED_FIELDS, RejectedRecord, ValidationReport, Vulnerability


# ---------- small parsing helpers ----------
def _is_blank(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip() == ""
    if isinstance(value, float) and math.isnan(value):
        return True
    return False


def _parse_number(value: Any) -> float:
    """Parse to a finite float or raise ValueError."""
    if isinstance(value, bool):
        raise ValueError("boolean is not a number")
    x = float(value) if isinstance(value, (int, float)) else float(str(value).strip())
    if not math.isfinite(x):
        raise ValueError("not finite")
    return x


def _parse_integer(value: Any) -> int:
    """Accepts 3, '3' and 3.0 / '3.0' (common in CSVs); rejects 3.5."""
    x = _parse_number(value)
    if not x.is_integer():
        raise ValueError("not an integer")
    return int(x)


# ---------- budget ----------
def parse_budget(value: Any) -> int:
    """Return the budget as a non-negative int, or raise ValueError."""
    try:
        budget = _parse_integer(value)
    except (ValueError, TypeError):
        raise ValueError("Budget must be a whole number.")
    if budget < 0:
        raise ValueError("Budget must be non-negative.")
    return budget


# ---------- single record ----------
def validate_record(raw: Dict[str, Any]) -> Tuple[Optional[Vulnerability], List[str]]:
    """Validate one raw record. Returns (Vulnerability or None, reasons)."""
    reasons: List[str] = []

    missing = [f for f in REQUIRED_FIELDS if _is_blank(raw.get(f))]
    for f in missing:
        reasons.append(f"missing value for '{f}'")

    def present(f: str) -> bool:
        return f not in missing

    severity = importance = cost = rr = None

    if present("severity"):
        try:
            severity = _parse_number(raw["severity"])
            if not 0 <= severity <= 10:
                reasons.append("severity must be between 0 and 10")
        except (ValueError, TypeError):
            reasons.append("severity must be a number")

    if present("asset_importance"):
        try:
            importance = _parse_integer(raw["asset_importance"])
            if not 1 <= importance <= 5:
                reasons.append("asset_importance must be an integer from 1 to 5")
        except (ValueError, TypeError):
            reasons.append("asset_importance must be an integer from 1 to 5")

    if present("cost"):
        try:
            cost = _parse_integer(raw["cost"])
            if cost < 0:
                reasons.append("cost must be non-negative")
        except (ValueError, TypeError):
            reasons.append("cost must be a whole number")

    if present("risk_reduction"):
        try:
            rr = _parse_number(raw["risk_reduction"])
            if rr < 0:
                reasons.append("risk_reduction must be non-negative")
        except (ValueError, TypeError):
            reasons.append("risk_reduction must be a number")

    if reasons:
        return None, reasons

    return (
        Vulnerability(
            id=str(raw["id"]).strip(),
            name=str(raw["name"]).strip(),
            severity=severity,
            asset_importance=importance,
            cost=cost,
            risk_reduction=rr,
        ),
        [],
    )


# ---------- many records ----------
def validate_records(records: List[Dict[str, Any]]) -> ValidationReport:
    """Validate all records; the first occurrence of a duplicate id wins."""
    report = ValidationReport()
    first_seen: Dict[str, int] = {}

    for idx, raw in enumerate(records, start=1):
        vuln, reasons = validate_record(raw)
        if vuln is not None:
            if vuln.id in first_seen:
                reasons = [f"duplicate id '{vuln.id}' (first used in row {first_seen[vuln.id]})"]
                vuln = None
            else:
                first_seen[vuln.id] = idx
        if vuln is None:
            report.rejected.append(RejectedRecord(idx, dict(raw), reasons))
        else:
            report.valid.append(vuln)
    return report


# ---------- CSV loading ----------
def load_csv(source) -> Tuple[List[Dict[str, Any]], List[str]]:
    """Read a CSV (path or file-like) as text. Returns (records, columns).

    An empty file yields ([], []) instead of an error.
    """
    try:
        df = pd.read_csv(source, dtype=str, keep_default_na=False)
    except pd.errors.EmptyDataError:
        return [], []
    df.columns = [str(c).strip().lower() for c in df.columns]
    return df.to_dict(orient="records"), list(df.columns)


def missing_columns(columns: List[str]) -> List[str]:
    """Required columns absent from the file header."""
    return [f for f in REQUIRED_FIELDS if f not in columns]