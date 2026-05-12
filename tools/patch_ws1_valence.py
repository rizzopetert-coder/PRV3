"""
PRV3 Session 15 — Workstream 1: Bulk valence template application, Q01–Q34.

Adds _opt_contrib entries for all Q01–Q34 questions that have NO DE options.
Questions with DE options (Q02, Q06, Q13, Q18, Q22, Q23, Q27A, Q32) are
handled in Workstream 2 — adding them here would cause KeyError in dispatch.

Q03B and Q03A-D-FOLLOW are excluded — routing questions, not P/F/A.

Template applied:
  P: primary_liability = HIGH(0.60) or MED(0.50); secondary = 50% of primary
  F: primary_asset = 0.40 only; no secondary signal
  A: primary_liability = 0.25 only; no secondary signal

Dual-dimension rule (Pete confirmed):
  P → primary full value + secondary 50%; F/A → primary only.

_opt_apt crossover folded into P options for Q03A and Q19.
Q31 seed mismatch corrected: authority+alliance (targets include decision_blindness).
Q32 dimension corrected: attitude (not authority/alliance) per Flag B — handled in WS2.

Usage:
    python tools/patch_ws1_valence.py --dry-run
    python tools/patch_ws1_valence.py --write
"""
import sys
import argparse
from pathlib import Path

TARGET = Path(__file__).parents[1] / "engine" / "data" / "questions.py"
ANCHOR = '        "Q35": {'

# ---------------------------------------------------------------------------
# The WS1 _opt_contrib entries — inserted immediately before "Q35": {
# ---------------------------------------------------------------------------
# Field shorthand (in the actual dict keys):
#   authority_liability / authority_asset
#   aptitude_liability  / aptitude_asset
#   alliance_liability  / alliance_asset
#   attitude_liability  / attitude_asset
#
# P/F/A tier key:
#   HIGH states in targets → P primary = 0.60, secondary = 0.30
#   MED  states in targets → P primary = 0.50, secondary = 0.25
# ---------------------------------------------------------------------------

