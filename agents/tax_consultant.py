"""
Agente Consultor Tributário - Nível 2 RAG.
Especialista em tributação internacional com base de conhecimento.
"""

import os
from typing import List, Dict, Any, Optional
from datetime import datetime

try:
    from agno.agent import Agent
    from agno.models.openai import OpenAIChat
    from agno.tools.toolkit import Toolkit
    AGNO_AVAILABLE = True
except ImportError:
    # Fallback para desenvolvimento sem Agno
    AGNO_AVAILABLE = False
    print("⚠️ Agno não disponível. Usando implementação simplificada.")

from ..models.query import TaxQuery, QueryResponse, SourceCitation, QueryType
from ..core.vector_store import TaxVectorStore


class TaxConsultantTools(Toolkit):
    """Ferramentas especializadas do consultor tributário."""
    
    def __init__(self, vector_store: TaxVectorStore):
        """
        Inicializa ferramentas do consultor.
        
        Args:
            vector_store: Store vetorial para busca de conhecimento
        """
        self.vector_store = vector_store
        
        super().__init__(
            name="tax_consultant_tools",
            tools=[
                self.search_tax_knowledge,
                self.get_country_specific_info,
                self.compare_jurisdictions,
                self.validate_tax_concept
            ]
        )
    
    def search_tax_knowledge(self, 
                           question: str, 
                           countries: List[str] = None,
                           max_results: int = 10) -> str:
        """
        Busca informações na base de conhecimento tributário.
        
        Args:
            question: Pergunta do usuário
            countries: Países específicos para filtrar
            max_results: Máximo de resultados
            
        Returns:
            str: Informações encontradas com citações
        """
        try:
            # Criar query estruturada
            query = TaxQuery(
                question=question,
                target_countries=countries or [],
                max_results=max_results,
                min_confidence=0.7
            )
            
            # Buscar na base de conhecimento
            results = self.vector_store.search(query, n_results=max_results)
            
            if not results:
                return "Nenhuma informação encontrada na base de conhecimento para esta consulta."
            
            # Formatar resultados com citações
            formatted_results = []
            
            for i, result in enumerate(results[:max_results], 1):
                text = result["text"]
                metadata = result["metadata"]
                score = result["relevance_score"]
                
                # Criar citação
                citation = f"[Fonte {i}]"
                if metadata.get("document_id"):
                    citation += f" {metadata['document_id'].replace('_', ' ').title()}"
                if metadata.get("page_number") and metadata.get("page_number") > 0:
                    citation += f", página {metadata['page_number']}"
                if metadata.get("section"):
                    citation += f", seção: {metadata['section']}"
                citation += f" (Relevância: {score:.1%})"
                
                formatted_results.append(f"{citation}\n{text}\n")
            
            return "\n---\n".join(formatted_results)
            
        except Exception as e:
            return f"Erro ao buscar informações: {str(e)}"
    
    def get_country_specific_info(self, 
                                country: str, 
                                topic: str = "tributacao") -> str:
        """
        Busca informações específicas de um país.
        
        Args:
            country: Nome do país
            topic: Tópico específico
            
        Returns:
            str: Informações do país
        """
        question = f"Informações sobre {topic} em {country}"
        return self.search_tax_knowledge(
            question=question,
            countries=[country.lower()],
            max_results=5
        )
    
    def compare_jurisdictions(self, 
                            countries: List[str], 
                            aspect: str = "tributacao") -> str:
        """
        Compara aspectos tributários entre jurisdições.
        
        Args:
            countries: Lista de países para comparar
            aspect: Aspecto a comparar
            
        Returns:
            str: Comparação entre países
        """
        if len(countries) < 2:
            return "Pelo menos dois países são necessários para comparação."
        
        question = f"Compare {aspect} entre {' e '.join(countries)}"
        return self.search_tax_knowledge(
            question=question,
            countries=[c.lower() for c in countries],
            max_results=8
        )
    
    def validate_tax_concept(self, concept: str) -> str:
        """
        Valida e explica conceitos tributários.
        
        Args:
            concept: Conceito tributário
            
        Returns:
            str: Explicação do conceito
        """
        question = f"Defina e explique o conceito de {concept}"
        return self.search_tax_knowledge(
            question=question,
            max_results=5
        )


