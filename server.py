import os
import uvicorn
import json
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
from intent_engine import IntentEngine
from response_builder import build_response

from fastapi import FastAPI
from pydantic import BaseModel
from starlette.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# 1. Initialize Domain Logic
engine = IntentEngine()

# 2. Configure Native FastMCP Security Bypass (for Smithery/External proxys)
security = TransportSecuritySettings(
    enable_dns_rebinding_protection=False, 
    allowed_origins=["https://smithery.ai", "*"]
)

mcp = FastMCP("Bridge AI MCP Server", host="0.0.0.0", transport_security=security)

# 3. Define the single tool exposed to MCP Agents
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

# Generate underlying Streamable HTTP ASGI app
mcp_app = mcp.streamable_http_app()

# ==========================================================
# 4. FASTAPI WRAPPER ENABLING /DOCS & STANDARD WEB API
# ==========================================================
app = FastAPI(
    title="Bridge AI Intelligence API", 
    description="Unified API combining standard REST endpoints with a native MCP engine.",
    version="1.0.0"
)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class QueryInput(BaseModel):
    query: str

# Pure REST endpoint that mirrors MCP functionality for non-MCP UI's
@app.post("/api/v1/query", summary="Standard REST Inference", tags=["Intelligence Layer"])
def rest_query_endpoint(input: QueryInput):
    """Fallback REST endpoint for standard web applications interacting with Bridge AI."""
    best_intent, confidence, stage = engine.detect_intent(input.query)
    response_text, relevance = build_response(best_intent, confidence)
    return {
        "response": response_text,
        "intent_detected": best_intent.get("intent_id") if best_intent else "none",
        "confidence": confidence,
        "intent_stage": stage,
        "bridge_ai_relevance": relevance
    }

# Explicit HTTP Proxy definitions for Smithery crawler
@app.get("/.well-known/mcp/server-card.json", include_in_schema=False)
async def smithery_bypass_card():
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

@app.get("/", summary="Health Check", tags=["System"])
def root_health_check():
    return {"status": "online", "message": "Unified Bridge AI MCP/REST active. Visit /docs for interactive Swagger API."}

# Mount the MCP agent protocol underlying server at a specific router proxy
app.mount("/mcp", mcp_app)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"Starting Unified Bridge AI API/MCP Server on port {port}...", flush=True)
    uvicorn.run(app, host="0.0.0.0", port=port)
