"""
tools/sleuth/tokens.py -- locked palette and font-family allowlists,
read from the real source (web/app/globals.css, web/app/layout.tsx),
not hardcoded from the build brief.

BRAND-COLOR SCOPE, confirmed with Pete before this file was written
(the brief's stated 4-color set -- Paper/Charcoal/Slate blue/Rust --
is a stale simplification; the real palette is a fully theme-reactive,
tiered system: v1 static Session-58 colors, v2 base tokens redefined
per [data-theme], and a v3 five-color expansion per theme, plus a
homepage-only .home-scope palette). Approach taken: extract every
`--custom-property: <literal-color>` declaration anywhere in
globals.css (any block, any theme scope) and treat the UNION as the
locked set, regardless of which theme it was declared under. This is
a deliberate v1 relaxation, not an oversight: precise per-theme cascade
resolution (Warm's --ink is only valid when crawling Warm) would be
more exact, but flat-union is far more robust against this file's real
structural complexity (three theme blocks plus at least one
independently-scoped .home-scope block) and still catches the actual
failure mode this check exists for -- a genuinely foreign color that
belongs to no design token anywhere -- without false-failing a legit
token used in the "wrong" theme's crawl due to a parsing edge case.
Tightening to true per-theme resolution is a reasonable v2 improvement
if false negatives become a real problem in practice.

Also includes a small NEUTRAL_ALLOWLIST (white, black, standard
Tailwind gray scale, transparent, currentColor). Confirmed via direct
reads this session that real pages already mix custom design tokens
with raw Tailwind neutrals (bg-white, text-gray-400, border-gray-200,
divide-gray-100 all appear in shipped components). Auto-failing 100%
of those on a v1 run would make the deterministic tier useless (a wall
of red on the site as it actually, legitimately exists today) --
treated as accepted neutrals rather than brand violations. This is a
judgment call, not a rule Pete confirmed line-by-line; documented here
so it's visible and easy to override, not buried in a regex.

FONT SCOPE: the brief said {Lora, Inter, JetBrains Mono}. Confirmed
stale against web/app/layout.tsx directly -- JetBrains Mono was
replaced by IBM Plex Mono (comment: "replaces JetBrains Mono, which
was confirmed unused"), and Source Serif 4 was added as a new,
currently-optional v2 typeface. Real locked set, per layout.tsx:
Lora (display), Inter (ui), IBM Plex Mono (mono), Source Serif 4
(serif, optional). Geist/Geist Mono are Next.js's own default
next/font imports, wired only as the document's technical body
fallback (`body { font-family: var(--font-sans) }`) -- accepted as a
safe fallback, not flagged as a foreign font, since it isn't a brand
choice going wrong, it's the framework's own base layer underneath
whatever explicit font-ui/font-display/font-mono class real content
carries.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
GLOBALS_CSS_PATH = REPO_ROOT / "web" / "app" / "globals.css"
LAYOUT_TSX_PATH = REPO_ROOT / "web" / "app" / "layout.tsx"

THEMES = ("warm", "dark", "neutral")

# Not brand tokens -- accepted structural/neutral values. Tailwind's default
# gray scale (50-950), true black/white, and the two non-color keywords.
NEUTRAL_ALLOWLIST = {
    "#ffffff", "#000000", "transparent", "currentcolor", "inherit",
    "rgba(0, 0, 0, 0)", "rgba(0,0,0,0)",
    # Tailwind v4 default gray scale (oklch-based in v4, but Tailwind still
    # accepts/emits these historical hex values in many contexts and this
    # codebase's own comments reference bare `gray-100`/`gray-200`/`gray-400`
    # utility classes directly) -- kept as hex for a simple string-membership
    # check against getComputedStyle's rgb()/hex output after normalization.
    "#f9fafb", "#f3f4f6", "#e5e7eb", "#d1d5db", "#9ca3af",
    "#6b7280", "#4b5563", "#374151", "#1f2937", "#111827", "#030712",
}

# Substring match against getComputedStyle(...).fontFamily -- next/font
# generates a stack like `'Lora', 'Lora Fallback'` or similar, never an
# exact bare "Lora", so membership is checked via substring, not equality.
ALLOWED_FONT_SUBSTRINGS = (
    "lora", "inter", "ibm plex mono", "source serif", "geist",
)


@dataclass(frozen=True)
class ThemeTokens:
    theme: str
    colors: frozenset[str]


_COMMENT_RE = re.compile(r"/\*.*?\*/", re.DOTALL)
_CUSTOM_PROP_COLOR_RE = re.compile(
    r"--[\w-]+\s*:\s*(#[0-9a-fA-F]{3,8}|rgba?\([^)]*\)|hsla?\([^)]*\))\s*;"
)
_HEX_RE = re.compile(r"^#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$")
_RGB_RE = re.compile(r"^rgba?\(\s*([\d.]+)[,\s]+([\d.]+)[,\s]+([\d.]+)(?:[,\s/]+([\d.]+%?))?\s*\)$")

# Real reason a plain string comparison doesn't work: globals.css declares
# colors as hex ("#14171A"), but getComputedStyle(...) always reports
# rgb()/rgba() ("rgb(20, 23, 26)") -- confirmed directly against a live
# crawl during this build, not assumed. Both sides are parsed to an (r, g,
# b) tuple (0-255 each) and compared numerically instead.
_KEYWORD_TRANSPARENT = {"transparent", "none", "inherit", "initial", "currentcolor"}


def _to_rgb_tuple(value: str) -> tuple[int, int, int, float] | None:
    """Returns (r, g, b, alpha) or None if unparseable/a non-color keyword."""
    v = value.strip().lower()
    if v in _KEYWORD_TRANSPARENT:
        return None
    hex_match = _HEX_RE.match(v)
    if hex_match:
        h = hex_match.group(1)
        if len(h) == 3:
            h = "".join(ch * 2 for ch in h)
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        return (r, g, b, 1.0)
    rgb_match = _RGB_RE.match(v)
    if rgb_match:
        r, g, b = (round(float(x)) for x in rgb_match.groups()[:3])
        alpha_raw = rgb_match.group(4)
        alpha = 1.0
        if alpha_raw is not None:
            alpha = float(alpha_raw.rstrip("%")) / (100.0 if alpha_raw.endswith("%") else 1.0)
        return (r, g, b, alpha)
    return None


@lru_cache(maxsize=1)
def load_locked_colors() -> frozenset[tuple[int, int, int, float]]:
    """
    Flat union of every literal color value assigned to any `--custom-
    property` anywhere in globals.css, PLUS the neutral allowlist, each
    parsed to an (r, g, b, alpha) tuple so hex- and rgb()-declared colors
    compare correctly against each other. See module docstring for why
    this is a flat union rather than per-theme cascade resolution.

    Cached (globals.css doesn't change mid-crawl, and a full-site run
    calls is_allowed_color() once per sampled element across every page --
    easily thousands of calls, not worth re-parsing the file for each).
    """
    if not GLOBALS_CSS_PATH.exists():
        raise FileNotFoundError(f"globals.css not found at {GLOBALS_CSS_PATH}")
    css = GLOBALS_CSS_PATH.read_text(encoding="utf-8")
    css = _COMMENT_RE.sub("", css)
    raw_values = {m.group(1) for m in _CUSTOM_PROP_COLOR_RE.finditer(css)} | set(NEUTRAL_ALLOWLIST)
    tuples = {_to_rgb_tuple(v) for v in raw_values}
    tuples.discard(None)
    return frozenset(tuples)


def is_allowed_color(css_color_value: str) -> bool:
    """
    css_color_value: whatever getComputedStyle(...) reports -- typically
    `rgb(r, g, b)` or `rgba(r, g, b, a)`, occasionally a keyword like
    `transparent`. Fully transparent colors (alpha 0, or the `transparent`
    keyword) are always allowed -- an invisible color can't be an on-page
    brand violation regardless of its RGB channels.
    """
    parsed = _to_rgb_tuple(css_color_value)
    if parsed is None:
        return True  # unparseable/keyword (transparent, currentColor, etc.) -- not a color violation
    if parsed[3] == 0.0:
        return True  # fully transparent
    locked = load_locked_colors()
    # Alpha-insensitive match on RGB channels: a locked token used at any
    # opacity is still that token, not a foreign color.
    return any(parsed[:3] == locked_rgb[:3] for locked_rgb in locked)


def is_allowed_font(computed_font_family: str) -> bool:
    lowered = computed_font_family.lower()
    return any(sub in lowered for sub in ALLOWED_FONT_SUBSTRINGS)


RUST_TOKEN_NAMES = ("--color-rust", "--urgency", "--urgency-text")
