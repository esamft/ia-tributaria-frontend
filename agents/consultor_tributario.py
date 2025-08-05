#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agente Consultor Tributário - Especialista em análise de consultas
Seguindo padrão Agno Framework
"""

from agno.agent import Agent
from agno.models.anthropic import Claude
from agno.tools.toolkit import Toolkit
from typing import List, Dict, Any
import json

class ConsultorTributarioTools(Toolkit):
    """Ferramentas especializadas do Consultor Tributário"""
    
    def __init__(self):
        super().__init__(
            name="consultor_tributario_tools",
            tools=[
                self.analisar_consulta,
                self.identificar_jurisdicoes,
                self.classificar_complexidade,
                self.extrair_conceitos_chave
            ]
        )
    
    @staticmethod
    def analisar_consulta(consulta: str) -> Dict[str, Any]:
        """Analisa a consulta tributária e identifica elementos principais"""
        consulta_lower = consulta.lower()
        
        # Identificar tipo de consulta
        tipos = {
            "residencia_fiscal": ["residência", "residencia", "domicílio", "domicilio"],
            "tratados": ["tratado", "bitributação", "dupla tributação", "tie-breaker"],
            "planejamento": ["planejamento", "estratégia", "otimização", "estrutura"],
            "cfc": ["cfc", "controlled foreign", "transparência fiscal", "lei 14754"],
            "compliance": ["fatca", "crs", "common reporting", "troca informações"],
            "exit_tax": ["exit tax", "saída do país", "desenquadramento"]
        }
        
        tipo_identificado = "geral"
        for tipo, palavras in tipos.items():
            if any(palavra in consulta_lower for palavra in palavras):
                tipo_identificado = tipo
                break
        
        # Identificar países mencionados
        paises = {
            "brasil": ["brasil", "brasileiro", "br"],
            "portugal": ["portugal", "português", "pt"],
            "uruguai": ["uruguai", "uruguaio"],
            "paraguai": ["paraguai", "paraguaio"],
            "espanha": ["espanha", "espanhol"],
            "eua": ["eua", "estados unidos", "america", "usa"],
            "alemanha": ["alemanha", "alemão", "german"],
            "frança": ["frança", "francês", "french"]
        }
        
        paises_identificados = []
        for pais, variantes in paises.items():
            if any(variante in consulta_lower for variante in variantes):
                paises_identificados.append(pais)
        
        return {
            "tipo_consulta": tipo_identificado,
            "paises": paises_identificados,
            "consulta_original": consulta,
            "necessita_pesquisa_detalhada": len(consulta.split()) > 10
        }
    
    @staticmethod
    def identificar_jurisdicoes(analise: Dict[str, Any]) -> List[str]:
        """Identifica jurisdições relevantes para a consulta"""
        paises = analise.get("paises", [])
        tipo = analise.get("tipo_consulta", "")
        
        # Adicionar jurisdições relevantes baseado no tipo
        jurisdicoes_relevantes = set(paises)
        
        if tipo == "residencia_fiscal":
            jurisdicoes_relevantes.update(["brasil"])  # Sempre incluir Brasil como referência
        
        if tipo == "tratados":
            jurisdicoes_relevantes.update(["brasil"])  # Brasil como base
        
        return list(jurisdicoes_relevantes)
    
    @staticmethod
    def classificar_complexidade(consulta: str, analise: Dict[str, Any]) -> str:
        """Classifica a complexidade da consulta"""
        pontuacao = 0
        
        # Fatores de complexidade
        if len(analise.get("paises", [])) > 1:
            pontuacao += 2
        
        if analise.get("tipo_consulta") in ["planejamento", "cfc", "tratados"]:
            pontuacao += 2
        
        if len(consulta.split()) > 20:
            pontuacao += 1
        
        palavras_complexas = ["estrutura", "holding", "offshore", "planejamento", "otimização"]
        if any(palavra in consulta.lower() for palavra in palavras_complexas):
            pontuacao += 2
        
        if pontuacao >= 5:
            return "alta"
        elif pontuacao >= 3:
            return "media"
        else:
            return "baixa"
    
    @staticmethod
    def extrair_conceitos_chave(consulta: str) -> List[str]:
        """Extrai conceitos-chave para orientar a pesquisa"""
        conceitos_map = {
            "residência fiscal": ["residencia", "domicilio", "183 dias", "centro interesses"],
            "tratados bitributação": ["tratado", "dupla tributacao", "tie-breaker"],
            "planejamento tributário": ["planejamento", "estrategia", "otimizacao"],
            "CFC": ["cfc", "controlled foreign", "transparencia fiscal"],
            "FATCA/CRS": ["fatca", "crs", "common reporting", "troca informacoes"],
            "exit tax": ["exit tax", "saida do pais", "desenquadramento"]
        }
        
        consulta_lower = consulta.lower()
        conceitos_encontrados = []
        
        for conceito, palavras in conceitos_map.items():
            if any(palavra in consulta_lower for palavra in palavras):
                conceitos_encontrados.append(conceito)
        
        return conceitos_encontrados or ["tributação internacional"]

def criar_agente_consultor():
    """Cria e configura o Agente Consultor Tributário"""
    
    return Agent(
        name="Consultor Tributário Internacional",
        model=Claude(id="claude-sonnet-4-20250514"),
        tools=[ConsultorTributarioTools()],
        description="""
        Sou um advogado especializado em Direito Tributário Internacional, responsável por:
        - Analisar consultas tributárias complexas
        - Identificar jurisdições e conceitos relevantes
        - Classificar a complexidade das questões
        - Orientar a estratégia de pesquisa e resposta
        """,
        instructions="""
        COMO CONSULTOR TRIBUTÁRIO:
        
        1. SEMPRE analise a consulta usando as ferramentas disponíveis
        2. Identifique o tipo de questão (residência, tratados, planejamento, etc.)
        3. Determine quais países/jurisdições estão envolvidos
        4. Classifique a complexidade (baixa, média, alta)
        5. Extraia conceitos-chave para orientar a pesquisa
        
        RESPONDA SEMPRE:
        - De forma profissional e jurídica
        - Com base na análise realizada
        - Orientando os próximos passos
        
        NÃO faça afirmações sobre legislação específica sem pesquisa prévia.
        """,
        show_tool_calls=True,
        markdown=True
    )

if __name__ == "__main__":
    # Teste do agente
    agente = criar_agente_consultor()
    
    resposta = agente.run("Como funciona a residência fiscal no Uruguai?")
    print(resposta.content)