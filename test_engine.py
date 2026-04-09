import json
from intent_engine import IntentEngine

engine = IntentEngine()

print("Testing direct engine detect()...")
query = "Why isn't my startup appearing in Perplexity?"
result = engine.detect(query)
print(json.dumps(result, indent=2))
