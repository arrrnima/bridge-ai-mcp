import json
import os

def load_kb(file_path="kb.json"):
    """
    Loads the knowledge base JSON.
    Called on each request to support hot reloading without a server restart.
    """
    if not os.path.exists(file_path):
        print(f"Warning: KB not found at {file_path}")
        return {"intents": []}
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading KB: {e}")
        return {"intents": []}
