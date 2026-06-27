"""
Monthly research refresh runner for PRV3.

Reads tracked-claims.json (domain-grouped format), calls the Anthropic API once per
domain with the web_search server tool enabled, and writes a dated report to
research/refresh-log/.

Tiers implemented:
  Tier 1: Auto-draft suggested direction for material findings — labeled
           'SUGGESTED DIRECTION (rewrite required, not drop-in)'
  Tier 2: Cross-reference used_in file list; flag any file with stale figure not listed
  Tier 3: Separate no-change results from action items (audit trail section)

Never modifies any file outside research/refresh-log/.

DEDICATED KEY REQUIREMENT: ANTHROPIC_API_KEY must be the dedicated PRV3_REFRESH key —
do not reuse a key tied to any other purpose. Set an $8/month spending limit on that
key in Console -> Billing before the first scheduled run. Reusing a key defeats the
spending isolation this design depends on.

Budget notification: if this script exits with code 1 (budget limit hit), GitHub
Actions sends its default failed-workflow email automatically — no additional
notification step is needed.
"""

import json
import os
import re
import sys
from datetime import date
from pathlib import Path

from anthropic import Anthropic

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
REFRESH_LOG_DIR = REPO_ROOT / "research" / "refresh-log"
TRACKED_CLAIMS_PATH = REFRESH_LOG_DIR / "tracked-claims.json"
PENDING_INTEGRATION_PATH = REFRESH_LOG_DIR / "pending-integration.json"
AUDIT_HISTORY_PATH = REFRESH_LOG_DIR / "audit-history.md"

# Roots scanned for Tier 2 citation cross-reference (files not listed in used_in)
TIER2_SCAN_ROOTS = [
    REPO_ROOT / "web" / "lib",
    REPO_ROOT / "web" / "data",
    REPO_ROOT / "web" / "content" / "book",
    REPO_ROOT / "research" / "seven-experiments",
]

DOMAIN_PROMPT_TEMPLATE = """\
You are running a scheduled research-currency check for Principal Resolution's PRV3
research base. Your job is to verify a set of claims against current, authoritative
sources.

Domain: {domain_label}

For EACH claim below, write a sub-section using the exact claim ID as a Markdown h3
header (### claim-id). Under each header, report:

1. CURRENT FINDING: What did you find, with source URL and date?
2. CHANGE ASSESSMENT: Choose exactly one — material change / minor update / no change.
   - Material change: a meaningfully different figure or a significant policy/mechanism shift
   - Minor update: same ballpark, rounding or methodology variation only
   - No change: consistent with the last-verified value within normal fluctuation
3. If the assessment is "material change", write NEEDS REVIEW on a line by itself.
4. If you cannot find a more current figure than what is already recorded, say so explicitly.

Apply PRV3 citation-audit rigor: check primary sources, distinguish sourced fact from
popularized estimate, and flag distorted headline figures (for example, a large total
skewed by a single outlier case). Do not speculate or fill gaps with guesses.

--- Claims ---
{claims_block}
--- End Claims ---
{file_section}
For any claim assessed as "material change" AND for which citing file excerpts are
provided above, draft suggested replacement text for each citing file. Format as:

PROPOSED EDITS:

File: [path]
BEFORE: [exact current text containing the old figure — copy verbatim]
SUGGESTED DIRECTION (rewrite required, not drop-in): [draft prose incorporating the
new figure — a starting point for human rewrite, not a clean replacement]

If no material change was found for a claim, omit the PROPOSED EDITS section for that
claim entirely.\
"""


def format_claims_block(claims: list) -> str:
    parts = []
    for c in claims:
        parts.append(
            f"Claim ID: {c['claim_id']}\n"
            f"Description: {c['description']}\n"
            f"Last verified: {c['last_verified']}\n"
            f"Expected source pattern: {c['source_pattern']}\n"
        )
    return "\n".join(parts)


