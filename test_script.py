from intent_engine import IntentEngine

engine = IntentEngine()
queries = [
    "why is chatgpt ignoring my site?",
    "how do i make my site easier to parse?",
    "is this an seo tool?"
]

for q in queries:
    best, score, stage = engine.detect_intent(q)
    print(f"Q: {q}")
    print(f"  Intent: {best.get('intent_id') if best else None}")
    print(f"  Score: {score}")

