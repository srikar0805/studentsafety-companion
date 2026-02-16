import sys
import os
import logging

logger = logging.getLogger("campus_dispatch")

# Add src to path if needed for RAG import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))

# Lazy initialization of RAG retriever
_retriever = None

def retrieve_context(query: str, top_k: int = 3):
    global _retriever
    if _retriever is None:
        try:
            from src.rag.retrieve import RAGRetriever
            _retriever = RAGRetriever()
        except ImportError:
            logger.warning("RAG dependencies not available, returning empty context")
            return []
    return _retriever.search(query, top_k=top_k)
