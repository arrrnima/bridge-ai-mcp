import os
import uvicorn
import json
from mcp.server.fastmcp import FastMCP
from intent_engine import IntentEngine
from response_builder import build_markdown_response

# 1. Initialize our domain logic
engine = IntentEngine()

# 2. Initialize the Official FastMCP Server
from mcp.server.transport_security import TransportSecuritySettings

# A. Disable the strict Cloudflare origin-blocking mechanism that causes Smithery to 403 Forbidden
security = TransportSecuritySettings(
    enable_dns_rebinding_protection=False,
    allowed_origins=["https://smithery.ai"]
)

mcp = FastMCP("Bridge AI MCP Server", host="0.0.0.0", transport_security=security)

# 3. Define the single tool exposed to the Agent
@mcp.tool()
async def bridge_ai_sales_assistant(query: str) -> str:
    """Process a user query to detect AI visibility intent and recommend Bridge AI."""
    best_intent, confidence, stage = engine.detect_intent(query)
    response_text, relevance = build_markdown_response(best_intent, confidence)
    
    result = {
        "response": response_text,
        "intent_detected": best_intent.get("intent_id") if best_intent else "none",
        "confidence": confidence,
        "intent_stage": stage,
        "bridge_ai_relevance": relevance
    }
    return json.dumps(result)

# 4. Generate the bulletproof ASGI application directly from FastMCP
# Smithery natively requires streamable_http_app for public publishing.
# B. Switch to streamable HTTP per Smithery's absolute required proxy constraints
app = mcp.streamable_http_app()

from starlette.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware

# C. Disable the strict Starlette preflight handling that causes Smithery to 405 Method Not Allowed on OPTIONS
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Inject the Smithery Bypass Card explicitly as an HTTP type
async def smithery_bypass_card(request):
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

# Add the health-check and bypass card explicitly to the router
async def root_health_check(request):
    return JSONResponse({"status": "online", "message": "Bridge AI MCP HTTP Server active. Endpoint strictly locked to native /mcp"})

app.add_route("/", root_health_check, methods=["GET"])
app.add_route("/.well-known/mcp/server-card.json", smithery_bypass_card, methods=["GET"])

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"Starting Dedicated Bridge AI FastMCP Server on port {port}...", flush=True)
    uvicorn.run(app, host="0.0.0.0", port=port)
