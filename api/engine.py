import os
import sys
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse

# Add repo root to path so engine package resolves
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from engine.main import (
    run_engine,
    accumulate_answers,
    run_checkpoint,
    run_accumulated_engine,
    run_condensed_engine,
    get_question_copy,
)
from engine.friction_tax import get_industry_wage

app = FastAPI()

ENGINE_SECRET = os.environ.get("ENGINE_SECRET", "")


def _check_secret(request: Request) -> None:
    # Shared secret validation — reject before any engine work
    secret = request.headers.get("x-engine-secret", "")
    if not ENGINE_SECRET or secret != ENGINE_SECRET:
        raise HTTPException(status_code=401, detail="Unauthorized")


@app.post("/api/engine")
async def invoke_engine(request: Request):
    _check_secret(request)

    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    try:
        narrative_response = payload.get("narrative_response", "") if isinstance(payload, dict) else ""
        signal_map_context = payload.get("signal_map_context", "") if isinstance(payload, dict) else ""
        result = run_engine(
            payload,
            narrative_response=narrative_response,
            signal_map_context=signal_map_context,
        )
        return JSONResponse(content=result)
    except KeyError as e:
        # Bad state ID or missing intake field — client fault
        raise HTTPException(status_code=400, detail=f"Unknown state ID: {e}")
    except (TypeError, ValueError) as e:
        # Bad intake fields — client fault
        raise HTTPException(status_code=400, detail=f"Invalid payload: {e}")
    except Exception:
        # Engine failure — do not expose internals
        raise HTTPException(status_code=500, detail="Engine error")


# ── Path 1 (Session 71, Phase 1) — same FastAPI app, same Vercel build ────────
# Two new routes on the existing api/engine.py serverless function rather
# than a new Vercel build target — see vercel.json for the routing entries
# that point both paths at this same file.
#
# CONFIRMED INCIDENT, not a hypothetical warning (Category D, this session):
# adding a new @app.post route here is NOT enough on its own. vercel.json's
# "routes" array is an explicit allowlist, checked before its own catch-all
# ("/(.*)" -> "/web/$1") -- any path not listed there 404s against the
# Next.js app before this file's code ever runs, no matter how correct the
# Python handler is. /api/condensed-complete shipped without its vercel.json
# entry, produced a clean 404 in production with an empty body and no
# Python-side stack trace (nothing here ever executed), and was only found
# via Vercel's runtime error logs, not by reading this file. Add the
# vercel.json entry FIRST, or in the same commit, every time -- verify it
# explicitly, don't rely on remembering this comment.

@app.post("/api/accumulate")
async def accumulate(request: Request):
    _check_secret(request)

    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    try:
        accumulated_vector = payload.get("accumulated_vector", {}) if isinstance(payload, dict) else {}
        question_id = payload.get("question_id", "") if isinstance(payload, dict) else ""
        option_ids = payload.get("option_ids", []) if isinstance(payload, dict) else []
        intake = payload.get("intake", {}) if isinstance(payload, dict) else {}
        # Checkpoint 2 (SeverityResult per-state redesign) -- both optional,
        # absent from the payload for any question_id that isn't a SEVER-##
        # follow-on with a recorded origin. No Pydantic model exists on this
        # route to "mirror" -- confirmed via direct read, every field here
        # is manually parsed via payload.get(), not a typed BaseModel.
        trigger_question_id = payload.get("trigger_question_id", "") if isinstance(payload, dict) else ""
        triggering_option_id = payload.get("triggering_option_id", "") if isinstance(payload, dict) else ""
        # accumulate_answers() (A.2, this session -- wraps
        # accumulate_one_answer() once per selected option) returns
        # {"accumulated_vector", "severity_inputs", "severity_follow_on_ids",
        # "severity_follow_on_origins"} -- passed straight through as the
        # response body. The Next.js caller unpacks accumulated_vector for
        # the session's own vector, persists every severity_input into
        # session.severity_inputs, splices every severity_follow_on_id into
        # question_sequence (mirroring checkpoint distinguishers), and
        # records severity_follow_on_origins for later per-option
        # attribution (Checkpoint 2).
        result = accumulate_answers(
            accumulated_vector, question_id, option_ids, intake,
            trigger_question_id, triggering_option_id,
        )
        return JSONResponse(content=result)
    except KeyError as e:
        # Unknown question_id or option_id — client fault
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Engine error")


