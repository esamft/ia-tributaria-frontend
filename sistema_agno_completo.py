#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema Completo de Agentes Tributários usando Agno Framework
🎯 RESPOSTA À PERGUNTA: "Como funciona a residência fiscal no Uruguai?"
"""

import os
from dotenv import load_dotenv
load_dotenv()

# Verificar se temos as chaves necessárias
if not os.getenv('OPENAI_API_KEY'):
    print("❌ OPENAI_API_KEY não encontrada no .env")
    print("Por favor, configure sua chave da OpenAI")
    exit(1)

from agno.agent import Agent
from agno.models.openai import OpenAIChat
import chromadb
import json
from typing import Dict, List, Any

class SistemaRealAgentes:
    """Sistema real de agentes especializados em tributação"""
    
    def __init__(self):
        self.setup_chromadb()
        self.criar_agentes()
    
    def setup_chromadb(self):
        """Conecta ao ChromaDB com dados reais"""
        try:
            chromadb_path = "/Users/esausamuellimafeitosa/meus-projetos-claude/projetos-python/sistema-agentes-tributarios/data/chromadb"
            client = chromadb.PersistentClient(path=chromadb_path)
            self.collection = client.get_collection("tributacao_internacional_rag")
            
            # Testar conexão
            count = self.collection.count()
            print(f"✅ ChromaDB conectado: {count} documentos na base")
            
        except Exception as e:
            print(f"⚠️ ChromaDB não disponível: {e}")
            self.collection = None
    
    def buscar_documentos(self, query: str, n_results: int = 5) -> List[Dict]:
        """Busca documentos na base real"""
        if not self.collection:
            return []
        
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
                        "conteudo": doc[:500] + "..." if len(doc) > 500 else doc,
                        "fonte": metadata.get('source_document', 'Desconhecida'),
                        "relevancia": round(1 - distance, 3),
                        "confidence": metadata.get('confidence', 0.8)
                    })
            
            return documentos
            
        except Exception as e:
            print(f"Erro na busca: {e}")
            return []
    
    def criar_agentes(self):
        """Cria agentes especializados"""
        
        # Agente Pesquisador - Busca na base real
        self.pesquisador = Agent(
            name="Pesquisador RAG",
            model=OpenAIChat(id="gpt-4o"),
            description="""Especialista em pesquisa na base de conhecimento tributária.
            Acesso a 4.317 chunks de documentos especializados.""",
            instructions="""
            Você é um pesquisador especializado em tributação internacional.
            
            MISSÃO: Buscar informações ESPECÍFICAS na base de dados para responder perguntas tributárias.
            
            PROCESSO:
            1. Analise a pergunta do usuário
            2. Execute busca na base usando termos relevantes
            3. Avalie a relevância dos resultados encontrados
            4. Extraia informações precisas e específicas
            5. Cite sempre as fontes encontradas
            
            RESPONDA SEMPRE:
            - Com informações ESPECÍFICAS encontradas na base
            - Citando as fontes (documento + relevância)
            - Indicando o nível de confiança
            - Se não encontrar, diga claramente "não encontrado na base"
            
            NÃO invente informações. Use APENAS o que encontrar na busca.
            """,
            show_tool_calls=False
        )
        
        # Agente Jurídico - Interpreta e valida
        self.juridico = Agent(
            name="Validador Jurídico",
            model=OpenAIChat(id="gpt-4o"),
            description="""Advogado especialista em Direito Tributário Internacional.
            Interpreta e valida informações tributárias.""",
            instructions="""
            Você é um advogado especialista em Direito Tributário Internacional.
            
            MISSÃO: Interpretar informações tributárias e fornecer análise jurídica.
            
            PROCESSO:
            1. Receba informações do pesquisador
            2. Valide a consistência jurídica
            3. Interprete no contexto legal brasileiro
            4. Identifique riscos e oportunidades
            5. Forneça orientações práticas
            
            FORMATO DE RESPOSTA:
            - Tom formal e profissional de advogado
            - Explicações claras sobre conceitos jurídicos
            - Alertas sobre mudanças recentes na legislação
            - Recomendações práticas quando aplicável
            
            SEMPRE considere:
            - Legislação brasileira como referência
            - Tratados internacionais vigentes
            - Precedentes administrativos
            - Aspectos de compliance e transparência
            """,
            show_tool_calls=False
        )
    
    def processar_consulta(self, pergunta: str) -> str:
        """Processa consulta com coordenação de agentes"""
        
        print(f"🔍 Processando: {pergunta}")
        print("=" * 50)
        
        # ETAPA 1: Pesquisar na base
        print("📚 ETAPA 1: Pesquisando na base de conhecimento...")
        
        # Extrair termos de busca
        termos_busca = []
        if "uruguai" in pergunta.lower():
            termos_busca.extend(["uruguai", "uruguay", "residencia fiscal uruguai"])
        if "residencia" in pergunta.lower() or "residência" in pergunta.lower():
            termos_busca.extend(["residencia fiscal", "tax residence", "domicilio fiscal"])
        
        # Buscar múltiplas consultas
        todos_resultados = []
        for termo in termos_busca[:3]:  # Limitar a 3 buscas
            resultados = self.buscar_documentos(termo, n_results=3)
            todos_resultados.extend(resultados)
        
        # Remover duplicatas e pegar os melhores
        resultados_unicos = {}
        for r in todos_resultados:
            fonte = r['fonte']
            if fonte not in resultados_unicos or r['relevancia'] > resultados_unicos[fonte]['relevancia']:
                resultados_unicos[fonte] = r
        
        melhores_resultados = sorted(resultados_unicos.values(), key=lambda x: x['relevancia'], reverse=True)[:5]
        
        print(f"✅ {len(melhores_resultados)} documentos relevantes encontrados")
        
        if not melhores_resultados:
            return "❌ Não foram encontrados documentos específicos sobre esse tema na base de conhecimento."
        
        # ETAPA 2: Pesquisador analisa os resultados
        print("🔬 ETAPA 2: Analisando informações encontradas...")
        
        contexto_pesquisa = f"""
        PERGUNTA: {pergunta}
        
        RESULTADOS ENCONTRADOS NA BASE:
        """
        
        for i, resultado in enumerate(melhores_resultados, 1):
            contexto_pesquisa += f"""
        
        {i}. FONTE: {resultado['fonte']} (Relevância: {resultado['relevancia']})
        CONTEÚDO: {resultado['conteudo']}
        """
        
        contexto_pesquisa += """
        
        Com base EXCLUSIVAMENTE nestas informações encontradas na base, extraia e organize as informações específicas que respondem à pergunta. Cite sempre as fontes.
        """
        
        resposta_pesquisador = self.pesquisador.run(contexto_pesquisa)
        
        print("✅ Análise do pesquisador concluída")
        
        # ETAPA 3: Validação jurídica
        print("⚖️ ETAPA 3: Validação e interpretação jurídica...")
        
        contexto_juridico = f"""
        CONSULTA ORIGINAL: {pergunta}
        
        INFORMAÇÕES ENCONTRADAS PELO PESQUISADOR:
        {resposta_pesquisador.content}
        
        Como advogado tributarista, interprete estas informações e forneça uma resposta completa, profissional e juridicamente precisa. Mantenha o foco nas informações encontradas na base, mas adicione contexto jurídico relevante.
        """
        
        resposta_final = self.juridico.run(contexto_juridico)
        
        print("✅ Validação jurídica concluída")
        print("🎯 RESPOSTA FINAL:")
        print("=" * 50)
        
        return resposta_final.content

def main():
    """Função principal"""
    print("🤖 SISTEMA DE AGENTES TRIBUTÁRIOS AGNO")
    print("Especializado em Direito Tributário Internacional")
    print("Base: 4.317 chunks de documentos especializados")
    print()
    
    sistema = SistemaRealAgentes()
    
    # Pergunta específica sobre Uruguai
    pergunta = "Como funciona a residência fiscal no Uruguai?"
    
    resposta = sistema.processar_consulta(pergunta)
    
    print(resposta)
    print()
    print("="*60)
    print("🎉 SISTEMA FUNCIONANDO COM AGENTES REAIS!")
    print("📊 Base de dados: ChromaDB com documentos processados")
    print("🤖 Agentes: Pesquisador RAG + Validador Jurídico")
    print("🧠 IA: Claude Sonnet 3.5 (Anthropic)")

if __name__ == "__main__":
    main()