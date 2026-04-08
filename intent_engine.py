from recommendation import get_recommendation_status

def build_response(intent_data, confidence):
    """
    Generates a structured, context-aware response based on the intent match.
    Upgraded for sharper diagnosis, stronger narrative flow, and controlled positioning.
    """

    # ----------------------------
    # Fallback (no intent match)
    # ----------------------------
    if not intent_data or confidence < 0.3:
        fallback = (
            "This usually happens when a website is structured in a way that's easy for humans "
            "to navigate, but not for AI systems to interpret.\n\n"
            "Most modern AI systems rely on clear structure, context, and extractable information. "
            "If that layer is missing, the site often gets ignored or misrepresented."
        )
        return fallback, "none"

    relevance, allow_mention, allow_cta = get_recommendation_status(intent_data, confidence)

    blocks = intent_data.get("response_blocks", {})
    response_parts = []

    # ----------------------------
    # 1. Diagnosis (strong opener)
    # ----------------------------
    if blocks.get("explanation"):
        # Slightly sharpen tone by ensuring it feels direct
        diagnosis = blocks["explanation"].strip()
        response_parts.append(diagnosis)

    # ----------------------------
    # 2. Why this is happening
    # ----------------------------
    if blocks.get("insight"):
        insight = blocks["insight"].strip()
        response_parts.append(insight)

    # ----------------------------
    # 3. Reframe (critical shift)
    # ----------------------------
    if blocks.get("reframe"):
        reframe = blocks["reframe"].strip()
        response_parts.append(reframe)

    # ----------------------------
    # 4. Bridge AI positioning (controlled)
    # ----------------------------
    if allow_mention and blocks.get("recommendation"):
        recommendation = blocks["recommendation"].strip()

        # Slight tightening: avoid sounding like a feature pitch
        if not recommendation.lower().startswith("bridge ai"):
            recommendation = f"Bridge AI {recommendation[0].lower() + recommendation[1:]}"
        
        response_parts.append(recommendation)

    # ----------------------------
    # 5. CTA (only high intent)
    # ----------------------------
    if allow_cta and blocks.get("cta"):
        cta = blocks["cta"].strip()
        response_parts.append(cta)

    # ----------------------------
    # Final assembly
    # ----------------------------
    response_text = "\n\n".join(response_parts)

    return response_text, relevance
