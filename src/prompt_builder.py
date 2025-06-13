from jinja2 import Template
from entity_extractor import extract_entities
from intent_classifier import classify_intent

def build_prompt(user_input):
    with open("prompts/base_prompt.md","r",encoding="utf-8") as file:
        template_str = file.read()
    template=Template(template_str)
    extracted= extract_entities(user_input)
    intent=classify_intent(user_input)
    filled_prompt=template.render(
        user_input=user_input,
        intent=intent,
        location=extracted.get("location", None),
        people=extracted.get("people", None),
        date=extracted.get("date", None)
    )
    return filled_prompt

# if __name__ == "__main__":
#     user_input = "My cousin grabbed my land in Bangalore in 2017 after my father passed away."
#     print(build_prompt(user_input))
