"""
tools/sleuth/report.py -- renders sleuth_report.md, findings grouped by
severity: structural break -> brand -> content/principle -> style nit
(candidate-tier findings render last within each category, clearly
marked as review-only, never counted toward the exit code).
"""
from __future__ import annotations

from datetime import datetime, timezone

from tools.sleuth.rules.finding import Category, Finding, Tier

CATEGORY_ORDER = [Category.STRUCTURAL, Category.BRAND, Category.CONTENT, Category.STYLE]
CATEGORY_LABELS = {
    Category.STRUCTURAL: "Structural breaks",
    Category.BRAND: "Brand violations",
    Category.CONTENT: "Content/principle violations",
    Category.STYLE: "Style nits (candidate tier -- review, not auto-fail)",
}


def render_report(
    findings: list[Finding],
    base_url: str,
    theme: str,
    page_count: int,
    known_gaps: list[str],
) -> str:
    deterministic = [f for f in findings if f.tier == Tier.DETERMINISTIC]
    candidate = [f for f in findings if f.tier == Tier.CANDIDATE]

    lines = [
        "# sleuth report",
        "",
        f"- Base URL: `{base_url}`",
        f"- Theme: `{theme}`",
        f"- Pages crawled: {page_count}",
        f"- Generated: {datetime.now(timezone.utc).isoformat()}",
        f"- **Deterministic (auto-fail) findings: {len(deterministic)}**",
        f"- Candidate (review) findings: {len(candidate)}",
        "",
    ]

    if known_gaps:
        lines.append("## Known gaps in this run")
        lines.append("")
        for gap in known_gaps:
            lines.append(f"- {gap}")
        lines.append("")

    for category in CATEGORY_ORDER:
        cat_deterministic = [f for f in deterministic if f.category == category]
        cat_candidate = [f for f in candidate if f.category == category]
        if not cat_deterministic and not cat_candidate:
            continue

        lines.append(f"## {CATEGORY_LABELS[category]}")
        lines.append("")

        if cat_deterministic:
            lines.append(f"### Deterministic ({len(cat_deterministic)}) -- exit code non-zero")
            lines.append("")
            for f in cat_deterministic:
                lines.append(f"- **[{f.rule_id}]** {f.message}")
                if f.url:
                    lines.append(f"  - URL: `{f.url}`")
                if f.detail:
                    lines.append(f"  - Detail: {f.detail}")
            lines.append("")

        if cat_candidate:
            lines.append(f"### Candidate -- flagged for review ({len(cat_candidate)})")
            lines.append("")
            for f in cat_candidate:
                lines.append(f"- **[{f.rule_id}]** {f.message}")
                if f.url:
                    lines.append(f"  - URL: `{f.url}`")
                if f.detail:
                    lines.append(f"  - Detail: {f.detail}")
            lines.append("")

    if not deterministic and not candidate:
        lines.append("No findings of any tier. Clean run.")
        lines.append("")

    return "\n".join(lines)
