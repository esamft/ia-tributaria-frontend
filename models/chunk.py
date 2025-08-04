"""
Modelos para chunks de texto processados.
Unidades básicas de informação no sistema RAG.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator


class ChunkMetadata(BaseModel):
    """Metadados específicos de um chunk."""
    
    # Origem
    document_id: str = Field(..., description="ID do documento pai")
    page_number: Optional[int] = Field(None, ge=1, description="Número da página")
    section: Optional[str] = Field(None, description="Seção do documento")
    
    # Localização no documento
    start_char: int = Field(..., ge=0, description="Posição inicial no texto")
    end_char: int = Field(..., ge=0, description="Posição final no texto")
    
    # Classificação automática
    detected_countries: List[str] = Field(default_factory=list, description="Países detectados")
    detected_topics: List[str] = Field(default_factory=list, description="Tópicos identificados")
    
    # Contexto
    has_numbers: bool = Field(False, description="Contém dados numéricos")
    has_dates: bool = Field(False, description="Contém datas")
    has_legal_refs: bool = Field(False, description="Contém referências legais")
    
    # Qualidade
    text_quality: float = Field(1.0, ge=0.0, le=1.0, description="Qualidade do texto (0-1)")
    information_density: float = Field(0.5, ge=0.0, le=1.0, description="Densidade de informação")
    
    @validator('detected_countries', 'detected_topics')
    def normalize_detected_lists(cls, v):
        """Normaliza listas detectadas."""
        if v:
            return list(set(item.lower().strip() for item in v if item.strip()))
        return []
    
    @validator('end_char')
    def validate_char_positions(cls, v, values):
        """Valida posições dos caracteres."""
        if 'start_char' in values and v <= values['start_char']:
            raise ValueError("end_char deve ser maior que start_char")
        return v


class Chunk(BaseModel):
    """Chunk de texto com metadados para sistema RAG."""
    
    # Identificação
    id: str = Field(..., description="ID único do chunk")
    text: str = Field(..., min_length=50, max_length=2000, description="Texto do chunk")
    
    # Metadados
    metadata: ChunkMetadata = Field(..., description="Metadados do chunk")
    
    # Embedding
    embedding_vector: Optional[List[float]] = Field(None, description="Vector de embedding")
    embedding_model: Optional[str] = Field(None, description="Modelo usado para embedding")
    
    # Processamento
    created_at: datetime = Field(default_factory=datetime.now, description="Data de criação")
    
    # ChromaDB específico
    collection_name: str = Field("tax_knowledge", description="Nome da collection")
    
    class Config:
        """Configuração do modelo."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    @validator('id')
    def validate_chunk_id(cls, v):
        """Valida formato do ID do chunk."""
        if not v or len(v) < 5:
            raise ValueError("ID do chunk deve ter pelo menos 5 caracteres")
        return v
    
    @validator('text')
    def validate_text_content(cls, v):
        """Valida conteúdo do texto."""
        # Remove espaços excessivos
        cleaned = ' '.join(v.split())
        if len(cleaned) < 50:
            raise ValueError("Chunk deve ter pelo menos 50 caracteres úteis")
        return cleaned
    
    def get_chromadb_format(self) -> Dict[str, Any]:
        """Retorna formato compatível com ChromaDB."""
        return {
            "ids": [self.id],
            "documents": [self.text],
            "metadatas": [{
                "document_id": self.metadata.document_id,
                "page_number": self.metadata.page_number,
                "section": self.metadata.section or "",
                "countries": ",".join(self.metadata.detected_countries),
                "topics": ",".join(self.metadata.detected_topics),
                "has_numbers": self.metadata.has_numbers,
                "has_dates": self.metadata.has_dates,
                "has_legal_refs": self.metadata.has_legal_refs,
                "text_quality": self.metadata.text_quality,
                "information_density": self.metadata.information_density,
                "created_at": self.created_at.isoformat()
            }]
        }
    
    def calculate_relevance_score(self, query_countries: List[str] = None, 
                                 query_topics: List[str] = None) -> float:
        """Calcula score de relevância baseado na query."""
        score = self.metadata.information_density
        
        # Boost por países correspondentes
        if query_countries:
            matching_countries = set(query_countries) & set(self.metadata.detected_countries)
            if matching_countries:
                score += 0.3 * (len(matching_countries) / len(query_countries))
        
        # Boost por tópicos correspondentes
        if query_topics:
            matching_topics = set(query_topics) & set(self.metadata.detected_topics)
            if matching_topics:
                score += 0.2 * (len(matching_topics) / len(query_topics))
        
        # Penalizar baixa qualidade
        score *= self.metadata.text_quality
        
        return min(score, 1.0)