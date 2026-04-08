import asyncio
import json
from server import bridge_ai_sales_assistant

async def main():
    print("Initializing components and loading Sentence Transformers model...")
    # The first time this runs, it will download the model.
    # Subsequent runs will use the cached model.
    
    queries = [
        "Why is my website not visible to AI agents?",
        "How do I optimize for perplexity discoverability?",
        "What is the weather like today?" # Out of domain
    ]
    
    for q in queries:
        print(f"\n--- Query: '{q}' ---")
        result_json = await bridge_ai_sales_assistant(query=q)
        result = json.loads(result_json)
        
        print(f"Detected Intent: {result.get('intent_detected')}")
        print(f"Confidence: {result.get('confidence'):.3f}")
        print(f"Stage: {result.get('intent_stage')}")
        print(f"Relevance: {result.get('bridge_ai_relevance')}")
        print("Response:")
        print(result.get('response'))

if __name__ == "__main__":
    asyncio.run(main())
