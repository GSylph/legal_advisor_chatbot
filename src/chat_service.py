from typing import Any, Dict, List, Tuple

from .api_client import extract_text_from_response, send_prompt
from .entity_extractor import extract_entities
from .intent_classifier import classify_intents
from .kb_retriever import PDFKnowledgeBase
from .logger import log_error, log_fallback_response
from .prompt_builder import build_prompt
from .response_formatter import format_and_structure_response, format_gemini_response


class ChatService:
    """
    Orchestrates a single chatbot turn using the existing MVP pipeline:
    intent classification → entity extraction → KB search → prompt building →
    Gemini call → response formatting.
    """

    def __init__(self, kb_path: str = "data/statutes", max_history: int = 3) -> None:
        self.max_history = max_history
        self.conversation_history: List[Dict[str, str]] = []

        self.kb = PDFKnowledgeBase(path=kb_path)
        try:
            self.kb.load_pdf()
        except Exception as exc:  # pragma: no cover - startup failure path
            log_error(f"Failed to load knowledge base from {kb_path}: {exc}")
            # Keep running without KB; search() will just return no context

    def run_turn(self, user_input: str) -> Tuple[Dict[str, Any], str]:
        """
        Execute one chat turn and return a tuple of:
        - structured_data: parsed sections from the Gemini response
        - formatted_text: human-readable formatted response string
        """
        try:
            intent = classify_intents(user_input)
            entities = extract_entities(user_input)
            context_chunks = self.kb.search(user_input)

            prompt = build_prompt(
                user_input=user_input,
                kb_chunks=context_chunks,
                conversation_history=self.conversation_history,
                intent=intent,
                entities=entities,
            )

            response = send_prompt(prompt)
            response_text = extract_text_from_response(response)
            structured_data, formatted_response = format_and_structure_response(
                response_text
            )

            if "⚠️ Gemini could not produce a structured response" in formatted_response:
                log_fallback_response(response_text)

            self._append_history(user_input, formatted_response)

            return structured_data, formatted_response

        except Exception as exc:
            log_error(str(exc))
            raise

    def _append_history(self, user_input: str, bot_response: str) -> None:
        self.conversation_history.append(
            {
                "user": user_input,
                "bot": bot_response,
            }
        )
        if len(self.conversation_history) > self.max_history:
            self.conversation_history.pop(0)