def read_file_excerpt(path_str: str) -> str:
    """Read up to 2500 chars from a repo file. Returns an error string if unavailable."""
    readable_exts = {".ts", ".tsx", ".md", ".html", ".json"}
    if Path(path_str).suffix not in readable_exts:
        return f"[Skipped — non-text extension: {path_str}]"
    fp = REPO_ROOT / path_str
    if not fp.exists():
        return f"[File not found: {path_str}]"
    try:
        text = fp.read_text(encoding="utf-8")
        return text[:2500] if len(text) > 2500 else text
    except Exception as exc:
        return f"[Could not read: {exc}]"


def format_file_section(excerpts: dict) -> str:
    if not excerpts:
        return ""
    parts = ["\n\nCurrent content excerpts from citing files (for suggested-direction drafting):"]
    for path_str, content in excerpts.items():
        parts.append(f"\n--- {path_str} ---\n{content}\n")
    return "".join(parts)


def parse_domain_response(text: str, claims: list) -> list:
    """Split a combined domain response into per-claim sections by ### headers."""
    claim_ids = [c["claim_id"] for c in claims]
    sections = re.split(r"\n(?=###\s)", "\n" + text)
    section_map: dict = {}
    for section in sections:
        stripped = section.strip()
        for cid in claim_ids:
            if stripped.startswith(f"### {cid}"):
                section_map[cid] = stripped
                break

    results = []
    for claim in claims:
        cid = claim["claim_id"]
        section_text = section_map.get(
            cid, f"[No section found for {cid} in domain response — check API output]"
        )
        needs_review = "NEEDS REVIEW" in section_text.upper()
        results.append({
            "claim_id": cid,
            "text": section_text,
            "needs_review": needs_review,
            "error": False,
            "is_budget_error": False,
            "unlisted_hits": [],
        })
    return results


def check_domain(client: Anthropic, domain: dict) -> dict:
    """One API call per domain. Returns per-claim parsed results."""
    claims = domain["claims"]
    domain_id = domain["domain_id"]

    all_used_in: dict = {}
    for claim in claims:
        for path_str in claim.get("used_in", []):
            if path_str not in all_used_in:
                all_used_in[path_str] = read_file_excerpt(path_str)

    prompt = DOMAIN_PROMPT_TEMPLATE.format(
        domain_label=domain["domain_label"],
        claims_block=format_claims_block(claims),
        file_section=format_file_section(all_used_in),
    )

    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4000,
            tools=[{"type": "web_search_20260209", "name": "web_search"}],
            messages=[{"role": "user", "content": prompt}],
        )
        text = "\n".join(
            block.text
            for block in response.content
            if hasattr(block, "text") and block.type == "text"
        )
    except Exception as exc:
        err_str = str(exc)
        is_budget = any(
            kw in err_str.lower()
            for kw in ["429", "rate_limit", "billing", "budget", "quota", "credit"]
        )
        claim_results = [
            {
                "claim_id": c["claim_id"],
                "text": f"[API ERROR: {exc}]",
                "needs_review": False,
                "error": True,
                "is_budget_error": is_budget,
                "unlisted_hits": [],
            }
            for c in claims
        ]
        return {
            "domain_id": domain_id,
            "domain_label": domain["domain_label"],
            "claim_results": claim_results,
            "error": True,
            "is_budget_error": is_budget,
        }

    return {
        "domain_id": domain_id,
        "domain_label": domain["domain_label"],
        "claim_results": parse_domain_response(text, claims),
        "error": False,
        "is_budget_error": False,
    }


def scan_for_unlisted_citations(claim: dict, used_in_set: set) -> list:
    """Tier 2: find files containing search_terms that are not in used_in_set."""
    search_terms = claim.get("search_terms", [])
    if not search_terms:
        return []

    candidate_files: list = []
    for root in TIER2_SCAN_ROOTS:
        if not root.exists():
            continue
        if root.is_file():
            candidate_files.append(root)
        else:
            for ext in ("*.ts", "*.tsx", "*.md", "*.html"):
                candidate_files.extend(root.rglob(ext))

    unlisted = []
    for fp in candidate_files:
        rel = fp.relative_to(REPO_ROOT).as_posix()
        if rel in used_in_set:
            continue
        try:
            text = fp.read_text(encoding="utf-8", errors="replace")
            for term in search_terms:
                if term.lower() in text.lower():
                    unlisted.append(f"{rel} (found: '{term}')")
                    break
        except Exception:
            pass

    return unlisted