WS1_BLOCK = '''\
        # -- WS1: bulk valence template, Q01–Q34 (Session 15) ------------------
        # Questions with DE options deferred to WS2: Q02 Q06 Q13 Q18 Q22 Q23 Q27A Q32
        # Q03B and Q03A-D-FOLLOW excluded (routing questions).
        "Q01": {  # Authority HIGH (founders_grip). Single-seeded.
            "A": {**_z, "authority_asset":    0.40},                    # F
            "B": {**_z, "authority_liability": 0.25},                   # A
            "C": {**_z, "authority_liability": 0.60},                   # P
            "D": {**_z, "authority_liability": 0.60},                   # P
            "E": {**_z, "authority_liability": 0.60},                   # P
        },
        "Q03A": {  # Authority HIGH + Attitude (dual). _opt_apt crossover folded.
            "A": {**_z, "authority_asset":     0.40},                   # F
            "B": {**_z, "authority_liability": 0.60, "attitude_liability": 0.30,
                        "aptitude_liability":  0.25},                   # P + crossover
            "C": {**_z, "authority_liability": 0.60, "attitude_liability": 0.30,
                        "aptitude_liability":  0.25},                   # P + crossover
            "D": {**_z, "authority_liability": 0.25},                   # A
        },
        "Q04": {  # Authority HIGH + Attitude (dual).
            "A": {**_z, "authority_asset":     0.40},                   # F
            "B": {**_z, "authority_liability": 0.25},                   # A
            "C": {**_z, "authority_liability": 0.25},                   # A
            "D": {**_z, "authority_liability": 0.60, "attitude_liability": 0.30},  # P
        },
        "Q05": {  # Attitude HIGH (the_untouchable). Single-seeded.
            "A": {**_z, "attitude_asset":     0.40},                    # F
            "B": {**_z, "attitude_liability": 0.25},                    # A
            "C": {**_z, "attitude_liability": 0.60},                    # P
            "D": {**_z, "attitude_liability": 0.60},                    # P
        },
        "Q07": {  # Alliance HIGH (the_fracture) + Authority (dual).
            "A": {**_z, "alliance_liability": 0.25},                    # A
            "B": {**_z, "alliance_liability": 0.60, "authority_liability": 0.30},  # P
            "C": {**_z, "alliance_liability": 0.60, "authority_liability": 0.30},  # P
            "D": {**_z, "alliance_liability": 0.60, "authority_liability": 0.30},  # P
        },
        "Q08": {  # No seed. Attitude MED (leadership_deafness) + Alliance (dual).
            "A": {**_z, "attitude_asset":     0.40},                    # F
            "B": {**_z, "attitude_liability": 0.25},                    # A
            "C": {**_z, "attitude_liability": 0.50, "alliance_liability": 0.25},   # P
            "D": {**_z, "attitude_liability": 0.50, "alliance_liability": 0.25},   # P
        },
        "Q09": {  # Alliance HIGH (the_fracture) + Authority (dual).
            "A": {**_z, "alliance_asset":     0.40},                    # F
            "B": {**_z, "alliance_liability": 0.25},                    # A
            "C": {**_z, "alliance_liability": 0.60, "authority_liability": 0.30},  # P
            "D": {**_z, "alliance_liability": 0.60, "authority_liability": 0.30},  # P
            "E": {**_z, "alliance_liability": 0.60, "authority_liability": 0.30},  # P
        },
        "Q10": {  # Aptitude HIGH (paper_tiger) + Authority (dual).
            "A": {**_z, "aptitude_asset":     0.40},                    # F
            "B": {**_z, "aptitude_liability": 0.25},                    # A
            "C": {**_z, "aptitude_liability": 0.60, "authority_liability": 0.30},  # P
            "D": {**_z, "aptitude_liability": 0.60, "authority_liability": 0.30},  # P
        },
        "Q11": {  # Attitude MED + Authority (dual).
            "A": {**_z, "attitude_asset":     0.40},                    # F
            "B": {**_z, "attitude_liability": 0.25},                    # A
            "C": {**_z, "attitude_liability": 0.50, "authority_liability": 0.25},  # P
            "D": {**_z, "attitude_liability": 0.50, "authority_liability": 0.25},  # P
            "E": {**_z, "attitude_liability": 0.50, "authority_liability": 0.25},  # P
        },
        "Q12": {  # Attitude HIGH (the_untouchable). Single-seeded.
            "A": {**_z, "attitude_asset":     0.40},                    # F
            "B": {**_z, "attitude_liability": 0.25},                    # A
            "C": {**_z, "attitude_liability": 0.60},                    # P
            "D": {**_z, "attitude_liability": 0.60},                    # P
            "E": {**_z, "attitude_liability": 0.25},                    # A
        },
        "Q14": {  # Authority MED (pay_exposure, pay_fog) + Aptitude (dual).
            "A": {**_z, "authority_asset":     0.40},                   # F
            "B": {**_z, "authority_liability": 0.25},                   # A
            "C": {**_z, "authority_liability": 0.25},                   # A
            "D": {**_z, "authority_liability": 0.50, "aptitude_liability": 0.25},  # P
            "E": {**_z, "authority_liability": 0.50, "aptitude_liability": 0.25},  # P
        },
        "Q15": {  # Attitude MED (diversity_ceiling) + Authority (dual).
            "A": {**_z, "attitude_asset":     0.40},                    # F
            "B": {**_z, "attitude_liability": 0.25},                    # A
            "C": {**_z, "attitude_liability": 0.50, "authority_liability": 0.25},  # P
            "D": {**_z, "attitude_liability": 0.50, "authority_liability": 0.25},  # P
            "E": {**_z, "attitude_liability": 0.50, "authority_liability": 0.25},  # P
        },
        "Q16": {  # Attitude MED (diversity_ceiling) + Authority (dual).
            "A": {**_z, "attitude_asset":     0.40},                    # F
            "B": {**_z, "attitude_liability": 0.50, "authority_liability": 0.25},  # P
            "C": {**_z, "attitude_liability": 0.50, "authority_liability": 0.25},  # P
            "D": {**_z, "attitude_liability": 0.50, "authority_liability": 0.25},  # P
            "E": {**_z, "attitude_liability": 0.25},                    # A
        },
        "Q17": {  # Attitude MED + Alliance (dual). All targets are Attitude.
            "A": {**_z, "attitude_asset":     0.40},                    # F
            "B": {**_z, "attitude_liability": 0.50, "alliance_liability": 0.25},   # P
            "C": {**_z, "attitude_liability": 0.50, "alliance_liability": 0.25},   # P
            "D": {**_z, "attitude_liability": 0.50, "alliance_liability": 0.25},   # P
            "E": {**_z, "attitude_liability": 0.50, "alliance_liability": 0.25},   # P
        },
        "Q19": {  # Authority MED + Attitude (dual). _opt_apt crossover folded.
            "A": {**_z, "authority_asset":     0.40},                   # F
            "B": {**_z, "authority_liability": 0.25},                   # A
            "C": {**_z, "authority_liability": 0.50, "attitude_liability": 0.25,
                        "aptitude_liability":  0.25},                   # P + crossover
            "D": {**_z, "authority_liability": 0.50, "attitude_liability": 0.25,
                        "aptitude_liability":  0.25},                   # P + crossover
        },
        "Q20": {  # Aptitude HIGH (built_to_fail) + Authority (dual).
            "A": {**_z, "aptitude_asset":     0.40},                    # F
            "B": {**_z, "aptitude_liability": 0.25},                    # A
            "C": {**_z, "aptitude_liability": 0.60, "authority_liability": 0.30},  # P
            "D": {**_z, "aptitude_liability": 0.60, "authority_liability": 0.30},  # P
        },
        "Q21": {  # Authority MED + Alliance (dual).
            "A": {**_z, "authority_asset":     0.40},                   # F
            "B": {**_z, "authority_liability": 0.25},                   # A
            "C": {**_z, "authority_liability": 0.50, "alliance_liability": 0.25},  # P
            "D": {**_z, "authority_liability": 0.50, "alliance_liability": 0.25},  # P
            "E": {**_z, "authority_liability": 0.50, "alliance_liability": 0.25},  # P
        },
        "Q24": {  # Attitude MED (invisible_burnout) + Alliance (dual).
            "A": {**_z, "attitude_asset":     0.40},                    # F
            "B": {**_z, "attitude_liability": 0.50, "alliance_liability": 0.25},   # P
            "C": {**_z, "attitude_liability": 0.50, "alliance_liability": 0.25},   # P
            "D": {**_z, "attitude_liability": 0.50, "alliance_liability": 0.25},   # P
        },
        "Q25": {  # Aptitude MED (dormant_talent, unformed_leader) + Authority (dual).
            "A": {**_z, "aptitude_asset":     0.40},                    # F
            "B": {**_z, "aptitude_liability": 0.25},                    # A
            "C": {**_z, "aptitude_liability": 0.50, "authority_liability": 0.25},  # P
            "D": {**_z, "aptitude_liability": 0.50, "authority_liability": 0.25},  # P
            "E": {**_z, "aptitude_liability": 0.50, "authority_liability": 0.25},  # P
        },
        "Q26": {  # Alliance HIGH (the_fracture) + Authority (dual).
            "A": {**_z, "alliance_asset":     0.40},                    # F
            "B": {**_z, "alliance_liability": 0.25},                    # A
            "C": {**_z, "alliance_liability": 0.60, "authority_liability": 0.30},  # P
            "D": {**_z, "alliance_liability": 0.60, "authority_liability": 0.30},  # P
        },
        "Q27B": {  # No seed. Attitude MED (C-Culture cluster). Single-dim.
            "A": {**_z, "attitude_asset":     0.40},                    # F
            "B": {**_z, "attitude_liability": 0.50},                    # P
            "C": {**_z, "attitude_liability": 0.50},                    # P
            "D": {**_z, "attitude_liability": 0.50},                    # P
            "E": {**_z, "attitude_liability": 0.50},                    # P
        },
        "Q28": {  # Authority HIGH (unsolved_problem) + Attitude (dual).
            "A": {**_z, "authority_asset":     0.40},                   # F
            "B": {**_z, "authority_liability": 0.25},                   # A
            "C": {**_z, "authority_liability": 0.60, "attitude_liability": 0.30},  # P
            "D": {**_z, "authority_liability": 0.60, "attitude_liability": 0.30},  # P
        },
        "Q29": {  # Attitude MED (diversity_ceiling) + Authority (dual).
            "A": {**_z, "attitude_asset":     0.40},                    # F
            "B": {**_z, "attitude_liability": 0.50, "authority_liability": 0.25},  # P
            "C": {**_z, "attitude_liability": 0.50, "authority_liability": 0.25},  # P
            "D": {**_z, "attitude_liability": 0.50, "authority_liability": 0.25},  # P
            "E": {**_z, "attitude_liability": 0.25},                    # A
        },
        "Q30": {  # Authority MED + Alliance (dual).
            "A": {**_z, "authority_asset":     0.40},                   # F
            "B": {**_z, "authority_liability": 0.25},                   # A
            "C": {**_z, "authority_liability": 0.25},                   # A
            "D": {**_z, "authority_liability": 0.50, "alliance_liability": 0.25},  # P
        },
        "Q31": {  # Authority HIGH (unsolved_problem) + Alliance (dual).
            # Seed had attitude but targets include decision_blindness (Alliance HIGH).
            # Corrected to authority+alliance to match actual targets.
            "A": {**_z, "authority_liability": 0.25},                   # A
            "B": {**_z, "authority_liability": 0.60, "alliance_liability": 0.30},  # P
            "C": {**_z, "authority_liability": 0.60, "alliance_liability": 0.30},  # P
            "D": {**_z, "authority_liability": 0.60, "alliance_liability": 0.30},  # P
        },
        "Q33": {  # Authority MED + Aptitude (dual).
            "A": {**_z, "authority_asset":     0.40},                   # F
            "B": {**_z, "authority_liability": 0.25},                   # A
            "C": {**_z, "authority_liability": 0.50, "aptitude_liability": 0.25},  # P
            "D": {**_z, "authority_liability": 0.50, "aptitude_liability": 0.25},  # P
        },
        "Q34": {  # Attitude MED + Alliance (dual). All targets are Attitude.
            "A": {**_z, "attitude_liability": 0.25},                    # A
            "B": {**_z, "attitude_liability": 0.25},                    # A
            "C": {**_z, "attitude_liability": 0.50, "alliance_liability": 0.25},   # P
            "D": {**_z, "attitude_liability": 0.50, "alliance_liability": 0.25},   # P
            "E": {**_z, "attitude_liability": 0.25},                    # A
        },
        # -- End WS1 entries ----------------------------------------------------
'''


