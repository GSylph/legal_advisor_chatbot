from src.chat_service import ChatService


def test_run_turn_smoke_with_mocked_pipeline(monkeypatch):
    monkeypatch.setattr("src.chat_service.classify_intents", lambda text: "legal_question")
    monkeypatch.setattr("src.chat_service.extract_entities", lambda text: {"people": [], "dates": [], "locations": []})
    monkeypatch.setattr("src.chat_service.send_prompt", lambda prompt: {"mock": True})
    monkeypatch.setattr("src.chat_service.extract_text_from_response", lambda response: "**1. Summary**\nSafe mock response")
    monkeypatch.setattr(
        "src.chat_service.format_and_structure_response",
        lambda text: ({"summary": "Safe mock response"}, "Safe mock response"),
    )

    class FakeKB:
        def __init__(self):
            self.loaded = False

        def load_pdf(self):
            self.loaded = True

        def search(self, query):
            return [
                {
                    "text": "Tenant rights require notice before eviction.",
                    "score": 1.0,
                    "document_name": "TenancyAct.pdf",
                    "document_path": "data/statutes/TenancyAct.pdf",
                    "page_number": 1,
                    "section_heading": "Section 4",
                }
            ]

    service = ChatService()
    service.kb = FakeKB()

    structured, formatted = service.run_turn("Can my landlord evict me immediately?")

    assert structured["summary"] == "Safe mock response"
    assert formatted == "Safe mock response"
    assert len(service.conversation_history) == 1
