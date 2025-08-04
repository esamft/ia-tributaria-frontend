"""
Core do sistema de agentes tributários.
Orquestração e componentes centrais.
"""

from .vector_store import TaxVectorStore
from .document_manager import DocumentManager
from .knowledge_base import TaxKnowledgeBase

__all__ = [
    "TaxVectorStore",
    "DocumentManager", 
    "TaxKnowledgeBase"
]