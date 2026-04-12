# Annotation Guidelines — Legal QA Benchmark

## Overview

This guide defines how to create and validate QA pairs for evaluating the Legal Advisor Chatbot on Singapore law. Each annotator should produce records following the schema below, ensuring factual accuracy against the source statute.

## Record Schema

```json
{
  "id": "b001",
  "question": "What is the penalty for theft of property worth over $1000?",
  "answer": "Imprisonment up to 7 years and a fine",
  "source_act": "Penal Code",
  "source_section": "379A",
  "task_type": "penalty_obligation",
  "difficulty": "medium",
  "domain": "employment"
}
```

## Task Types

### 1. statute_existence
Does a specific Act exist in Singapore law?

**Examples:**
- "Is there a Personal Data Protection Act in Singapore?" → Yes, PDPA 2012.
- "Does Singapore have a Freedom of Information Act?" → No.
- "Is there a law governing employment contracts in Singapore?" → Yes, Employment Act 1968.

### 2. section_location
Which section of which Act covers a given topic?

**Examples:**
- "Which section of the Employment Act covers notice periods?" → Section 10.
- "Where in the PDPA is consent for data collection defined?" → Section 13.
- "Which provision of the Employment Act addresses salary payment deadlines?" → Section 21.

### 3. penalty_obligation
What is the penalty, obligation, or legal consequence for a given action?

**Examples:**
- "What happens if an employer withholds salary beyond 7 days?" → Violation of Section 21 of the Employment Act; employer may be fined.
- "What is the consequence of collecting personal data without consent?" → Breach of Section 13 PDPA; financial penalty up to $1 million.
- "What remedies exist for wrongful termination?" → Reinstatement or compensation under Section 14 of the Employment Act.

### 4. defined_term
How does a specific Act define a legal term?

**Examples:**
- "How does the PDPA define 'personal data'?" → Data about an individual who can be identified from that data.
- "What is 'constructive dismissal' under Singapore law?" → When an employer's conduct fundamentally breaches the employment contract, forcing the employee to resign.
- "How does the Employment Act define 'employee'?" → A person who has entered into a contract of service with an employer.

### 5. amendment_date
When was a provision last amended or enacted?

**Examples:**
- "When was the PDPA enacted?" → 2012, with major amendments in 2020.
- "When was Section 10 of the Employment Act last amended?" → Amended under the Employment (Amendment) Act 2018.
- "When did the data breach notification requirement come into effect?" → February 2021 (Part VIA of the PDPA).

### 6. cross_reference
Which Act or body of law governs a given area?

**Examples:**
- "Which law governs unfair trade practices in Singapore?" → Consumer Protection (Fair Trading) Act.
- "What regulates personal data handling by businesses?" → Personal Data Protection Act 2012.
- "Which Act covers employment disputes?" → Employment Act 1968 and the Employment Claims Act 2016.

## Domains

Each question belongs to one of three domains:
- **employment** — Employment Act 1968, wrongful termination, wages, notice, retrenchment
- **contract** — Contract law, misrepresentation, unfair practices, Consumer Protection (Fair Trading) Act
- **pdpa** — Personal Data Protection Act 2012, consent, data breaches, DNC registry

## Difficulty Levels

- **easy** — Direct factual lookup, single statute reference
- **medium** — Requires combining 1–2 provisions or contextual reasoning
- **hard** — Requires cross-referencing statutes, edge cases, or nuanced interpretation

## Quality Checklist

1. The gold answer is factually correct against the source statute text
2. The source_act and source_section are precise and verifiable
3. The question is unambiguous and answerable from the corpus
4. The task_type is correctly assigned
5. The difficulty is reasonable (not all "easy")
6. Domain distribution is balanced across employment, contract, and PDPA
