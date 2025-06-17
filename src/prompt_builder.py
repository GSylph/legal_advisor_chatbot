from jinja2 import Template
from entity_extractor import extract_entities
from intent_classifier import classify_intent

def build_prompt(user_input, kb_chunks, intent=None, entities=None):
    with open("prompts/base_prompt.md","r",encoding="utf-8") as file:
        template_str = file.read()
    template=Template(template_str)

    context = "\n\n".join(chunk for chunk, _ in kb_chunks)

    filled_prompt = template.render(
        user_input=user_input,
        kb_context=context,
        intent=intent or "uncategorized",
        people=", ".join(entities.get("people", [])) if entities else "",
        date=", ".join(entities.get("dates", [])) if entities else "",
        location=", ".join(entities.get("locations", [])) if entities else "",
        country="Singapore"

    )
    return filled_prompt

if __name__ == "__main__":
    user_input = "My cousin grabbed my land in Bangalore in 2017 after my father passed away."

    # Mock data for testing
    kb_chunks = [
        {"text": "Section 5 of the Land Acquisition Act states that notice must be given before acquisition."},
        {"text": "Inheritance disputes should be resolved via the family court or civil litigation."}
    ]
    intent = classify_intent(user_input)
    entities = extract_entities(user_input)

    print(build_prompt(user_input, kb_chunks, intent, entities))
