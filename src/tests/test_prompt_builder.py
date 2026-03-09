from src.prompt_builder import build_prompt
from src.entity_extractor import extract_entities
from src.intent_classifier import classify_intents

user_input = "My uncle is taking over my inherited property in Delhi after my father's death."

# ✅ Use dict format instead of tuple
kb_chunks = [{"text": "The Hindu Succession Act deals with inheritance among Hindus.", "score": 5}]

intent = classify_intents(user_input)
entities = extract_entities(user_input)
history = [{"user": "Can I inherit property without a will?", "bot": "Yes, based on succession laws."}]

print("\n=== PROMPT ===")
prompt = build_prompt(user_input, kb_chunks, history, intent, entities)
print(prompt)
