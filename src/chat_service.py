from typing import Any, Dict, Generator, List, Optional, Tuple
import re
import time
import uuid

from .api_client import extract_text_from_response, send_prompt, send_prompt_stream
from .citation_checker import verify_citations
from .entity_extractor import extract_entities
from .intent_classifier import classify_intents
from .kb_retriever import PDFKnowledgeBase
from .logger import log_error, log_fallback_response
from .prompt_builder import build_prompt
from .response_formatter import format_and_structure_response, format_gemini_response
from .rules import check_consistency
from .audit import log_interaction

# Retriever modes matching PLAN.md T14
VALID_RETRIEVERS = {"bm25", "dense", "hybrid", "none"}

# Confidence tag pattern from LLM output
CONFIDENCE_PATTERN = re.compile(
    r"\[Confidence:\s*(HIGH|MEDIUM|LOW|INSUFFICIENT CONTEXT)\]", re.IGNORECASE
)


class ChatService:
    """
    Orchestrates a single chatbot turn using the EALAI pipeline:
    intent classification → entity extraction → KB search → prompt building →
    LLM call → response formatting → symbolic rule check → audit logging.
    """

    def __init__(
        self,
        kb_path: str = "corpus/raw",
        max_history: int = 3,
        refusal_threshold: float = 0.4,
    ) -> None:
        self.max_history = max_history
        self.refusal_threshold = refusal_threshold
        self.conversation_history: List[Dict[str, str]] = []
        self.session_id = str(uuid.uuid4())

        self.kb = PDFKnowledgeBase(path=kb_path)
        try:
            self.kb.load_pdf()
        except Exception as exc:  # pragma: no cover - startup failure path
            log_error(f"Failed to load knowledge base from {kb_path}: {exc}")

    def _retrieve(
        self, query: str, retriever: str = "hybrid"
    ) -> List[Dict[str, Any]]:
        """Run retrieval using the specified mode."""
        if retriever == "none":
            return []
        if retriever == "bm25":
            return self.kb.search_keyword(query)
        if retriever == "dense":
            return self.kb.search_semantic(query)
        # default: hybrid (RRF)
        return self.kb.search(query)

    @staticmethod
    def _extract_confidence(text: str) -> str:
        """Extract [Confidence: ...] tag from LLM output."""
        match = CONFIDENCE_PATTERN.search(text)
        return match.group(1).upper() if match else "UNKNOWN"

    def run_turn(
        self,
        user_input: str,
        session_id: str = None,
        retriever: str = "hybrid",
    ) -> Tuple[Dict[str, Any], str]:
        """
        Execute one chat turn and return a tuple of:
        - structured_data: parsed sections, rule results, scores, latency
        - formatted_text: human-readable formatted response string

        retriever: one of "bm25", "dense", "hybrid", "none"
        """
        if retriever not in VALID_RETRIEVERS:
            retriever = "hybrid"

        current_session_id = session_id or self.session_id
        t_start = time.monotonic()

        try:
            intents = classify_intents(user_input)
            entities = extract_entities(user_input)
            context_chunks = self._retrieve(user_input, retriever=retriever)

            # Collect retrieval scores
            retrieval_scores = [float(c.get("score", 0.0)) for c in context_chunks]

            # T17: Refusal threshold — skip LLM if semantic confidence too low.
            # Per PLAN.md T17, use dense retrieval scores (0–1 range) for the
            # refusal decision. For non-semantic retrievers, run a separate
            # semantic probe to get a normalized confidence signal.
            if retriever != "none" and context_chunks:
                if retriever == "dense":
                    refusal_scores = retrieval_scores
                else:
                    # Quick semantic probe for a normalized confidence signal
                    semantic_probe = self.kb.search_semantic(user_input, top_n=1)
                    refusal_scores = [float(c.get("score", 0.0)) for c in semantic_probe] if semantic_probe else [0.0]
                max_score = max(refusal_scores) if refusal_scores else 0.0
                if max_score < self.refusal_threshold:
                    latency_ms = int((time.monotonic() - t_start) * 1000)
                    refusal_data = {
                        "answer": (
                            "I cannot find relevant Singapore statute provisions for this query. "
                            "Please consult a qualified legal professional."
                        ),
                        "sources": [],
                        "confidence": "INSUFFICIENT CONTEXT",
                        "retrieval_scores": retrieval_scores,
                        "latency_ms": latency_ms,
                        "refused": True,
                        "session_id": current_session_id,
                    }
                    refusal_text = refusal_data["answer"]
                    # Log the refusal
                    audit_hash = log_interaction(
                        session_id=current_session_id,
                        query=user_input,
                        retrieved_context=context_chunks,
                        rule_result={"rule_matched": False, "consistent": None},
                        response_data=refusal_data,
                    )
                    refusal_data["audit_hash"] = audit_hash
                    return refusal_data, refusal_text

            prompt = build_prompt(
                user_input=user_input,
                kb_chunks=context_chunks,
                conversation_history=self.conversation_history,
                intent=", ".join(intents),
                entities=entities,
            )

            response = send_prompt(prompt)
            response_text = extract_text_from_response(response)
            structured_data, formatted_response = format_and_structure_response(
                response_text
            )

            if "⚠️ Gemini could not produce a structured response" in formatted_response:
                log_fallback_response(response_text)
                return structured_data, formatted_response

            # Extract confidence tag from LLM output
            confidence = self._extract_confidence(response_text)

            # Citation validity check (T15)
            citation_result = verify_citations(response_text, context_chunks)

            # EALAI: Symbolic Rule Check
            rule_result = check_consistency(
                entities=entities,
                intents=intents,
                user_input=user_input,
                llm_statute=structured_data.get("applicable_law", "")
            )

            # EALAI: Audit Logging
            audit_hash = log_interaction(
                session_id=current_session_id,
                query=user_input,
                retrieved_context=context_chunks,
                rule_result=rule_result,
                response_data=structured_data
            )

            latency_ms = int((time.monotonic() - t_start) * 1000)

            # Enrich structured data with EALAI results
            structured_data["rule_result"] = rule_result
            structured_data["audit_hash"] = audit_hash
            structured_data["session_id"] = current_session_id
            structured_data["context_sources"] = [
                c.get("document_name") or c.get("source", "") for c in context_chunks
            ]
            structured_data["confidence"] = confidence
            structured_data["retrieval_scores"] = retrieval_scores
            structured_data["latency_ms"] = latency_ms
            structured_data["citation_result"] = citation_result
            structured_data["retriever"] = retriever

            # Add warning to formatted response if inconsistent
            if rule_result.get("consistent") is False:
                warning_msg = (
                    "\n\n⚠️ **WARNING: INTERNAL CONSISTENCY CHECK FAILED**\n"
                    "The AI's legal conclusion may not align with programmed statutory rules. "
                    "Please double-check the applicable law section carefully."
                )
                formatted_response += warning_msg
                structured_data["warning"] = "Inconsistency detected between LLM and Rule Engine."

            self._append_history(user_input, formatted_response)

            return structured_data, formatted_response

        except Exception as exc:
            log_error(str(exc))
            raise

    def run_turn_streaming(
        self,
        user_input: str,
        session_id: str = None,
        retriever: str = "hybrid",
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Streaming variant of run_turn(). Yields dicts:
          {"type": "token",   "text": str}
          {"type": "done",    "metadata": dict}
          {"type": "refused", "metadata": dict}
          {"type": "error",   "message": str}
        """
        if retriever not in VALID_RETRIEVERS:
            retriever = "hybrid"

        current_session_id = session_id or self.session_id
        t_start = time.monotonic()

        try:
            intents = classify_intents(user_input)
            entities = extract_entities(user_input)
            context_chunks = self._retrieve(user_input, retriever=retriever)
            retrieval_scores = [float(c.get("score", 0.0)) for c in context_chunks]

            # Refusal check — identical logic to run_turn
            if retriever != "none" and context_chunks:
                if retriever == "dense":
                    refusal_scores = retrieval_scores
                else:
                    semantic_probe = self.kb.search_semantic(user_input, top_n=1)
                    refusal_scores = [float(c.get("score", 0.0)) for c in semantic_probe] if semantic_probe else [0.0]
                max_score = max(refusal_scores) if refusal_scores else 0.0
                if max_score < self.refusal_threshold:
                    latency_ms = int((time.monotonic() - t_start) * 1000)
                    refusal_answer = (
                        "I cannot find relevant Singapore statute provisions for this query. "
                        "Please consult a qualified legal professional."
                    )
                    refusal_data = {
                        "answer": refusal_answer,
                        "sources": [],
                        "confidence": "INSUFFICIENT CONTEXT",
                        "retrieval_scores": retrieval_scores,
                        "latency_ms": latency_ms,
                        "refused": True,
                        "session_id": current_session_id,
                    }
                    audit_hash = log_interaction(
                        session_id=current_session_id,
                        query=user_input,
                        retrieved_context=context_chunks,
                        rule_result={"rule_matched": False, "consistent": None},
                        response_data=refusal_data,
                    )
                    refusal_data["audit_hash"] = audit_hash
                    yield {
                        "type": "refused",
                        "metadata": {
                            "session_id": current_session_id,
                            "structured": refusal_data,
                            "audit_hash": audit_hash,
                            "consistency_flag": None,
                            "warning": None,
                            "formatted_text": refusal_answer,
                            "answer": refusal_answer,
                        },
                    }
                    return

            prompt = build_prompt(
                user_input=user_input,
                kb_chunks=context_chunks,
                conversation_history=self.conversation_history,
                intent=", ".join(intents),
                entities=entities,
            )

            # Stream tokens
            full_text = ""
            for token in send_prompt_stream(prompt):
                full_text += token
                yield {"type": "token", "text": token}

            # Post-stream pipeline (runs after all tokens sent)
            structured_data, formatted_response = format_and_structure_response(full_text)
            confidence = self._extract_confidence(full_text)
            citation_result = verify_citations(full_text, context_chunks)
            rule_result = check_consistency(
                entities=entities,
                intents=intents,
                user_input=user_input,
                llm_statute=structured_data.get("applicable_law", ""),
            )
            audit_hash = log_interaction(
                session_id=current_session_id,
                query=user_input,
                retrieved_context=context_chunks,
                rule_result=rule_result,
                response_data=structured_data,
            )

            latency_ms = int((time.monotonic() - t_start) * 1000)
            structured_data.update({
                "rule_result": rule_result,
                "audit_hash": audit_hash,
                "session_id": current_session_id,
                "context_sources": [
                    c.get("document_name") or c.get("source", "") for c in context_chunks
                ],
                "confidence": confidence,
                "retrieval_scores": retrieval_scores,
                "latency_ms": latency_ms,
                "citation_result": citation_result,
                "retriever": retriever,
            })

            warning = None
            if rule_result.get("consistent") is False:
                warning = "Inconsistency detected between LLM and Rule Engine."
                structured_data["warning"] = warning

            self._append_history(user_input, formatted_response)

            yield {
                "type": "done",
                "metadata": {
                    "session_id": current_session_id,
                    "structured": structured_data,
                    "audit_hash": audit_hash,
                    "consistency_flag": rule_result.get("consistent"),
                    "warning": warning,
                    "formatted_text": formatted_response,
                },
            }

        except Exception as exc:
            log_error(str(exc))
            yield {"type": "error", "message": str(exc)}

    def _append_history(self, user_input: str, bot_response: str) -> None:
        self.conversation_history.append(
            {
                "user": user_input,
                "bot": bot_response,
            }
        )
        if len(self.conversation_history) > self.max_history:
            self.conversation_history.pop(0)

