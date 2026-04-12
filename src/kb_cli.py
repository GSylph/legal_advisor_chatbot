import argparse
import json
import sys
from typing import Dict

from .kb_retriever import PDFKnowledgeBase
from .logger import log_error


def _summary(kb: PDFKnowledgeBase) -> Dict[str, int]:
    docs = {chunk.get("document_name", "") for chunk in kb.chunks}
    pages = {
        (chunk.get("document_name", ""), int(chunk.get("page_number", 0)))
        for chunk in kb.chunks
    }
    return {
        "document_count": len([d for d in docs if d]),
        "pages": len([p for p in pages if p[1] > 0]),
        "chunks": len(kb.chunks),
    }


def cmd_index(path: str, mode: str) -> int:
    kb = PDFKnowledgeBase(path=path, search_mode=mode)
    kb.load_pdf()
    if mode in {"semantic", "hybrid"}:
        try:
            kb.search_semantic("index warmup", top_n=1)
        except Exception as exc:
            log_error(f"Index warmup failed: {exc}")
            print("WARNING: semantic index warmup failed; keyword mode remains available.")

    print(json.dumps({"command": "index", **_summary(kb)}, indent=2))
    return 0


def cmd_list(path: str, mode: str) -> int:
    kb = PDFKnowledgeBase(path=path, search_mode=mode)
    kb.load_pdf()
    docs = sorted({chunk.get("document_name", "") for chunk in kb.chunks if chunk.get("document_name")})
    print(json.dumps({"command": "list", "documents": docs, **_summary(kb)}, indent=2))
    return 0


def cmd_reindex(path: str, mode: str) -> int:
    kb = PDFKnowledgeBase(path=path, search_mode=mode)
    kb.load_pdf()
    try:
        kb._vector_store.clear()  # internal lifecycle call for explicit rebuild.
    except Exception as exc:
        log_error(f"Failed to clear index: {exc}")

    if mode in {"semantic", "hybrid"}:
        try:
            kb.search_semantic("reindex warmup", top_n=1)
        except Exception as exc:
            log_error(f"Reindex warmup failed: {exc}")
            print("WARNING: semantic reindex warmup failed; keyword mode remains available.")

    print(json.dumps({"command": "reindex", **_summary(kb)}, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Knowledge base management CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    for name in ("index", "list", "reindex"):
        cmd = subparsers.add_parser(name)
        cmd.add_argument("--path", default="corpus/raw", help="Path containing PDF statutes")
        cmd.add_argument(
            "--mode",
            default="hybrid",
            choices=["keyword", "semantic", "hybrid"],
            help="Retrieval mode",
        )

    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "index":
            return cmd_index(path=args.path, mode=args.mode)
        if args.command == "list":
            return cmd_list(path=args.path, mode=args.mode)
        if args.command == "reindex":
            return cmd_reindex(path=args.path, mode=args.mode)
    except Exception as exc:
        log_error(f"kb_cli {args.command} failed: {exc}")
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
