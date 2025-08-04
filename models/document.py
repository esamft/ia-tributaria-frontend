"""
Modelos para documentos da base de conhecimento tributário.
"""

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator


class DocumentType(str, Enum):
    """Tipos de documentos na base de conhecimento."""
    GUIDE = "guide"           # Guias oficiais (EY Guide)
    BOOK = "book"             # Livros especializados
    REPORT = "report"         # Relatórios de pesquisa
    LEGISLATION = "legislation"  # Leis e regulamentos
    TREATY = "treaty"         # Tratados internacionais
    CASE_STUDY = "case_study" # Casos práticos
    STRUCTURE = "structure"   # Documentos estruturais


class SourceType(str, Enum):
    """Tipo de fonte do documento."""
    PDF = "pdf"
    MARKDOWN = "markdown"
    DOCX = "docx"
    TXT = "txt"
    HTML = "html"


class DocumentMetadata(BaseModel):
    """Metadados estruturados de um documento."""
    
    # Identificação
    title: str = Field(..., min_length=3, description="Título do documento")
    author: Optional[str] = Field(None, description="Autor ou organização")
    language: str = Field("pt", description="Idioma principal")
    
    # Classificação
    document_type: DocumentType = Field(..., description="Tipo do documento")
    source_type: SourceType = Field(..., description="Formato da fonte")
    
    # Geográfico
    countries: List[str] = Field(default_factory=list, description="Países cobertos")
    regions: List[str] = Field(default_factory=list, description="Regiões geográficas")
    
    # Temático
    topics: List[str] = Field(default_factory=list, description="Tópicos tributários")
    keywords: List[str] = Field(default_factory=list, description="Palavras-chave")
    
    # Temporal
    publication_date: Optional[datetime] = Field(None, description="Data de publicação")
    validity_start: Optional[datetime] = Field(None, description="Início da vigência")
    validity_end: Optional[datetime] = Field(None, description="Fim da vigência")
    
    # Qualidade
    confidence_level: float = Field(1.0, ge=0.0, le=1.0, description="Nível de confiança (0-1)")
    official_source: bool = Field(False, description="Fonte oficial governamental")
    
    # Técnico
    total_pages: Optional[int] = Field(None, ge=1, description="Total de páginas")
    file_size_mb: Optional[float] = Field(None, ge=0.0, description="Tamanho em MB")
    
    @validator('countries', 'regions', 'topics', 'keywords')
    def normalize_lists(cls, v):
        """Normaliza listas removendo duplicatas e convertendo para lowercase."""
        if v:
            return list(set(item.lower().strip() for item in v if item.strip()))
        return []
    
    @validator('confidence_level')
    def validate_confidence(cls, v):
        """Valida nível de confiança."""
        return round(v, 2)


class Document(BaseModel):
    """Documento completo na base de conhecimento."""
    
    # Identificação única
    id: str = Field(..., description="ID único do documento")
    file_path: Path = Field(..., description="Caminho do arquivo")
    
    # Conteúdo
    content: str = Field(..., min_length=10, description="Conteúdo extraído")
    metadata: DocumentMetadata = Field(..., description="Metadados estruturados")
    
    # Processamento
    processed_at: datetime = Field(default_factory=datetime.now, description="Data de processamento")
    processing_version: str = Field("1.0", description="Versão do processamento")
    
    # ChromaDB
    chunks_count: int = Field(0, ge=0, description="Número de chunks gerados")
    embedded: bool = Field(False, description="Se foi incorporado ao vector DB")
    
    class Config:
        """Configuração do modelo."""
        arbitrary_types_allowed = True
        json_encoders = {
            Path: str,
            datetime: lambda v: v.isoformat()
        }
    
    @validator('id')
    def validate_id(cls, v):
        """Valida formato do ID."""
        if not v or len(v) < 3:
            raise ValueError("ID deve ter pelo menos 3 caracteres")
        return v.lower().replace(" ", "_")
    
    @validator('file_path')
    def validate_file_path(cls, v):
        """Valida se o arquivo existe."""
        if not isinstance(v, Path):
            v = Path(v)
        return v
    
    def get_summary(self) -> Dict[str, Any]:
        """Retorna resumo do documento para debug."""
        return {
            "id": self.id,
            "title": self.metadata.title,
            "type": self.metadata.document_type.value,
            "source": self.metadata.source_type.value,
            "countries": len(self.metadata.countries),
            "topics": len(self.metadata.topics),
            "content_length": len(self.content),
            "chunks": self.chunks_count,
            "embedded": self.embedded,
            "confidence": self.metadata.confidence_level
        }