@app.post("/api/checkpoint")
async def checkpoint(request: Request):
    _check_secret(request)

    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    try:
        checkpoint_position = payload.get("checkpoint_position", "") if isinstance(payload, dict) else ""
        accumulated_vector = payload.get("accumulated_vector", {}) if isinstance(payload, dict) else {}
        answered_question_count = payload.get("answered_question_count", 0) if isinstance(payload, dict) else 0
        already_asked = payload.get("already_asked", []) if isinstance(payload, dict) else []
        result = run_checkpoint(
            checkpoint_position, accumulated_vector, answered_question_count, already_asked
        )
        return JSONResponse(content=result)
    except (TypeError, ValueError) as e:
        # Invalid checkpoint_position (engine.checkpoint.evaluate_checkpoint) —
        # client fault
        raise HTTPException(status_code=400, detail=f"Invalid payload: {e}")
    except Exception:
        raise HTTPException(status_code=500, detail="Engine error")


@app.post("/api/complete")
async def complete(request: Request):
    _check_secret(request)

    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    try:
        accumulated_vector = payload.get("accumulated_vector", {}) if isinstance(payload, dict) else {}
        intake = payload.get("intake", {}) if isinstance(payload, dict) else {}
        answered_question_count = payload.get("answered_question_count", 0) if isinstance(payload, dict) else 0
        checkpoint_results = payload.get("checkpoint_results", {}) if isinstance(payload, dict) else {}
        severity_inputs = payload.get("severity_inputs", []) if isinstance(payload, dict) else []
        answers_log = payload.get("answers_log", []) if isinstance(payload, dict) else []
        result = run_accumulated_engine(
            accumulated_vector, intake, answered_question_count, checkpoint_results,
            severity_inputs, answers_log,
        )
        return JSONResponse(content=result)
    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"Unknown state ID: {e}")
    except (TypeError, ValueError) as e:
        raise HTTPException(status_code=400, detail=f"Invalid payload: {e}")
    except Exception:
        raise HTTPException(status_code=500, detail="Engine error")


@app.post("/api/condensed-complete")
async def condensed_complete(request: Request):
    # Category D (free condensed diagnostic), this session -- completion
    # endpoint for the separate condensed session flow. No checkpoint_
    # results/severity_inputs/answers_log params (run_accumulated_engine()
    # has them) -- Category D's condensed session never collects any of
    # them by design. Merges the financial benchmark range into the same
    # response so the TS caller makes one round trip, not two -- the
    # get_industry_wage() lookup is a pure function, no reason to split
    # it into its own endpoint.
    _check_secret(request)

    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    try:
        accumulated_vector = payload.get("accumulated_vector", {}) if isinstance(payload, dict) else {}
        intake = payload.get("intake", {}) if isinstance(payload, dict) else {}
        answered_question_count = payload.get("answered_question_count", 0) if isinstance(payload, dict) else 0
        result = run_condensed_engine(accumulated_vector, answered_question_count)

        industry = intake.get("industry", "") if isinstance(intake, dict) else ""
        wage = get_industry_wage(industry)
        result["condensed_financial_range"] = (
            {"low": round(wage * 0.50, 2), "high": round(wage * 0.75, 2), "currency": "USD"}
            if wage is not None
            else {"low": None, "high": None, "currency": "USD"}
        )

        return JSONResponse(content=result)
    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"Unknown state ID: {e}")
    except (TypeError, ValueError) as e:
        raise HTTPException(status_code=400, detail=f"Invalid payload: {e}")
    except Exception:
        raise HTTPException(status_code=500, detail="Engine error")


@app.post("/api/question-copy")
async def question_copy(request: Request):
    _check_secret(request)

    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    try:
        question_id = payload.get("question_id", "") if isinstance(payload, dict) else ""
        copy = get_question_copy(question_id)
        return JSONResponse(content=copy)
    except KeyError as e:
        # Unknown question_id — client fault
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Engine error")
