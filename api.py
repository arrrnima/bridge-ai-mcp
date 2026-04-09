import os
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
from intent_engine import IntentEngine
from response_builder import build_structured_response, build_markdown_response

app = FastAPI(title="Bridge AI Sales Intelligence REST API")

# Initialize the Intent Engine once when the app starts
engine = IntentEngine()

class QueryInput(BaseModel):
    query: str

@app.post("/mcp")
def handle_query(input: QueryInput):
    # 1. Detect Intent purely for Markdown branch
    best_intent, confidence, stage = engine.detect_intent(input.query)
    
    # 2. Build the markdown response (ONLY FOR REST UI) & structured data
    response_text, relevance = build_markdown_response(best_intent, confidence)
    
    # 3. Pull the purely formatted JSON dict
    structured = engine.detect(input.query)
    
    # 4. Return combined payload
    return {
        "response": response_text,
        "data": structured,
        "intent": structured["name"],
        "confidence": structured["confidence"]
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"Starting Bridge AI REST Server API on port {port}...", flush=True)
    uvicorn.run(app, host="0.0.0.0", port=port)
