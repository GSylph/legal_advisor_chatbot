from src.response_formatter import format_gemini_response

# Simulate an empty or garbage Gemini response
raw_response = "This is something vague with no clear legal structure."

formatted = format_gemini_response(raw_response)
print("\n=== FALLBACK TEST ===")
print(formatted)
