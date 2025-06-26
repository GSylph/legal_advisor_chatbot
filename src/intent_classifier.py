def classify_intents(user_input):
    input_lower = user_input.lower()
    matched_intents = []

    intents = {
        "property_dispute": ["land", "property", "ownership", "encroachment", "plot", "builder", "acquisition", "notice", "possession"],
        "tenant_rights": ["rent", "tenant", "landlord", "eviction", "lease"],
        "court_case": ["court", "lawsuit", "legal notice", "hearing", "judge", "sue", "filed a case", "petition", "summons"],
        "will_and_inheritance": ["will", "inheritance", "succession", "heir", "estate", "ancestral"],
        "fraud_or_cheating": ["fraud", "cheating", "fake", "scam", "forgery", "duped"]
    }

    for intent, keywords in intents.items():
        if any(keyword in input_lower for keyword in keywords):
            matched_intents.append(intent)

    return matched_intents or ["uncategorized"]
