"""
PRV3 -- Gemini NotebookLM source export.

Produces a flat staging folder (gemini_export/, repo root, gitignored) of
every file prompts/gemini-notebooklm-source-checklist.md's Sections 1-6
name, in a format NotebookLM actually accepts. NotebookLM rejects raw
.py/.ts/.tsx uploads by extension (confirmed 2026-08-19) -- code files get
copied with their content unchanged and a .txt extension appended; the two
governing docs (CLAUDE.md, tools/_mob.txt) are already in accepted formats
and get copied as-is.

Source of truth: EXPORT_FILES below, hardcoded rather than parsed from the
checklist doc -- the doc mixes rationale prose with file paths in a way
that makes robust parsing more fragile than it's worth. To keep the two
from drifting apart silently, this script also extracts every backtick-
quoted, extension-bearing path out of the checklist doc's Sections 1-6 and
warns (does not fail) if anything listed there is missing from
EXPORT_FILES below.

**If you edit the checklist doc's Sections 1-6 file list, update
EXPORT_FILES here too** -- this list is not auto-derived from the doc.

Output naming: original path with "/" replaced by "-", then:
  - code files (.py/.ts/.tsx): ".txt" appended (e.g. engine/severity.py
    -> engine-severity.py.txt)
  - already-accepted files (.md/.txt): extension kept as-is
    (e.g. tools/_mob.txt -> tools-_mob.txt)

manifest.txt (written into the same staging folder) records the git commit
hash at export time, the export timestamp, and every file's source path ->
export filename mapping -- compare its commit hash against `git rev-parse
HEAD` later to know instantly whether a re-export is needed.

Usage:
    python tools/export_gemini_sources.py
"""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CHECKLIST_PATH = REPO_ROOT / "prompts" / "gemini-notebooklm-source-checklist.md"
EXPORT_DIR = REPO_ROOT / "gemini_export"

# -- Canonical export list -----------------------------------------------------
# Mirrors prompts/gemini-notebooklm-source-checklist.md Sections 1-6 exactly.
# (category_label, relative_path) -- category_label is for manifest grouping only.

EXPORT_FILES: list[tuple[str, str]] = [
    # Section 1 -- Core engine files
    ("engine", "engine/severity.py"),
    ("engine", "engine/main.py"),
    ("engine", "engine/output.py"),
    ("engine", "engine/contract.py"),
    ("engine", "engine/output_synthesis.py"),
    ("engine", "engine/friction_tax.py"),
    ("engine", "engine/accumulation.py"),
    ("engine", "engine/checkpoint.py"),
    ("engine", "engine/resolution_families.py"),
    ("engine", "engine/narrative.py"),
    ("engine", "engine/data/questions.py"),
    ("engine", "engine/data/states.py"),
    ("engine", "engine/data/intake.py"),
    ("engine", "engine/data/salience.py"),
    ("engine", "engine/data/fallback_synthesis.py"),
    ("engine", "engine/data/jurisdiction.py"),
    ("engine", "engine/data/validate.py"),
    # Section 2 -- Calibration harness and API bridge
    ("harness_api", "tools/calibration_runner.py"),
    ("harness_api", "api/engine.py"),
    # Section 3 -- Web-layer types, routing, and state
    ("web_lib", "web/lib/types.ts"),
    ("web_lib", "web/lib/engine-client.ts"),
    ("web_lib", "web/lib/session-store.ts"),
    ("web_lib", "web/lib/condensed-session-store.ts"),
    ("web_lib", "web/lib/resolution-family.ts"),
    ("web_lib", "web/lib/book-manifest.ts"),
    ("web_lib", "web/lib/book-state-index.ts"),
    ("web_lib", "web/data/taxonomy.ts"),
    # Section 4 -- Live API routes
    ("web_routes", "web/app/api/diagnostic/session/start/route.ts"),
    ("web_routes", "web/app/api/diagnostic/session/answer/route.ts"),
    ("web_routes", "web/app/api/diagnostic/session/resume/route.ts"),
    ("web_routes", "web/app/api/result/route.ts"),
    ("web_routes", "web/app/api/share/create/route.ts"),
    ("web_routes", "web/app/api/share/[id]/route.ts"),
    ("web_routes", "web/app/api/diagnostic/condensed/start/route.ts"),
    ("web_routes", "web/app/api/diagnostic/condensed/answer/route.ts"),
    ("web_routes", "web/app/api/interpret/route.ts"),
    ("web_routes", "web/app/api/dev/diagnostic-preview/route.ts"),
    # Section 5 -- Live rendering components
    ("web_components", "web/components/PrivateOutput.tsx"),
    ("web_components", "web/components/ShareableOutput.tsx"),
    ("web_components", "web/components/CondensedOutput.tsx"),
    ("web_components", "web/components/DiagnosticFlow.tsx"),
    ("web_components", "web/components/CondensedDiagnosticFlow.tsx"),
    # Section 6 -- Governing and reference docs (already accepted formats)
    ("governing_docs", "CLAUDE.md"),
    ("governing_docs", "tools/_mob.txt"),
]

