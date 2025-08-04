#!/usr/bin/env python3
"""
Servidor web para IA Tributária Internacional.
Entry point para a API REST que se conecta ao frontend Next.js.
"""

import os
import sys
from pathlib import Path

# Carregar variáveis de ambiente
from dotenv import load_dotenv
load_dotenv()

def check_web_dependencies():
    """Verifica dependências para servidor web."""
    missing = []
    
    try:
        import fastapi
    except ImportError:
        missing.append("fastapi")
    
    try:
        import uvicorn
    except ImportError:
        missing.append("uvicorn")
    
    if missing:
        print(f"❌ Dependências web ausentes: {', '.join(missing)}")
        print("Execute: pip install fastapi uvicorn[standard]")
        sys.exit(1)

def check_environment():
    """Verifica configuração do ambiente."""
    required_vars = ["OPENAI_API_KEY"]
    missing = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)
    
    if missing:
        print(f"❌ Variáveis de ambiente ausentes: {', '.join(missing)}")
        print("Configure no arquivo .env")
        return False
    
    return True

def main():
    """Inicia servidor web FastAPI."""
    
    print("🌐 IA Tributária Internacional - Servidor Web")
    print("=" * 50)
    
    # Verificações
    check_web_dependencies()
    
    if not check_environment():
        print("⚠️ Continuando sem todas as variáveis (modo limitado)")
    
    try:
        from api.web_server import run_server
        
        # Configurações do servidor
        host = os.getenv("HOST", "0.0.0.0")
        port = int(os.getenv("PORT", "8000"))
        reload = os.getenv("RELOAD", "true").lower() == "true"
        
        print(f"🚀 Iniciando servidor em http://{host}:{port}")
        print(f"📖 API Docs: http://{host}:{port}/docs")
        print(f"🔍 Health Check: http://{host}:{port}/health")
        print(f"📊 Status: http://{host}:{port}/status")
        print("=" * 50)
        print("💡 Dica: Execute o frontend Next.js em outro terminal:")
        print("   cd ia-tributaria-frontend && npm run dev")
        print("=" * 50)
        
        # Iniciar servidor
        run_server(host=host, port=port, reload=reload)
        
    except ImportError as e:
        print(f"❌ Erro ao importar módulos web: {e}")
        print("Verifique se FastAPI e Uvicorn estão instalados")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n👋 Servidor web encerrado pelo usuário")
    except Exception as e:
        print(f"❌ Erro crítico no servidor web: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()