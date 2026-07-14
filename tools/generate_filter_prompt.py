"""
Generate a Filter A/B/C consolidation prompt for a batch of candidates,
pulling exact source text from tools/consolidation_source_corpus.json so
nothing in the prompt is hand-typed, retyped from memory, or paraphrased —
the same fabrication risk this whole verification effort exists to catch,
just moved one step earlier in the pipeline.

Two modes:
  --list-names          Print every taxonomy state and experiment candidate
                         name currently in the corpus, so a batch config JSON
                         can be built without guessing at exact spelling.
  --config CONFIG.json  Generate a prompt from a batch config file (see
                         tools/batch_config_example.json for the format).
                         Writes tools/gemini_prompts/{batch_name}_prompt.txt
                         and also prints the prompt to stdout.

A name that doesn't match anything in the corpus is a hard abort, not a
skip — a silently-dropped candidate or check_against state is exactly the
kind of gap that produces an unverifiable Gemini response later.

NOTE on the hard-rules preamble below: this session's actual prior Filter
A/B/C prompts were never captured in this conversation — only Gemini's
responses to them were. The preamble is therefore NOT a verbatim copy of an
earlier prompt; it's built from (a) the Filter A/B/C framework definition
that IS on record in research/seven-experiments/consolidation-mapping-trace.md
(quoted directly, not paraphrased), and (b) explicit rules against every
failure pattern verify_gemini_quotes.py has actually caught across four real
responses this session: paraphrase-as-verbatim, unmarked ellipsis splicing,
self-quote misattribution, clause reordering, and silent omission.
"""
import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CORPUS_PATH = Path(__file__).resolve().parent / "consolidation_source_corpus.json"
PROMPTS_DIR = Path(__file__).resolve().parent / "gemini_prompts"

FILTER_DEFINITIONS = """\
FILTER A/B/C FRAMEWORK
(Verbatim from research/seven-experiments/consolidation-mapping-trace.md —
the same framework already used to disposition The Squeeze, E1, E4, and E5.)

Filter A — Severity vs. State: is this a tier/variant of another state, not a distinct condition?
Filter B — Root vs. Presenting Complaint: does this produce other states rather than standing alone?
Filter C — Sufficient Consequence Footprint: does it drive a genuinely distinct resolution path?

Outcome categories: STATE (survives as a named state), COLLAPSE (folds into an existing
state, usually as a severity/variant flag), ROOT (named as a root mechanism in resolution
design, not a standalone diagnostic state), ELIMINATE (dropped — fails Filter C entirely)."""

HARD_RULES = """\
HARD RULES — READ BEFORE STARTING

1. VERBATIM QUOTES ONLY. Every quote you use — from the candidate's own text or from any
   comparison state — must be an exact, contiguous substring of the source text supplied
   below. No paraphrasing, no rewording, no reordering of clauses, no summarizing-as-if-
   quoting. If you are not quoting a source's exact words, do not put it in quotation marks.

2. MARK ANY OMISSION. If you need to skip part of a quoted passage, use "..." at the exact
   point of the omission. Do not silently drop words, phrases, or parentheticals — an
   ellipsis-free quote is a claim that nothing was cut. Do not use "..." to splice together
   two segments that are not actually in that order in the source.

3. LABEL SELF-REFERENCE EXPLICITLY. If you quote the candidate's own text again while
   discussing a comparison state (for emphasis, or to restate the candidate's own claim),
   label it "(candidate's own text)" — do not present it as if it were a quote from the
   comparison state currently being discussed.

4. NAME WHAT YOU CLEARED. You do not need full Filter A/B/C reasoning for every one of the
   47 locked states — but state plainly which states you scanned and ruled out without a
   plausible match, so a human can see the sweep was real, not skipped.

5. FULL FILTER A/B/C REASONING is required for every check_against state listed for a
   candidate below — apply all three filters explicitly, not just an overall verdict.

6. FINAL DISPOSITION FORMAT — exactly this pattern, once per candidate, plain text (no
   backticks around the target name):
   **DISPOSITION:** STATE
   **DISPOSITION:** COLLAPSE (Target: Exact Taxonomy State Name)
   **DISPOSITION:** ROOT
   **DISPOSITION:** ELIMINATE
   Use the taxonomy state's exact name as written in the source text below — not a
   paraphrase, not a shortened form. If COLLAPSE, name exactly one target; if the
   candidate genuinely splits across two states, say so explicitly in prose rather than
   naming two states in one Target field."""

OUTPUT_FORMAT = """\
OUTPUT FORMAT — one section per candidate, in the order listed below:

#### [Candidate Name]

* **Candidate:** "[exact candidate text — copy from the SOURCE TEXT block below]"

##### Checks Against Existing States:

* **Check vs. [State Name]:** "[exact state text — copy from the SOURCE TEXT block below]"
* *Analysis:* [your reasoning — any quotes inside this prose must also be verbatim per Rule 1]

(repeat the "Check vs." pair for every check_against state listed for this candidate)

##### Filter Evaluation:

* **Filter A (Severity vs. State):** [Pass/Collapse — reasoning]
* **Filter B (Root vs. Presenting Complaint):** [Pass/Collapse — reasoning]
* **Filter C (Sufficient Consequence Footprint):** [Pass/Collapse — reasoning]

**DISPOSITION:** [STATE / COLLAPSE (Target: Exact Name) / ROOT / ELIMINATE]

---"""


