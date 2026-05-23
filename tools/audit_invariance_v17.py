"""
Invariance audit v17: verify S18 locks, v16 contrast locks, and v17 new values
by reading engine/data/questions.py as text and parsing field values directly.
"""
import re
from pathlib import Path

src = Path(__file__).parents[1] / "engine" / "data" / "questions.py"
text = src.read_text(encoding="utf-8")

# Parse each question block into option->field->value map
# Pattern: "QXX": { "A": {...}, "B": {...}, ... }
def parse_questions(text):
    qs = {}
    q_pat = re.compile(r'"(Q\d+)"\s*:\s*\{', re.MULTILINE)
    opt_pat = re.compile(r'"([A-Z])"\s*:\s*\{([^}]+)\}', re.MULTILINE)
    field_pat = re.compile(r'"(\w+)"\s*:\s*(-?\d+\.\d+|-?\d+)')

    for qm in q_pat.finditer(text):
        qid = qm.group(1)
        # Find the block after this match — scan ahead for option lines
        block_start = qm.end()
        # Find matching closing brace (simple: grab up to next top-level "QXX": or end)
        next_q = q_pat.search(text, block_start)
        block_end = next_q.start() if next_q else len(text)
        block = text[block_start:block_end]

        opts = {}
        for om in opt_pat.finditer(block):
            opt_key = om.group(1)
            opt_body = om.group(2)
            fields = {}
            for fm in field_pat.finditer(opt_body):
                fname = fm.group(1)
                fval = float(fm.group(2))
                fields[fname] = fval
            opts[opt_key] = fields
        qs[qid] = opts
    return qs

qs = parse_questions(text)

S18_LOCKS = [
    ("Q02", "B", "authority_liability", 0.25),
    ("Q04", "D", "authority_liability", 0.25),
    ("Q10", "C", "authority_liability", 0.25),
    ("Q11", "C", "attitude_liability",  0.50),
    ("Q11", "C", "authority_liability", 0.05),
    ("Q15", "C", "attitude_liability",  0.50),
    ("Q15", "C", "authority_liability", 0.25),
    ("Q15", "C", "alliance_liability",  -0.15),
    ("Q23", "C", "attitude_liability",  0.50),
    ("Q23", "D", "attitude_liability",  0.50),
]

V16_LOCKS = [
    ("Q14", "B", "aptitude_liability",  -0.05),
    ("Q14", "C", "aptitude_liability",  -0.05),
    ("Q16", "B", "aptitude_liability",  -0.20),
    ("Q16", "C", "aptitude_liability",  -0.20),
    ("Q22", "B", "authority_liability", -0.10),
    ("Q26", "C", "authority_liability", -0.30),
    ("Q35", "B", "authority_liability", -0.35),
    ("Q36", "E", "authority_liability", -0.40),
]

V17_CHECKS = [
    ("Q07", "B", "alliance_liability",  0.80),
    ("Q11", "D", "attitude_liability",  0.75),
    ("Q15", "D", "attitude_liability",  0.75),
    ("Q26", "C", "alliance_liability",  0.80),
    ("Q35", "B", "aptitude_liability",  0.80),
    ("Q36", "E", "aptitude_liability",  0.80),
    ("Q01", "B", "authority_liability", -0.15),
    ("Q28", "B", "authority_liability", -0.15),
    ("Q13", "E", "authority_liability", -0.15),
    ("Q13", "E", "authority_asset",     0.40),   # must still be present
]

all_ok = True

for locks, label in [(S18_LOCKS, "S18"), (V16_LOCKS, "v16-contrast"), (V17_CHECKS, "v17-new")]:
    for (q, opt, field, expected) in locks:
        opts = qs.get(q, {})
        fields = opts.get(opt, {})
        actual = fields.get(field, "MISSING")
        ok = (abs(actual - expected) < 1e-9) if isinstance(actual, float) else False
        status = "OK  " if ok else "FAIL"
        if not ok:
            all_ok = False
        print(f"[{status}] {label:12s}  {q}-{opt}.{field:22s}  expected={expected:6.2f}  actual={actual}")

print()
print("INVARIANCE PASS" if all_ok else "INVARIANCE FAIL — see above")
