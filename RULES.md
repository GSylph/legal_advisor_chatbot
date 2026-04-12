# RULES.md — Symbolic Rule Engine Reference (Singapore Law)

> Authoritative list of all 20 experta rules.
> Any change must be reflected here AND in `src/rules.py` AND in the paper appendix.
> Never add a rule without a corresponding benchmark test case in `data/benchmark.json`.

---

## Jurisdiction Note

Rules cover **Singapore law**. Primary statutes referenced:
- Employment Act 1968 (Cap. 91) — employment and termination
- Contracts Act (application of English law principles)
- Personal Data Protection Act 2012 (PDPA) — data protection
- Consumer Protection (Fair Trading) Act — consumer rights
- Misrepresentation Act — contract misrepresentation
- EU AI Act — referenced for GDPR-aligned compliance (Singapore clients with EU exposure)

---

## Attribute Reference (Input to Rule Engine)

These are set by `_map_entities_to_attrs()` in `rules.py`, based on `entity_extractor.py` output.
Only set attributes that are clearly determinable from the query. Never guess.

| Attribute | Possible Values | Domain |
|---|---|---|
| `employment_type` | `permanent`, `contractual`, `part_time` | Employment |
| `notice_given` | `true`, `false` | Employment |
| `cause` | `misconduct`, `poor_performance`, `redundancy`, `none` | Employment |
| `notice_period_weeks` | integer string | Employment |
| `wage_withheld` | `true`, `false` | Employment |
| `days_delayed` | integer string | Employment |
| `salary_above_threshold` | `true`, `false` | Employment (EA coverage threshold) |
| `contract_type` | `fixed_term`, `permanent`, `verbal` | Contract |
| `early_termination` | `true`, `false` | Contract |
| `penalty_clause` | `present`, `absent` | Contract |
| `misrepresentation` | `fraudulent`, `negligent`, `innocent`, `none` | Contract |
| `consideration_absent` | `true`, `false` | Contract |
| `minor_party` | `true`, `false` | Contract |
| `unfair_practice` | `true`, `false` | Consumer |
| `good_returned` | `true`, `false` | Consumer |
| `days_since_purchase` | integer string | Consumer |
| `data_collected` | `personal`, `sensitive`, `anonymous` | PDPA |
| `consent_obtained` | `true`, `false` | PDPA |
| `purpose_notified` | `true`, `false` | PDPA |
| `data_subject_request` | `access`, `correction`, `withdrawal`, `erasure` | PDPA |
| `breach_detected` | `true`, `false` | PDPA |
| `notification_delay_days` | integer string | PDPA |
| `do_not_call` | `true`, `false` | PDPA (DNC Registry) |
| `ai_system_risk` | `high`, `limited`, `minimal` | AI governance |
| `conformity_assessment` | `done`, `not_done` | AI governance |

---

## Singapore Employment Law Rules (8)

### Rule 1 — Wrongful Termination Without Notice
```
IF employment_type = "permanent"
   AND notice_given = "false"
   AND cause = "none"
THEN
   statute    = "Employment Act 1968"
   section    = "Section 11"
   violation  = "Wrongful dismissal without notice or salary in lieu of notice"
   confidence = "high"
```
**Test case:** "My employer fired me today without any notice. I have been working full-time for 3 years."

---

### Rule 2 — Insufficient Notice Period
```
IF employment_type = "permanent"
   AND notice_given = "true"
   AND notice_period_weeks < "4"
   AND salary_above_threshold = "false"
THEN
   statute    = "Employment Act 1968"
   section    = "Section 10"
   violation  = "Notice period shorter than statutory minimum"
   confidence = "high"
```
**Test case:** "My employer gave me only 1 week's notice before termination but my contract says 1 month."

---

### Rule 3 — Wage Withholding Beyond 7 Days
```
IF wage_withheld = "true"
   AND days_delayed > "7"
THEN
   statute    = "Employment Act 1968"
   section    = "Section 21"
   violation  = "Salary not paid within 7 days after end of salary period"
   confidence = "high"
```
**Test case:** "My employer has not paid my salary 2 weeks after the end of the month."

