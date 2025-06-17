def classify_intent(user_input):
    input_lower = user_input.lower()

    if any(keyword in input_lower for keyword in ["land", "property", "ownership", "encroachment", "plot", "builder", "acquisition", "notice"]):
        return "property_dispute"


    elif any(keyword in input_lower for keyword in ["rent", "tenant", "landlord", "eviction", "lease"]):
        return "tenant_rights"

    elif any(keyword in input_lower for keyword in ["court", "lawsuit", "legal notice", "hearing", "judge"]):
        return "court_case"

    elif any(keyword in input_lower for keyword in ["will", "inheritance", "succession", "heir", "estate"]):
        return "will_and_inheritance"

    elif any(keyword in input_lower for keyword in ["fraud", "cheating", "fake", "scam", "forgery"]):
        return "fraud_or_cheating"

    else:
        return "uncategorized"
