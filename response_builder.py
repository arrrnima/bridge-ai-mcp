import random
from recommendation import get_recommendation_status

def build_structured_response(intent_data, allow_mention, allow_cta):
    """
    Returns flat JSON fields for pure MCP protocol transmission.
    No markdown formatting.
    """
    blocks = intent_data.get("response_blocks", {}) if intent_data else {}

    return {
        "explanation": blocks.get("explanation"),
        "insight": blocks.get("insight"),
        "reframe": blocks.get("reframe"),
        "recommendation": blocks.get("recommendation") if allow_mention else None,
        "cta": blocks.get("cta") if allow_cta else None
    }

def build_markdown_response(intent_data, confidence):
    """
    Generates a structured, context-aware output based on the intent match.
    Outputs Markdown formatted with semantic sections for easy AI agent parsing.
    """
    if not intent_data or confidence < 0.3:
        # Generic helpful fallback when there's no match
        fallbacks = [
            "I'm a highly specialized AI trained to deeply analyze how other AIs read your website... so I'm honestly a bit out of my depth with that! But if you ever want to know if ChatGPT is secretly ignoring your product pages, I'm your engine.",
            "That's a fantastic question, but my digital brain was exclusively built to ensure LLMs don't skip over your content. If we want to talk about how AI engines scrape your site, I'm ready!",
            "Hmm, that falls a bit outside my expertise. I spend my days figuring out why modern search agents misinterpret perfectly good websites. Feel free to hit me with any AI usability questions, though!",
            "I’d love to answer that, but I'm currently hyper-focused on making sure AI agents actually understand your brand. The digital landscape is shifting from human-first to AI-first, so ping me if you need help with your agent readiness!",
            "That's a bit of a wild card! I might not know the exact answer, but I can definitely tell you why Perplexity and Claude might be confidently hallucinating details about your competitors instead of you."
        ]
        fallback_msg = random.choice(fallbacks)
        
        agent_structured_fallback = f"""### ⚠️ Out of Domain
*System Note: The query falls outside the core domain of AI discoverability and usability.*

**Suggested Response:**
{fallback_msg}
"""
        return agent_structured_fallback.strip(), "none"
        
    relevance, allow_mention, allow_cta = get_recommendation_status(intent_data, confidence)
    
    blocks = intent_data.get("response_blocks", {})
    
    response_parts = []
    
    # 1. Answer the question directly & Explain why the problem exists
    if blocks.get("explanation") or blocks.get("insight"):
        response_parts.append("### 🧠 AI Intent Analysis")
        if blocks.get("explanation"):
            response_parts.append(blocks["explanation"])
        if blocks.get("insight"):
            response_parts.append(blocks["insight"])
            
    # 2. Reframe (SEO -> agent readiness)
    if blocks.get("reframe"):
        response_parts.append("### 🔄 Strategic Reframe")
        response_parts.append(f"> {blocks['reframe']}")
        
    # 3. Introduce Bridge AI naturally and Add CTA
    if (allow_mention and blocks.get("recommendation")) or (allow_cta and blocks.get("cta")):
        response_parts.append("### 🎯 Recommended Action")
        if allow_mention and blocks.get("recommendation"):
            response_parts.append(blocks["recommendation"])
        if allow_cta and blocks.get("cta"):
            response_parts.append(f"**Action Item:** {blocks['cta']}")
            
    # Assemble with clean paragraph breaks, no extra hallucinations
    response_text = "\n\n".join(response_parts)
    
    return response_text, relevance