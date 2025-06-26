import os
from datetime import datetime


LOG_DIR= "storage/logs"
os.makedirs(LOG_DIR, exist_ok=True)

def log_fallback_response(raw_response: str):
    filename = os.path.join(LOG_DIR, "fallback_responses.log")
    with open(filename, "a") as f:
        f.write("\n=== Gemini Fallback @ " + datetime.now().isoformat() + " ===\n")
        f.write(raw_response.strip() + "\n\n")

def log_error(error_message: str):
    filename=os.path.join(LOG_DIR, "errors.log")
    with open(filename, "a") as f:
        f.write("\n[ERROR] " + datetime.now().isoformat() + "\n")
        f.write(error_message.strip() + "\n\n")