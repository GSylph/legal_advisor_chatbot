#Wrapper that loads Gemini API client 
from dotenv import load_dotenv
import os
import google.genai as genai


# Load environment variables from .env file
load_dotenv()


# Get the API key from environment variables
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable is not set.")

# Initialize the Gemini API client with google.genai
client = genai.Client(api_key=API_KEY)

# Print a success message
print("Gemini API client initialized successfully.")

def send_prompt(prompt):
    """Send a prompt to the Gemini model and return the response."""
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response
    except Exception as e:
        raise RuntimeError(f"Error generating content: {str(e)}")
    
def extract_text_from_response(response):
    try:
        return response.text
    except Exception as e:
        raise ValueError(f"Failed to extract text from Gemini response: {e}")