---

### Rule 4 — Constructive Dismissal
```
IF employment_type = "permanent"
   AND cause = "none"
   AND early_termination = "true"
THEN
   statute    = "Employment Act 1968"
   section    = "Section 14 / common law"
   violation  = "Potential constructive dismissal — significant contract variation without consent"
   confidence = "medium"
```
**Test case:** "My employer cut my salary by 40% without my agreement and I had to resign."

---

### Rule 5 — Termination for Redundancy (Retrenchment)
```
IF cause = "redundancy"
   AND notice_given = "false"
THEN
   statute    = "Employment Act 1968 / Tripartite Guidelines on Managing Excess Manpower"
   section    = "Section 45 / Tripartite Advisory"
   violation  = "Retrenchment without notice or retrenchment benefit may be claimable"
   confidence = "medium"
```
**Test case:** "My company said I am being made redundant due to restructuring with no notice period."

---

### Rule 6 — Fixed-Term Contract Early Termination
```
IF contract_type = "fixed_term"
   AND early_termination = "true"
   AND penalty_clause = "absent"
THEN
   statute    = "Contract law principles (Singapore)"
   section    = "Breach of contract / damages"
   violation  = "Early termination of fixed-term contract may constitute breach"
   confidence = "high"
```
**Test case:** "My employer terminated my 1-year fixed-term contract after 4 months with no penalty clause."

---

### Rule 7 — Unauthorised Salary Deduction
```
IF wage_withheld = "true"
   AND days_delayed = "0"
THEN
   statute    = "Employment Act 1968"
   section    = "Section 27"
   violation  = "Deductions from salary not permitted except under Section 27 exceptions"
   confidence = "high"
```
**Test case:** "My employer deducted money from my salary without my agreement."

---

### Rule 8 — Minor Party Contract
```
IF minor_party = "true"
THEN
   statute    = "Contracts (Age of Majority) Act 1970 / Minors' Contracts Act"
   section    = "Age of majority provisions"
   violation  = "Contract with a minor is generally not enforceable against the minor"
   confidence = "high"
```
**Test case:** "I signed a service agreement with a 16-year-old. Is it enforceable?"

---

## Singapore Contract Law Rules (4)

### Rule 9 — Contract Without Consideration
```
IF consideration_absent = "true"
THEN
   statute    = "Singapore contract law (common law)"
   section    = "Consideration doctrine"
   violation  = "Contract without consideration is not enforceable"
   confidence = "high"
```
**Test case:** "I promised to give my friend my laptop for free in writing. Is this a binding contract?"

---

### Rule 10 — Fraudulent Misrepresentation
```
IF misrepresentation = "fraudulent"
THEN
   statute    = "Misrepresentation Act (Cap. 390)"
   section    = "Section 2(1)"
   violation  = "Fraudulent misrepresentation — contract voidable, damages available"
   confidence = "high"
```
**Test case:** "The seller deliberately told me false information about the property to get me to buy it."

---

### Rule 11 — Negligent Misrepresentation
```
IF misrepresentation = "negligent"
THEN
   statute    = "Misrepresentation Act (Cap. 390)"
   section    = "Section 2(1)"
   violation  = "Negligent misrepresentation — damages claimable even without fraud intent"
   confidence = "high"
```
**Test case:** "The agent gave me incorrect information about the property's rental history without checking."

---

### Rule 12 — Consumer Unfair Practice
```
IF unfair_practice = "true"
   AND good_returned = "false"
   AND days_since_purchase < "30"
THEN
   statute    = "Consumer Protection (Fair Trading) Act (Cap. 52A)"
   section    = "Section 6"
   violation  = "Unfair practice by supplier — consumer may seek cancellation of contract"
   confidence = "medium"
```
**Test case:** "A shop used high-pressure sales tactics to get me to buy a product I did not need."

---

## Singapore PDPA / Data Protection Rules (8)

