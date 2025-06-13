#Wrapper that loads Gemini API client 
from dotenv import load_dotenv
import os
import  google.generativeai as  genai


# Load environment variables from .env file
load_dotenv()


# Get the API key from environment variables
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable is not set.")

# Initialize the Gemini API client
genai.configure(api_key=API_KEY)


# Print a success message
print("Gemini API client initialized successfully.")

model=genai.GenerativeModel("gemini-2.0-flash")
# Check if the model is loaded correctly
if not model:
    raise RuntimeError("Failed to load the Gemini model.")
# Print a success message
print("Gemini model loaded successfully.")

def send_prompt(prompt):
    """Send a prompt to the Gemini model and return the response."""
    try:
        response = model.generate_content(contents=prompt, stream=False)
        return response
    except Exception as e:
        raise RuntimeError(f"Error generating content: {str(e)}")
    
def extract_text_from_response(response):
    try:
        return response.candidates[0].content.parts[0].text
    except Exception as e:
        raise ValueError(f"Failed to extract text from Gemini response: {e}")
