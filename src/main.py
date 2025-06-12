from api_client import send_prompt

while(True):
    user_input = input("Enter your prompt: ")
    response = send_prompt(user_input)
    print("\n--------------------------:\n")
    print("Gemini:\n")
    for chunk in response:
        print(chunk.text)
    print("\n--------------------------:\n")