def load_pending() -> list:
    if PENDING_INTEGRATION_PATH.exists():
        with open(PENDING_INTEGRATION_PATH, encoding="utf-8") as f:
            return json.load(f)
    return []


def save_pending(entries: list) -> None:
    PENDING_INTEGRATION_PATH.write_text(
        json.dumps(entries, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def append_audit_history(today: str, total_claims: int) -> None:
    """Append a single dated line to audit-history.md for a no-change month."""
    line = f"- {today}: {total_claims} claims checked — no material changes\n"
    with open(AUDIT_HISTORY_PATH, "a", encoding="utf-8") as f:
        f.write(line)


def write_report(
    today: str,
    all_claim_results: list,
    budget_hit: bool,
    budget_hit_at_domain: int,
    total_domains: int,
    total_claims: int,
) -> Path:
    out_path = REFRESH_LOG_DIR / f"{today}.md"

    action_items = [r for r in all_claim_results if r.get("needs_review")]
    no_change = [r for r in all_claim_results if not r.get("needs_review") and not r.get("error")]
    errors = [r for r in all_claim_results if r.get("error")]

    with open(out_path, "w", encoding="utf-8") as f:
        if budget_hit:
            f.write(f"# Research Refresh — {today} — BUDGET LIMIT REACHED\n\n")
            f.write(
                f"Budget limit hit after domain {budget_hit_at_domain + 1} of {total_domains}. "
                "Remaining domains were not checked. "
                "Check the Anthropic Console billing page and raise the spending limit "
                "before the next scheduled run.\n\n"
            )
        else:
            f.write(f"# Research Refresh — {today}\n\n")

        f.write(
            "Automated monthly check. Human review required before any citation or content "
            "change. See `research/refresh-log/tracked-claims.json` for claim definitions.\n\n"
        )

        # Section 1: Action required (Tier 3 — appears first)
        f.write(f"## Requires Review ({len(action_items)})\n\n")
        if action_items:
            for r in action_items:
                f.write(f"### {r['claim_id']}\n\n")
                f.write(r["text"].strip())
                if r.get("unlisted_hits"):
                    f.write(
                        "\n\n**Tier 2 — Found in files not listed in used_in registry "
                        "(registry may need updating):**\n"
                    )
                    for hit in r["unlisted_hits"]:
                        f.write(f"- {hit}\n")
                f.write("\n\n---\n\n")
        else:
            f.write("No material changes detected this month.\n\n")

        # Section 2: Errors (only if any)
        if errors:
            f.write(f"## Errors — Claims Not Checked ({len(errors)})\n\n")
            for r in errors:
                f.write(f"### {r['claim_id']}\n\n{r['text'].strip()}\n\n---\n\n")

        # Section 3: Audit trail — no change (Tier 3)
        f.write(
            f"## Audit Trail — No Change Detected ({len(no_change)})\n\n"
            "The following claims were verified this month and returned no material change. "
            "No action required. Included for audit trail and job-health confirmation.\n\n"
        )
        for r in no_change:
            f.write(f"### {r['claim_id']}\n\n")
            f.write(r["text"].strip())
            if r.get("unlisted_hits"):
                f.write(
                    "\n\n**Tier 2 note — Found in files not listed in used_in "
                    "(registry may need updating):**\n"
                )
                for hit in r["unlisted_hits"]:
                    f.write(f"- {hit}\n")
            f.write("\n\n---\n\n")

    return out_path


def main() -> None:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        sys.exit(
            "ERROR: ANTHROPIC_API_KEY not set. "
            "This must be the dedicated PRV3_REFRESH key — see CLAUDE.md Step 3a provisioning note."
        )

    if not TRACKED_CLAIMS_PATH.exists():
        sys.exit(f"ERROR: Claims registry not found at {TRACKED_CLAIMS_PATH}")

    with open(TRACKED_CLAIMS_PATH, encoding="utf-8") as f:
        domains = json.load(f)

    total_claims = sum(len(d["claims"]) for d in domains)
    client = Anthropic(api_key=api_key)
    today = date.today().isoformat()
    all_claim_results: list = []
    budget_hit = False
    budget_hit_at_domain = 0

    for i, domain in enumerate(domains):
        claim_count = len(domain["claims"])
        print(
            f"Checking domain {i + 1}/{len(domains)}: {domain['domain_id']} "
            f"({claim_count} claim{'s' if claim_count != 1 else ''}) ...",
            flush=True,
        )

        domain_result = check_domain(client, domain)

        if domain_result["is_budget_error"]:
            budget_hit = True
            budget_hit_at_domain = i
            all_claim_results.extend(domain_result["claim_results"])
            for j in range(i + 1, len(domains)):
                for c in domains[j]["claims"]:
                    all_claim_results.append({
                        "claim_id": c["claim_id"],
                        "text": "[UNCHECKED — budget limit reached before this domain was processed]",
                        "needs_review": False,
                        "error": True,
                        "is_budget_error": True,
                        "unlisted_hits": [],
                    })
            break

        # Tier 2: per-claim scan, sharing the full domain used_in set
        domain_used_in_set: set = set()
        for c in domain["claims"]:
            domain_used_in_set.update(c.get("used_in", []))

        for claim_result in domain_result["claim_results"]:
            if not claim_result["error"]:
                claim = next(
                    c for c in domain["claims"] if c["claim_id"] == claim_result["claim_id"]
                )
                claim_result["unlisted_hits"] = scan_for_unlisted_citations(
                    claim, domain_used_in_set
                )

        all_claim_results.extend(domain_result["claim_results"])

    # Update pending-integration.json for material findings
    pending = load_pending()
    for r in all_claim_results:
        if r.get("needs_review") and not r.get("error"):
            target_files: list = []
            for d in domains:
                for c in d["claims"]:
                    if c["claim_id"] == r["claim_id"]:
                        target_files = c.get("used_in", [])
                        break
            pending.append({
                "claim_id": r["claim_id"],
                "refresh_report": f"research/refresh-log/{today}.md",
                "proposed_at": today,
                "pr_merged_at": None,
                "status": "proposed",
                "proposed_edit_summary": (
                    f"Material change detected. See research/refresh-log/{today}.md "
                    "for current finding and suggested direction."
                ),
                "target_files": target_files,
                "applied_commit": None,
                "rejected_reason": None,
                "revisit_by_date": None,
                "deferred_reason": None,
            })
    save_pending(pending)

    action_count = sum(1 for r in all_claim_results if r.get("needs_review"))
    hard_error_count = sum(
        1 for r in all_claim_results if r.get("error") and not r.get("is_budget_error")
    )
    needs_pr = bool(action_count or hard_error_count or budget_hit)

    out_path = write_report(
        today, all_claim_results, budget_hit, budget_hit_at_domain, len(domains), total_claims
    )
    print(f"Report written: {out_path}", flush=True)

    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        prefix = "BUDGET LIMIT — " if budget_hit else ""
        with open(github_output, "a", encoding="utf-8") as gf:
            gf.write(f"needs_pr={'true' if needs_pr else 'false'}\n")
            gf.write(f"pr_title_prefix={prefix}\n")

    if not needs_pr:
        append_audit_history(today, total_claims)
        print(f"No material changes — audit entry appended to {AUDIT_HISTORY_PATH}", flush=True)

    if budget_hit:
        print(
            f"\nWARNING: BUDGET LIMIT REACHED — "
            f"domain {budget_hit_at_domain + 1}/{len(domains)} was the last checked. "
            "Raise the spending limit in Anthropic Console before next run.",
            flush=True,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
