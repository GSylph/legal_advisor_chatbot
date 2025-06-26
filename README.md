# 📘 Legal Advisor Chatbot (Singapore Law) - README

An intelligent legal assistant CLI chatbot powered by Google Gemini API that helps users understand Singaporean legal topics. It classifies intent, extracts entities, retrieves statutory context, and provides structured, human-readable legal answers.

---

## 🚀 MVP Features

### ✅ Core Capabilities

* **Natural Language Legal Q\&A**
* **Intent Classification** (e.g., legal question, follow-up, definition)
* **Entity Extraction** (locations, names, dates)
* **Prompt Building via Jinja2 Templates**
* **PDF Knowledge Base Retrieval** (RAG-ready)
* **Structured Output Formatting** (Summary, Context, Steps, etc.)
* **Memory Injection for Last N Conversations**
* **CLI Interface** for local testing
* **Logging of Fallbacks and Errors**

---

## 🗂️ Project Structure

```
legal_advisor_chatbot/
├── src/
│   ├── main.py                # CLI chatbot entrypoint
│   ├── api_client.py          # Gemini API integration
│   ├── intent_classifier.py   # Classifies user intent
│   ├── entity_extractor.py    # Extracts dates, people, locations
│   ├── prompt_builder.py      # Builds prompt from template + context
│   ├── response_formatter.py  # Formats Gemini output
│   ├── kb_retriever.py        # PDF loader + keyword search
│   ├── logger.py              # Logs fallback and error cases
│   └── tests/                 # Contains test_fallback.py, test_formatter.py etc.
├── prompts/
│   └── base_prompt.md         # Jinja2 prompt template
├── data/
│   └── statutes/              # Legal PDFs for KB (optional)
├── storage/
│   └── logs/                  # Logs for fallback + errors
├── .env                       # API keys, config vars
├── requirements.txt
├── README.md                  # You're here!
├── execution_plan.md          # Roadmap, TODOs, notes
└── API_REFERENCE.md           # Function-by-function developer docs
```

---

## 🧠 How It Works

1. **User Enters Prompt** →
2. **Intent + Entity Detection** →
3. **PDF Knowledge Base Search** →
4. **Prompt Template Filled** (context + history) →
5. **Sent to Gemini API** →
6. **Response Parsed into Structure** →
7. **Result Displayed in CLI**

---

## 🧪 Testing (MVP Level)

* `test_fallback.py`: Tests for edge cases in unstructured output
* `test_formatter.py`: Verifies structured formatting of Gemini output
* `test_prompt_builder.py`: Ensures prompt rendering with history and context

---

## 🧾 Prompt Template (`prompts/base_prompt.md`)

Contains instructions to the Gemini LLM:

* Always structure answer in sections: Summary, Context, Steps, Warnings, Contacts, Disclaimer
* Inject entities (people, locations, dates)
* Inject up to 3 turns of chat history
* Act like a legal assistant for Singapore

---

## 📋 Example Interaction

```bash
$ python src/main.py
📜 Legal Advisor Chatbot (type 'exit' to quit)

Enter your prompt: My cousin took my father’s property after he died.

🧠 Gemini says:
📋 Summary: Your issue involves inheritance law...
📚 Legal Context: According to Section 5 of...
📝 Steps to Take:
 • Gather documents
 • Contact a civil lawyer
⚠️ Warnings: Time limits apply for claims.
📞 Contacts: Legal Aid Bureau
⚖️ Disclaimer: This is general guidance only...
```

---

## ⚒️ Logging System

* `fallback_responses.log`: When response was not parseable into structure
* `errors.log`: Unhandled exceptions or runtime issues

---

## 💬 Intent Handling

Currently hardcoded logic for basic intents:

```python
if intent == "follow_up":
    handle_follow_up()
elif intent == "legal_question":
    format_structured_response()
```

✅ Works well for MVP, but post-MVP should adopt intent-handler mapping or schema-driven logic.

---

## 📈 Future Work

| Area              | Upgrade                                  |
| ----------------- | ---------------------------------------- |
| Intent System     | Replace rules with fine-tuned classifier |
| Entity Extraction | Legal-BERT or Gemini API NER             |
| KB Search         | RAG with vector store (FAISS, Chroma)    |
| Prompting         | Template per intent or schema-driven     |
| Output            | Support JSON + Markdown responses        |
| Memory            | Add vector memory / persistent memory    |
| UI                | Streamlit or Flask frontend              |
| Deployment        | Dockerize + `docker-compose.yml`         |

---

## 🐳 Docker Usage (To be done)

**Dockerfile**:

```Dockerfile
FROM python:3.10
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "src/main.py"]
```

**docker-compose.yml**:

```yaml
version: '3.8'
services:
  chatbot:
    build: .
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
    ports:
      - "7860:7860"
```

---

## 📚 License & Credits

This MVP is educational and experimental. Not intended for commercial use. Built using:

* Python
* Google Gemini API
* spaCy (NER)
* Jinja2 (prompt templating)
* Rich / argparse (optional future CLI upgrades)

---

## 🏁 Final Words

🎉 MVP is complete and fully functional via CLI.
You can:

* Ask legal questions
* Get answers backed by relevant law
* Log and debug fallbacks
* View structured responses

---