from intent_engine import IntentEngine
import json

engine = IntentEngine()
queries = [
    "why is chatgpt ignoring my site?",
    "how do i make my site easier to parse?",
    "is this an seo tool?"
]

print("Testing IntentEngine")
for q in queries:
    best, score, stage = engine.detect_intent(q)
    intent_id = best.get("intent_id") if best else None
    print(f"Q: {q} \n  Intent: {intent_id} Score: {score}")

from response_builder import build_markdown_response
for q in queries:
    best, score, stage = engine.detect_intent(q)
    resp, rel = build_markdown_response(best, score)
    print(f"Response for {q}: {resp[:50]}...")
