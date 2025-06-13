import spacy

# Load the English NLP model
nlp = spacy.load("en_core_web_sm")

def extract_entities(user_input):
    doc = nlp(user_input)

    entities = {
        "locations": [],
        "people": [],
        "dates": [],
    }

    for ent in doc.ents:
        if ent.label_ in ["GPE", "LOC"]:  # Geo-political entity / location
            entities["locations"].append(ent.text)
        elif ent.label_ == "PERSON":
            entities["people"].append(ent.text)
        elif ent.label_ in ["DATE"]:
            entities["dates"].append(ent.text)

    return entities

if __name__ == "__main__":
    test_input = "My uncle encroached on our farm in Pune in 2015 after my father passed away."
    doc = nlp(test_input)
    print([(token.text, token.label_) for token in doc.ents ])
    print(extract_entities(test_input))

