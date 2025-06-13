# 🧑‍⚖️ Legal Advisor Chatbot (Singapore Law Focus)

The **Legal Advisor Chatbot** is an AI-powered assistant that helps users understand what to do during **land/property-related legal disputes**, such as:

1. 🏠 Property Law Issues
2. 🧾 Land Ownership Conflicts
3. ⚖️ Property or Inheritance Disputes
4. 🏨 Tenant & Landlord Rights

The chatbot uses Google Gemini to provide early-stage legal guidance based on the legal structure of **Singapore** — a country selected for its simpler and more predictable property law system.

> ⚠️ This chatbot does **not** replace a human lawyer. It gives **educational, general-purpose legal steps** — not personalized legal advice.

---

## 🔑 Features

* 📌 Suggests actionable next steps in common legal situations
* ⚠️ Provides legal risks/warnings users should be aware of
* 🧠 Understands who’s involved, where, and when (NER)
* ✨ Powered by Gemini via Google Generative AI

---

## 💬 Sample Use Cases

* “My uncle encroached on our land after my father passed away.”
* “I have a dispute with my neighbor over a 5-foot pathway in London.”
* “What rights do tenants have in Singapore without written contracts?”

---

## ✅ Current Progress (What’s Working)

### ✅ 1. Project Folder Setup

```
legal-advisor-chatbot/
├── run.py                 # Entry script
├── requirements.txt
├── .env                  # Stores Gemini API key
├── .gitignore            # Ignores .env, pycache, etc.
├── prompts/
│   └── base_prompt.md    # Jinja2 prompt template
├── src/
│   ├── main.py           # Chat loop (CLI)
│   ├── api_client.py     # Gemini API wrapper
│   ├── intent_classifier.py # Rule-based intent recognition
│   ├── entity_extractor.py  # Extracts people, date, location
│   └── prompt_builder.py    # Renders prompt using template
├── data/
│   └── statutes/         # (planned) Law PDFs
├── storage/
│   ├── logs/             # (planned) Log errors/responses
│   └── sessions/         # (planned) Store chat history
```

---

### ✅ 2. Gemini Integration

* `api_client.py` sends prompts to Gemini (`gemini-pro`, `gemini-1.5-flash`) using `google.generativeai`
* Response is streamed and printed

---

### ✅ 3. Interactive Chat CLI

* `main.py` handles chat loop
* Calls intent classifier → entity extractor → prompt builder → Gemini response
* Gracefully handles `exit` or `quit`

---

### ✅ 4. Intent Classification

* Rule-based keywords return one of:

  * `property_dispute`
  * `tenant_rights`
  * `will_and_inheritance`
  * `court_case`
  * `fraud_or_cheating`
  * `uncategorized`

---

### ✅ 5. Entity Extraction

* Uses `spaCy` and PhraseMatcher
* Extracts:

  * `location`: from user input (e.g. "Singapore", "Pune")
  * `people`: e.g. "uncle", "father"
  * `date`: e.g. "in 2015", "after my father passed away"

---

### ✅ 6. Prompt Building

* Jinja2 template in `base_prompt.md`:

```
You are a legal advisor chatbot for {{ country or "Singapore" }}.
...
{{ intent }}
{{ people }}
{{ location }}
{{ date }}
...
```

* Dynamically rendered using data from NER and intent classifier
* Ensures grounded, structured prompt with disclaimer

---

## 🚧 Next Steps (Roadmap)

### ⏭️ 1. `response_formatter.py`

* Structure Gemini replies into sections:

  * 🧾 Summary of dispute
  * ✅ Steps to follow
  * ⚠️ Warnings or legal risks
  * 📞 Whom to contact (e.g., police, local authority)
  * 📚 Referenced laws/sections if applicable

### ⏭️ 2. `kb_retriever.py` (optional)

* Load PDFs or text from `data/statutes/`
* Match intent/query to relevant excerpts
* Option: Use embedding-based semantic search later

### ⏭️ 3. Logging & Sessions

* Save conversation data:

  * Input, intent, entities, response, timestamps
* JSON or SQLite (optional) in `storage/sessions/`
* Error logs go to `storage/logs/`

### ⏭️ 4. UI (Optional Future)

* Upgrade from CLI to web (Flask/Streamlit/Gradio)
* Let users pick jurisdiction (Singapore, India, etc.)

---

## 🧪 How to Run Locally

```bash
git clone https://github.com/yourname/legal-advisor-chatbot
cd legal-advisor-chatbot
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file with:

```
GEMINI_API_KEY=your-google-api-key
```

---

## ⚙️ Dependencies (requirements.txt)

```
google-generativeai
python-dotenv
spacy
jinja2
```

Also run:

```bash
python -m spacy download en_core_web_sm
```

---

## 📜 Legal Disclaimer

This chatbot provides **general educational legal guidance** only. It is **not a substitute for a licensed lawyer**, and no part of the conversation constitutes a legal verdict. Always consult certified legal professionals for real cases.
