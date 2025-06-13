import re
import textwrap

def extract_section(text, header):
    pattern = re.compile(
        rf"(?i)^\s*{header}\s*\n(.*?)(?=\n\s*[A-Z][^\n]*\n|\Z)", 
        re.DOTALL | re.MULTILINE
    )
    match = pattern.search(text)
    if match:
        return match.group(1).strip()
    return ""




def extract_bullets(section_text):
    """Parses bullet points or step-like lines from a section."""
    bullets = []
    lines = section_text.splitlines()
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # Accept bullets or numbered steps
        if re.match(r"^[-*•]\s+", line) or re.match(r"^\d+\.\s+", line):
            bullets.append(re.sub(r"^[-*•]|\d+\.", "", line).strip())
        else:
            bullets.append(line)
    return bullets




def format_response(raw_text):
    raw_text = textwrap.dedent(raw_text)  # Remove any indentation from multiline strings
    return {
        "summary": extract_section(raw_text, "Summary") or "Not available.",
        "steps_to_take": extract_bullets(extract_section(raw_text, "Steps to Take")) or ["No steps provided."],
        "warnings": extract_bullets(extract_section(raw_text, "Warnings")) or ["No warnings found."],
        "relevant_contacts": extract_bullets(extract_section(raw_text, "Relevant Contacts")) or ["None specified."],
        "disclaimer": extract_section(raw_text, "Disclaimer") or "This is not legal advice."
    }

if __name__ == "__main__":
    sample_text = """
    Summary
This case involves a property boundary dispute between neighbors.

Steps to Take
- Review land title documents.
- Contact a licensed surveyor.
- File a report with the Singapore Land Authority (SLA).
- Consider mediation before pursuing court action.

Warnings
- Do not begin construction before resolving the dispute.
- Avoid trespassing on disputed land.

Relevant Contacts
- Singapore Land Authority (SLA)
- Community Justice Centre (for mediation)
- A certified property lawyer

Disclaimer
This advice is provided by an AI and should not be considered a legal verdict.
"""
    formatted = format_response(sample_text)
    print("Formatted Response:")
    for key, value in formatted.items():
        print(f"{key}: {value} \n")