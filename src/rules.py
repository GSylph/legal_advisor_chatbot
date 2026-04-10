from typing import Optional, List, Dict
import re

class SingaporeLegalEngine:
    """
    A custom, robust symbolic rule engine for Singapore Law.
    Replaces experta for better compatibility with modern Python.
    """
    def __init__(self):
        self.result = {
            "rule_matched": False,
            "statute": None,
            "section": None,
            "violation": None,
            "confidence": "none"
        }

    def run(self, attrs: dict):
        # 1. Employment Act 1968 - Section 11 (Wrongful Termination)
        if (attrs.get("employment_type") == "permanent" and 
            attrs.get("notice_given") == "false" and 
            attrs.get("cause") == "none"):
            self.result = {
                "rule_matched": True,
                "statute": "Employment Act 1968",
                "section": "Section 11",
                "violation": "Wrongful dismissal without notice or salary in lieu of notice",
                "confidence": "high"
            }
            return

        # 2. Employment Act 1968 - Section 10 (Insufficient Notice)
        if (attrs.get("employment_type") == "permanent" and 
            attrs.get("notice_given") == "true"):
            weeks = attrs.get("notice_period_weeks")
            if weeks and int(weeks) < 4:
                self.result = {
                    "rule_matched": True,
                    "statute": "Employment Act 1968",
                    "section": "Section 10",
                    "violation": "Notice period shorter than statutory minimum",
                    "confidence": "high"
                }
                return

        # 3. Employment Act 1968 - Section 21 (Wage Withholding)
        if attrs.get("wage_withheld") == "true":
            days = attrs.get("days_delayed")
            if days and int(days) > 7:
                self.result = {
                    "rule_matched": True,
                    "statute": "Employment Act 1968",
                    "section": "Section 21",
                    "violation": "Salary not paid within 7 days after end of salary period",
                    "confidence": "high"
                }
                return

        # 4. Constructive Dismissal
        if (attrs.get("employment_type") == "permanent" and 
            attrs.get("cause") == "none" and 
            attrs.get("early_termination") == "true"):
            self.result = {
                "rule_matched": True,
                "statute": "Employment Act 1968",
                "section": "Section 14 / common law",
                "violation": "Potential constructive dismissal — significant contract variation without consent",
                "confidence": "medium"
            }
            return

        # 5. Redundancy
        if (attrs.get("cause") == "redundancy" and 
            attrs.get("notice_given") == "false"):
            self.result = {
                "rule_matched": True,
                "statute": "Employment Act 1968 / Tripartite Guidelines",
                "section": "Section 45 / Tripartite Advisory",
                "violation": "Retrenchment without notice or retrenchment benefit may be claimable",
                "confidence": "medium"
            }
            return

        # 6. Fixed-Term Contract Early Termination
        if (attrs.get("contract_type") == "fixed_term" and 
            attrs.get("early_termination") == "true" and 
            attrs.get("penalty_clause") == "absent"):
            self.result = {
                "rule_matched": True,
                "statute": "Contract law principles (Singapore)",
                "section": "Breach of contract / damages",
                "violation": "Early termination of fixed-term contract may constitute breach",
                "confidence": "high"
            }
            return

        # 7. Unauthorised Deduction
        if (attrs.get("wage_withheld") == "true" and 
            attrs.get("days_delayed") == "0"):
            self.result = {
                "rule_matched": True,
                "statute": "Employment Act 1968",
                "section": "Section 27",
                "violation": "Deductions from salary not permitted except under Section 27 exceptions",
                "confidence": "high"
            }
            return

        # 8. Minor Contract
        if attrs.get("minor_party") == "true":
            self.result = {
                "rule_matched": True,
                "statute": "Contracts (Age of Majority) Act 1970 / Minors' Contracts Act",
                "section": "Age of majority provisions",
                "violation": "Contract with a minor is generally not enforceable against the minor",
                "confidence": "high"
            }
            return

        # 9. No Consideration
        if attrs.get("consideration_absent") == "true":
            self.result = {
                "rule_matched": True,
                "statute": "Singapore contract law (common law)",
                "section": "Consideration doctrine",
                "violation": "Contract without consideration is not enforceable",
                "confidence": "high"
            }
            return

        # 10. Fraudulent Misrepresentation
        if attrs.get("misrepresentation") == "fraudulent":
            self.result = {
                "rule_matched": True,
                "statute": "Misrepresentation Act (Cap. 390)",
                "section": "Section 2(1)",
                "violation": "Fraudulent misrepresentation — contract voidable, damages available",
                "confidence": "high"
            }
            return

        # 11. Negligent Misrepresentation
        if attrs.get("misrepresentation") == "negligent":
            self.result = {
                "rule_matched": True,
                "statute": "Misrepresentation Act (Cap. 390)",
                "section": "Section 2(1)",
                "violation": "Negligent misrepresentation — damages claimable even without fraud intent",
                "confidence": "high"
            }
            return

        # 12. Consumer Unfair Practice
        if attrs.get("unfair_practice") == "true" and attrs.get("good_returned") == "false":
            days = attrs.get("days_since_purchase")
            if days and int(days) < 30:
                self.result = {
                    "rule_matched": True,
                    "statute": "Consumer Protection (Fair Trading) Act (Cap. 52A)",
                    "section": "Section 6",
                    "violation": "Unfair practice by supplier — consumer may seek cancellation of contract",
                    "confidence": "medium"
                }
                return

        # 13. PDPA - Collection without Consent
        if (attrs.get("data_collected") == "personal" and 
            attrs.get("consent_obtained") == "false" and 
            attrs.get("purpose_notified") == "false"):
            self.result = {
                "rule_matched": True,
                "statute": "Personal Data Protection Act 2012",
                "section": "Section 13 / Section 20",
                "violation": "Personal data collected without consent and without notifying purpose",
                "confidence": "high"
            }
            return

        # 14. PDPA - Access Request
        if attrs.get("data_subject_request") == "access":
            self.result = {
                "rule_matched": True,
                "statute": "Personal Data Protection Act 2012",
                "section": "Section 21",
                "violation": "Organisation must provide access to personal data within reasonable time",
                "confidence": "high"
            }
            return

        # 15. PDPA - Correction Request
        if attrs.get("data_subject_request") == "correction":
            self.result = {
                "rule_matched": True,
                "statute": "Personal Data Protection Act 2012",
                "section": "Section 22",
                "violation": "Organisation must correct personal data that is inaccurate or incomplete",
                "confidence": "high"
            }
            return

        # 16. PDPA - Consent Withdrawal
        if (attrs.get("data_subject_request") == "withdrawal" and 
            attrs.get("consent_obtained") == "true"):
            self.result = {
                "rule_matched": True,
                "statute": "Personal Data Protection Act 2012",
                "section": "Section 16",
                "violation": "Organisation must give effect to withdrawal of consent within reasonable time",
                "confidence": "high"
            }
            return

        # 17. PDPA - Breach Notification
        if attrs.get("breach_detected") == "true":
            days = attrs.get("notification_delay_days")
            if days and int(days) > 3:
                self.result = {
                    "rule_matched": True,
                    "statute": "Personal Data Protection Act 2012 (amended 2021)",
                    "section": "Section 26D",
                    "violation": "Data breach causing significant harm must be notified to PDPC within 3 business days",
                    "confidence": "high"
                }
                return

        # 18. PDPA - DNC Registry
        if attrs.get("do_not_call") == "true":
            self.result = {
                "rule_matched": True,
                "statute": "Personal Data Protection Act 2012",
                "section": "Part IX — Do Not Call Registry",
                "violation": "Sending unsolicited telemarketing messages to DNC-registered number",
                "confidence": "high"
            }
            return

        # 19. PDPA - Sensitive Data
        if (attrs.get("data_collected") == "sensitive" and 
            attrs.get("consent_obtained") == "false"):
            self.result = {
                "rule_matched": True,
                "statute": "Personal Data Protection Act 2012 / PDPC Advisory Guidelines",
                "section": "Section 13 + PDPC Advisory on NRIC",
                "violation": "Sensitive personal data (health, NRIC, financial) requires explicit consent",
                "confidence": "high"
            }
            return

        # 20. AI Governance
        if (attrs.get("ai_system_risk") == "high" and 
            attrs.get("conformity_assessment") == "not_done"):
            self.result = {
                "rule_matched": True,
                "statute": "PDPC Model AI Governance Framework (Singapore) / EU AI Act Art.43",
                "section": "PDPC Framework Section 2 / EU AI Act Article 43",
                "violation": "High-risk AI system deployed without governance assessment or conformity check",
                "confidence": "medium"
            }
            return


