import spacy
from spacy.matcher import PhraseMatcher

# Load the English NLP model
nlp = spacy.load("en_core_web_sm")

FAMILY_ROLES=["uncle","aunt","cousin","brother","sister","mother","father","grandfather","grandmother","nephew","niece","dad","mom","son","daughter"]

matcher=PhraseMatcher(nlp.vocab,attr="LOWER")
pattern=[nlp.make_doc(term) for term in FAMILY_ROLES]
matcher.add("FAMILY_ROLES", pattern)

def extract_entities(user_input):
    doc = nlp(user_input)

    locations= []
    dates= []
    people= []
    family_roles= []

    for ent in doc.ents:
        if ent.label_ in ["GPE", "LOC"]:
            locations.append(ent.text)
        elif ent.label_ == "PERSON":
            people.append(ent.text)
        elif ent.label_ == "DATE":
            dates.append(ent.text)

        
    matches = matcher(doc)
    for match_id, start, end in matches:
        span = doc[start:end]
        family_roles.append(span.text)

    # Merge family_roles into people 
    combined_people = list(set(people + family_roles))
    return {
        "locations": locations,
        "people": combined_people,
        "dates": dates
    }

if __name__ == "__main__":
    test_input = "My uncle encroached on our farm in Pune in 2015 after my father passed away."
    doc = nlp(test_input)
    print([(token.text, token.label_) for token in doc.ents ])
    print(extract_entities(test_input))

