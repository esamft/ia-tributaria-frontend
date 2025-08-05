#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agente Validador Jurídico - Especialista em validação de informações tributárias
Seguindo padrão Agno Framework
"""

from agno.agent import Agent
from agno.models.anthropic import Claude
from agno.tools.toolkit import Toolkit
from typing import List, Dict, Any, Optional
import json
from datetime import datetime

class ValidadorJuridicoTools(Toolkit):
    """Ferramentas especializadas do Validador Jurídico"""
    
    def __init__(self):
        super().__init__(
            name="validador_juridico_tools",
            tools=[
                self.validar_consistencia_legal,
                self.verificar_atualizacao_normativa,
                self.analisar_conflitos_jurisdicionais,
                self.validar_aplicabilidade_tratados,
                self.verificar_precedentes
            ]
        )
    
    @staticmethod
    def validar_consistencia_legal(informacao: str, jurisdicao: str, fontes: List[Dict]) -> Dict[str, Any]:
        """Valida a consistência legal da informação"""
        
        # Princípios fundamentais do direito tributário internacional
        principios_validacao = {
            "residencia_fiscal": [
                "Teste dos 183 dias deve ser específico por jurisdição",
                "Centro de interesses vitais deve ser demonstrável",
                "Nacionalidade é critério subsidiário na maioria dos países"
            ],
            "tratados": [
                "Tratados prevalecem sobre legislação interna",
                "Tie-breakers seguem ordem hierárquica específica",
                "Procedimento amigável deve estar disponível"
            ],
            "cfc": [
                "Regras CFC aplicam-se apenas a controladas",
                "Alíquota efetiva deve ser considerada",
                "Exceções por atividade operacional existem"
            ]
        }
        
        # Identificar tipo de informação
        info_lower = informacao.lower()
        tipo_identificado = "geral"
        
        for tipo, criterios in principios_validacao.items():
            if any(palavra in info_lower for palavra in tipo.split('_')):
                tipo_identificado = tipo
                break
        
        # Score de consistência baseado nas fontes
        score_consistencia = 0
        alertas = []
        
        # Verificar qualidade das fontes
        fontes_primarias = [f for f in fontes if f.get("relevancia", 0) > 0.8]
        if len(fontes_primarias) >= 2:
            score_consistencia += 0.4
        else:
            alertas.append("Poucas fontes primárias de alta relevância")
        
        # Verificar consistência temporal
        ano_atual = datetime.now().year
        for fonte in fontes:
            if "2024" in fonte.get("documento", "") or "2025" in fonte.get("documento", ""):
                score_consistencia += 0.3
                break
        else:
            alertas.append("Verificar atualização das informações")
        
        # Verificar jurisdição específica
        if jurisdicao.lower() in informacao.lower():
            score_consistencia += 0.3
        else:
            alertas.append(f"Informação pode não ser específica para {jurisdicao}")
        
        return {
            "informacao_validada": informacao,
            "jurisdicao": jurisdicao,
            "tipo_informacao": tipo_identificado,
            "score_consistencia": min(score_consistencia, 1.0),
            "alertas": alertas,
            "principios_aplicaveis": principios_validacao.get(tipo_identificado, []),
            "recomendacao": "aprovada" if score_consistencia > 0.7 else "revisao_necessaria"
        }
    
    @staticmethod
    def verificar_atualizacao_normativa(pais: str, area_tributaria: str) -> Dict[str, Any]:
        """Verifica se há atualizações normativas recentes"""
        
        # Base de mudanças conhecidas 2024-2025
        mudancas_recentes = {
            "portugal": {
                "2024": "Fim do regime NHR, introdução do IFICI",
                "status": "alterado_significativamente"
            },
            "brasil": {
                "2023": "Lei 14.754/2023 - novas regras CFC",
                "status": "alterado_recentemente"
            },
            "uruguai": {
                "2024": "Manutenção do sistema territorial",
                "status": "estavel"
            },
            "paraguai": {
                "2024": "Sistema territorial mantido, CRS implementado",
                "status": "estavel_com_compliance"
            }
        }
        
        pais_info = mudancas_recentes.get(pais.lower(), {
            "status": "verificar_atualizacoes",
            "observacao": "Informações podem necessitar verificação adicional"
        })
        
        return {
            "pais": pais,
            "area": area_tributaria,
            "status_normativo": pais_info.get("status", "desconhecido"),
            "ultima_alteracao": pais_info.get("2024", pais_info.get("2023", "Não identificada")),
            "necessita_verificacao": pais_info.get("status") == "verificar_atualizacoes",
            "data_verificacao": datetime.now().strftime("%Y-%m-%d")
        }
    
    @staticmethod
    def analisar_conflitos_jurisdicionais(paises: List[str], situacao: str) -> Dict[str, Any]:
        """Analisa potenciais conflitos entre jurisdições"""
        
        if len(paises) < 2:
            return {"conflito": "nao_aplicavel", "paises": paises}
        
        # Matriz de conflitos conhecidos
        conflitos_comuns = {
            ("brasil", "portugal"): {
                "area": "residencia_fiscal",
                "risco": "medio",
                "solucao": "Tratado Brasil-Portugal, tie-breakers aplicáveis"
            },
            ("brasil", "uruguai"): {
                "area": "residencia_fiscal",
                "risco": "baixo",
                "solucao": "Tratado vigente, sistema territorial uruguaio facilita"
            },
            ("brasil", "paraguai"): {
                "area": "residencia_fiscal", 
                "risco": "baixo",
                "solucao": "Sistema territorial paraguaio, poucos conflitos"
            },
            ("brasil", "eua"): {
                "area": "compliance",
                "risco": "alto",
                "solucao": "FATCA obrigatório, tratado aplicável"
            }
        }
        
        # Normalizar nomes dos países
        paises_norm = [p.lower() for p in paises]
        
        conflitos_identificados = []
        for combinacao, detalhes in conflitos_comuns.items():
            if all(pais in paises_norm for pais in combinacao):
                conflitos_identificados.append({
                    "jurisdicoes": combinacao,
                    "detalhes": detalhes
                })
        
        return {
            "paises_analisados": paises,
            "conflitos_identificados": conflitos_identificados,
            "nivel_complexidade": "alta" if len(conflitos_identificados) > 1 else "media" if conflitos_identificados else "baixa",
            "recomendacoes": [
                "Verificar tratados específicos vigentes",
                "Analisar tie-breakers aplicáveis",
                "Considerar procedimento amigável se necessário"
            ]
        }
    
    @staticmethod
    def validar_aplicabilidade_tratados(pais_origem: str, pais_destino: str, tipo_renda: str) -> Dict[str, Any]:
        """Valida a aplicabilidade de tratados para evitar dupla tributação"""
        
        # Base de tratados conhecidos (simplificada)
        tratados_vigentes = {
            ("brasil", "portugal"): {"vigente": True, "ano": "2000", "atualizado": "2022"},
            ("brasil", "uruguai"): {"vigente": True, "ano": "2019", "atualizado": "2019"},
            ("brasil", "paraguai"): {"vigente": False, "observacao": "Não há tratado específico"},
            ("brasil", "espanha"): {"vigente": True, "ano": "1974", "atualizado": "revisão pendente"},
            ("brasil", "alemanha"): {"vigente": True, "ano": "1975", "atualizado": "2021"},
            ("brasil", "eua"): {"vigente": False, "observacao": "Acordo limitado para transporte"}
        }
        
        chave = (pais_origem.lower(), pais_destino.lower())
        chave_inversa = (pais_destino.lower(), pais_origem.lower())
        
        tratado_info = tratados_vigentes.get(chave) or tratados_vigentes.get(chave_inversa)
        
        if not tratado_info:
            return {
                "aplicavel": False,
                "motivo": "Tratado não identificado na base",
                "alternativas": ["Verificar legislação interna", "Consultar Receita Federal"]
            }
        
        if not tratado_info.get("vigente"):
            return {
                "aplicavel": False,
                "motivo": tratado_info.get("observacao", "Tratado não vigente"),
                "alternativas": ["Aplicar legislação interna", "Verificar acordos multilaterais"]
            }
        
        return {
            "aplicavel": True,
            "tratado": f"Tratado {pais_origem.title()}-{pais_destino.title()}",
            "ano_assinatura": tratado_info.get("ano"),
            "ultima_atualizacao": tratado_info.get("atualizado"),
            "tipo_renda": tipo_renda,
            "proximos_passos": [
                "Verificar texto específico do tratado",
                "Aplicar tie-breakers se necessário",
                "Considerar procedimento amigável para casos complexos"
            ]
        }
    
    @staticmethod
    def verificar_precedentes(jurisdicao: str, conceito: str) -> Dict[str, Any]:
        """Verifica precedentes jurisprudenciais relevantes"""
        
        # Base simplificada de precedentes importantes
        precedentes_relevantes = {
            "brasil": {
                "residencia_fiscal": [
                    "CARF: Conceito de centro de interesses vitais",
                    "STJ: Aplicação do teste dos 183 dias",
                    "RFB: Posicionamento sobre residência presumida"
                ],
                "tratados": [
                    "CARF: Interpretação de tie-breakers",
                    "STF: Hierarquia dos tratados tributários"
                ]
            },
            "portugal": {
                "residencia_fiscal": [
                    "AT: Critérios de demonstração de vínculos",
                    "STA: Presunção de residência por cônjuge/filhos"
                ]
            }
        }
        
        precedentes = precedentes_relevantes.get(jurisdicao.lower(), {}).get(conceito.lower(), [])
        
        return {
            "jurisdicao": jurisdicao,
            "conceito": conceito,
            "precedentes_encontrados": len(precedentes),
            "precedentes": precedentes,
            "relevancia": "alta" if precedentes else "consultar_diretamente",
            "observacao": "Precedentes encontrados na base interna" if precedentes else "Verificar jurisprudência atualizada"
        }

def criar_agente_validador():
    """Cria e configura o Agente Validador Jurídico"""
    
    return Agent(
        name="Validador Jurídico Tributário",
        model=Claude(id="claude-sonnet-4-20250514"),
        tools=[ValidadorJuridicoTools()],
        description="""
        Sou um validador jurídico especializado em Direito Tributário Internacional, responsável por:
        - Validar a consistência legal das informações encontradas
        - Verificar atualizações normativas recentes
        - Analisar conflitos jurisdicionais
        - Validar aplicabilidade de tratados
        - Verificar precedentes jurisprudenciais
        """,
        instructions="""
        COMO VALIDADOR JURÍDICO:
        
        1. SEMPRE valide informações com validar_consistencia_legal()
        2. Verifique atualizações normativas para cada país mencionado
        3. Analise conflitos quando múltiplas jurisdições estão envolvidas
        4. Valide aplicabilidade de tratados quando relevante
        5. Busque precedentes para questões complexas
        
        CRITÉRIOS DE VALIDAÇÃO:
        - Score de consistência > 0.7 = informação confiável
        - Sempre citar alertas identificados
        - Recomendar verificação adicional quando necessário
        
        FORMATO DE RESPOSTA:
        - Status da validação (aprovada/revisão necessária)
        - Alertas e observações importantes
        - Recomendações para uso da informação
        
        SEMPRE mantenha rigor jurídico e prudência profissional.
        """,
        show_tool_calls=True,
        markdown=True
    )

if __name__ == "__main__":
    # Teste do agente
    agente = criar_agente_validador()
    
    resposta = agente.run("Valide a informação sobre residência fiscal no Uruguai baseada no sistema territorial")
    print(resposta.content)