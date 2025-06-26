from api_client import send_prompt
from api_client import extract_text_from_response
from intent_classifier import classify_intents
from entity_extractor import extract_entities
from prompt_builder import build_prompt
from response_formatter import format_gemini_response
from kb_retriever import PDFKnowledgeBase
from logger import log_fallback_response, log_error

def main():
    kb= PDFKnowledgeBase(path="data/statutes")
    kb.load_pdf()
    print("\n📘 Welcome to the Singapore Legal Advisor Chatbot!")
    print("Type your legal question below. Type 'exit' or 'quit' to end the session.\n")
    
    conversation_history = []
    max_history = 3

    while True:
        user_input = input("🧑 You: ").strip()
        if user_input.lower() in ["exit", "quit"]:
            print("👋 Exiting. Stay legally safe!")
            break

        try:

            intent = classify_intents(user_input)

            entities = extract_entities(user_input)

            context_chunks = kb.search(user_input)

            prompt = build_prompt(user_input,context_chunks,conversation_history, intent, entities)
            # print("\n🧾 FINAL PROMPT TO LLM:\n", prompt)
            
            response = send_prompt(prompt)
            response_text = extract_text_from_response(response)
            formatted_response = format_gemini_response(response_text)
            if "⚠️ Gemini could not produce a structured response" in formatted_response:
                log_fallback_response(response_text)

            conversation_history.append({
                "user": user_input,
                "bot": formatted_response  # Or whatever variable stores formatted output
            })
            if len(conversation_history) > max_history:
                conversation_history.pop(0)

            print("\n🤖 Gemini Legal Advisor:\n")
            print(formatted_response)
            print("\n" + "="*55 + "\n")
            # for chunk in response:
            #     if hasattr(chunk, "text"):
            #         print(chunk.text.strip(), end="")
            #     else:
            #         print(str(chunk).strip(), end="")
            # print("\n\n-------------------------------------------------------\n")

        except Exception as e:
            log_error(str(e))
            print(f"⚠️ Error: {e}")
            print("Please try again or check logs.")

if __name__ == "__main__":
    main()