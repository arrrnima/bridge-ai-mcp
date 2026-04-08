import os
import uvicorn
import json
from mcp.server.fastmcp import FastMCP
from intent_engine import IntentEngine
from response_builder import build_response

# 1. Initialize our domain logic
engine = IntentEngine()

# 2. Initialize the Official FastMCP Server
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
# We specifically use streamable_http_app to correctly intercept Smithery's `POST /mcp`.
# This returns a pure Starlette app that natively fires its own Lifespan events.
app = mcp.streamable_http_app()

from starlette.responses import JSONResponse

# Inject the Railway health-check directly into the native Starlette app
async def root_health_check(request):
    """Railway requires a successful 200 response on the root URL to not crash."""
    return JSONResponse({"status": "online", "message": "Bridge AI MCP HTTP Server active. Endpoint strictly locked to /mcp"})

# Inject the Smithery Bypass Card referencing the HTTP context
async def smithery_bypass_card(request):
    """Provides Smithery the explicitly declared endpoints to bypass proxy failures"""
    return JSONResponse({
      "$schema": "https://smithery.ai/schema/server-card.json",
      "name": "bridge-ai-sales",
      "version": "1.0.0",
      "description": "Bridge AI Sales Intelligence Context Protocol",
      "endpoints": [
        {
          "type": "http",
          "url": "https://bridge-ai-mcp-production.up.railway.app/mcp"
        }
      ]
    })

app.add_route("/", root_health_check, methods=["GET"])
app.add_route("/.well-known/mcp/server-card.json", smithery_bypass_card, methods=["GET"])

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"Starting Dedicated Bridge AI FastMCP Server on port {port}...", flush=True)
    uvicorn.run(app, host="0.0.0.0", port=port)
