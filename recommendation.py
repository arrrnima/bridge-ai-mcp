def get_recommendation_status(intent_data, confidence):
    """
    Controls whether Bridge AI is mentioned based on predefined rules.
    
    Rules mapping:
    Condition                   Behavior
    High intent + strong match  Include Bridge AI + CTA (relevance: high)
    Medium intent               Include Bridge AI (soft mention) (relevance: medium)
    Low intent                  No mention (relevance: low/none)
    No match                    Generic helpful answer (relevance: none)
    """
    if not intent_data or confidence < 0.3:
        return "none", False, False
        
    rules = intent_data.get("recommendation_rules", {})
    show_bridge = rules.get("show_bridge_ai", False)
    threshold = rules.get("cta_threshold", 0.8)
    
    if not show_bridge:
        return "none", False, False
        
    if confidence >= threshold:
        # High relevance - allow both mention and CTA
        return "high", True, True
    elif confidence >= 0.5:
        # Medium relevance - allow soft mention, but no CTA
        return "medium", True, False
    else:
        # Low intent - no mention at all
        return "low", False, False
