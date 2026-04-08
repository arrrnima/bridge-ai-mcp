import json
from typing import Optional, Dict, Any

from fastapi import FastAPI
from pydantic import BaseModel
from mcp.server.fastmcp import FastMCP

from intent_engine import IntentEngine
from response_builder import build_response


# ----------------------------
# INIT
# ----------------------------

app = FastAPI()
mcp = FastMCP("Bridge AI Sales Intelligence")
engine = IntentEngine()


# ----------------------------
# REQUEST MODEL
# ----------------------------

class QueryInput(BaseModel):
    query: str


# ----------------------------
# CORE LOGIC
# ----------------------------

async def process_query(query: str):
    best_intent, confidence, stage = engine.detect_intent(query)
    response_text, relevance = build_response(best_intent, confidence)

    return {
        "response": response_text,
        "intent_detected": best_intent.get("intent_id") if best_intent else "none",
        "confidence": confidence,
        "intent_stage": stage,
        "bridge_ai_relevance": relevance
    }


# ----------------------------
# ROUTES
# ----------------------------

@app.get("/")
def health():
    return {"status": "ok"}


@app.post("/mcp-test")
async def test_api(input: QueryInput):
    return await process_query(input.query)


# ----------------------------
# MCP TOOL
# ----------------------------

@mcp.tool()
async def bridge_ai_sales_assistant(
    query: str,
    context: Optional[Dict[str, Any]] = None
) -> str:
    result = await process_query(query)
    return json.dumps(result)