def run(dry_run: bool) -> None:
    src = TARGET.read_text(encoding="utf-8")

    count = src.count(ANCHOR)
    if count != 1:
        print(f"ERROR: anchor found {count} times (expected 1). Aborting.")
        sys.exit(1)

    new_src = src.replace(ANCHOR, WS1_BLOCK + ANCHOR, 1)

    if dry_run:
        print("DRY-RUN — patch_ws1_valence.py")
        print(f"Target : {TARGET}")
        print(f"Anchor : {ANCHOR!r}")
        print(f"Lines inserted: {WS1_BLOCK.count(chr(10))}")
        print()
        print("--- INSERTION BLOCK (first 60 lines) ---")
        for i, line in enumerate(WS1_BLOCK.splitlines()[:60], 1):
            print(f"{i:3}: {line}")
        print("...")
        print()
        print("Dual-seeded questions in WS1 block:")
        dual = [
            ("Q03A", "Authority HIGH(0.60)", "Attitude(0.30)", "+ apt_l 0.25 crossover on P"),
            ("Q04",  "Authority HIGH(0.60)", "Attitude(0.30)", ""),
            ("Q07",  "Alliance  HIGH(0.60)", "Authority(0.30)", ""),
            ("Q08",  "Attitude  MED (0.50)", "Alliance (0.25)", "no seed — dim derived from targets"),
            ("Q09",  "Alliance  HIGH(0.60)", "Authority(0.30)", ""),
            ("Q10",  "Aptitude  HIGH(0.60)", "Authority(0.30)", ""),
            ("Q11",  "Attitude  MED (0.50)", "Authority(0.25)", ""),
            ("Q14",  "Authority MED (0.50)", "Aptitude (0.25)", ""),
            ("Q15",  "Attitude  MED (0.50)", "Authority(0.25)", ""),
            ("Q16",  "Attitude  MED (0.50)", "Authority(0.25)", ""),
            ("Q17",  "Attitude  MED (0.50)", "Alliance (0.25)", "targets all Attitude; Alliance from seed"),
            ("Q19",  "Authority MED (0.50)", "Attitude (0.25)", "+ apt_l 0.25 crossover on P"),
            ("Q20",  "Aptitude  HIGH(0.60)", "Authority(0.30)", ""),
            ("Q21",  "Authority MED (0.50)", "Alliance (0.25)", ""),
            ("Q24",  "Attitude  MED (0.50)", "Alliance (0.25)", ""),
            ("Q25",  "Aptitude  MED (0.50)", "Authority(0.25)", ""),
            ("Q26",  "Alliance  HIGH(0.60)", "Authority(0.30)", ""),
            ("Q28",  "Authority HIGH(0.60)", "Attitude (0.30)", ""),
            ("Q29",  "Attitude  MED (0.50)", "Authority(0.25)", ""),
            ("Q30",  "Authority MED (0.50)", "Alliance (0.25)", ""),
            ("Q31",  "Authority HIGH(0.60)", "Alliance (0.30)", "seed corrected: was attitude, targets include decision_blindness"),
            ("Q33",  "Authority MED (0.50)", "Aptitude (0.25)", ""),
            ("Q34",  "Attitude  MED (0.50)", "Alliance (0.25)", "targets all Attitude; Alliance from seed"),
        ]
        print(f"{'QID':<8} {'Primary':<22} {'Secondary':<18} Notes")
        print("-" * 80)
        for qid, pri, sec, note in dual:
            print(f"{qid:<8} {pri:<22} {sec:<18} {note}")
        print()
        print("Single-seeded in WS1 block:")
        print("  Q01  Authority HIGH(0.60)  (no secondary)")
        print("  Q05  Attitude  HIGH(0.60)  (no secondary)")
        print("  Q12  Attitude  HIGH(0.60)  (no secondary)")
        print("  Q27B Attitude  MED (0.50)  (no seed — C-Culture cluster, dim from targets)")
        print()
        print("WS2 scope (DE options — added in WS2, complete entry per question):")
        print("  Q02 Q06 Q13 Q18 Q22 Q23 Q27A Q32")
        print()
        print("Excluded (routing questions — unchanged):")
        print("  Q03B  Q03A-D-FOLLOW")
        print()
        print("No file written. Pass --write to apply.")
    else:
        TARGET.write_text(new_src, encoding="utf-8")
        print(f"Written: {TARGET}")
        print("Verifying import...")
        import importlib, importlib.util
        spec = importlib.util.spec_from_file_location("questions", TARGET)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        lib = mod.QUESTION_LIBRARY
        ws1_ids = [
            "Q01","Q03A","Q04","Q05","Q07","Q08","Q09","Q10","Q11","Q12",
            "Q14","Q15","Q16","Q17","Q19","Q20","Q21","Q24","Q25","Q26",
            "Q27B","Q28","Q29","Q30","Q31","Q33","Q34",
        ]
        ok = 0
        for qid in ws1_ids:
            q = lib[qid]
            for opt in q.answer_options:
                _ = opt.dimensional_contributions  # triggers KeyError if missing
            ok += 1
        print(f"Import OK. {ok}/{len(ws1_ids)} WS1 questions verified (no KeyError).")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--write",   action="store_true")
    args = parser.parse_args()
    if not args.dry_run and not args.write:
        parser.print_help()
        sys.exit(1)
    run(dry_run=args.dry_run)
