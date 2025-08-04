#!/usr/bin/env python3
"""
Script de teste e validação do Sistema de Agentes Tributários.
Verifica funcionamento completo antes do uso.
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Carregar variáveis de ambiente
from dotenv import load_dotenv
load_dotenv()

def test_imports():
    """Testa importação de todos os módulos."""
    print("🧪 Testando importações...")
    
    try:
        # Dependências externas
        import rich
        import openai  
        import chromadb
        import pypdf
        from pydantic import BaseModel
        print("  ✅ Dependências externas OK")
        
        # Módulos internos
        from models.document import Document, DocumentMetadata
        from models.chunk import Chunk, ChunkMetadata
        from models.query import TaxQuery, QueryResponse
        from tools.pdf_processor import PDFProcessor
        from tools.markdown_processor import MarkdownProcessor
        from tools.chunking_tools import ChunkingTools
        from core.vector_store import TaxVectorStore
        from core.document_manager import DocumentManager
        from core.knowledge_base import TaxKnowledgeBase
        from agents.tax_consultant import TaxConsultantAgent
        from ui.cli_interface import TaxSystemCLI
        print("  ✅ Módulos internos OK")
        
        return True
        
    except ImportError as e:
        print(f"  ❌ Erro de importação: {e}")
        return False

def test_environment():
    """Testa configuração do ambiente."""
    print("🌍 Testando ambiente...")
    
    # Verificar API key
    if not os.getenv("OPENAI_API_KEY"):
        print("  ❌ OPENAI_API_KEY não configurada")
        return False
    else:
        print("  ✅ OPENAI_API_KEY configurada")
    
    # Verificar estrutura de pastas
    required_dirs = ["data", "agents", "core", "models", "tools", "ui"]
    for dir_name in required_dirs:
        if not Path(dir_name).exists():
            print(f"  ❌ Diretório ausente: {dir_name}")
            return False
    print("  ✅ Estrutura de pastas OK")
    
    # Verificar arquivos de dados
    data_path = Path("data")
    pdf_files = list(data_path.glob("*.pdf"))
    md_files = list(data_path.glob("*.md"))
    
    if not pdf_files and not md_files:
        print("  ⚠️ Nenhum documento encontrado em data/")
        print("     Sistema funcionará, mas sem base de conhecimento")
    else:
        print(f"  ✅ Documentos encontrados: {len(pdf_files)} PDFs, {len(md_files)} MDs")
    
    return True

def test_models():
    """Testa modelos Pydantic."""
    print("📋 Testando modelos...")
    
    try:
        from models.document import Document, DocumentMetadata, DocumentType, SourceType
        from models.chunk import Chunk, ChunkMetadata
        from models.query import TaxQuery, QueryResponse, QueryType
        
        # Teste DocumentMetadata
        metadata = DocumentMetadata(
            title="Teste",
            document_type=DocumentType.GUIDE,
            source_type=SourceType.PDF,
            countries=["portugal", "brasil"],
            topics=["tributacao", "residencia"],
            confidence_level=0.9
        )
        
        # Teste TaxQuery
        query = TaxQuery(
            question="Teste de query?",
            query_type=QueryType.GENERAL,
            target_countries=["portugal"]
        )
        
        print("  ✅ Modelos Pydantic OK")
        return True
        
    except Exception as e:
        print(f"  ❌ Erro nos modelos: {e}")
        return False

def test_processors():
    """Testa processadores de documentos.""" 
    print("🛠️ Testando processadores...")
    
    try:
        from tools.pdf_processor import PDFProcessor
        from tools.markdown_processor import MarkdownProcessor
        from tools.chunking_tools import ChunkingTools
        
        # Instanciar processadores
        pdf_proc = PDFProcessor()
        md_proc = MarkdownProcessor()
        chunking = ChunkingTools()
        
        print("  ✅ Processadores instanciados OK")
        
        # Testar se há documentos para processar
        data_path = Path("data")
        pdf_files = list(data_path.glob("*.pdf"))
        
        if pdf_files:
            print(f"  ✅ {len(pdf_files)} PDFs disponíveis para teste")
        else:
            print("  ⚠️ Nenhum PDF para teste")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Erro nos processadores: {e}")
        return False

def test_vector_store():
    """Testa sistema de armazenamento vetorial."""
    print("🗂️ Testando vector store...")
    
    try:
        from core.vector_store import TaxVectorStore
        
        # Criar vector store de teste
        vs = TaxVectorStore(db_path="./data/test_chroma_db")
        
        # Verificar estatísticas
        stats = vs.get_collection_stats()
        print(f"  ✅ Vector store criado - {stats.get('total_chunks', 0)} chunks")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Erro no vector store: {e}")
        return False

def test_knowledge_base():
    """Testa base de conhecimento integrada."""
    print("🧠 Testando base de conhecimento...")
    
    try:
        from core.knowledge_base import TaxKnowledgeBase
        
        # Criar base de conhecimento
        kb = TaxKnowledgeBase()
        
        # Verificar health check
        health = kb.health_check()
        print(f"  ✅ Base criada - Status: {health['status']}")
        
        if health['issues']:
            print("  ⚠️ Problemas identificados:")
            for issue in health['issues'][:3]:
                print(f"    • {issue}")
        
        if health['recommendations']:
            print("  💡 Recomendações:")
            for rec in health['recommendations'][:3]:
                print(f"    • {rec}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Erro na base de conhecimento: {e}")
        return False

def test_quick_processing():
    """Teste rápido de processamento (se houver documentos)."""
    print("⚡ Teste rápido de processamento...")
    
    try:
        from core.knowledge_base import TaxKnowledgeBase
        
        kb = TaxKnowledgeBase()
        
        # Verificar se há documentos disponíveis
        docs = kb.document_manager.list_available_documents()
        unprocessed = [d for d in docs if not d["is_processed"]]
        
        if not unprocessed:
            print("  ⚠️ Todos os documentos já processados ou nenhum disponível")
            return True
        
        # Processar o menor documento disponível para teste
        smallest_doc = min(unprocessed, key=lambda x: x["size_mb"])
        
        if smallest_doc["size_mb"] > 5:  # Não processar arquivos > 5MB no teste
            print(f"  ⚠️ Menor documento ({smallest_doc['name']}) muito grande para teste rápido")
            return True
        
        print(f"  🔄 Processando {smallest_doc['name']} ({smallest_doc['size_mb']:.1f}MB)...")
        
        result = kb.document_manager.process_single_document(
            kb.data_path / smallest_doc['name']
        )
        
        if result["success"]:
            print(f"  ✅ Processado: {result['chunks_count']} chunks em {result['processing_time']}")
            
            # Teste de consulta simples
            response = kb.quick_query("Teste de consulta")
            if "Erro" not in response:
                print("  ✅ Consulta de teste funcionou")
            else:
                print("  ⚠️ Consulta com problemas")
                
            return True
        else:
            print(f"  ❌ Falha no processamento: {result.get('error')}")
            return False
        
    except Exception as e:
        print(f"  ❌ Erro no teste de processamento: {e}")
        return False

def test_cli_interface():
    """Testa interface CLI."""
    print("🖥️ Testando interface CLI...")
    
    try:
        from ui.cli_interface import TaxSystemCLI
        from core.knowledge_base import TaxKnowledgeBase
        
        kb = TaxKnowledgeBase()
        cli = TaxSystemCLI(kb)
        
        print("  ✅ Interface CLI instanciada OK")
        return True
        
    except Exception as e:
        print(f"  ❌ Erro na interface CLI: {e}")
        return False

def main():
    """Executa todos os testes."""
    print("🚀 TESTE COMPLETO DO SISTEMA DE AGENTES TRIBUTÁRIOS")
    print("=" * 60)
    print(f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Diretório: {Path.cwd()}")
    print("=" * 60)
    
    tests = [
        ("Importações", test_imports),
        ("Ambiente", test_environment), 
        ("Modelos", test_models),
        ("Processadores", test_processors),
        ("Vector Store", test_vector_store),
        ("Base de Conhecimento", test_knowledge_base),
        ("Interface CLI", test_cli_interface),
        ("Processamento Rápido", test_quick_processing)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n📝 {test_name}")
        print("-" * 40)
        
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSOU")
            else:
                failed += 1  
                print(f"❌ {test_name}: FALHOU")
        except Exception as e:
            failed += 1
            print(f"💥 {test_name}: ERRO - {e}")
    
    # Relatório final
    print("\n" + "=" * 60)
    print("📊 RELATÓRIO FINAL")
    print("=" * 60)
    print(f"✅ Testes passaram: {passed}")
    print(f"❌ Testes falharam: {failed}")
    print(f"📈 Taxa de sucesso: {passed/(passed+failed)*100:.1f}%")
    
    if failed == 0:
        print("\n🎉 SISTEMA TOTALMENTE FUNCIONAL!")
        print("Execute 'python main.py' para iniciar")
    elif passed > failed:
        print("\n⚠️ SISTEMA PARCIALMENTE FUNCIONAL")
        print("Alguns componentes têm problemas, mas sistema básico funciona")
        print("Execute 'python main.py' para iniciar (com limitações)")
    else:
        print("\n🚫 SISTEMA COM PROBLEMAS CRÍTICOS")
        print("Corrija os erros antes de usar o sistema")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())