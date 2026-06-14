import os
import sys
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse

# Add repo root to path so engine package resolves
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from engine.main import run_engine

app = FastAPI()

ENGINE_SECRET = os.environ.get("ENGINE_SECRET", "")


@app.post("/api/engine")
async def invoke_engine(request: Request):
    # Shared secret validation — reject before any engine work
    secret = request.headers.get("x-engine-secret", "")
    if not ENGINE_SECRET or secret != ENGINE_SECRET:
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    try:
        result = run_engine(payload)
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
