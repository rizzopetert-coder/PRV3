"""Stage 6: two stale comments in web/lib/types.ts that named the deleted output-renderer.ts.
Usage: python tools/patch_stage6_comments.py --dry-run | --write"""
import sys
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "web/lib/types.ts"
EDITS = [
    ("// Imported by: output-renderer.ts, /api/result, /api/share/create, /api/share/[id]",
     "// Imported by: /api/result, /api/share/create, /api/share/[id]"),
    ("  // 9 real call sites (PrivateOutput.tsx, output-renderer.ts,",
     "  // 9 real call sites (PrivateOutput.tsx,"),
]
raw = P.read_bytes().decode("utf-8")
crlf = "\r\n" in raw
t = raw.replace("\r\n", "\n")
for o, n in EDITS:
    assert t.count(o) == 1, (t.count(o), o)
    t = t.replace(o, n)
print("2 edits ok")
if "--write" in sys.argv:
    P.write_bytes((t.replace("\n", "\r\n") if crlf else t).encode("utf-8"))
    print("WROTE")
