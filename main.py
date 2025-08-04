#!/usr/bin/env python3
"""
Sistema de Agentes IA para Tributação Internacional
Powered by Agno Framework

Entry point principal do sistema.
"""

import os
import sys
from pathlib import Path

# Carregar variáveis de ambiente
from dotenv import load_dotenv
load_dotenv()

# Verificar dependências críticas
def check_dependencies():
    """Verifica se dependências críticas estão instaladas."""
    missing = []
    
    try:
        import rich
    except ImportError:
        missing.append("rich")
    
    try:
        import openai
    except ImportError:
        missing.append("openai")
    
    try:
        import chromadb
    except ImportError:
        missing.append("chromadb")
    
    try:
        import pypdf
    except ImportError:
        missing.append("pypdf")
    
    if missing:
        print(f"❌ Dependências ausentes: {', '.join(missing)}")
        print("Execute: pip install -r requirements.txt")
        sys.exit(1)

def check_environment():
    """Verifica variáveis de ambiente necessárias."""
    required_vars = ["OPENAI_API_KEY"]
    missing = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)
    
    if missing:
        print(f"❌ Variáveis de ambiente ausentes: {', '.join(missing)}")
        print("Configure no arquivo .env (use .env.example como referência)")
        sys.exit(1)

def main():
    """Ponto de entrada principal do sistema."""
    
    # Verificações iniciais
    check_dependencies()
    check_environment()
    
    # Importar componentes principais
    try:
        from ui.cli_interface import TaxSystemCLI
        from core.knowledge_base import TaxKnowledgeBase
        
        # Inicializar base de conhecimento
        knowledge_base = TaxKnowledgeBase()
        
        # Inicializar interface CLI
        cli = TaxSystemCLI(knowledge_base)
        
        # Iniciar interface
        cli.start()
        
    except ImportError as e:
        print(f"❌ Erro ao importar módulos: {e}")
        print("Verifique se todos os arquivos estão presentes")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n👋 Sistema encerrado pelo usuário")
    except Exception as e:
        print(f"❌ Erro crítico: {e}")
        print("Consulte os logs ou execute com --debug para mais detalhes")
        sys.exit(1)

if __name__ == "__main__":
    main()