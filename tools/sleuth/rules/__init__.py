"""
tools/sleuth/rules -- the four rule engines (structural, brand, content,
candidate). Each module exposes a single `check(crawl, **kwargs) ->
list[Finding]` function. See tools/sleuth/rules/finding.py for the shared
Finding shape and the deterministic/candidate tier distinction.
"""
from tools.sleuth.rules.finding import Finding, Tier

__all__ = ["Finding", "Tier"]