### Rule 13 — Collection Without Consent or Notification
```
IF data_collected = "personal"
   AND consent_obtained = "false"
   AND purpose_notified = "false"
THEN
   statute    = "Personal Data Protection Act 2012"
   section    = "Section 13 / Section 20"
   violation  = "Personal data collected without consent and without notifying purpose"
   confidence = "high"
```
**Test case:** "A company collected my NRIC number without telling me why or asking my permission."

---

### Rule 14 — Data Access Request
```
IF data_subject_request = "access"
THEN
   statute    = "Personal Data Protection Act 2012"
   section    = "Section 21"
   violation  = "Organisation must provide access to personal data within reasonable time"
   confidence = "high"
```
**Test case:** "I asked a company to tell me what personal data they hold about me and they refused."

---

### Rule 15 — Data Correction Request
```
IF data_subject_request = "correction"
THEN
   statute    = "Personal Data Protection Act 2012"
   section    = "Section 22"
   violation  = "Organisation must correct personal data that is inaccurate or incomplete"
   confidence = "high"
```
**Test case:** "My bank has the wrong address on file and refuses to correct it."

---

### Rule 16 — Consent Withdrawal
```
IF data_subject_request = "withdrawal"
   AND consent_obtained = "true"
THEN
   statute    = "Personal Data Protection Act 2012"
   section    = "Section 16"
   violation  = "Organisation must give effect to withdrawal of consent within reasonable time"
   confidence = "high"
```
**Test case:** "I withdrew my consent for a company to use my email address for marketing but they kept emailing me."

---

### Rule 17 — Mandatory Data Breach Notification (Significant Harm)
```
IF breach_detected = "true"
   AND notification_delay_days > "3"
THEN
   statute    = "Personal Data Protection Act 2012 (amended 2021)"
   section    = "Section 26D"
   violation  = "Data breach causing significant harm must be notified to PDPC within 3 business days"
   confidence = "high"
```
**Test case:** "We had a data breach last week involving customer financial data and have not notified anyone."

---

### Rule 18 — DNC Registry Violation
```
IF do_not_call = "true"
THEN
   statute    = "Personal Data Protection Act 2012"
   section    = "Part IX — Do Not Call Registry"
   violation  = "Sending unsolicited telemarketing messages to DNC-registered number"
   confidence = "high"
```
**Test case:** "I registered my number on the Do Not Call list but companies keep calling me to sell things."

---

### Rule 19 — Sensitive Personal Data (Higher Protection Standard)
```
IF data_collected = "sensitive"
   AND consent_obtained = "false"
THEN
   statute    = "Personal Data Protection Act 2012 / PDPC Advisory Guidelines"
   section    = "Section 13 + PDPC Advisory on NRIC"
   violation  = "Sensitive personal data (health, NRIC, financial) requires explicit consent"
   confidence = "high"
```
**Test case:** "A clinic shared my medical records with a third party without asking me."

---

### Rule 20 — High-Risk AI System Without Assessment
```
IF ai_system_risk = "high"
   AND conformity_assessment = "not_done"
THEN
   statute    = "PDPC Model AI Governance Framework (Singapore) / EU AI Act Art.43 (if EU-facing)"
   section    = "PDPC Framework Section 2 / EU AI Act Article 43"
   violation  = "High-risk AI system deployed without governance assessment or conformity check"
   confidence = "medium"
```
**Test case:** "We are deploying an AI system for employee performance scoring with no governance review."

---

## Checklist for Adding a New Rule

- [ ] Scenario not covered by any existing rule
- [ ] Statutory reference verified against Singapore Statutes Online (https://sso.agc.gov.sg)
- [ ] Benchmark test case added to `data/benchmark.json`
- [ ] Attribute key(s) defined in the Attribute Reference table above
- [ ] Rule added to this file and to `src/rules.py`
- [ ] Unit test added to `src/tests/test_rules.py`
- [ ] Rule count updated in `GEMINI.md` and `ARCHITECTURE.md`
- [ ] Paper Section 3.2 updated if total count changed