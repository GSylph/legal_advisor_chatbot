from .logger import log_error
from .chat_service import ChatService
import sys

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

def main():
    service = ChatService(kb_path="corpus/raw")
    print("\n📘 Welcome to the Singapore Legal Advisor Chatbot!")
    print("Type your legal question below. Type 'exit' or 'quit' to end the session.\n")

    while True:
        user_input = input("🧑 You: ").strip()
        if user_input.lower() in ["exit", "quit"]:
            print("👋 Exiting. Stay legally safe!")
            break

        try:
            _, formatted_response = service.run_turn(user_input)
        except Exception as e:
            log_error(str(e))
            print(f"⚠️ Error: {e}")
            print("Please try again or check logs.")
            continue

        print("\n🤖 Gemini Legal Advisor:\n")
        print(formatted_response)
        print("\n" + "=" * 55 + "\n")

if __name__ == "__main__":
    main()