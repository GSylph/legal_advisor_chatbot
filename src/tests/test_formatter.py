from src.response_formatter import format_and_structure_response, format_gemini_response


def test_formatter_parses_numbered_sections():
	raw_response = """
**1. Summary**
Your property rights are protected under inheritance law.

**2. Steps**
* **Consult Lawyer**: Get legal advice.
* **File Complaint**: Approach civil court if necessary.
"""

	structured, formatted = format_and_structure_response(raw_response)

	assert structured["summary"]
	assert len(structured["steps"]) == 2
	assert "📝 **Steps to Take:**" in formatted


def test_formatter_parses_emoji_markdown_sections_without_fallback():
	raw_response = """
📋 **Summary:**
Landlord threats to force you out without a court order are unlawful.

📝 **Steps to Take:**
* **Document all threats**: Save messages and call records.
* **Seek urgent legal advice**: Ask a tenancy lawyer about injunction options.

⚠️ **Warnings:**
* **Do not self-evict**: Leave only under valid court process.

📞 **Relevant Contacts:**
* **Law Society of Singapore**: Lawyer referrals at www.lawsociety.org.sg

⚖️ **Disclaimer:**
AI-generated guidance only, not legal advice.
"""

	formatted = format_gemini_response(raw_response)

	assert "⚠️ Gemini could not produce a structured response." not in formatted
	assert "📋 **Summary:**" in formatted
	assert "📞 **Relevant Contacts:**" in formatted
