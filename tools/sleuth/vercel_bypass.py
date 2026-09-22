"""
tools/sleuth/vercel_bypass.py -- Vercel Protection Bypass for Automation,
mechanics verified against Vercel's current docs (fetched this session,
"Protection Bypass for Automation", last_updated 2026-09-16) rather than
assumed from memory, per the build brief's explicit instruction.

Confirmed mechanics:
- Header `x-vercel-protection-bypass: <secret value>` (not a token name --
  the literal secret value goes in the header).
- For multi-page, in-browser automation specifically (a BFS crawl across
  many navigations in one browser context is exactly this case, not a
  single stateless request), Vercel's own docs recommend ALSO sending
  `x-vercel-set-bypass-cookie: true` alongside the header on requests --
  this makes Vercel set the bypass as a cookie via a redirect's Set-Cookie
  header, so subsequent navigations in the same context stay authenticated
  without needing to re-send the header on every single request. Their own
  documented Playwright example sets both via `extraHTTPHeaders`, which is
  also what this module targets (the Node crawler sets both as default
  context-level extra headers, so literally every request in the crawl
  carries both -- redundant with the cookie once set, but harmless, and
  removes any risk of a missed request falling through unauthenticated).
- `VERCEL_AUTOMATION_BYPASS_SECRET` is Vercel's own conventional env var
  name for the secret it auto-injects into deployments, but this tool
  reads the secret from whatever env var NAME is passed via --bypass-secret
  (the CLI flag takes an env var name, not the secret itself, so the
  secret itself never appears in shell history or process listings) --
  matching the build brief's own flag shape, not hardcoded to Vercel's
  own conventional name.
"""
from __future__ import annotations

import os


class BypassSecretMissingError(RuntimeError):
    pass


def resolve_bypass_secret(env_var_name: str) -> str:
    value = os.environ.get(env_var_name)
    if not value:
        raise BypassSecretMissingError(
            f"--bypass-secret was given as '{env_var_name}', but that "
            f"environment variable is unset or empty. Set it to the real "
            f"Vercel Protection Bypass for Automation secret before running "
            f"sleuth against a protected deployment."
        )
    return value


def build_bypass_headers(secret: str) -> dict[str, str]:
    return {
        "x-vercel-protection-bypass": secret,
        "x-vercel-set-bypass-cookie": "true",
    }
