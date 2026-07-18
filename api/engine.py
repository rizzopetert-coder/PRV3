import os
import sys
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse

# Add repo root to path so engine package resolves
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from engine.main import (
    run_engine,
    accumulate_one_answer,
    run_checkpoint,
    run_accumulated_engine,
    get_question_copy,
)

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
# than a new Python build target — see vercel.json for the routing entries
# that point both paths at this same file.

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
        option_id = payload.get("option_id", "") if isinstance(payload, dict) else ""
        intake = payload.get("intake", {}) if isinstance(payload, dict) else {}
        updated_vector = accumulate_one_answer(accumulated_vector, question_id, option_id, intake)
        return JSONResponse(content=updated_vector)
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
        result = run_accumulated_engine(
            accumulated_vector, intake, answered_question_count, checkpoint_results
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
