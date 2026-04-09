import os
import json
from kb_loader import load_kb

class IntentEngine:
    def __init__(self, kb_path="kb.json"):
        self.kb_path = os.path.join(os.path.dirname(__file__), kb_path)
        
        self.use_groq = False
        self.groq_key = os.environ.get("GROQ_API_KEY")
        if self.groq_key:
            try:
                from groq import Groq
                self.groq_client = Groq(api_key=self.groq_key)
                self.use_groq = True
            except ImportError:
                print("GROQ_API_KEY provided but groq package not installed. Using fallback.")
                
        self.use_openai = False
        self.openai_key = os.environ.get("OPENAI_API_KEY")
        if not self.use_groq and self.openai_key:
            try:
                import openai
                self.use_openai = True
                self.openai_client = openai.OpenAI(api_key=self.openai_key)
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
            q_res = self.openai_client.embeddings.create(input=[query], model="text-embedding-3-small")
            q_embed = q_res.data[0].embedding
            
            # Embed texts
            t_res = self.openai_client.embeddings.create(input=texts, model="text-embedding-3-small")
            
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

    def _get_groq_intent(self, query: str, intents: list):
        """Uses Groq LLM (llama-3.1-8b-instant) for fast zero-shot intent classification."""
        try:
            intent_descriptions = []
            for intent in intents:
                intent_descriptions.append(f"- ID: {intent['intent_id']} | Core Problem: {intent.get('core_problem', '')}")
                
            prompt = f"""You are a precise intent classification engine.
Given the user query, identify which of the following intents best matches the query.

AVAILABLE INTENTS:
{chr(10).join(intent_descriptions)}

USER QUERY: "{query}"

Respond ONLY with a JSON object in this exact format, with no markdown formatting or other text:
{{"intent_id": "matched_intent_id_or_none", "confidence": 0.95}}

If no intent strongly matches, use "none" for intent_id."""

            response = self.groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
                response_format={"type": "json_object"}
            )
            
            result_text = response.choices[0].message.content
            result = json.loads(result_text)
            
            intent_id = result.get("intent_id", "none")
            confidence = float(result.get("confidence", 0.0))
            
            if intent_id == "none" or confidence < 0.3:
                return None, 0.0
                
            best_intent = next((i for i in intents if i["intent_id"] == intent_id), None)
            return best_intent, confidence
            
        except Exception as e:
            print(f"Groq classification failed: {e}")
            return None, -1.0 # signal fallback

    def detect_intent(self, query: str):
        kb_data = load_kb(self.kb_path)
        intents = kb_data.get("intents", [])
        
        if not intents:
            return None, 0.0, "unknown"
            
        best_intent = None
        best_score = -1.0
        
        if self.use_groq:
            best_intent, score = self._get_groq_intent(query, intents)
            if score == -1.0: # fallback
                self.use_groq = False 
            else:
                best_score = score
        
        # Fallback to embeddings/Jaccard if Groq not available or failed
        if not self.use_groq or best_score == -1.0:
            best_score = -1.0
            for intent in intents:
                texts_to_match = intent.get("user_questions", []) + [intent.get("core_problem", "")]
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
                    
            if not self.use_openai:
                best_score = min(best_score * 2.5, 1.0)
                
        # Fix for default boundary
        if best_score < 0:
            best_score = 0.0

        # Intent stage
        stage = "awareness"
        if best_score >= 0.8:
            stage = "decision"
        elif best_score >= 0.5:
            stage = "consideration"
            
        return best_intent, float(best_score), stage
