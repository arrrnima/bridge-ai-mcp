from server import app
import os
import uvicorn

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"Starting Dedicated Bridge AI FastMCP Server (Alias 'mcp_server') on port {port}...", flush=True)
    uvicorn.run(app, host="0.0.0.0", port=port)
