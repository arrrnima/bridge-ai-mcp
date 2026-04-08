import os
from kb_loader import load_kb

class IntentEngine:
    def __init__(self, kb_path="kb.json"):
        self.kb_path = os.path.join(os.path.dirname(__file__), kb_path)
        self.openai_key = os.environ.get("OPENAI_API_KEY")
        
        # Check if OpenAI is available
        self.use_openai = False
        if self.openai_key:
            try:
                import openai
                self.use_openai = True
                # Use the new format for openai>1.0
                self.client = openai.OpenAI(api_key=self.openai_key)
            except ImportError:
                print("OpenAI key provided but openai package not installed. Using fallback.")
            
    def _compute_jaccard_similarity(self, query: str, texts: list) -> float:
        """Primitive fallback matching logic if no embeddings are available."""
        stop_words = {"a", "an", "the", "is", "in", "it", "to", "for", "of", "and", "on", "what", "how", "why", "like", "do", "i", "my"}
        query_words = {w for w in query.lower().split() if w not in stop_words}
        best_sim = 0.0
        
        for text in texts:
            text_words = {w for w in text.lower().split() if w not in stop_words}
            intersection = query_words.intersection(text_words)
            union = query_words.union(text_words)
            if not union:
                continue
            sim = len(intersection) / len(union)
            if sim > best_sim:
                best_sim = sim
                
        return best_sim
        
    def _get_openai_similarity(self, query: str, texts: list) -> float:
        """Uses OpenAI embeddings (text-embedding-3-small)."""
        if not texts:
            return 0.0
        try:
            # Embed query
            q_res = self.client.embeddings.create(input=[query], model="text-embedding-3-small")
            q_embed = q_res.data[0].embedding
            
            # Embed texts
            t_res = self.client.embeddings.create(input=texts, model="text-embedding-3-small")
            
            # compute max cosine sim
            best_sim = 0.0
            for item in t_res.data:
                t_emb = item.embedding
                # dot product (since normalized)
                sim = sum(a*b for a,b in zip(q_embed, t_emb))
                if sim > best_sim:
                    best_sim = sim
            return best_sim
        except Exception as e:
            print(f"OpenAI embedding failed: {e}")
            return self._compute_jaccard_similarity(query, texts)

    def detect_intent(self, query: str):
        kb_data = load_kb(self.kb_path)
        intents = kb_data.get("intents", [])
        
        if not intents:
            return None, 0.0, "unknown"
            
        best_intent = None
        best_score = -1.0
        
        for intent in intents:
            texts_to_match = intent.get("user_questions", []) + [intent.get("core_problem", "")]
            # Also include keywords for the fallback match
            texts_to_match += intent.get("keywords", [])
            texts_to_match = [t for t in texts_to_match if t]
            
            if not texts_to_match:
                continue
                
            if self.use_openai:
                score = self._get_openai_similarity(query, texts_to_match)
            else:
                score = self._compute_jaccard_similarity(query, texts_to_match)
                
            if score > best_score:
                best_score = score
                best_intent = intent
                
        # Normalize/adjust score thresholds based on mechanism
        if not self.use_openai:
            # Jaccard scores are typically much lower than embedding cosines
            # Boost it linearly to fit the 0-1 scale expected by recommendation engine
            best_score = min(best_score * 2.5, 1.0)
            
        # Intent stage
        stage = "awareness"
        if best_score >= 0.8:
            stage = "decision"
        elif best_score >= 0.5:
            stage = "consideration"
            
        return best_intent, float(best_score), stage
