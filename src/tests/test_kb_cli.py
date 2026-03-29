import json

import src.kb_cli as kb_cli


class FakeKB:
    def __init__(self, path=None, search_mode="hybrid"):
        self.path = path
        self.search_mode = search_mode
        self.chunks = [
            {
                "chunk_id": "A:1:1",
                "text": "A",
                "document_name": "A.pdf",
                "document_path": "data/statutes/A.pdf",
                "page_number": 1,
                "section_heading": None,
            },
            {
                "chunk_id": "B:2:1",
                "text": "B",
                "document_name": "B.pdf",
                "document_path": "data/statutes/B.pdf",
                "page_number": 2,
                "section_heading": None,
            },
        ]

    def load_pdf(self):
        return None

    def search_semantic(self, query, top_n=1):
        return []

    @property
    def _vector_store(self):
        class Store:
            @staticmethod
            def clear():
                return None

        return Store()


def test_index_command_outputs_summary(monkeypatch, capsys):
    monkeypatch.setattr(kb_cli, "PDFKnowledgeBase", FakeKB)
    code = kb_cli.main(["index", "--path", "data/statutes", "--mode", "hybrid"])
    out = capsys.readouterr().out

    assert code == 0
    payload = json.loads(out)
    assert payload["command"] == "index"
    assert payload["document_count"] == 2
    assert payload["chunks"] == 2


def test_list_command_outputs_documents(monkeypatch, capsys):
    monkeypatch.setattr(kb_cli, "PDFKnowledgeBase", FakeKB)
    code = kb_cli.main(["list", "--path", "data/statutes", "--mode", "keyword"])
    out = capsys.readouterr().out

    assert code == 0
    payload = json.loads(out)
    assert payload["command"] == "list"
    assert payload["documents"] == ["A.pdf", "B.pdf"]


def test_reindex_command_outputs_summary(monkeypatch, capsys):
    monkeypatch.setattr(kb_cli, "PDFKnowledgeBase", FakeKB)
    code = kb_cli.main(["reindex", "--path", "data/statutes", "--mode", "hybrid"])
    out = capsys.readouterr().out

    assert code == 0
    payload = json.loads(out)
    assert payload["command"] == "reindex"
    assert payload["pages"] == 2