_CODE_EXTENSIONS = {".py", ".ts", ".tsx"}
_ALREADY_ACCEPTED_EXTENSIONS = {".md", ".txt"}


def export_filename(relative_path: str) -> str:
    flat = relative_path.replace("/", "-")
    ext = Path(relative_path).suffix
    if ext in _CODE_EXTENSIONS:
        return flat + ".txt"
    if ext in _ALREADY_ACCEPTED_EXTENSIONS:
        return flat
    raise ValueError(
        f"{relative_path!r}: extension {ext!r} is neither a known code "
        f"extension nor an already-accepted format -- add explicit "
        f"handling before exporting this file."
    )


def extract_checklist_paths(checklist_text: str) -> set[str]:
    """Backtick-quoted, extension-bearing paths inside Sections 1 through 6
    only (stop at Section 7, the exclude list -- those paths shouldn't be
    exported). Best-effort drift check, not a parser EXPORT_FILES depends on."""
    section_6_end = checklist_text.find("## 7. Explicitly exclude")
    scoped_text = checklist_text if section_6_end == -1 else checklist_text[:section_6_end]

    known_exts = _CODE_EXTENSIONS | _ALREADY_ACCEPTED_EXTENSIONS
    candidates = re.findall(r"`([^`]+)`", scoped_text)
    paths = set()
    for c in candidates:
        if "/" not in c and c != "CLAUDE.md":
            continue
        ext = Path(c).suffix
        if ext in known_exts:
            paths.add(c)
    return paths


# Paths that appear in backticks within Sections 1-6 but are explicitly,
# deliberately NOT exported -- the checklist's own "Deliberately not
# included" rationale (Section 1: calibration profile data, not
# architecture). Listed here so the drift check doesn't cry wolf on a
# known, documented choice every single run.
KNOWN_DELIBERATE_EXCLUSIONS = {
    "engine/test_profiles*.py",
    "engine/test_suite.py",
}


def check_drift(checklist_text: str) -> list[str]:
    doc_paths = extract_checklist_paths(checklist_text)
    export_paths = {p for _cat, p in EXPORT_FILES}
    missing_from_script = sorted(doc_paths - export_paths - KNOWN_DELIBERATE_EXCLUSIONS)
    return missing_from_script


def get_commit_hash() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=REPO_ROOT, capture_output=True, text=True, check=True,
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        return f"UNKNOWN (git rev-parse failed: {e})"


def main() -> int:
    checklist_text = CHECKLIST_PATH.read_text(encoding="utf-8")
    drift = check_drift(checklist_text)
    if drift:
        print("WARNING: checklist doc lists files not present in EXPORT_FILES "
              "(tools/export_gemini_sources.py) -- doc and script have drifted:")
        for p in drift:
            print(f"  MISSING FROM SCRIPT: {p}")
        print()

    missing_sources = [p for _cat, p in EXPORT_FILES if not (REPO_ROOT / p).is_file()]
    if missing_sources:
        print("ABORT: EXPORT_FILES names files that don't exist in the repo:")
        for p in missing_sources:
            print(f"  {p}")
        return 1

    if EXPORT_DIR.exists():
        shutil.rmtree(EXPORT_DIR)
    EXPORT_DIR.mkdir(parents=True)

    commit_hash = get_commit_hash()
    timestamp = datetime.now(timezone.utc).isoformat()

    manifest_lines = [
        f"commit: {commit_hash}",
        f"exported_at_utc: {timestamp}",
        f"file_count: {len(EXPORT_FILES)}",
        "",
        "files (source_path -> export_filename):",
    ]

    for category, rel_path in EXPORT_FILES:
        src = REPO_ROOT / rel_path
        # newline="" on read + write preserves the source file's exact line
        # endings -- Windows' default text-mode write otherwise silently
        # converts \n -> \r\n, which byte-for-byte diverges from source
        # (confirmed: engine/severity.py is LF-only on disk; a naive
        # write_text() here produced a CRLF copy that reads identically
        # but isn't actually byte-identical -- fixed by forcing newline="").
        content = src.read_text(encoding="utf-8", newline="")
        out_name = export_filename(rel_path)
        (EXPORT_DIR / out_name).write_text(content, encoding="utf-8", newline="")
        manifest_lines.append(f"  [{category}] {rel_path} -> {out_name}")

    manifest_text = "\n".join(manifest_lines) + "\n"
    (EXPORT_DIR / "manifest.txt").write_text(manifest_text, encoding="utf-8")

    print(f"Exported {len(EXPORT_FILES)} files to {EXPORT_DIR}")
    print(f"Commit: {commit_hash}")
    print(f"Timestamp: {timestamp}")
    print(f"Manifest: {EXPORT_DIR / 'manifest.txt'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