def load_corpus() -> dict:
    if not CORPUS_PATH.exists():
        raise SystemExit(
            f"ABORT: corpus not found at {CORPUS_PATH}. "
            f"Run: python tools/verify_gemini_quotes.py --build-corpus"
        )
    return json.loads(CORPUS_PATH.read_text(encoding="utf-8"))


def cmd_list_names():
    corpus = load_corpus()

    print(f"--- Taxonomy states ({len(corpus['taxonomy_states'])}) ---")
    for name in corpus["taxonomy_state_names"]:
        print(f"  {name}")

    print(f"\n--- Book pieces ---")
    for key, piece in corpus["book_pieces"].items():
        print(f"  {key} ({piece['path']})")

    for tag, exp in corpus["experiments"].items():
        names = sorted(exp["candidates"].keys())
        print(f"\n--- {tag} candidates ({len(names)}) — {exp['path']} ---")
        for name in names:
            n_texts = len(exp["candidates"][name])
            note = f"  [{n_texts} text variants]" if n_texts > 1 else ""
            print(f"  {name}{note}")


def find_state_text(corpus: dict, name: str) -> str:
    for state in corpus["taxonomy_states"].values():
        if state["name"] == name:
            return state["description"]
    raise SystemExit(
        f"ABORT: check_against state '{name}' not found in corpus taxonomy_states.\n"
        f"Run --list-names to see exact spelling. Refusing to silently skip it."
    )


def find_candidate_texts(corpus: dict, name: str, source_file: str) -> list:
    exp = corpus["experiments"].get(source_file)
    if exp is None:
        raise SystemExit(
            f"ABORT: unknown source_file '{source_file}' — expected one of "
            f"{', '.join(corpus['experiments'].keys())}."
        )
    texts = exp["candidates"].get(name)
    if not texts:
        raise SystemExit(
            f"ABORT: candidate '{name}' not found in {source_file}'s corpus candidates.\n"
            f"Run --list-names to see exact spelling. Refusing to silently skip it."
        )
    return texts


def build_prompt(config: dict, corpus: dict) -> str:
    batch_name = config["batch_name"]
    lines = []
    lines.append(f"FILTER A/B/C CONSOLIDATION PASS — {batch_name}")
    lines.append("=" * 72)
    lines.append("")
    lines.append(FILTER_DEFINITIONS)
    lines.append("")
    lines.append(HARD_RULES)
    lines.append("")
    lines.append(OUTPUT_FORMAT)
    lines.append("")
    lines.append("=" * 72)
    lines.append("SOURCE TEXT — copy quotes from here exactly. Do not retype from memory.")
    lines.append("=" * 72)

    for c in config["candidates"]:
        name = c["name"]
        source_file = c["source_file"]
        cand_num = c.get("candidate_number", "")
        check_against = c.get("check_against", [])

        texts = find_candidate_texts(corpus, name, source_file)

        header = f"--- CANDIDATE: {name} ({source_file}"
        header += f" {cand_num})" if cand_num else ")"
        header += " ---"
        lines.append("")
        lines.append(header)

        if len(texts) == 1:
            lines.append(f'"{texts[0]}"')
        else:
            lines.append(
                f"({len(texts)} distinct texts exist in the corpus under this name — "
                f"quote whichever one is actually being referenced; do not blend them "
                f"into a single quote.)"
            )
            for i, t in enumerate(texts, 1):
                lines.append(f'  variant {i}: "{t}"')

        if not check_against:
            lines.append("")
            lines.append("  [NO check_against STATES SPECIFIED for this candidate — Pete/Claude")
            lines.append("   should confirm a plausible comparison set before this goes to Gemini.")
            lines.append("   Do not let Gemini pick its own comparison set unprompted.]")
        else:
            for state_name in check_against:
                state_text = find_state_text(corpus, state_name)
                lines.append("")
                lines.append(f"  CHECK AGAINST: {state_name}")
                lines.append(f'  "{state_text}"')

    lines.append("")
    lines.append("=" * 72)
    lines.append(f"END OF SOURCE TEXT — {len(config['candidates'])} candidates in this batch.")
    lines.append("=" * 72)

    return "\n".join(lines)


def cmd_generate(config_path: Path):
    config = json.loads(config_path.read_text(encoding="utf-8"))
    corpus = load_corpus()

    prompt = build_prompt(config, corpus)

    PROMPTS_DIR.mkdir(exist_ok=True)
    slug = re.sub(r"[^a-z0-9]+", "_", config["batch_name"].lower()).strip("_")
    out_path = PROMPTS_DIR / f"{slug}_prompt.txt"
    out_path.write_text(prompt, encoding="utf-8")

    print(prompt)
    print(f"\nWrote: {out_path}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--list-names", action="store_true",
                        help="Print every taxonomy state and experiment candidate name in the corpus")
    group.add_argument("--config", metavar="CONFIG.json",
                        help="Generate a prompt from a batch config JSON file")
    args = parser.parse_args()

    if args.list_names:
        cmd_list_names()
    else:
        path = Path(args.config)
        if not path.exists():
            raise SystemExit(f"ABORT: config not found: {path}")
        cmd_generate(path)


if __name__ == "__main__":
    main()
