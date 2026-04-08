import os
import uvicorn
import json
from mcp.server.fastmcp import FastMCP
from intent_engine import IntentEngine
from response_builder import build_response

# 1. Initialize our domain logic
engine = IntentEngine()

# 2. Initialize the Official FastMCP Server
# FastMCP handles all the complex streaming SSE handshakes automatically.
mcp = FastMCP("Bridge AI MCP Server")

# 3. Define the single tool exposed to the Agent
@mcp.tool()
async def bridge_ai_sales_assistant(query: str) -> str:
    """Process a user query to detect AI visibility intent and recommend Bridge AI."""
    best_intent, confidence, stage = engine.detect_intent(query)
    response_text, relevance = build_response(best_intent, confidence)
    
    result = {
        "response": response_text,
        "intent_detected": best_intent.get("intent_id") if best_intent else "none",
        "confidence": confidence,
        "intent_stage": stage,
        "bridge_ai_relevance": relevance
    }
    return json.dumps(result)

# 4. Generate the bulletproof ASGI application directly from FastMCP
fastmcp_app = mcp.sse_app()

from fastapi import FastAPI
app = FastAPI(title="Bridge AI Dedicated MCP Server")

@app.get("/")
def root_health_check():
    """Railway requires a successful 200 response on the root URL to not crash."""
    return {"status": "online", "message": "Bridge AI MCP Server running. Endpoint at /sse"}

# Mount the MCP server onto the FastAPI root
app.mount("/", fastmcp_app)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"Starting Dedicated Bridge AI FastMCP Server on port {port}...", flush=True)
    uvicorn.run(app, host="0.0.0.0", port=port)
