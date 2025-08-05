#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agente Pesquisador RAG - Especialista em busca na base de conhecimento
Seguindo padrão Agno Framework
"""

from agno.agent import Agent
from agno.models.anthropic import Claude
from agno.tools.toolkit import Toolkit
from typing import List, Dict, Any, Optional
import chromadb
import os
import json

class PesquisadorRAGTools(Toolkit):
    """Ferramentas especializadas do Pesquisador RAG"""
    
    def __init__(self, chromadb_path: str = None):
        if not chromadb_path:
            chromadb_path = "/Users/esausamuellimafeitosa/meus-projetos-claude/projetos-python/sistema-agentes-tributarios/data/chromadb"
        
        self.chromadb_path = chromadb_path
        self.collection = self._setup_chromadb()
        
        super().__init__(
            name="pesquisador_rag_tools",
            tools=[
                self.buscar_documentos,
                self.buscar_por_pais,
                self.buscar_conceito_especifico,
                self.obter_fontes_relevantes,
                self.validar_informacao
            ]
        )
    
    def _setup_chromadb(self):
        """Configura conexão com ChromaDB"""
        try:
            client = chromadb.PersistentClient(path=self.chromadb_path)
            collection = client.get_collection("tributacao_internacional_rag")
            return collection
        except Exception as e:
            print(f"Erro ao conectar ChromaDB: {e}")
            return None
    
    def buscar_documentos(self, query: str, n_results: int = 5) -> Dict[str, Any]:
        """Busca documentos relevantes na base de conhecimento"""
        if not self.collection:
            return {"erro": "ChromaDB não disponível", "resultados": []}
        
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                include=['documents', 'metadatas', 'distances']
            )
            
            documentos = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    metadata = results['metadatas'][0][i] if results['metadatas'] else {}
                    distance = results['distances'][0][i] if results['distances'] else 1.0
                    
                    documentos.append({
                        "conteudo": doc,
                        "fonte": metadata.get('source_document', 'Desconhecida'),
                        "relevancia": 1 - distance,  # Converter distância em relevância
                        "metadata": metadata
                    })
            
            return {
                "query": query,
                "total_encontrados": len(documentos),
                "resultados": documentos
            }
            
        except Exception as e:
            return {"erro": f"Erro na busca: {e}", "resultados": []}
    
    def buscar_por_pais(self, pais: str, conceito: str = "", n_results: int = 3) -> Dict[str, Any]:
        """Busca informações específicas sobre um país"""
        query = f"{pais} {conceito} tributação fiscal residência"
        return self.buscar_documentos(query.strip(), n_results)
    
    def buscar_conceito_especifico(self, conceito: str, contexto: str = "", n_results: int = 4) -> Dict[str, Any]:
        """Busca informações sobre conceito tributário específico"""
        query = f"{conceito} {contexto} direito tributário internacional"
        return self.buscar_documentos(query.strip(), n_results)
    
    def obter_fontes_relevantes(self, resultados: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extrai e organiza as fontes dos resultados"""
        fontes = []
        
        for resultado in resultados.get("resultados", []):
            fonte = {
                "documento": resultado.get("fonte", "Documento desconhecido"),
                "relevancia": resultado.get("relevancia", 0),
                "tipo": resultado.get("metadata", {}).get("document_type", "tributario"),
                "resumo": resultado.get("conteudo", "")[:200] + "..."
            }
            fontes.append(fonte)
        
        # Ordenar por relevância
        fontes.sort(key=lambda x: x["relevancia"], reverse=True)
        return fontes
    
    def validar_informacao(self, afirmacao: str, contexto_pais: str = "") -> Dict[str, Any]:
        """Valida uma afirmação buscando evidências na base"""
        query = f"{afirmacao} {contexto_pais} verificação"
        resultados = self.buscar_documentos(query, n_results=3)
        
        score_confianca = 0
        evidencias = []
        
        for resultado in resultados.get("resultados", []):
            if resultado.get("relevancia", 0) > 0.7:
                score_confianca += resultado["relevancia"]
                evidencias.append(resultado["conteudo"][:300])
        
        return {
            "afirmacao": afirmacao,
            "confianca": min(score_confianca, 1.0),
            "evidencias": evidencias,
            "fonte_primaria": resultados.get("resultados", [{}])[0].get("fonte", "")
        }

def criar_agente_pesquisador():
    """Cria e configura o Agente Pesquisador RAG"""
    
    return Agent(
        name="Pesquisador RAG Tributário",
        model=Claude(id="claude-sonnet-4-20250514"),
        tools=[PesquisadorRAGTools()],
        description="""
        Sou um especialista em pesquisa de informações tributárias, responsável por:
        - Buscar informações precisas na base de conhecimento (4.317 chunks)
        - Localizar dados específicos por país e conceito
        - Validar informações com base nas fontes disponíveis
        - Fornecer evidências documentais para as análises
        """,
        instructions="""
        COMO PESQUISADOR RAG:
        
        1. SEMPRE use as ferramentas de busca antes de responder
        2. Priorize resultados com alta relevância (> 0.7)
        3. Cite SEMPRE as fontes específicas encontradas
        4. Para consultas por país, use buscar_por_pais()
        5. Para conceitos específicos, use buscar_conceito_especifico()
        6. Valide informações importantes com validar_informacao()
        
        FORMATO DE RESPOSTA:
        - Informação encontrada
        - Fonte(s) específica(s)
        - Nível de confiança
        - Contexto adicional se disponível
        
        NÃO invente informações se não encontrar na base.
        SEMPRE indique quando algo não foi encontrado.
        """,
        show_tool_calls=True,
        markdown=True
    )

if __name__ == "__main__":
    # Teste do agente
    agente = criar_agente_pesquisador()
    
    resposta = agente.run("Busque informações sobre residência fiscal no Uruguai")
    print(resposta.content)