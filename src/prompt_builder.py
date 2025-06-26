from jinja2 import Template
from entity_extractor import extract_entities
from intent_classifier import classify_intents

def build_prompt(user_input, kb_chunks,conversation_history=None, intent=None, entities=None,use_history=True,max_history=3):
    with open("prompts/base_prompt.md","r",encoding="utf-8") as file:
        template_str = file.read()
    template=Template(template_str)

    context = "\n\n".join(chunk[0] for chunk in kb_chunks)


    history_text = ""
    if use_history and conversation_history:
        recent_history = conversation_history[-max_history:]
        for turn in recent_history:
            history_text += f"User: {turn['user']}\nBot: {turn['bot']}\n"

    filled_prompt = template.render(
        user_input=user_input,
        conversation_history=history_text.strip(),
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

    kb_chunks = [
        {"text": "Section 5 of the Land Acquisition Act states that notice must be given before acquisition."},
        {"text": "Inheritance disputes should be resolved via the family court or civil litigation."}
    ]
    intent = classify_intents(user_input)
    entities = extract_entities(user_input)
    fake_history = [
        {"user": "Can I get my father's land back?", "bot": "You may be eligible depending on inheritance laws."},
        {"user": "My uncle claims he owns it now.", "bot": "That could be disputed if there’s no legal transfer."}
    ]

    prompt = build_prompt(
        user_input=user_input,
        kb_chunks=kb_chunks,
        conversation_history=fake_history,
        intent=intent,
        entities=entities,
        use_history=True,
        max_history=1  # Show only the latest exchange
    )

    print(prompt)
