from api_client import send_prompt
from intent_classifier import classify_intent

def handle_user_input(user_input):
    intent=classify_intent(user_input)
    print(f"[DEBUG] Intent: {intent}")

while(True):
    user_input = input("Enter your prompt: ")
    handle_user_input(user_input)
    # response = send_prompt(user_input)
    # print("\n--------------------------:\n")
    # print("Gemini:\n")
    # for chunk in response:
    #     print(chunk.text)
    # print("\n--------------------------:\n")
