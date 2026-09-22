"""
tools/sleuth/rules/finding.py -- the shared shape every rule engine
returns. Two tiers, per the build brief: DETERMINISTIC findings make
sleuth exit non-zero (a real break, auto-fail); CANDIDATE findings are
logged in sleuth_report.md for human/AI review and never affect the
exit code, however many there are.

Severity groups (structural break -> brand -> content/principle ->
style nit) are a presentation concern, not a data-model one -- see
tools/sleuth/report.py's GROUP_ORDER, which sorts on `category`.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Tier(str, Enum):
    DETERMINISTIC = "deterministic"
    CANDIDATE = "candidate"


class Category(str, Enum):
    STRUCTURAL = "structural"
    BRAND = "brand"
    CONTENT = "content"
    STYLE = "style"


@dataclass
class Finding:
    tier: Tier
    category: Category
    rule_id: str
    message: str
    url: str = ""
    detail: str = ""

    def to_dict(self) -> dict:
        return {
            "tier": self.tier.value,
            "category": self.category.value,
            "rule_id": self.rule_id,
            "message": self.message,
            "url": self.url,
            "detail": self.detail,
        }