def check_consistency(entities: dict, intents: List[str], user_input: str, llm_statute: str) -> dict:
    """
    Args:
        entities: output of entity_extractor.extract()
        intents: list of matched intent labels
        user_input: the raw user query
        llm_statute: extracted applicable_law string from response_formatter

    Returns:
        dict with keys: rule_matched, statute, section, violation, consistent, confidence
    """
    attrs = _map_entities_to_attrs(entities, intents, user_input)

    engine = SingaporeLegalEngine()
    engine.run(attrs)

    result = engine.result.copy()

    # Consistency check: does LLM statute match rule engine statute?
    if result["rule_matched"] and llm_statute:
        llm_statute_lower = llm_statute.lower()
        rule_statute_lower = result["statute"].lower()
        
        # 1. Statute name matching
        # Check if the core statute name matches (e.g., "Personal Data Protection Act" or "Employment Act")
        statute_name_match = False
        core_names = ["Employment Act", "Personal Data Protection Act", "Misrepresentation Act", "Consumer Protection", "Contracts Act"]
        for cn in core_names:
            cnl = cn.lower()
            if cnl in llm_statute_lower and cnl in rule_statute_lower:
                statute_name_match = True
                break
        
        if not statute_name_match:
            statute_name_match = (rule_statute_lower in llm_statute_lower) or (llm_statute_lower in rule_statute_lower)
        
        # 2. Section matching (numeric)
        section_match = False
        if result["section"]:
            # Extract all numbers from both section strings
            rule_sections = re.findall(r'\d+', result["section"])
            llm_sections = re.findall(r'\d+', llm_statute)
            
            # If any number from rule's section matches any number in LLM's statute string
            if any(s in llm_sections for s in rule_sections):
                section_match = True
            
        result["consistent"] = statute_name_match and (section_match or not result["section"])
        
        # Special case: common law rules with no numeric section
        if "common law" in rule_statute_lower:
            result["consistent"] = statute_name_match
            
    else:
        result["consistent"] = None  # Cannot determine — no rule matched

    return result


