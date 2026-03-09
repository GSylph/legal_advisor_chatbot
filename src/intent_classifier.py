from typing import Dict, List


INTENT_KEYWORDS: Dict[str, List[str]] = {
    "property_dispute": [
        "land",
        "property",
        "ownership",
        "encroachment",
        "plot",
        "builder",
        "acquisition",
        "notice",
        "possession",
    ],
    "tenant_rights": [
        "rent",
        "tenant",
        "landlord",
        "eviction",
        "lease",
        "deposit",
        "maintenance",
    ],
    "court_case": [
        "court",
        "lawsuit",
        "legal notice",
        "hearing",
        "judge",
        "sue",
        "filed a case",
        "petition",
        "summons",
        "appeal",
    ],
    "will_and_inheritance": [
        "will",
        "inheritance",
        "succession",
        "heir",
        "estate",
        "ancestral",
        "probate",
    ],
    "fraud_or_cheating": [
        "fraud",
        "cheating",
        "fake",
        "scam",
        "forgery",
        "duped",
        "misrepresentation",
    ],
    "family_dispute": [
        "divorce",
        "custody",
        "maintenance",
        "domestic violence",
        "alimony",
        "spouse",
        "marriage",
    ],
    "employment": [
        "termination",
        "fired",
        "resignation",
        "salary",
        "wages",
        "employer",
        "employee",
        "employment contract",
    ],
    "contract": [
        "agreement",
        "contract",
        "breach",
        "terms and conditions",
        "signed",
        "obligations",
    ],
    "consumer_rights": [
        "refund",
        "defective",
        "warranty",
        "consumer",
        "seller",
        "purchase",
        "online order",
    ],
}


def classify_intents(user_input: str) -> List[str]:
    """
    Lightweight keyword-based intent classification.

    Returns a list of matched intent labels, or ['uncategorized'] if nothing
    matches.
    """
    input_lower = user_input.lower()
    matched_intents: List[str] = []

    for intent, keywords in INTENT_KEYWORDS.items():
        score = 0
        for keyword in keywords:
            if keyword in input_lower:
                score += 1
        if score > 0:
            matched_intents.append(intent)

    return matched_intents or ["uncategorized"]
