from api_client import send_prompt
from api_client import extract_text_from_response
from intent_classifier import classify_intent
from entity_extractor import extract_entities
from prompt_builder import build_prompt
from response_formatter import format_gemini_response

def main():
    print("📜 Legal Advisor Chatbot (type 'exit' to quit)\n")

    while True:
        user_input = input("Enter your prompt: ").strip()
        if user_input.lower() in ["exit", "quit"]:
            print("👋 Exiting. Stay legally safe!")
            break

        try:
            intent = classify_intent(user_input)

            entities = extract_entities(user_input)

            prompt = build_prompt(user_input, intent, entities)

            response = send_prompt(prompt)
            response_text = extract_text_from_response(response)
            formatted_response = format_gemini_response(response_text)

            print("\n" + "="*55 + "\n")
            print(formatted_response)
            print("\n" + "="*55 + "\n")
            # for chunk in response:
            #     if hasattr(chunk, "text"):
            #         print(chunk.text.strip(), end="")
            #     else:
            #         print(str(chunk).strip(), end="")
            # print("\n\n-------------------------------------------------------\n")

        except Exception as e:
            print(f"⚠️ Error: {e}")
            print("Please try again or check logs.")

if __name__ == "__main__":
    main()