"""
Modelos para queries e respostas do sistema tributário.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator


class QueryType(str, Enum):
    """Tipos de consulta tributária."""
    GENERAL = "general"                    # Consulta geral
    COUNTRY_SPECIFIC = "country_specific"  # Específica de país
    COMPARATIVE = "comparative"            # Comparação entre países
    PLANNING = "planning"                  # Planejamento tributário
    COMPLIANCE = "compliance"              # Obrigações e compliance
    TREATY = "treaty"                      # Tratados fiscais
    CRYPTO = "crypto"                      # Criptoativos
    IMMIGRATION = "immigration"            # Imigração e vistos


class TaxQuery(BaseModel):
    """Query estruturada para consulta tributária."""
    
    # Conteúdo da consulta
    question: str = Field(..., min_length=10, description="Pergunta do usuário")
    query_type: QueryType = Field(QueryType.GENERAL, description="Tipo de consulta")
    
    # Filtros geográficos
    target_countries: List[str] = Field(default_factory=list, description="Países de interesse")
    source_country: Optional[str] = Field("brasil", description="País de origem")
    
    # Filtros temáticos
    topics: List[str] = Field(default_factory=list, description="Tópicos específicos")
    
    # Contexto do usuário
    user_profile: Optional[str] = Field(None, description="Perfil do usuário")
    priority_level: int = Field(1, ge=1, le=5, description="Nível de prioridade")
    
    # Controle de busca
    max_results: int = Field(10, ge=1, le=50, description="Máximo de resultados")
    include_sources: bool = Field(True, description="Incluir citações de fonte")
    min_confidence: float = Field(0.7, ge=0.0, le=1.0, description="Confiança mínima")
    
    # Metadados
    session_id: Optional[str] = Field(None, description="ID da sessão")
    created_at: datetime = Field(default_factory=datetime.now, description="Timestamp da query")
    
    @validator('question')
    def validate_question(cls, v):
        """Valida e limpa a pergunta."""
        cleaned = v.strip()
        if len(cleaned) < 10:
            raise ValueError("Pergunta deve ter pelo menos 10 caracteres")
        return cleaned
    
    @validator('target_countries', 'topics')
    def normalize_filter_lists(cls, v):
        """Normaliza listas de filtros."""
        if v:
            return [item.lower().strip() for item in v if item.strip()]
        return []
    
    def extract_keywords(self) -> List[str]:
        """Extrai palavras-chave da pergunta."""
        # Lista de termos tributários relevantes
        tax_terms = [
            "residencia", "residente", "fiscal", "imposto", "tributacao",
            "bitributacao", "tratado", "acordo", "exit tax", "cgt",
            "ganhos", "capital", "dividendos", "juros", "royalties",
            "pis", "cofins", "irpf", "irpj", "csll", "iof",
            "offshore", "holding", "planejamento", "otimizacao",
            "compliance", "declaracao", "cbcs", "fatca", "crs",
            "crypto", "bitcoin", "criptomoeda", "nft", "defi"
        ]
        
        question_lower = self.question.lower()
        found_terms = [term for term in tax_terms if term in question_lower]
        
        # Adicionar países mencionados
        found_terms.extend(self.target_countries)
        
        return list(set(found_terms))


class SourceCitation(BaseModel):
    """Citação de fonte para uma resposta."""
    
    document_id: str = Field(..., description="ID do documento")
    document_title: str = Field(..., description="Título do documento")
    page_number: Optional[int] = Field(None, description="Número da página")
    section: Optional[str] = Field(None, description="Seção específica")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confiança na citação")
    relevant_text: str = Field(..., description="Texto relevante citado")


class QueryResponse(BaseModel):
    """Resposta estruturada para consulta tributária."""
    
    # Resposta principal
    answer: str = Field(..., min_length=50, description="Resposta principal")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confiança na resposta")
    
    # Citações obrigatórias
    sources: List[SourceCitation] = Field(..., min_length=1, description="Fontes citadas")
    
    # Informações adicionais
    related_topics: List[str] = Field(default_factory=list, description="Tópicos relacionados")
    suggested_countries: List[str] = Field(default_factory=list, description="Países sugeridos")
    
    # Limitações
    limitations: List[str] = Field(default_factory=list, description="Limitações da resposta")
    requires_professional_advice: bool = Field(True, description="Requer consultoria profissional")
    
    # Metadados da busca
    search_results_count: int = Field(..., ge=0, description="Chunks encontrados")
    processing_time_ms: int = Field(..., ge=0, description="Tempo de processamento")
    
    # Referência à query original
    original_query: TaxQuery = Field(..., description="Query original")
    response_timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp da resposta")
    
    class Config:
        """Configuração do modelo."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    @validator('answer')
    def validate_answer_quality(cls, v):
        """Valida qualidade da resposta."""
        if len(v.strip()) < 50:
            raise ValueError("Resposta deve ter pelo menos 50 caracteres")
        
        # Verifica se contém disclaimer mínimo
        disclaimers = ["consulte", "profissional", "advogado", "contador", "específic"]
        if not any(term in v.lower() for term in disclaimers):
            v += "\n\nATENÇÃO: Esta resposta é baseada em informações gerais. Consulte sempre um profissional qualificado para sua situação específica."
        
        return v.strip()
    
    def format_for_cli(self) -> str:
        """Formata resposta para exibição em CLI."""
        output = []
        
        # Resposta principal
        output.append(f"📋 RESPOSTA (Confiança: {self.confidence_score:.1%})")
        output.append("=" * 60)
        output.append(self.answer)
        output.append("")
        
        # Fontes
        output.append("📚 FONTES:")
        for i, source in enumerate(self.sources, 1):
            citation = f"{i}. {source.document_title}"
            if source.page_number:
                citation += f" (página {source.page_number})"
            if source.section:
                citation += f" - {source.section}"
            citation += f" [Confiança: {source.confidence:.1%}]"
            output.append(citation)
        output.append("")
        
        # Informações complementares
        if self.related_topics:
            output.append(f"🔗 Tópicos relacionados: {', '.join(self.related_topics)}")
        
        if self.suggested_countries:
            output.append(f"🌍 Países sugeridos: {', '.join(self.suggested_countries)}")
        
        if self.limitations:
            output.append("⚠️  LIMITAÇÕES:")
            for limitation in self.limitations:
                output.append(f"  • {limitation}")
        
        return "\n".join(output)