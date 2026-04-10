# Wrapper that loads Groq API client with key rotation
import os
import time
import re
import threading
from groq import Groq
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Load API keys: GROQ_API_KEY is primary, GROQ_API_KEY_2, _3, etc. are extras
# Set multiple keys in .env to rotate past daily token limits:
#   GROQ_API_KEY=gsk_abc...
#   GROQ_API_KEY_2=gsk_def...
#   GROQ_API_KEY_3=gsk_ghi...
_api_keys = []
primary = os.getenv("GROQ_API_KEY")
if primary:
    _api_keys.append(primary)
for i in range(2, 20):
    key = os.getenv(f"GROQ_API_KEY_{i}")
    if key:
        _api_keys.append(key)

if not _api_keys:
    raise ValueError("GROQ_API_KEY environment variable is not set.")

_current_key_idx = 0
client = Groq(api_key=_api_keys[0])
MODEL = "llama-3.1-8b-instant"
_key_lock = threading.Lock()

print(f"Groq API client initialized with {len(_api_keys)} key(s).")

# Retry settings
MAX_RETRIES = 5
BASE_WAIT = 10  # seconds


def _rotate_key() -> bool:
    """Switch to the next API key. Returns False if all keys exhausted. Thread-safe."""
    global _current_key_idx, client
    with _key_lock:
        _current_key_idx += 1
        if _current_key_idx >= len(_api_keys):
            return False
        client = Groq(api_key=_api_keys[_current_key_idx])
        print(f"  [key-rotation] switched to key {_current_key_idx + 1}/{len(_api_keys)}")
        return True


def _is_daily_limit(error_msg: str) -> bool:
    """Check if the 429 is a daily (TPD) limit vs a short-term (RPM/TPM) limit."""
    return "tokens per day" in error_msg.lower() or "TPD" in error_msg


def _parse_retry_after(error_msg: str) -> float:
    """Extract wait time from Groq 429 error message."""
    match = re.search(r"Please try again in (\d+)m([\d.]+)s", error_msg)
    if match:
        return int(match.group(1)) * 60 + float(match.group(2))
    match = re.search(r"Please try again in ([\d.]+)s", error_msg)
    if match:
        return float(match.group(1))
    return 0


SYSTEM_PROMPT = (
    "You are a legal advisor helping people understand Singapore law. "
    "Only use information from the provided context. "
    "Never invent statutory references not present in the context. "
    "Every factual claim must cite the source as [Act Name, Section X]. "
    "End every answer with [Confidence: HIGH / MEDIUM / LOW / INSUFFICIENT CONTEXT] "
    "based on how well the provided context supports your answer. "
    "If context is insufficient, say so explicitly — do not guess."
)


def send_prompt_stream(prompt: str):
    """Stream token chunks from Groq. Yields raw text strings.
    Uses same retry/key-rotation logic as send_prompt().
    """
    for attempt in range(MAX_RETRIES):
        try:
            stream = client.chat.completions.create(
                model=MODEL,
                temperature=0.1,
                max_tokens=1000,
                stream=True,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ]
            )
            for chunk in stream:
                delta = chunk.choices[0].delta.content
                if delta:
                    yield delta
            return
        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "rate_limit" in error_msg.lower():
                if _is_daily_limit(error_msg):
                    print(f"  [daily-limit] key {_current_key_idx + 1} exhausted")
                    if _rotate_key():
                        continue
                    raise RuntimeError(
                        f"All {len(_api_keys)} API keys exhausted daily limit."
                    )
                wait = _parse_retry_after(error_msg)
                if wait <= 0:
                    wait = BASE_WAIT * (2 ** attempt)
                print(f"  [rate-limited] waiting {wait:.0f}s (attempt {attempt + 1}/{MAX_RETRIES})...")
                time.sleep(wait + 1)
                continue
            raise RuntimeError(f"Streaming error: {error_msg}")
    raise RuntimeError(f"Rate limit exceeded after {MAX_RETRIES} retries")


def send_prompt(prompt: str):
    """Send a prompt to the Groq model with key rotation and retry on rate limits."""
    last_error = None
    for attempt in range(MAX_RETRIES):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                temperature=0.1,  # low temp: legal advice must be consistent
                max_tokens=1000,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ]
            )
            return response
        except Exception as e:
            last_error = e
            error_msg = str(e)
            if "429" in error_msg or "rate_limit" in error_msg.lower():
                # Daily limit → rotate key immediately
                if _is_daily_limit(error_msg):
                    print(f"  [daily-limit] key {_current_key_idx + 1} exhausted")
                    if _rotate_key():
                        continue  # retry immediately with new key
                    raise RuntimeError(
                        f"All {len(_api_keys)} API keys exhausted daily limit. "
                        f"Add more keys to .env or wait for reset."
                    )
                # Short-term limit (RPM/TPM) → wait and retry same key
                wait = _parse_retry_after(error_msg)
                if wait <= 0:
                    wait = BASE_WAIT * (2 ** attempt)
                print(f"  [rate-limited] waiting {wait:.0f}s (attempt {attempt + 1}/{MAX_RETRIES})...")
                time.sleep(wait + 1)
                continue
            raise RuntimeError(f"Error generating content via Groq: {error_msg}")
    raise RuntimeError(f"Rate limit exceeded after {MAX_RETRIES} retries: {last_error}")


def extract_text_from_response(response):
    """Extract text from the Groq response object."""
    try:
        return response.choices[0].message.content
    except Exception as e:
        raise ValueError(f"Failed to extract text from Groq response: {e}")
