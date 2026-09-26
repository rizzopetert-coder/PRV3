"""
tools/sleuth/route_manifest.py -- the "expected" route set, used as the
source of truth for orphan detection (step 2's crawl-reachable set is
diffed against this).

DESIGN DECISION, confirmed with Pete before this file was written: the
build brief asked for web/app/**/page.tsx to be enumerated directly and
book-manifest.ts's entries expanded by hand, checking
web/app/book/[type]/[slug]/page.tsx for the real path shape. Direct
inspection found THREE MORE dynamic /book/* route generators beyond
[type]/[slug] -- dimension, pillar, and state -- each pulling from a
different data source (PUBLIC_DIMENSION_LABELS, a PILLARS list +
slugifyPillar(), and a threshold-gated computeQualifyingStateIds()).
Hand-porting all four generateStaticParams() implementations into
Python would risk silent drift from the real TS logic every time any
of them changes.

Instead: run (or reuse) a real `next build` and read the resulting
.next/prerender-manifest.json, which already lists every statically
generated route, fully expanded, because Next.js itself resolved every
generateStaticParams() call to produce it. Zero reimplementation, zero
drift risk -- this is Next's own authoritative answer to "what static
routes actually exist," not a Python approximation of it.

web/app/**/page.tsx is still globbed here, but only to identify routes
that are genuinely NOT static (dynamic segments with no
generateStaticParams, i.e. Next's routes-manifest marks them
server-rendered "on demand" -- /share/[id], /dev/diagnostic-preview/[id],
/first-call/admin's underlying data, /api/*). Those are excluded from
orphan detection entirely (there is no fixed, enumerable "expected"
instance of a per-session dynamic route), not silently treated as
missing.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
WEB_DIR = REPO_ROOT / "web"
PRERENDER_MANIFEST_PATH = WEB_DIR / ".next" / "prerender-manifest.json"
ROUTES_MANIFEST_PATH = WEB_DIR / ".next" / "routes-manifest.json"
APP_DIR = WEB_DIR / "app"

# Routes that exist in the app tree but are legitimately excluded from
# orphan detection -- dev-only tooling, or genuinely per-instance dynamic
# with no fixed set of "expected" values.
EXCLUDED_PREFIXES = (
    "/api/",
    "/dev/",
    "/share/",
    "/first-call/admin",
)

# Exact-match, not prefix-match: browser-convention/file-based routes Next
# can register as "static routes" (a real file exists under app/) that are
# never meant to be reached via an <a href> link from page content -- a
# missing inbound link to /favicon.ico is not a site-structure problem.
EXCLUDED_EXACT_ROUTES = (
    "/favicon.ico",
    "/robots.txt",
    "/sitemap.xml",
    "/manifest.json",
    "/manifest.webmanifest",
    "/_global-error",
    "/_not-found",
)


@dataclass
class RouteManifest:
    static_routes: frozenset[str]
    dynamic_route_patterns: frozenset[str]  # e.g. "/share/[id]" -- informational only
    excluded_routes: frozenset[str]

    def is_orphan_candidate(self, path: str) -> bool:
        """
        True if `path` is a real static route that SHOULD be checked for
        orphan status (i.e. it's not a dev/admin/API/dynamic-per-instance
        route, and not a browser-convention file route like favicon.ico).
        """
        path = path.rstrip("/") or "/"
        if path in EXCLUDED_EXACT_ROUTES:
            return False
        if any(path.startswith(p) for p in EXCLUDED_PREFIXES):
            return False
        return path in self.static_routes


def _ensure_build(skip_build: bool = False) -> None:
    if skip_build and PRERENDER_MANIFEST_PATH.exists():
        return
    print("[route_manifest] running `npm run build` in web/ to produce a fresh "
          "prerender-manifest.json ...", file=sys.stderr)
    result = subprocess.run(
        ["npm", "run", "build"],
        cwd=str(WEB_DIR),
        capture_output=True,
        text=True,
        shell=(sys.platform == "win32"),
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"`npm run build` failed (exit {result.returncode}); sleuth cannot "
            f"trust a route manifest from a build that didn't succeed. "
            f"stderr tail:\n{result.stderr[-4000:]}"
        )


def _glob_dynamic_placeholders() -> frozenset[str]:
    """
    Informational only: page.tsx files under a `[segment]` directory,
    reported as their literal bracket pattern (e.g. "/share/[id]"), not
    resolved to real instances. Used only to sanity-check that every
    dynamic segment found on disk is accounted for in EXCLUDED_PREFIXES
    or in the prerender manifest's own dynamicRoutes list -- not used to
    build the expected-routes set itself.
    """
    patterns = set()
    for page in APP_DIR.rglob("page.tsx"):
        rel = page.relative_to(APP_DIR).parent
        # "(group)" folders are Next route groups -- stripped from the
        # URL, so dropped here too or "/(site)/share/[id]" would never
        # match the manifest's "/share/[id]".
        parts = [p for p in rel.parts
                 if p != "." and not (p.startswith("(") and p.endswith(")"))]
        if parts and any(p.startswith("[") for p in parts):
            patterns.add("/" + "/".join(parts))
    return frozenset(patterns)


def build_route_manifest(skip_build: bool = False) -> RouteManifest:
    _ensure_build(skip_build=skip_build)

    if not PRERENDER_MANIFEST_PATH.exists():
        raise FileNotFoundError(
            f"{PRERENDER_MANIFEST_PATH} still missing after build attempt -- "
            f"cannot build a route manifest without it."
        )

    prerender = json.loads(PRERENDER_MANIFEST_PATH.read_text(encoding="utf-8"))
    static_routes = set(prerender.get("routes", {}).keys())
    dynamic_routes = set(prerender.get("dynamicRoutes", {}).keys())

    # Sanity cross-check against the on-disk page.tsx tree, not a silent trust
    # fall -- warn (don't fail) if a dynamic segment on disk isn't reflected
    # anywhere in the manifest or the excluded-prefix list, since that would
    # mean a real route this tool doesn't know how to classify.
    disk_dynamic = _glob_dynamic_placeholders()
    unaccounted = []
    for pattern in disk_dynamic:
        if pattern in dynamic_routes:
            continue
        if any(pattern.startswith(p.rstrip("/")) for p in EXCLUDED_PREFIXES):
            continue
        unaccounted.append(pattern)
    if unaccounted:
        print(
            f"[route_manifest] WARNING: {len(unaccounted)} dynamic route "
            f"pattern(s) on disk are not in prerender-manifest's dynamicRoutes "
            f"and not in EXCLUDED_PREFIXES -- add them explicitly rather than "
            f"letting them silently pass or silently fail: {sorted(unaccounted)}",
            file=sys.stderr,
        )

    return RouteManifest(
        static_routes=frozenset(static_routes),
        dynamic_route_patterns=frozenset(dynamic_routes),
        excluded_routes=frozenset(EXCLUDED_PREFIXES),
    )


if __name__ == "__main__":
    manifest = build_route_manifest(skip_build="--skip-build" in sys.argv)
    print(f"{len(manifest.static_routes)} static routes, "
          f"{len(manifest.dynamic_route_patterns)} dynamic patterns")
    for r in sorted(manifest.static_routes):
        print(" ", r)
