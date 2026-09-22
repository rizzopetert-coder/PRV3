"""
tools/sleuth/cli.py -- site-integrity crawler for principalresolution.com.
Entry point. One theme per invocation (parameterized, not a multi-theme
run) -- run it once per theme you want checked.

Usage:
    python tools/sleuth/cli.py --base-url https://principalresolution.com --theme warm
    python tools/sleuth/cli.py --base-url http://localhost:3000 --theme dark --skip-build
    python tools/sleuth/cli.py --base-url https://<preview>.vercel.app --theme neutral \\
        --bypass-secret VERCEL_AUTOMATION_BYPASS_SECRET

Outputs (written to --output-dir, default tools/sleuth/output/):
    sleuth_raw.json    -- full crawl extract (pages, links, computed
                          styles, axe-core violations), for re-running
                          rule checks without re-crawling.
    sleuth_report.md   -- severity-grouped findings.

Exit code: non-zero if any DETERMINISTIC-tier finding exists, zero if
the run completed clean or with only CANDIDATE-tier flags (per the
build brief: candidate tier is "logged only -> exit 0").
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
WEB_DIR = REPO_ROOT / "web"
SLEUTH_DIR = Path(__file__).resolve().parent
CRAWLER_SCRIPT = SLEUTH_DIR / "crawler" / "crawl.mjs"

sys.path.insert(0, str(REPO_ROOT))

from tools.sleuth.route_manifest import build_route_manifest
from tools.sleuth.rules import structural, brand, content, candidate
from tools.sleuth.rules.finding import Tier
from tools.sleuth.report import render_report
from tools.sleuth.vercel_bypass import build_bypass_headers, resolve_bypass_secret

KNOWN_GAPS = [
    'No coined-term (P-10) scan: the build brief asked for "possible coined-term '
    'hits," but P-10 is the rule ("no coined terms"), not an enumerated term list -- '
    "no such list exists anywhere in this repo to check against. Not implemented "
    "with a fake heuristic; see tools/sleuth/rules/candidate.py's module docstring.",
    "Brand-color check uses a flat union of every locked color across all themes "
    "and scopes (not strict per-theme cascade resolution) -- see tools/sleuth/"
    "tokens.py's module docstring for why, and the tradeoff this accepts.",
    "Glossary-exemption list (tools/sleuth/config.py) is currently empty -- "
    "confirmed no src/data/glossary.json or equivalent page exists in this repo. "
    "Will activate automatically if such a page is ever built.",
    "Shadow-model exemption list has exactly one confirmed entry "
    "(pete@principalresolution.com) -- anything else that should be exempt needs "
    "the same explicit confirmation before being added.",
]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="sleuth -- site-integrity crawler")
    p.add_argument("--base-url", required=True)
    p.add_argument("--theme", required=True, choices=["warm", "dark", "neutral"])
    p.add_argument("--bypass-secret", default=None,
                    help="Name of an environment variable holding the Vercel "
                         "Protection Bypass for Automation secret (not the secret itself).")
    p.add_argument("--output-dir", default=str(SLEUTH_DIR / "output"))
    p.add_argument("--skip-build", action="store_true",
                    help="Reuse the existing web/.next build output instead of running `npm run build` first.")
    p.add_argument("--concurrency", type=int, default=3)
    p.add_argument("--max-pages", type=int, default=400)
    p.add_argument("--per-page-timeout-ms", type=int, default=20000)
    return p.parse_args()


def run_crawl(args: argparse.Namespace, extra_headers: dict[str, str], output_dir: Path) -> dict:
    job_spec = {
        "baseUrl": args.base_url,
        "theme": args.theme,
        "extraHeaders": extra_headers,
        "userAgent": "SleuthBot/1.0",
        "concurrency": args.concurrency,
        "maxPages": args.max_pages,
        "perPageTimeoutMs": args.per_page_timeout_ms,
        "_startedAt": datetime.now(timezone.utc).isoformat(),
    }

    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
        json.dump(job_spec, f)
        job_spec_path = f.name

    raw_output_path = output_dir / "sleuth_raw.json"
    output_dir.mkdir(parents=True, exist_ok=True)

    result = subprocess.run(
        ["node", str(CRAWLER_SCRIPT), job_spec_path, str(raw_output_path)],
        cwd=str(WEB_DIR),
        capture_output=True,
        text=True,
    )
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr, file=sys.stderr)
        raise RuntimeError(f"crawl.mjs exited {result.returncode}")

    return json.loads(raw_output_path.read_text(encoding="utf-8"))


def main() -> int:
    args = parse_args()
    output_dir = Path(args.output_dir)

    extra_headers: dict[str, str] = {}
    if args.bypass_secret:
        secret = resolve_bypass_secret(args.bypass_secret)
        extra_headers = build_bypass_headers(secret)

    print(f"[sleuth] building route manifest (skip_build={args.skip_build}) ...")
    route_manifest = build_route_manifest(skip_build=args.skip_build)
    print(f"[sleuth] {len(route_manifest.static_routes)} expected static routes.")

    print(f"[sleuth] crawling {args.base_url} (theme={args.theme}) ...")
    crawl = run_crawl(args, extra_headers, output_dir)
    print(f"[sleuth] crawled {crawl['pageCount']} pages.")

    max_pages_hit = crawl["pageCount"] >= args.max_pages

    findings = []
    findings += structural.check(crawl, route_manifest, max_pages_hit)
    findings += brand.check(crawl)
    findings += content.check(crawl)
    findings += candidate.check(crawl)

    report_md = render_report(
        findings,
        base_url=args.base_url,
        theme=args.theme,
        page_count=crawl["pageCount"],
        known_gaps=KNOWN_GAPS,
    )
    report_path = output_dir / "sleuth_report.md"
    report_path.write_text(report_md, encoding="utf-8")

    deterministic_count = sum(1 for f in findings if f.tier == Tier.DETERMINISTIC)
    candidate_count = sum(1 for f in findings if f.tier == Tier.CANDIDATE)

    print(f"[sleuth] {deterministic_count} deterministic finding(s), {candidate_count} candidate finding(s).")
    print(f"[sleuth] report: {report_path}")
    print(f"[sleuth] raw data: {output_dir / 'sleuth_raw.json'}")

    return 1 if deterministic_count > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
