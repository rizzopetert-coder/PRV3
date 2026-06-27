"""
Monthly research refresh runner for PRV3.

Reads tracked-claims.json, calls the Anthropic API once per claim with the
web_search server tool enabled, and writes a dated report to research/refresh-log/.

Tiers implemented:
  Tier 1: Auto-draft proposed edits for material findings (in PR report, never auto-applied)
  Tier 2: Cross-reference used_in file list; flag any file with stale figure not listed
  Tier 3: Separate no-change results from action items (audit trail section)

Never modifies any file outside research/refresh-log/.

DEDICATED KEY REQUIREMENT: This script uses the ANTHROPIC_API_KEY environment variable.
That key must be a dedicated PRV3_REFRESH key — do not reuse a key tied to any other purpose.
Set an $8/month spending limit on that key in Console -> Billing before the first scheduled run.
"""

import json
import os
import sys
from datetime import date
from pathlib import Path

from anthropic import Anthropic

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
REFRESH_LOG_DIR = REPO_ROOT / "research" / "refresh-log"
TRACKED_CLAIMS_PATH = REFRESH_LOG_DIR / "tracked-claims.json"
PENDING_INTEGRATION_PATH = REFRESH_LOG_DIR / "pending-integration.json"

# Roots scanned for Tier 2 citation cross-reference (files not listed in used_in)
TIER2_SCAN_ROOTS = [
    REPO_ROOT / "web" / "lib",
    REPO_ROOT / "web" / "data",
    REPO_ROOT / "web" / "content" / "book",
    REPO_ROOT / "research" / "seven-experiments",
]

PROMPT_TEMPLATE = """\
You are running a scheduled research-currency check for Principal Resolution's PRV3 research
base. Your job is to verify one specific claim against current, authoritative sources.

Claim ID: {claim_id}
Description: {description}
Last verified: {last_verified}
Expected source pattern: {source_pattern}

Search for the current, most authoritative figure or status for this claim. Then report:

1. CURRENT FINDING: What did you find, with source URL and date?
2. CHANGE ASSESSMENT: Choose exactly one — material change / minor update / no change.
   - Material change: a meaningfully different figure or a significant policy/mechanism shift
   - Minor update: same ballpark, rounding or methodology variation only
   - No change: consistent with the last-verified value within normal fluctuation
3. If the assessment is "material change", write NEEDS REVIEW on a line by itself.
4. If you cannot find a more current figure than what is already recorded, say so explicitly.

Apply the same rigor as PRV3's existing citation audit: check primary sources, distinguish
sourced fact from popularized estimate, and flag any distorted headline figures (for example,
a large total skewed by a single outlier case). Do not speculate or fill gaps with guesses.
{file_section}
If the assessment is "material change" AND citing file excerpts are provided above, draft exact
proposed replacement text for each file. Format as:

PROPOSED EDITS:

File: [path]
BEFORE: [exact current text containing the old figure — copy verbatim]
AFTER: [proposed replacement with the new figure, preserving surrounding context]

If no material change was found, omit the PROPOSED EDITS section entirely.\
"""


def read_used_in_excerpts(used_in_paths: list) -> dict:
    """Read file excerpts for Tier 1 diff drafting. Cap each at 2500 chars."""
    excerpts = {}
    readable_exts = {".ts", ".tsx", ".md", ".html", ".json"}
    for path_str in used_in_paths:
        if not isinstance(path_str, str):
            continue
        if Path(path_str).suffix not in readable_exts:
            continue
        fp = REPO_ROOT / path_str
        if fp.exists():
            try:
                text = fp.read_text(encoding="utf-8")
                excerpts[path_str] = text[:2500] if len(text) > 2500 else text
            except Exception as exc:
                excerpts[path_str] = f"[Could not read: {exc}]"
        else:
            excerpts[path_str] = f"[File not found: {path_str}]"
    return excerpts


def scan_for_unlisted_citations(claim: dict) -> list:
    """Tier 2: find files that contain search_terms but are not in used_in."""
    search_terms = claim.get("search_terms", [])
    if not search_terms:
        return []

    used_in = set(claim.get("used_in", []))
    unlisted = []

    candidate_files = []
    for root in TIER2_SCAN_ROOTS:
        if not root.exists():
            continue
        if root.is_file():
            candidate_files.append(root)
        else:
            for ext in ("*.ts", "*.tsx", "*.md", "*.html"):
                candidate_files.extend(root.rglob(ext))

    for fp in candidate_files:
        rel = fp.relative_to(REPO_ROOT).as_posix()
        if rel in used_in:
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


def check_claim(client: Anthropic, claim: dict) -> dict:
    """Single API call per claim: web_search verify + Tier 1 diff draft."""
    used_in_paths = claim.get("used_in", [])
    excerpts = read_used_in_excerpts(used_in_paths)

    file_section = ""
    if excerpts:
        parts = ["\n\nCurrent content excerpts from citing files (for proposed-edit drafting):"]
        for path_str, content in excerpts.items():
            parts.append(f"\n--- {path_str} ---\n{content}\n")
        file_section = "".join(parts)

    prompt = PROMPT_TEMPLATE.format(
        claim_id=claim["claim_id"],
        description=claim["description"],
        last_verified=claim["last_verified"],
        source_pattern=claim["source_pattern"],
        file_section=file_section,
    )

    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2000,
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
        return {
            "claim_id": claim["claim_id"],
            "result": f"[API ERROR: {exc}]",
            "needs_review": False,
            "error": True,
            "is_budget_error": is_budget,
            "unlisted_hits": [],
        }

    needs_review = "NEEDS REVIEW" in text.upper()
    return {
        "claim_id": claim["claim_id"],
        "result": text,
        "needs_review": needs_review,
        "error": False,
        "is_budget_error": False,
        "unlisted_hits": [],
    }


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


