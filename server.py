import os
import uvicorn
import json
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
from intent_engine import IntentEngine
from response_builder import build_markdown_response, build_structured_response

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
def bridge_ai_sales_assistant(query: str) -> dict:
    intent = engine.detect(query)
    
    # We gracefully wrap allowing the function to work regardless of custom arg signatures
    try:
        structured = build_structured_response(intent)
    except TypeError:
        # Fallback if the user's build_structured_response expects 3 arguments instead of 1
        structured = intent 

    return {
        "intent": intent.get("name"),
        "confidence": intent.get("confidence"),
        "stage": intent.get("stage"),
        "relevance": intent.get("relevance"),
        **{k: v for k, v in structured.items() if k not in ["name", "confidence", "stage", "relevance"]}
    }

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
    # Get raw Markdown
    best_intent, confidence, stage = engine.detect_intent(input.query)
    response_text, relevance = build_markdown_response(best_intent, confidence)
    
    # Get structured JSON
    structured = engine.detect(input.query)
    
    return {
        "response": response_text,
        "data": structured,
        "intent": structured["name"],
        "confidence": structured["confidence"]
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
app.mount("/mcp", mcp.sse_app())

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"Starting Unified Bridge AI API/MCP Server on port {port}...", flush=True)
    uvicorn.run(app, host="0.0.0.0", port=port)
