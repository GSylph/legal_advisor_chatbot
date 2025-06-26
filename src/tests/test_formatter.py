import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from response_formatter import format_gemini_response

raw_response = """
**1. Summary**
Your property rights are protected under inheritance law.

**2. Steps**
* **Consult Lawyer**: Get legal advice.
* **File Complaint**: Approach civil court if necessary.
"""

formatted = format_gemini_response(raw_response)
print("\n=== FORMATTED RESPONSE ===")
print(formatted)
