from jinja2 import Template
from entity_extractor import extract_entities
from intent_classifier import classify_intent

def build_prompt(user_input, intent=None, entities=None):
    with open("prompts/base_prompt.md","r",encoding="utf-8") as file:
        template_str = file.read()
    template=Template(template_str)
    filled_prompt = template.render(
        user_input=user_input,
        intent=intent or "uncategorized",
        location=", ".join(entities.get("locations", [])) if entities.get("locations") else None,
        people=entities.get("people", "") if entities else "",
        date=", ".join(entities.get("dates", [])) if entities.get("dates") else None,
        country="Singapore"

    )
    return filled_prompt

# if __name__ == "__main__":
#     user_input = "My cousin grabbed my land in Bangalore in 2017 after my father passed away."
#     print(build_prompt(user_input))