class TaxConsultantAgent:
    """
    Agente Consultor Tributário Internacional.
    Nível 2 - RAG com base de conhecimento especializada.
    """
    
    def __init__(self, vector_store: TaxVectorStore):
        """
        Inicializa o agente consultor.
        
        Args:
            vector_store: Store vetorial para busca
        """
        self.vector_store = vector_store
        self.tools = TaxConsultantTools(vector_store)
        
        # Instruções especializadas do agente
        self.system_instructions = """
Você é um especialista em tributação pessoal internacional baseado no EY Worldwide Personal Tax and Immigration Guide e outras fontes confiáveis da base de conhecimento.

REGRAS OBRIGATÓRIAS:
1. Responda APENAS com base nos documentos da base de conhecimento
2. SEMPRE cite fonte específica (documento, página, seção quando disponível)  
3. Use linguagem técnica precisa do setor tributário
4. Se a informação não estiver na base, informe claramente
5. Priorize informações do país específico quando mencionado
6. Inclua referências cruzadas quando relevante
7. Sempre termine com disclaimer sobre consultoria profissional

ESTRUTURA DE RESPOSTA:
- Resposta técnica direta
- Citações específicas das fontes
- Considerações importantes
- Disclaimer profissional

EXEMPLOS DE CITAÇÕES CORRETAS:
- "Segundo o EY Guide 2025, página 150, seção Portugal..."
- "Conforme relatório sobre tendências 2024-2025..."
- "O livro do Estrategista menciona em capítulo 3..."

DISCLAIMER OBRIGATÓRIO:
"ATENÇÃO: Esta resposta é baseada em informações gerais da base de conhecimento. Para sua situação específica, sempre consulte um profissional qualificado em tributação internacional."
"""
        
        # Inicializar agente Agno se disponível
        if AGNO_AVAILABLE:
            self._initialize_agno_agent()
        else:
            self.agno_agent = None
    
    def _initialize_agno_agent(self):
        """Inicializa agente usando framework Agno."""
        try:
            self.agno_agent = Agent(
                name="Consultor Tributário Internacional",
                model=OpenAIChat(
                    id="gpt-4o",
                    api_key=os.getenv("OPENAI_API_KEY")
                ),
                tools=[self.tools],
                description="Especialista em tributação pessoal internacional",
                instructions=self.system_instructions,
                show_tool_calls=True,
                markdown=True
            )
            print("✅ Agente Agno inicializado com sucesso")
        except Exception as e:
            print(f"⚠️ Erro ao inicializar agente Agno: {e}")
            self.agno_agent = None
    
    def query(self, question: str, **kwargs) -> QueryResponse:
        """
        Processa uma consulta tributária.
        
        Args:
            question: Pergunta do usuário
            **kwargs: Parâmetros adicionais (countries, query_type, etc.)
            
        Returns:
            QueryResponse: Resposta estruturada
        """
        start_time = datetime.now()
        
        # Criar query estruturada
        tax_query = TaxQuery(
            question=question,
            target_countries=kwargs.get('countries', []),
            query_type=kwargs.get('query_type', QueryType.GENERAL),
            max_results=kwargs.get('max_results', 10),
            min_confidence=kwargs.get('min_confidence', 0.7)
        )
        
        try:
            if self.agno_agent and AGNO_AVAILABLE:
                # Usar agente Agno
                response_text = self._query_with_agno(tax_query)
            else:
                # Usar implementação simplificada
                response_text = self._query_simplified(tax_query)
            
            # Buscar chunks para citações
            search_results = self.vector_store.search(tax_query)
            
            # Criar citações
            sources = self._create_source_citations(search_results[:5])
            
            # Calcular métricas
            processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
            confidence = self._calculate_response_confidence(search_results, response_text)
            
            # Criar resposta estruturada
            response = QueryResponse(
                answer=response_text,
                confidence_score=confidence,
                sources=sources,
                search_results_count=len(search_results),
                processing_time_ms=processing_time,
                original_query=tax_query,
                related_topics=self._extract_related_topics(search_results),
                suggested_countries=self._extract_suggested_countries(search_results),
                limitations=["Baseado apenas na base de conhecimento disponível",
                           "Informações podem estar desatualizadas",
                           "Não substitui consultoria profissional personalizada"]
            )
            
            return response
            
        except Exception as e:
            # Resposta de erro
            return QueryResponse(
                answer=f"Erro ao processar consulta: {str(e)}",
                confidence_score=0.0,
                sources=[],
                search_results_count=0,
                processing_time_ms=int((datetime.now() - start_time).total_seconds() * 1000),
                original_query=tax_query,
                limitations=["Sistema temporariamente indisponível"]
            )
    
    def _query_with_agno(self, tax_query: TaxQuery) -> str:
        """Processa query usando agente Agno."""
        
        # Construir prompt contextualizado
        prompt = f"""
Pergunta: {tax_query.question}

Países de interesse: {', '.join(tax_query.target_countries) if tax_query.target_countries else 'Não especificado'}

Tipo de consulta: {tax_query.query_type.value}

Por favor, responda com base na base de conhecimento disponível, seguindo as regras estabelecidas.
"""
        
        try:
            response = self.agno_agent.run(prompt)
            return str(response)
        except Exception as e:
            return f"Erro na consulta com agente Agno: {str(e)}"
    
    def _query_simplified(self, tax_query: TaxQuery) -> str:
        """Implementação simplificada sem Agno."""
        
        # Buscar informações relevantes
        search_results = self.vector_store.search(tax_query)
        
        if not search_results:
            return "Não foram encontradas informações na base de conhecimento para responder a esta consulta."
        
        # Combinar informações dos melhores resultados
        combined_info = []
        for result in search_results[:3]:  # Top 3 resultados
            combined_info.append(result["text"])
        
        context = "\n\n".join(combined_info)
        
        # Resposta baseada no contexto encontrado
        response = f"""
Com base nas informações disponíveis na base de conhecimento:

{context}

ATENÇÃO: Esta resposta é baseada em informações gerais da base de conhecimento. Para sua situação específica, sempre consulte um profissional qualificado em tributação internacional.
"""
        
        return response.strip()
    
    def _create_source_citations(self, search_results: List[Dict[str, Any]]) -> List[SourceCitation]:
        """Cria citações estruturadas das fontes."""
        citations = []
        
        for result in search_results:
            metadata = result["metadata"]
            
            # Determinar título do documento
            doc_title = metadata.get("document_id", "Documento").replace("_", " ").title()
            
            citation = SourceCitation(
                document_id=metadata.get("document_id", "unknown"),
                document_title=doc_title,
                page_number=metadata.get("page_number") if metadata.get("page_number", 0) > 0 else None,
                section=metadata.get("section") or None,
                confidence=result.get("relevance_score", 0.0),
                relevant_text=result["text"][:200] + "..." if len(result["text"]) > 200 else result["text"]
            )
            
            citations.append(citation)
        
        return citations
    
    def _calculate_response_confidence(self, search_results: List[Dict], response_text: str) -> float:
        """Calcula confiança da resposta baseada nos resultados."""
        if not search_results:
            return 0.0
        
        # Média dos scores dos resultados utilizados
        avg_relevance = sum(r.get("relevance_score", 0) for r in search_results[:3]) / min(3, len(search_results))
        
        # Ajustar baseado no tamanho da resposta
        response_length_factor = min(1.0, len(response_text) / 500)  # Respostas mais longas = mais confiança
        
        # Penalizar se muito poucos resultados
        results_factor = min(1.0, len(search_results) / 5)
        
        final_confidence = avg_relevance * response_length_factor * results_factor
        
        return min(final_confidence, 1.0)
    
    def _extract_related_topics(self, search_results: List[Dict]) -> List[str]:
        """Extrai tópicos relacionados dos resultados."""
        topics = set()
        
        for result in search_results:
            metadata = result["metadata"]
            if metadata.get("topics"):
                result_topics = metadata["topics"].split(",")
                topics.update(t.strip() for t in result_topics if t.strip())
        
        return list(topics)[:10]  # Limitar a 10 tópicos
    
    def _extract_suggested_countries(self, search_results: List[Dict]) -> List[str]:
        """Extrai países sugeridos dos resultados."""
        countries = set()
        
        for result in search_results:
            metadata = result["metadata"]
            if metadata.get("countries"):
                result_countries = metadata["countries"].split(",")
                countries.update(c.strip() for c in result_countries if c.strip())
        
        return list(countries)[:8]  # Limitar a 8 países
    
    def get_status(self) -> Dict[str, Any]:
        """Retorna status do agente."""
        return {
            "agent_type": "TaxConsultantAgent",
            "level": "2 - RAG",
            "agno_enabled": AGNO_AVAILABLE and self.agno_agent is not None,
            "vector_store_stats": self.vector_store.get_collection_stats(),
            "tools_available": len(self.tools.tools) if self.tools else 0,
            "system_instructions_length": len(self.system_instructions)
        }