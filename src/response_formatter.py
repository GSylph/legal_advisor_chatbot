import re
from typing import Dict, List, Optional, Tuple

class ResponseFormatter:
    def __init__(self):
        self.sections = {}
        self.section_keywords = {
            'summary': ['summary', 'overview', 'background', 'introduction', 'about'],
            'context': ['context', 'legal framework', 'relevant laws', 'regulations', 'statutes', 'provisions', 'legal basis'],
            'steps': ['steps', 'step', 'action', 'procedure', 'process', 'do'],
            'warnings': ['warning', 'caution', 'alert', 'beware', 'avoid', 'danger'],
            'contacts': ['contact', 'authority', 'organization', 'agency', 'bureau', 'office'],
            'disclaimer': ['disclaimer', 'note', 'important', 'legal advice', 'guidance']
        }
    
    def parse_response(self, response_text: str) -> Dict:
        """
        Dynamically parse response text and extract structured information
        """
        self.sections = {
            'summary': '',
            'context': '',
            'steps': [],
            'warnings': [],
            'contacts': [],
            'disclaimer': ''
        }
        
        # Clean and normalize text
        cleaned_text = self._normalize_text(response_text)
        
        # Find section headers dynamically
        section_headers = self._find_section_headers(cleaned_text)
        
        # Extract content for each section
        for section_name, header_info in section_headers.items():
            content = self._extract_section_content(cleaned_text, header_info, section_headers)
            self._process_section_content(section_name, content)
        
        return self.sections
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text for better parsing"""
        # Remove excessive whitespace but preserve structure
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = re.sub(r'[ \t]+', ' ', text)
        return text.strip()
    
    def _find_section_headers(self, text: str) -> Dict[str, Dict]:
        """
        Dynamically find section headers based on keywords and patterns
        """
        headers = {}
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            line_clean = line.strip().lower()
            
            # Skip empty lines
            if not line_clean:
                continue
            
            # Check if line looks like a header (bold, numbered, etc.)
            if self._is_header_like(line):
                section_type = self._classify_header(line_clean)
                if section_type:
                    headers[section_type] = {
                        'line_number': i,
                        'original_text': line.strip(),
                        'clean_text': line_clean
                    }
        
        return headers
    
    def _is_header_like(self, line: str) -> bool:
        """
        Check if a line looks like a section header
        """
        line_clean = line.strip()
        
        # Patterns that suggest a header
        header_patterns = [
            r'^\*\*\d+\.\s*.*\*\*',  # **1. Section Name**
            r'^\d+\.\s*[A-Z]',       # 1. Section Name
            r'^\*\*[A-Z].*\*\*',     # **Section Name**
            r'^[A-Z][A-Z\s]+:',      # SECTION NAME:
            r'^#{1,6}\s',            # Markdown headers
        ]
        
        return any(re.match(pattern, line_clean) for pattern in header_patterns)
    
    def _classify_header(self, header_text: str) -> Optional[str]:
        """
        Classify header text into section types based on keywords
        """
        # Remove formatting and get key words
        clean_header = re.sub(r'[*#\d\.\-:]', '', header_text).strip()
        words = clean_header.split()
        
        # Score each section type based on keyword matches
        scores = {}
        for section_type, keywords in self.section_keywords.items():
            score = 0
            for word in words:
                for keyword in keywords:
                    if keyword in word or word in keyword:
                        score += 1
            if score > 0:
                scores[section_type] = score
        
        # Return the section type with highest score
        return max(scores, key=scores.get) if scores else None
    
    def _extract_section_content(self, text: str, header_info: Dict, all_headers: Dict) -> str:
        """
        Extract content between current header and next header
        """
        lines = text.split('\n')
        start_line = header_info['line_number'] + 1
        
        # Find the next header to determine end boundary
        next_line = len(lines)
        for other_section, other_header in all_headers.items():
            if other_header['line_number'] > header_info['line_number']:
                next_line = min(next_line, other_header['line_number'])
        
        # Extract content between headers
        content_lines = lines[start_line:next_line]
        return '\n'.join(content_lines).strip()
    
    def _process_section_content(self, section_type: str, content: str) -> None:
        """
        Process content based on section type
        """
        if section_type in ['disclaimer', 'summary', 'context']:
            self.sections[section_type] = self._clean_text_content(content)
        else:
            items = self._extract_list_items(content)
            self.sections[section_type] = items
    
    def _extract_list_items(self, content: str) -> List[Dict]:
        """
        Extract list items from content (bullet points, numbered items, etc.)
        """
        items = []
        
        # First try to extract items with title and description in one go
        # Pattern: * **Title**: Description (multi-line)
        title_desc_pattern = r'\*\s*\*\*(.*?)\*\*:\s*(.*?)(?=\*\s*\*\*|$)'
        matches = re.findall(title_desc_pattern, content, re.MULTILINE | re.DOTALL)
        
        if matches:
            for title, description in matches:
                title_clean = self._clean_text_content(title)
                desc_clean = self._clean_text_content(description)
                
                # Skip if description is too short or just says "Item"
                if desc_clean and len(desc_clean) > 5 and desc_clean.lower() != 'item':
                    items.append({
                        'title': title_clean,
                        'description': desc_clean
                    })
        
        # If no title:description pattern found, try simple bullet points
        if not items:
            simple_patterns = [
                r'\*\s*(.*?)(?=\*\s*|$)',      # * Item
                r'^\d+\.\s*(.*?)(?=^\d+\.|$)', # 1. Item
                r'[-•]\s*(.*?)(?=[-•]|$)',     # - Item or • Item
            ]
            
            for pattern in simple_patterns:
                matches = re.findall(pattern, content, re.MULTILINE | re.DOTALL)
                if matches:
                    for match in matches:
                        item_text = self._clean_text_content(match)
                        if len(item_text) > 10:  # Filter out very short items
                            # Try to split into title and description if colon present
                            if ':' in item_text:
                                parts = item_text.split(':', 1)
                                items.append({
                                    'title': parts[0].strip(),
                                    'description': parts[1].strip()
                                })
                            else:
                                # Use first few words as title if item is long
                                words = item_text.split()
                                if len(words) > 8:
                                    title = ' '.join(words[:3])
                                    description = ' '.join(words[3:])
                                    items.append({
                                        'title': title,
                                        'description': description
                                    })
                                else:
                                    items.append({
                                        'title': 'Information',
                                        'description': item_text
                                    })
                    break  # Use first successful pattern
        
        # If still no items found, treat as single block
        if not items and content.strip():
            cleaned_content = self._clean_text_content(content)
            if len(cleaned_content) > 10:
                items.append({
                    'title': 'Information',
                    'description': cleaned_content
                })
        
        return items
    
    def _clean_text_content(self, text: str) -> str:
        """Clean text content by removing formatting and normalizing"""
        # Remove markdown formatting
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # Bold
        text = re.sub(r'\*(.*?)\*', r'\1', text)      # Italic
        text = re.sub(r'`(.*?)`', r'\1', text)        # Code
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def _extract_contact_info(self, text: str) -> Dict:
        """Extract contact information like websites, emails, phones"""
        contact_info = {}
        
        # Extract websites
        websites = re.findall(r'https?://[^\s\]]+', text)
        if websites:
            contact_info['website'] = websites[0]
        
        # Extract emails
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
        if emails:
            contact_info['email'] = emails[0]
        
        # Extract phone numbers (basic pattern)
        phones = re.findall(r'[\+]?[\d\s\-\(\)]{8,}', text)
        if phones:
            contact_info['phone'] = phones[0].strip()
        
        return contact_info
    
    def format_output(self, parsed_data: Dict) -> str:
        """
        Format parsed data into readable output
        """
        output = "🧠 Gemini says:\n\n"
        
        # Format summary first
        if parsed_data.get('summary'):
            output += "📋 **Summary:**\n"
            output += f"{parsed_data['summary']}\n\n"
        
        # Format context section (new addition)
        if parsed_data.get('context'):
            output += "📚 **Legal Context & Framework:**\n"
            output += f"{parsed_data['context']}\n\n"
        else:
            output += "📚 **Legal Context & Framework:**\n"
            output += "No specific legal context or framework information was provided in the response.\n\n"
        
        # Format steps
        if parsed_data.get('steps'):
            output += "📝 **Steps to Take:**\n"
            for step in parsed_data['steps']:
                title = step.get('title', 'Step')
                description = step.get('description', '')
                output += f"• **{title}**: {description}\n"
            output += "\n"
        else:
            output += "📝 **Steps to Take:**\n- No specific steps provided.\n\n"
        
        # Format warnings
        if parsed_data.get('warnings'):
            output += "⚠️ **Warnings:**\n"
            for warning in parsed_data['warnings']:
                title = warning.get('title', 'Warning')
                description = warning.get('description', '')
                output += f"• **{title}**: {description}\n"
            output += "\n"
        else:
            output += "⚠️ **Warnings:**\n- No specific warnings found.\n\n"
        
        # Format contacts
        if parsed_data.get('contacts'):
            output += "📞 **Relevant Contacts:**\n"
            for contact in parsed_data['contacts']:
                title = contact.get('title', 'Contact')
                description = contact.get('description', '')
                output += f"• **{title}**: {description}"
                
                # Add contact info if available
                contact_info = self._extract_contact_info(description)
                if contact_info.get('website'):
                    output += f" | Website: {contact_info['website']}"
                output += "\n"
            output += "\n"
        else:
            output += "📞 **Relevant Contacts:**\n- No specific contacts provided.\n\n"
        
        # Format disclaimer
        output += "⚖️ **Disclaimer:**\n"
        if parsed_data.get('disclaimer'):
            output += parsed_data['disclaimer']
        else:
            output += "This information is for general guidance only and does not constitute professional legal advice."
        
        return output

def format_gemini_response(response_text: str) -> str:
    """
    Main function to format Gemini response
    
    Args:
        response_text (str): Raw response text from Gemini
    
    Returns:
        str: Formatted response
    """
    formatter = ResponseFormatter()
    parsed_data = formatter.parse_response(response_text)
    return formatter.format_output(parsed_data)

# Example usage and testing
if __name__ == "__main__":
    # Test with sample response including context
    sample_response = """
    **1. Summary**
    This is a summary of the legal issue regarding employment termination.
    
    **2. Context**
    This is the context of the legal issue, including relevant laws and regulations retrieved from the knowledge base. According to Section 25-F of the Industrial Disputes Act, 1947, no workman employed in any industry who has been in continuous service for not less than one year under an employer shall be retrenched by that employer until certain conditions are met. The Employee State Insurance Act, 1948 also provides certain protections for workers facing termination.

    **3. Steps to Take**
    * **Gather Evidence:** Collect all relevant documents and photographs including employment contract, termination letter, and service records.
    * **Consult Lawyer:** Seek professional legal advice from a qualified labor law attorney.
    * **File Complaint:** Submit formal complaint to relevant labor authorities or industrial tribunal.
    
    **4. Warnings**
    * **Do Not Delay:** Time limitations may apply to your case under the Industrial Disputes Act.
    * **Avoid Direct Confrontation:** This could escalate the situation and harm your legal position.
    
    **5. Relevant Contacts**
    * **Legal Aid Bureau:** Provides assistance to those who need legal help. Website: https://example.com
    * **Labor Commissioner Office:** Contact for filing labor dispute complaints and guidance.
    * **Industrial Tribunal:** For formal adjudication of industrial disputes.
    
    **6. Disclaimer**
    This information is for general guidance only and does not constitute legal advice. Please consult with a qualified attorney for advice specific to your situation.
    """
    
    formatted = format_gemini_response(sample_response)
    print(formatted)