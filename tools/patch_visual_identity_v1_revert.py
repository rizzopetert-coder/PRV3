"""
PRV3 -- Revert the /diagnostic reskin's four OD-07 (visual identity v2)
surfaces back to the locked v1 identity (Session 58: paper/charcoal/
slate/rust, font-display/Lora), plus recolor (not remove) the shared
ConstellationField component so it keeps rendering the real
dimension_summary-driven diagnostic shape using v1 colors, and unmount
ThemeSwitcher from NavBar.

Scope (7 files):
  1. web/app/page.tsx              -- homepage, mechanical class rename
  2. web/components/DiagnosticFlow.tsx        -- mechanical class rename
  3. web/app/diagnostic/page.tsx   -- mechanical class rename
  4. web/components/PrivateOutput.tsx         -- mechanical class rename
  5. web/components/ConstellationField.tsx    -- functional var()
     substitutions (oxide/oxide-text->color-slate, urgency/urgency-text
     ->color-rust, slate->color-slate, line->#e5e7eb) + ~10 descriptive
     comments updated to match
  6. web/components/ConstellationField.test.ts -- 3 hard-asserted
     severityAccentTokens() return values + their it() descriptions
  7. web/components/NavBar.tsx     -- clean ThemeSwitcher unmount
     (imports, dead pathname/isHomepage plumbing, JSX block, stale
     header comment all removed together)

globals.css token definitions and ThemeSwitcher.tsx itself are NOT
touched -- OD-07 infrastructure stays in place, dormant.

Usage:
  python tools/patch_visual_identity_v1_revert.py --dry-run
  python tools/patch_visual_identity_v1_revert.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Each edit: (path, old, new, expected_count)
# expected_count > 1 is used for the mechanical, file-wide class-token
# renames (order-independent, non-overlapping substrings, verified by
# exact grep count before this script was written). expected_count == 1
# is used everywhere a specific unique block is being targeted.
EDITS: list[tuple[str, str, str, int]] = []


def edit(path: str, old: str, new: str, expected_count: int = 1):
    EDITS.append((path, old, new, expected_count))


# ---------------------------------------------------------------------
# 1-4. Mechanical Tailwind class-token renames across the four UI files
# ---------------------------------------------------------------------

edit("web/app/page.tsx", "text-ink", "text-charcoal", 9)
edit("web/app/page.tsx", "bg-ink", "bg-charcoal", 1)
edit("web/app/page.tsx", "border-ink", "border-charcoal", 2)
edit("web/app/page.tsx", "bg-field", "bg-paper", 1)
edit("web/app/page.tsx", "font-serif", "font-display", 3)

edit("web/components/DiagnosticFlow.tsx", "text-ink", "text-charcoal", 6)
edit("web/components/DiagnosticFlow.tsx", "bg-ink", "bg-charcoal", 2)
edit("web/components/DiagnosticFlow.tsx", "border-ink", "border-charcoal", 2)
edit("web/components/DiagnosticFlow.tsx", "font-serif", "font-display", 3)

edit("web/app/diagnostic/page.tsx", "text-ink", "text-charcoal", 5)
edit("web/app/diagnostic/page.tsx", "bg-ink", "bg-charcoal", 4)
edit("web/app/diagnostic/page.tsx", "border-ink", "border-charcoal", 3)
edit("web/app/diagnostic/page.tsx", "bg-field", "bg-paper", 3)
edit("web/app/diagnostic/page.tsx", "font-serif", "font-display", 2)

edit("web/components/PrivateOutput.tsx", "text-ink", "text-charcoal", 4)

# ---------------------------------------------------------------------
# 5. ConstellationField.tsx -- functional var() substitutions + comments
# ---------------------------------------------------------------------

CF = "web/components/ConstellationField.tsx"

edit(
    CF,
    "// never uses --urgency/--urgency-text, enforced structurally — render()",
    "// never uses --color-rust, enforced structurally — render()",
)
edit(
    CF,
    "// hardcodes stroke to var(--oxide) unconditionally, no code path in",
    "// hardcodes stroke to var(--color-slate) unconditionally, no code path in",
)
edit(
    CF,
    "// ambient mode can ever reference --urgency. A decorative loop cycling",
    "// ambient mode can ever reference --color-rust. A decorative loop cycling",
)
edit(
    CF,
    '// mockups/pr-results-constellation-mockup.html. --urgency/--urgency-text\n'
    '// ONLY when severityTier is genuinely "Endemic"; --oxide/--oxide-text at',
    '// mockups/pr-results-constellation-mockup.html. --color-rust\n'
    '// ONLY when severityTier is genuinely "Endemic"; --color-slate at',
)
edit(
    CF,
    "// ALWAYS --oxide/--slate, never severity-conditional — only the dominant",
    "// ALWAYS --color-slate, never severity-conditional — only the dominant",
)
edit(
    CF,
    "// Reference guide diamonds at 25% / 50% / 75% of LIVE_MAX_R — always\n"
    "// --line, never severity-conditional.",
    "// Reference guide diamonds at 25% / 50% / 75% of LIVE_MAX_R — always\n"
    "// #e5e7eb, never severity-conditional.",
)
edit(
    CF,
    '// --urgency/--urgency-text ONLY when severityTier is genuinely "Endemic".\n'
    "// --oxide/--oxide-text at Emerging/Entrenched. This is the one piece of",
    '// --color-rust ONLY when severityTier is genuinely "Endemic".\n'
    "// --color-slate at Emerging/Entrenched. This is the one piece of",
)
edit(
    CF,
    '  if (tier === "Endemic") {\n'
    '    return { stroke: "var(--urgency)", text: "var(--urgency-text)" };\n'
    "  }\n"
    '  return { stroke: "var(--oxide)", text: "var(--oxide-text)" };',
    '  if (tier === "Endemic") {\n'
    '    return { stroke: "var(--color-rust)", text: "var(--color-rust)" };\n'
    "  }\n"
    '  return { stroke: "var(--color-slate)", text: "var(--color-slate)" };',
)
edit(
    CF,
    "      // HARD CAP: always --oxide, never --urgency. See file header.\n"
    '      ringGroup.setAttribute("stroke", "var(--oxide)");',
    "      // HARD CAP: always --color-slate, never --color-rust. See file header.\n"
    '      ringGroup.setAttribute("stroke", "var(--color-slate)");',
)
edit(
    CF,
    "      <polygon\n"
    "        ref={shapeRef}\n"
    "        points={pointsAttr(RESTING_FRAME)}\n"
    '        fill="color-mix(in srgb, var(--oxide) 10%, transparent)"\n'
    '        stroke="var(--oxide)"\n'
    '        strokeWidth="1.4"\n'
    '        opacity="0.8"\n'
    "      />\n"
    "      <g\n"
    "        ref={ringGroupRef}\n"
    "        filter={`url(#${filterId})`}\n"
    '        fill="none"\n'
    '        stroke="var(--oxide)"\n'
    '        strokeWidth="1"\n'
    "      >",
    "      <polygon\n"
    "        ref={shapeRef}\n"
    "        points={pointsAttr(RESTING_FRAME)}\n"
    '        fill="color-mix(in srgb, var(--color-slate) 10%, transparent)"\n'
    '        stroke="var(--color-slate)"\n'
    '        strokeWidth="1.4"\n'
    '        opacity="0.8"\n'
    "      />\n"
    "      <g\n"
    "        ref={ringGroupRef}\n"
    "        filter={`url(#${filterId})`}\n"
    '        fill="none"\n'
    '        stroke="var(--color-slate)"\n'
    '        strokeWidth="1"\n'
    "      >",
)
edit(
    CF,
    '      <g stroke="var(--line)" strokeWidth="1" fill="none">\n'
    "        <line x1={CENTER.x} y1={CENTER.y - 190} x2={CENTER.x} y2={CENTER.y + 190} />\n"
    "        <line x1={CENTER.x - 190} y1={CENTER.y} x2={CENTER.x + 190} y2={CENTER.y} />\n"
    "      </g>",
    '      <g stroke="#e5e7eb" strokeWidth="1" fill="none">\n'
    "        <line x1={CENTER.x} y1={CENTER.y - 190} x2={CENTER.x} y2={CENTER.y + 190} />\n"
    "        <line x1={CENTER.x - 190} y1={CENTER.y} x2={CENTER.x + 190} y2={CENTER.y} />\n"
    "      </g>",
)
edit(
    CF,
    "      {/* Reference grid — always --line, never severity-conditional. */}\n"
    '      <g stroke="var(--line)" strokeWidth="1" fill="none">',
    "      {/* Reference grid — always #e5e7eb, never severity-conditional. */}\n"
    '      <g stroke="#e5e7eb" strokeWidth="1" fill="none">',
)
edit(
    CF,
    "      {/* Axis labels — always --slate, except the dominant axis, which\n"
    "          takes the severity-conditional accent text color. */}",
    "      {/* Axis labels — always --color-slate, except the dominant axis, which\n"
    "          takes the severity-conditional accent text color. */}",
)
edit(
    CF,
    '          fill={k === domKey ? accent.text : "var(--slate)"}',
    '          fill={k === domKey ? accent.text : "var(--color-slate)"}',
)
edit(
    CF,
    "      {/* The weighted shape — ALWAYS --oxide, never severity-conditional.\n"
    "          Confirmed from the mockup: only the dominant vertex's rings,\n"
    "          center dot, and axis label switch to --urgency at Endemic. */}",
    "      {/* The weighted shape — ALWAYS --color-slate, never severity-conditional.\n"
    "          Confirmed from the mockup: only the dominant vertex's rings,\n"
    "          center dot, and axis label switch to --color-rust at Endemic. */}",
)
edit(
    CF,
    "      <polygon\n"
    "        points={shapePoints}\n"
    '        fill="color-mix(in srgb, var(--oxide) 14%, transparent)"\n'
    '        stroke="var(--oxide)"\n'
    '        strokeWidth="1.5"\n'
    "      />",
    "      <polygon\n"
    "        points={shapePoints}\n"
    '        fill="color-mix(in srgb, var(--color-slate) 14%, transparent)"\n'
    '        stroke="var(--color-slate)"\n'
    '        strokeWidth="1.5"\n'
    "      />",
)
edit(
    CF,
    "      {/* Non-dominant vertex dots — always --slate. */}",
    "      {/* Non-dominant vertex dots — always --color-slate. */}",
)
edit(
    CF,
    '          <circle key={k} cx={points[k].x} cy={points[k].y} r={4} fill="var(--slate)" />',
    '          <circle key={k} cx={points[k].x} cy={points[k].y} r={4} fill="var(--color-slate)" />',
)
edit(
    CF,
    "      {/* Severity rings — fixed 5-ring pattern, radii/opacity never vary\n"
    "          by severity tier. Only the color varies (accent.stroke: --oxide\n"
    "          at Emerging/Entrenched, --urgency only at genuine Endemic). */}",
    "      {/* Severity rings — fixed 5-ring pattern, radii/opacity never vary\n"
    "          by severity tier. Only the color varies (accent.stroke: --color-slate\n"
    "          at Emerging/Entrenched, --color-rust only at genuine Endemic). */}",
)

# ---------------------------------------------------------------------
# 6. ConstellationField.test.ts -- 3 hard-asserted return values
# ---------------------------------------------------------------------

CFT = "web/components/ConstellationField.test.ts"

edit(
    CFT,
    '  it("uses --urgency tokens only for genuine Endemic severity", () => {\n'
    '    expect(severityAccentTokens("Endemic")).toEqual({\n'
    '      stroke: "var(--urgency)",\n'
    '      text: "var(--urgency-text)",\n'
    "    });\n"
    "  });",
    '  it("uses the v1 rust token only for genuine Endemic severity", () => {\n'
    '    expect(severityAccentTokens("Endemic")).toEqual({\n'
    '      stroke: "var(--color-rust)",\n'
    '      text: "var(--color-rust)",\n'
    "    });\n"
    "  });",
)
edit(
    CFT,
    '  it("uses --oxide tokens for Entrenched", () => {\n'
    '    expect(severityAccentTokens("Entrenched")).toEqual({\n'
    '      stroke: "var(--oxide)",\n'
    '      text: "var(--oxide-text)",\n'
    "    });\n"
    "  });",
    '  it("uses the v1 slate token for Entrenched", () => {\n'
    '    expect(severityAccentTokens("Entrenched")).toEqual({\n'
    '      stroke: "var(--color-slate)",\n'
    '      text: "var(--color-slate)",\n'
    "    });\n"
    "  });",
)
edit(
    CFT,
    '  it("uses --oxide tokens for Emerging", () => {\n'
    '    expect(severityAccentTokens("Emerging")).toEqual({\n'
    '      stroke: "var(--oxide)",\n'
    '      text: "var(--oxide-text)",\n'
    "    });\n"
    "  });",
    '  it("uses the v1 slate token for Emerging", () => {\n'
    '    expect(severityAccentTokens("Emerging")).toEqual({\n'
    '      stroke: "var(--color-slate)",\n'
    '      text: "var(--color-slate)",\n'
    "    });\n"
    "  });",
)

# ---------------------------------------------------------------------
# 7. NavBar.tsx -- clean ThemeSwitcher unmount
# ---------------------------------------------------------------------

NB = "web/components/NavBar.tsx"

edit(
    NB,
    'import { usePathname } from "next/navigation";\n'
    'import { ThemeSwitcher } from "@/components/ThemeSwitcher";\n'
    "\n"
    "// NavBar is shared across every route (mounted once in the root layout) —\n"
    "// NOT homepage-specific. The Stage 4 brief scopes the theme switcher to\n"
    '// "the homepage nav" while also requiring every other route stay\n'
    "// untouched. Since there is no separate homepage-only nav, the switcher\n"
    '// is mounted here but gated on pathname === "/" — every other route\n'
    "// renders this component exactly as before (confirmed via the Stage 4\n"
    "// production-build diff), only the homepage additionally shows it.\n"
    "export function NavBar() {",
    "export function NavBar() {",
)
edit(
    NB,
    "  const [aboutOpen, setAboutOpen] = useState(false);\n"
    "  const aboutRef = useRef<HTMLDivElement>(null);\n"
    "  const pathname = usePathname();\n"
    '  const isHomepage = pathname === "/";',
    "  const [aboutOpen, setAboutOpen] = useState(false);\n"
    "  const aboutRef = useRef<HTMLDivElement>(null);",
)
edit(
    NB,
    "        {isHomepage && (\n"
    '          <div className="w-55">\n'
    "            <ThemeSwitcher />\n"
    "          </div>\n"
    "        )}\n"
    "      </div>",
    "      </div>",
)


def apply(dry_run: bool) -> int:
    errors = 0
    changed = 0
    file_cache: dict[str, str] = {}
    for rel_path, old, new, expected_count in EDITS:
        path = REPO_ROOT / rel_path
        text = file_cache.get(rel_path)
        if text is None:
            text = path.read_text(encoding="utf-8")
        count = text.count(old)
        if count != expected_count:
            print(
                f"ERROR: {rel_path} -- expected {expected_count} match(es), found {count}"
            )
            print(f"  old (first 100 chars): {old[:100]!r}")
            errors += 1
            continue
        text = text.replace(old, new)
        file_cache[rel_path] = text
        changed += 1
        if dry_run:
            print(f"OK (dry-run): {rel_path} -- {count} match(es), would replace")

    if errors:
        print(f"\n{errors} edit(s) FAILED validation. No files written.")
        return 1

    if not dry_run:
        for rel_path, text in file_cache.items():
            (REPO_ROOT / rel_path).write_text(text, encoding="utf-8")
            print(f"WRITTEN: {rel_path}")

    print(f"\n{changed}/{len(EDITS)} edits {'validated' if dry_run else 'applied'}.")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()
    sys.exit(apply(dry_run=args.dry_run))


if __name__ == "__main__":
    main()
