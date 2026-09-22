"""
tools/sleuth/rules/brand.py -- font-family, locked-color, rust-reservation,
and axe-core contrast/ARIA checks. All DETERMINISTIC tier per the build
brief. See tools/sleuth/tokens.py for how the locked color/font sets are
derived (confirmed against real source, not the build brief's stale
4-color/JetBrains-Mono assumption).

RUST-RESERVATION CHECK, redesigned mid-build after a real false-positive
was caught in this session's own test crawl: the brief's rule is "rust
color present on any element not classed/tagged as Endemic-severity."
An earlier version of this check matched computed color numerically
against --urgency/--urgency-text -- and immediately flagged every
--oxide-text element site-wide (hundreds of hits on /book alone),
because globals.css's own comment confirms --oxide/--oxide-text and
--urgency/--urgency-text are LITERALLY THE SAME hex value in both Warm
and Dark themes ("In Warm and Dark these currently share values; in
Neutral they diverge"). --oxide-text is the general, unrestricted
accent color, used everywhere by design -- so rust/urgency cannot be
distinguished from ordinary oxide usage by computed color alone in two
of the three themes. Checking computed color for this specific rule is
fundamentally unreliable, not just imprecise.

Redesigned to key off the literal Tailwind class name instead, which
does carry real intent: this check flags any element whose className
contains a `rust`-suffixed color utility (bg-rust, text-rust,
border-rust, ring-rust, from-rust, to-rust, via-rust -- the only
concrete, checkable rust reference that exists in this codebase, since
--urgency itself has no direct Tailwind utility mapped in globals.css's
`@theme inline` block and would only appear via verbose arbitrary-value
syntax). The one confirmed exception, ServiceSidebar.tsx's First Call
section (bg-rust, deliberate Pete-approved background fill, confirmed
via that file's own comment as the only bg-rust-as-background usage in
the codebase): matched narrowly by the element sitting inside an
`<a href="/first-call">` link, not by the class name alone -- exempting
on class name alone would exempt any future bg-rust misuse just because
it reused the same class, which defeats the point of an auto-fail
check.
"""
from __future__ import annotations

import re

from tools.sleuth.rules.finding import Category, Finding, Tier
from tools.sleuth.tokens import is_allowed_color, is_allowed_font, _to_rgb_tuple

_RUST_CLASS_RE = re.compile(r"(?:^|\s)(?:bg|text|border|ring|from|to|via)-rust(?:\s|$)")


def check(crawl: dict) -> list[Finding]:
    findings: list[Finding] = []

    for page in crawl.get("pages", []):
        url = page["url"]
        if page.get("navError"):
            continue

        for cs in page.get("computedStyles") or []:
            class_name = cs.get("className") or ""
            enclosing_href = cs.get("enclosingHref") or ""

            has_rust_class = bool(_RUST_CLASS_RE.search(f" {class_name} "))
            is_known_exception = has_rust_class and enclosing_href.rstrip("/").endswith("/first-call")
            if has_rust_class and not is_known_exception:
                findings.append(Finding(
                    tier=Tier.DETERMINISTIC, category=Category.BRAND,
                    rule_id="unreserved-rust-usage",
                    message="Rust-colored utility class found outside the one confirmed exception (ServiceSidebar's First Call section) -- rust is reserved for genuine Endemic-severity signaling.",
                    url=url, detail=f"<{cs.get('tag')}> \"{cs.get('textSample')}\" class=\"{class_name}\"",
                ))

            font = cs.get("fontFamily") or ""
            if font and not is_allowed_font(font):
                findings.append(Finding(
                    tier=Tier.DETERMINISTIC, category=Category.BRAND,
                    rule_id="off-brand-font",
                    message=f"Computed font-family '{font}' is outside the locked type set (Lora/Inter/IBM Plex Mono/Source Serif).",
                    url=url, detail=f"<{cs.get('tag')}> \"{cs.get('textSample')}\"",
                ))

            for field_name in ("color", "backgroundColor"):
                value = cs.get(field_name)
                if not value:
                    continue
                parsed = _to_rgb_tuple(value)
                if parsed is None or parsed[3] == 0.0:
                    continue

                if not is_allowed_color(value):
                    findings.append(Finding(
                        tier=Tier.DETERMINISTIC, category=Category.BRAND,
                        rule_id="off-brand-color",
                        message=f"Computed {field_name} '{value}' is outside the locked palette (checked against every color token defined in globals.css, all themes, plus standard neutrals).",
                        url=url, detail=f"<{cs.get('tag')}> \"{cs.get('textSample')}\" class=\"{class_name}\"",
                    ))

        for violation in page.get("axeViolations") or []:
            if violation.get("id") == "sleuth-axe-error":
                findings.append(Finding(
                    tier=Tier.CANDIDATE, category=Category.BRAND,
                    rule_id="axe-injection-error",
                    message="axe-core failed to run on this page (injection or evaluation error, not a real content finding).",
                    url=url, detail=violation.get("description", ""),
                ))
                continue
            findings.append(Finding(
                tier=Tier.DETERMINISTIC, category=Category.BRAND,
                rule_id=f"axe-{violation['id']}",
                message=f"{violation.get('help', violation['id'])} ({violation.get('nodes', 0)} node(s), impact: {violation.get('impact')}).",
                url=url, detail="; ".join(str(t) for t in violation.get("targets", [])),
            ))

    return findings
