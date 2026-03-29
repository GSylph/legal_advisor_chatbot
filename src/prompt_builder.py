from jinja2 import Template
from pathlib import Path

from .entity_extractor import extract_entities
from .intent_classifier import classify_intents
template_path = Path("prompts") / "base_prompt.md"


def format_conversation_history(history):
    return "\n".join([f"User: {turn['user']}\nBot: {turn['bot']}" for turn in history])


def _chunk_to_text(chunk):
    if isinstance(chunk, dict):
        source_bits = [chunk.get("document_name", ""), f"p.{chunk.get('page_number')}" if chunk.get("page_number") else ""]
        heading = chunk.get("section_heading")
        if heading:
            source_bits.append(str(heading))
        source_label = ", ".join([item for item in source_bits if item])
        if source_label:
            return f"[{source_label}]\n{chunk.get('text', '').strip()}"
        return chunk.get("text", "")
    if isinstance(chunk, (tuple, list)) and chunk:
        return str(chunk[0])
    return str(chunk)

def build_prompt(user_input, kb_chunks,conversation_history=None, intent=None, entities=None,use_history=True,max_history=3,country="Singapore"):
    with open(template_path,"r",encoding="utf-8") as file:
        template_str = file.read()
    template=Template(template_str)

    context = "\n\n".join(_chunk_to_text(chunk) for chunk in kb_chunks)



    people=", ".join(entities.get("people", [])) if entities else ""
    date=", ".join(entities.get("dates", [])) if entities else ""
    location=", ".join(entities.get("locations", [])) if entities else ""
    history_text = ""
    if use_history and conversation_history:
        recent_history = conversation_history[-max_history:]
        history_text = format_conversation_history(recent_history)
    filled_prompt = template.render(
        user_input=user_input,
        conversation_history=history_text.strip(),
        kb_context=context,
        intent=intent or "uncategorized",
        people=people,
        date=date,
        location=location,
        country=country

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