def write_report(today: str, results: list, budget_hit: bool, budget_hit_at: int, total: int) -> Path:
    out_path = REFRESH_LOG_DIR / f"{today}.md"

    action_items = [r for r in results if r.get("needs_review")]
    no_change = [r for r in results if not r.get("needs_review") and not r.get("error")]
    errors = [r for r in results if r.get("error")]

    with open(out_path, "w", encoding="utf-8") as f:
        if budget_hit:
            f.write(f"# Research Refresh — {today} — BUDGET LIMIT REACHED\n\n")
            f.write(
                f"Budget limit hit after claim {budget_hit_at + 1} of {total}. "
                f"{total - budget_hit_at - 1} claims were not checked. "
                "Check the Anthropic Console billing page and set or raise the spending limit "
                "before the next scheduled run.\n\n"
            )
        else:
            f.write(f"# Research Refresh — {today}\n\n")

        f.write(
            "Automated monthly check. Human review required before any citation or content "
            "change. See `research/refresh-log/tracked-claims.json` for claim definitions.\n\n"
        )

        # Section 1: Action required (Tier 3 — these appear first)
        f.write(f"## Requires Review ({len(action_items)})\n\n")
        if action_items:
            for r in action_items:
                f.write(f"### {r['claim_id']}\n\n")
                f.write(r["result"].strip())
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
                f.write(f"### {r['claim_id']}\n\n{r['result'].strip()}\n\n---\n\n")

        # Section 3: Audit trail — no change (Tier 3 — visually separated)
        f.write(
            f"## Audit Trail — No Change Detected ({len(no_change)})\n\n"
            "The following claims were verified this month and returned no material change. "
            "No action required. Included for audit trail and job-health confirmation.\n\n"
        )
        for r in no_change:
            f.write(f"### {r['claim_id']}\n\n")
            f.write(r["result"].strip())
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
            "ERROR: ANTHROPIC_API_KEY environment variable not set. "
            "This must be the dedicated PRV3_REFRESH key — see CLAUDE.md Step 3a provisioning note."
        )

    if not TRACKED_CLAIMS_PATH.exists():
        sys.exit(f"ERROR: Claims registry not found at {TRACKED_CLAIMS_PATH}")

    with open(TRACKED_CLAIMS_PATH, encoding="utf-8") as f:
        claims = json.load(f)

    client = Anthropic(api_key=api_key)
    today = date.today().isoformat()
    results = []
    budget_hit = False
    budget_hit_at = 0

    for i, claim in enumerate(claims):
        print(f"Checking {i + 1}/{len(claims)}: {claim['claim_id']} ...", flush=True)
        r = check_claim(client, claim)

        if r["is_budget_error"]:
            budget_hit = True
            budget_hit_at = i
            results.append(r)
            # Mark all remaining claims as unchecked
            for j in range(i + 1, len(claims)):
                results.append({
                    "claim_id": claims[j]["claim_id"],
                    "result": "[UNCHECKED — budget limit reached before this claim was processed]",
                    "needs_review": False,
                    "error": True,
                    "is_budget_error": True,
                    "unlisted_hits": [],
                })
            break

        if not r["error"]:
            r["unlisted_hits"] = scan_for_unlisted_citations(claim)

        results.append(r)

    # Update pending-integration.json for all material findings
    pending = load_pending()
    for r in results:
        if r.get("needs_review") and not r.get("error"):
            claim = next((c for c in claims if c["claim_id"] == r["claim_id"]), {})
            pending.append({
                "claim_id": r["claim_id"],
                "refresh_report": f"research/refresh-log/{today}.md",
                "proposed_at": today,
                "pr_merged_at": None,
                "status": "proposed",
                "proposed_edit_summary": (
                    f"Material change detected. See research/refresh-log/{today}.md "
                    "for current finding and proposed edits."
                ),
                "target_files": claim.get("used_in", []),
                "applied_commit": None,
                "rejected_reason": None,
            })
    save_pending(pending)

    out_path = write_report(today, results, budget_hit, budget_hit_at, len(claims))
    print(f"Report written: {out_path}", flush=True)

    # Write budget status for the GitHub Action to pick up
    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        prefix = "BUDGET LIMIT — " if budget_hit else ""
        with open(github_output, "a", encoding="utf-8") as gf:
            gf.write(f"pr_title_prefix={prefix}\n")

    if budget_hit:
        print(
            f"\nWARNING: BUDGET LIMIT REACHED — "
            f"{budget_hit_at}/{len(claims)} claims were checked. "
            "Check Anthropic Console billing before next run.",
            flush=True,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
