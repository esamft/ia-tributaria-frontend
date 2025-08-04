"""
Modelos de dados para o Sistema de Agentes Tributários.
Estruturas Pydantic para validação e organização dos dados.
"""

from .document import Document, DocumentMetadata, DocumentType, SourceType
from .chunk import Chunk, ChunkMetadata
from .query import TaxQuery, QueryResponse
from .country import Country, TaxJurisdiction

__all__ = [
    "Document",
    "DocumentMetadata", 
    "DocumentType",
    "SourceType",
    "Chunk",
    "ChunkMetadata",
    "TaxQuery",
    "QueryResponse",
    "Country",
    "TaxJurisdiction"
]