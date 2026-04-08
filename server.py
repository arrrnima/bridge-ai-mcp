import json
from typing import Optional, Dict, Any

from fastapi import FastAPI
from pydantic import BaseModel
from mcp.server.fastmcp import FastMCP

from intent_engine import IntentEngine
from response_builder import build_response


# ----------------------------
# INIT CORE SYSTEM
# ----------------------------

# MCP Server
mcp = FastMCP("Bridge AI Sales Intelligence")

# Intent Engine (loaded once)
engine = IntentEngine()

# FastAPI App (for testing)
app = FastAPI()


# ----------------------------
# REQUEST MODEL (API)
# ----------------------------

class QueryInput(BaseModel):
    query: str


# ----------------------------
# CORE LOGIC (shared)
# ----------------------------

async def process_query(query: str):
    # 1. Detect intent
    best_intent, confidence, stage = engine.detect_intent(query)

    # 2. Build response
    response_text, relevance = build_response(best_intent, confidence)

    # 3. Format output
    return {
        "response": response_text,
        "intent_detected": best_intent.get("intent_id") if best_intent else "none",
        "confidence": confidence,
        "intent_stage": stage,
        "bridge_ai_relevance": relevance
    }


# ----------------------------
# MCP TOOL (for AI agents)
# ----------------------------

@mcp.tool()
async def bridge_ai_sales_assistant(
    query: str,
    context: Optional[Dict[str, Any]] = None
) -> str:
    result = await process_query(query)
    return json.dumps(result, indent=2)


# ----------------------------
# API ROUTES (for testing)
# ----------------------------

@app.get("/")
def home():
    return {"status": "Bridge AI MCP API running"}

@app.post("/mcp-test")
async def test_api(input: QueryInput):
    return await process_query(input.query)


# ----------------------------
# RUN MODES
# ----------------------------

if __name__ == "__main__":
    import sys

    if "api" in sys.argv:
        import uvicorn
        uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
    else:
        # Default = MCP mode
        mcp.run()
