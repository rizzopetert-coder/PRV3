"""
web/components/ContextOrientation.tsx: fix a real WCAG AA contrast
failure on the trigger button, root-caused precisely before touching
anything.

sleuth's full-site crawl flagged this element (`.md:inline-flex >
.align-middle`) on the vast majority of pages -- it renders wherever
ContextOrientation is used (BookPieceContent, book/toc, DiagnosticFlow,
PrivateOutput, ShareableOutput), so it's a single component, not
several unrelated instances sharing a class name (confirmed by reading
the component, not assumed from the selector alone).

Root cause, confirmed via live axe-core measurement (not a CSS-value
calculation -- the declared color, text-[color:var(--slate)], actually
clears real AA against --field as plain text in every theme, matching
the same token already verified fine on ServiceSidebar). The trigger's
wrapping <div> carries `data-emphasis={resolved ? "primary" : "receded"}`,
and globals.css's locked "recede/resolve" interaction mechanic sets
`[data-emphasis="receded"] { opacity: 0.55; }`. Since `resolved` starts
false and the trigger is the ONLY thing rendered before the panel opens
(the panel itself doesn't exist in the DOM until resolved -- {resolved
&& (...)}), this mechanic's only visible effect here is a PERMANENT
55% dimming of the trigger at rest. Verified live: axe measures 2.14-
2.92:1 depending on theme, well under the 4.5:1 minimum -- not a
borderline case.

This is a real accessibility problem beyond contrast alone: a
persistently-needed "learn more" affordance shouldn't render
permanently faded by default, on every page it appears on, until a
user happens to hover or focus it. The recede/resolve mechanic makes
sense for content that's genuinely one-of-several-unselected-options
(its documented original use case) -- this trigger isn't that; it's a
standalone, always-actionable affordance, not competing for attention
against sibling choices.

Fix: `data-emphasis={resolved ? "primary" : "receded"}` removed from
the always-rendered outer wrapper entirely -- not moved, just deleted.
Confirmed safe by reading `desktopPanel`'s own definition: it already
hardcodes `data-emphasis="primary"` on its own root div (line 102),
independent of the outer wrapper -- so the outer wrapper's version was
redundant for the panel's own styling and only ever mattered for
dimming the trigger. Removing it changes nothing about the panel's
appearance (still primary/opacity:1 whenever it exists in the DOM) and
only removes the permanent dimming of the trigger that sits alongside
it. The mobile trigger (already at full opacity, never wrapped in
data-emphasis) is unchanged.

Flagged, not silently decided: this does touch the locked recede/
resolve mechanic's application on this one component. The fix removes
it from the trigger's own rendering, not from the mechanic itself
(unchanged everywhere else it's used -- ConstellationField,
self-selection interface, etc.). Held for review before commit per
standing instruction.

Usage:
    python tools/patch_contrast_context_orientation.py --dry-run
    python tools/patch_contrast_context_orientation.py --write
"""
import argparse
import pathlib
import sys

PATH = pathlib.Path('web/components/ContextOrientation.tsx')

OLD = '''  return (
    <div
      className={`${variant === "floating" ? "fixed z-30" : "relative inline-block"} ${
        className ?? ""
      }`}
      data-emphasis={resolved ? "primary" : "receded"}
    >
      <button
        {...triggerCommon}
        aria-describedby={resolved ? panelId : undefined}
        aria-haspopup={variant === "modal-drawer" ? "dialog" : undefined}
        aria-expanded={variant === "modal-drawer" ? resolved : resolved || open}
        className={`hidden md:inline-flex items-center ${triggerClass}`}
        onMouseEnter={variant !== "modal-drawer" ? () => setResolved(true) : undefined}
        onFocus={variant !== "modal-drawer" ? () => setResolved(true) : undefined}
        onBlur={variant !== "modal-drawer" ? () => setResolved(false) : undefined}
        onClick={variant === "modal-drawer" ? () => setResolved((cur) => !cur) : undefined}
      >
        <TriggerLabel title={title} />
      </button>
      {desktopPanel}'''

NEW = '''  return (
    <div
      className={`${variant === "floating" ? "fixed z-30" : "relative inline-block"} ${
        className ?? ""
      }`}
    >
      <button
        {...triggerCommon}
        aria-describedby={resolved ? panelId : undefined}
        aria-haspopup={variant === "modal-drawer" ? "dialog" : undefined}
        aria-expanded={variant === "modal-drawer" ? resolved : resolved || open}
        className={`hidden md:inline-flex items-center ${triggerClass}`}
        onMouseEnter={variant !== "modal-drawer" ? () => setResolved(true) : undefined}
        onFocus={variant !== "modal-drawer" ? () => setResolved(true) : undefined}
        onBlur={variant !== "modal-drawer" ? () => setResolved(false) : undefined}
        onClick={variant === "modal-drawer" ? () => setResolved((cur) => !cur) : undefined}
      >
        <TriggerLabel title={title} />
      </button>
      {desktopPanel}'''


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true')
    g.add_argument('--write', action='store_true')
    args = ap.parse_args()

    content = PATH.read_text(encoding='utf-8')
    count = content.count(OLD)
    if count != 1:
        print(f'ERROR: anchor found {count} times, expected exactly 1.', file=sys.stderr)
        sys.exit(1)

    new_content = content.replace(OLD, NEW, 1)

    if args.dry_run:
        print('DRY RUN -- anchor found exactly once, replacement would apply cleanly.')
        print(f'Old length: {len(content)}, new length: {len(new_content)}, delta: {len(new_content) - len(content)}')
    else:
        PATH.write_text(new_content, encoding='utf-8')
        print('WRITE complete.')
        print(f'Old length: {len(content)}, new length: {len(new_content)}, delta: {len(new_content) - len(content)}')


if __name__ == '__main__':
    main()
