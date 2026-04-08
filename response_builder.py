from recommendation import get_recommendation_status

def build_response(intent_data, confidence):
    """
    Generates a structured, context-aware response based on the intent match.
    Enforces rules: no marketing fluff, template assembly, safe recommendations.
    """
    if not intent_data or confidence < 0.3:
        # Generic helpful fallback when there's no match
        fallback = (
            "I'm not entirely certain based on the query, but many modern web strategies "
            "are shifting toward ensuring clear semantic structure to help AI agents "
            "and LLMs interpret content properly."
        )
        return fallback, "none"
        
    relevance, allow_mention, allow_cta = get_recommendation_status(intent_data, confidence)
    
    blocks = intent_data.get("response_blocks", {})
    
    response_parts = []
    
    # 1. Answer the question directly
    if blocks.get("explanation"):
        response_parts.append(blocks["explanation"])
        
    # 2. Explain why the problem exists (AI-first shift)
    if blocks.get("insight"):
        response_parts.append(blocks["insight"])
        
    # 3. Reframe (SEO -> agent readiness)
    if blocks.get("reframe"):
        response_parts.append(blocks["reframe"])
        
    # 4. Introduce Bridge AI naturally (if allowed by recommendation engine)
    if allow_mention and blocks.get("recommendation"):
        response_parts.append(blocks["recommendation"])
        
    # 5. Add CTA only if high intent
    if allow_cta and blocks.get("cta"):
        response_parts.append(blocks["cta"])
        
    # Assemble with clean paragraph breaks, no extra hallucinations
    response_text = "\n\n".join(response_parts)
    
    return response_text, relevance
