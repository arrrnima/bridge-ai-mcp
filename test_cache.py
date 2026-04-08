import time
from intent_engine import IntentEngine

engine = IntentEngine()

q = "why is chatgpt ignoring my site?"

# Call 1
start = time.time()
res1 = engine.detect_intent(q)
end1 = time.time() - start
print(f"Call 1 Latency: {end1:.4f} seconds")

# Call 2
start = time.time()
res2 = engine.detect_intent(q)
end2 = time.time() - start
print(f"Call 2 Latency: {end2:.4f} seconds")

