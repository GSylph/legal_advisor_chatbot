import pytest
from src.rules import check_consistency

def test_rule1_wrongful_termination():
    # Scenario: Wrongful termination without notice
    user_input = "My employer fired me today without any notice. I have been working full-time for 3 years."
    intents = ["employment"]
    entities = {} # Rule engine uses heuristic mapping in rules.py
    llm_statute = "Employment Act 1968, Section 11"
    
    result = check_consistency(entities, intents, user_input, llm_statute)
    assert result["rule_matched"] is True
    assert result["statute"] == "Employment Act 1968"
    assert result["section"] == "Section 11"
    assert result["consistent"] is True

def test_rule3_wage_withholding():
    # Scenario: Salary withheld for more than 7 days
    user_input = "My employer has not paid my salary 2 weeks after the end of the month."
    intents = ["employment"]
    entities = {}
    llm_statute = "Employment Act 1968, Section 21"
    
    result = check_consistency(entities, intents, user_input, llm_statute)
    assert result["rule_matched"] is True
    assert result["section"] == "Section 21"
    assert result["consistent"] is True

def test_rule13_pdpa_no_consent():
    # Scenario: Personal data collected without consent
    user_input = "A company collected my NRIC number without telling me why or asking my permission."
    intents = ["pdpa"]
    entities = {}
    llm_statute = "Personal Data Protection Act 2012, Section 13"
    
    result = check_consistency(entities, intents, user_input, llm_statute)
    assert result["rule_matched"] is True
    assert "Personal Data Protection Act" in result["statute"]
    assert result["consistent"] is True

def test_inconsistency_detection():
    # Scenario: LLM identifies a statute that doesn't match the symbolic rule
    user_input = "My employer fired me without notice."
    intents = ["employment"]
    entities = {}
    llm_statute = "PDPA Section 1" # Clearly irrelevant to termination
    
    result = check_consistency(entities, intents, user_input, llm_statute)
    assert result["rule_matched"] is True
    assert result["consistent"] is False

def test_no_rule_match():
    # Scenario: Query doesn't trigger any specific legal rule
    user_input = "How is the weather in Singapore?"
    intents = ["uncategorized"]
    entities = {}
    llm_statute = ""
    
    result = check_consistency(entities, intents, user_input, llm_statute)
    assert result["rule_matched"] is False
    assert result["consistent"] is None