def _map_entities_to_attrs(entities: dict, intents: List[str], query: str) -> dict:
    """
    Heuristic mapping from query and intents to symbolic attributes.
    """
    attrs = {}
    q = query.lower()

    # Domain context from intents or keywords
    if "employment" in intents or any(x in q for x in ["fired", "employer", "salary", "termination", "wages", "work"]):
        # Default to permanent for employment context unless explicitly stated otherwise
        attrs["employment_type"] = "permanent"
        if any(x in q for x in ["contractual", "temporary", "part-time"]):
            attrs["employment_type"] = "contractual"
        
        # Notice
        if any(x in q for x in ["no notice", "without any notice", "without notice", "fired today"]):
            attrs["notice_given"] = "false"
        elif any(x in q for x in ["gave me", "notice period"]):
            attrs["notice_given"] = "true"
            
        # Cause
        if any(x in q for x in ["redundant", "retrenchment", "downsizing"]):
            attrs["cause"] = "redundancy"
        elif any(x in q for x in ["fired", "terminated"]):
            attrs["cause"] = "misconduct" if "misconduct" in q else "none"
        
        # Notice Period
        weeks_match = re.search(r'(\d+)\s+week', q)
        if weeks_match:
            attrs["notice_period_weeks"] = weeks_match.group(1)
            
        # Wage
        if any(x in q for x in ["salary", "pay", "wage"]):
            if any(x in q for x in ["not paid", "owes me", "withheld", "deducted", "weeks after"]):
                attrs["wage_withheld"] = "true"
                
                days_match = re.search(r'(\d+)\s+day', q)
                if days_match:
                    attrs["days_delayed"] = days_match.group(1)
                elif "2 weeks" in q:
                    attrs["days_delayed"] = "14"
                elif "1 month" in q:
                    attrs["days_delayed"] = "30"
                elif "deducted" in q:
                    attrs["days_delayed"] = "0"

    if "contract" in intents or "agreement" in q:
        if "fixed-term" in q or "1-year" in q:
            attrs["contract_type"] = "fixed_term"
        
        if any(x in q for x in ["terminated", "ended"]):
            attrs["early_termination"] = "true"
            
        if any(x in q for x in ["no penalty", "without penalty"]):
            attrs["penalty_clause"] = "absent"
            
        if "promise" in q and "free" in q:
            attrs["consideration_absent"] = "true"
            
        if any(x in q for x in ["false information", "lied", "deliberately"]):
            attrs["misrepresentation"] = "fraudulent"
        elif "incorrect information" in q or "without checking" in q:
            attrs["misrepresentation"] = "negligent"

        if any(x in q for x in ["16-year-old", "minor", "child"]):
            attrs["minor_party"] = "true"

    if "consumer_rights" in intents or any(x in q for x in ["buy", "purchase", "refund", "shop"]):
        if any(x in q for x in ["high-pressure", "forced", "unfair"]):
            attrs["unfair_practice"] = "true"
            attrs["good_returned"] = "false"
            attrs["days_since_purchase"] = "1"

    if "pdpa" in intents or any(x in q for x in ["pdpa", "data", "privacy", "nric", "collected"]):
        if any(x in q for x in ["nric", "medical", "health", "financial"]):
            attrs["data_collected"] = "sensitive"
        else:
            attrs["data_collected"] = "personal"
            
        if any(x in q for x in ["without asking", "no permission", "without my permission", "telling me why", "permission"]):
            attrs["consent_obtained"] = "false"
            attrs["purpose_notified"] = "false"
        
        if any(x in q for x in ["refused", "asked", "provide"]):
            if "what personal data they hold" in q or "access" in q:
                attrs["data_subject_request"] = "access"
            elif "wrong address" in q or "correct" in q:
                attrs["data_subject_request"] = "correction"
            elif "withdrew my consent" in q or "stop using" in q:
                attrs["data_subject_request"] = "withdrawal"
                attrs["consent_obtained"] = "true"

        if "breach" in q:
            attrs["breach_detected"] = "true"
            if "last week" in q:
                attrs["notification_delay_days"] = "7"
                
        if any(x in q for x in ["do not call", "dnc"]):
            attrs["do_not_call"] = "true"

    if "ai" in q and ("system" in q or "risk" in q):
        attrs["ai_system_risk"] = "high"
        attrs["conformity_assessment"] = "not_done"

    return attrs
