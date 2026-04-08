from fastapi import FastAPI, Depends
from starlette.requests import Request
from starlette.responses import StreamingResponse
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.types import Tool, TextContent
import uvicorn
import json
import logging
import anyio
import os

from intent_engine import IntentEngine
from response_builder import build_response

app = FastAPI(title="Bridge AI Dedicated MCP Endpoint")
engine = IntentEngine()

mcp_server = Server("bridge-ai-sales")

@mcp_server.list_tools()
async def handle_list_tools() -> list[Tool]:
    return [
        Tool(
            name="bridge_ai_sales_assistant",
            description="Process a user query to detect AI visibility intent and recommend Bridge AI",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The user query analyzing website discoverability in AI"}
                },
                "required": ["query"]
            }
        )
    ]

@mcp_server.call_tool()
async def handle_call_tool(name: str, arguments: dict | None) -> list[TextContent]:
    if name != "bridge_ai_sales_assistant":
        raise ValueError(f"Unknown tool: {name}")
        
    query = arguments.get("query", "")
    best_intent, confidence, stage = engine.detect_intent(query)
    response_text, relevance = build_response(best_intent, confidence)
    
    result = {
        "response": response_text,
        "intent_detected": best_intent.get("intent_id") if best_intent else "none",
        "confidence": confidence,
        "intent_stage": stage,
        "bridge_ai_relevance": relevance
    }
    
    return [TextContent(type="text", text=json.dumps(result))]


# The SSE Transport requires maintaining a mapping of transports to sessions
sse_transport = None

@app.get("/")
def health_check():
    """Simple health check endpoint for the root URL"""
    return {
        "status": "online", 
        "service": "Bridge AI Dedicated MCP Server", 
        "mcp_endpoint": "/mcp"
    }

@app.get("/mcp")
async def handle_mcp_sse(request: Request):
    """
    Dedicated endpoint expecting an MCP SSE connection at /mcp
    """
    global sse_transport
    
    # Intialize SSE Transport mapped to handle return POST messages via standard route
    sse_transport = SseServerTransport("/mcp/messages")
    
    async def run_mcp():
        from mcp.server.models import InitializationOptions
        try:
            await mcp_server.run(
                sse_transport.read_messages(),
                sse_transport.write_message,
                InitializationOptions(
                    server_name="bridge-ai-sales",
                    server_version="1.0.0",
                    capabilities=mcp_server.get_capabilities()
                )
            )
        except Exception as e:
            logging.error(f"MCP Session Error: {e}")

    anyio.create_task_group().start_soon(run_mcp)
    
    return StreamingResponse(
        sse_transport.handle_sse(request.scope, request.receive, request._send),
        media_type="text/event-stream"
    )


@app.post("/mcp/messages")
async def handle_mcp_messages(request: Request):
    """
    Standard route where MCP clients POST JSON-RPC payloads
    """
    global sse_transport
    if sse_transport is None:
        return {"error": "MCP SSE stream not open yet"}
        
    # Defer handling of POST message to the official SseServerTransport
    await sse_transport.handle_post_message(request.scope, request.receive, request._send)
    return {"status": "ok"}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"Starting Dedicated Bridge AI MCP API Route on port {port}...", flush=True)
    uvicorn.run("mcp_server:app", host="0.0.0.0", port=port)
