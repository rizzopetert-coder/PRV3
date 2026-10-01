"""
Condensed intro copy (Pete's approved copy, 2026-09-30). The intro promised "a rough
sense of what it costs", false since Stage 3a hid the condensed dollar figure.
Replaced with: "It names the most prominent pattern in your answers. The full
diagnostic goes further." The leading sentence is kept.

Usage: python tools/patch_condensed_intro_copy.py --dry-run | --write
"""
import sys
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "web/components/CondensedDiagnosticFlow.tsx"
OLD = """          This is a thinner version of the full diagnostic. It names the most prominent pattern
          and gives you a rough sense of what it costs — the full diagnostic goes further.
"""
NEW = """          This is a thinner version of the full diagnostic. It names the most prominent pattern
          in your answers. The full diagnostic goes further.
"""
raw = P.read_bytes().decode("utf-8")
crlf = "\r\n" in raw
t = raw.replace("\r\n", "\n")
assert t.count(OLD) == 1, t.count(OLD)
t = t.replace(OLD, NEW)
print("1 edit ok", "CRLF" if crlf else "LF")
if "--write" in sys.argv:
    P.write_bytes((t.replace("\n", "\r\n") if crlf else t).encode("utf-8"))
    print("WROTE")
else:
    print("DRY RUN")
