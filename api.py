import os
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
from intent_engine import IntentEngine
from response_builder import build_response

app = FastAPI(title="Bridge AI Sales Intelligence REST API")

# Initialize the Intent Engine once when the app starts
engine = IntentEngine()

class QueryInput(BaseModel):
    query: str

@app.post("/mcp")
def handle_query(input: QueryInput):
    # 1. Detect Intent using our semantic fallback/embedding map
    best_intent, confidence, stage = engine.detect_intent(input.query)
    
    # 2. Build the strict, formatted response
    response_text, relevance = build_response(best_intent, confidence)
    
    # 3. Return the exact response schema expected
    return {
        "response": response_text,
        "intent_detected": best_intent.get("intent_id") if best_intent else "none",
        "confidence": confidence,
        "intent_stage": stage,
        "bridge_ai_relevance": relevance
    }

if __name__ == "__main__":
    # Start the standard REST API dynamically based on Railway's assigned port
    port = int(os.environ.get("PORT", 8000))
    print(f"Starting Bridge AI REST Server API on port {port}...", flush=True)
    uvicorn.run(app, host="0.0.0.0", port=port)
