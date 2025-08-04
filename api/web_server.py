"""
Servidor web FastAPI para integração com frontend Next.js.
Expõe endpoints REST para consultas tributárias.
"""

import os
import sys
from pathlib import Path
from typing import List, Optional
from datetime import datetime

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse
    from pydantic import BaseModel, Field
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    print("⚠️ FastAPI não disponível. Execute: pip install fastapi uvicorn")

# Adicionar root do projeto ao path
sys.path.append(str(Path(__file__).parent.parent))

try:
    from core.knowledge_base import TaxKnowledgeBase
    from models.query import TaxQuery, QueryType
    BACKEND_AVAILABLE = True
except ImportError as e:
    BACKEND_AVAILABLE = False
    print(f"⚠️ Backend não disponível: {e}")


# Modelos da API
class QueryRequest(BaseModel):
    """Request para consulta tributária."""
    question: str = Field(..., min_length=5, description="Pergunta do usuário")
    countries: List[str] = Field(default_factory=list, description="Países de interesse")
    max_results: int = Field(10, ge=1, le=50, description="Máximo de resultados")
    min_confidence: float = Field(0.7, ge=0.0, le=1.0, description="Confiança mínima")


class SourceResponse(BaseModel):
    """Fonte citada na resposta."""
    document_title: str
    page_number: Optional[int] = None
    section: Optional[str] = None
    confidence: float
    relevant_text: str


class QueryResponse(BaseModel):
    """Resposta da consulta tributária."""
    answer: str
    confidence_score: float
    sources: List[SourceResponse]
    search_results_count: int
    processing_time_ms: int
    related_topics: List[str] = Field(default_factory=list)
    suggested_countries: List[str] = Field(default_factory=list)


class SystemStatus(BaseModel):
    """Status do sistema."""
    status: str
    backend_available: bool
    knowledge_base_ready: bool
    total_chunks: int
    unique_documents: int
    countries_covered: int
    topics_covered: int
    last_updated: str


# Inicializar FastAPI
if FASTAPI_AVAILABLE:
    app = FastAPI(
        title="IA Tributária Internacional API",
        description="API REST para consultas tributárias internacionais com RAG",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )

    # CORS para Next.js frontend
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",  # Next.js dev
            "http://localhost:3001",
            "https://ia-tributaria.vercel.app",  # Deploy Vercel
            "https://*.vercel.app",
        ],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["*"],
    )

    # Inicializar base de conhecimento globalmente
    knowledge_base = None
    if BACKEND_AVAILABLE:
        try:
            print("🚀 Inicializando base de conhecimento...")
            knowledge_base = TaxKnowledgeBase()
            print("✅ Base de conhecimento inicializada")
        except Exception as e:
            print(f"❌ Erro ao inicializar base: {e}")
            knowledge_base = None


    @app.get("/", response_model=dict)
    async def root():
        """Endpoint raiz com informações da API."""
        return {
            "message": "IA Tributária Internacional API",
            "version": "1.0.0",
            "docs": "/docs",
            "health": "/health",
            "status": "/status"
        }


    @app.get("/health", response_model=dict)
    async def health_check():
        """Health check para monitoring."""
        return {
            "status": "healthy" if knowledge_base else "degraded",
            "timestamp": datetime.now().isoformat(),
            "backend_available": BACKEND_AVAILABLE,
            "knowledge_base_ready": knowledge_base is not None
        }


    @app.get("/status", response_model=SystemStatus)
    async def get_system_status():
        """Status detalhado do sistema."""
        if not knowledge_base:
            return SystemStatus(
                status="error",
                backend_available=BACKEND_AVAILABLE,
                knowledge_base_ready=False,
                total_chunks=0,
                unique_documents=0,
                countries_covered=0,
                topics_covered=0,
                last_updated=datetime.now().isoformat()
            )

        try:
            system_stats = knowledge_base.get_system_status()
            vs_stats = system_stats.get("vector_store", {})
            doc_stats = system_stats.get("documents", {})

            return SystemStatus(
                status="healthy" if system_stats.get("system_ready") else "warning",
                backend_available=BACKEND_AVAILABLE,
                knowledge_base_ready=system_stats.get("system_ready", False),
                total_chunks=vs_stats.get("total_chunks", 0),
                unique_documents=vs_stats.get("unique_documents", 0),
                countries_covered=doc_stats.get("countries_covered", 0),
                topics_covered=doc_stats.get("topics_covered", 0),
                last_updated=system_stats.get("last_updated", datetime.now().isoformat())
            )

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro ao obter status: {str(e)}")


    @app.post("/query", response_model=QueryResponse)
    async def process_query(request: QueryRequest):
        """Processar consulta tributária."""
        if not knowledge_base:
            raise HTTPException(
                status_code=503, 
                detail="Base de conhecimento não disponível. Verifique se o sistema foi configurado."
            )

        try:
            start_time = datetime.now()

            # Processar consulta
            response = knowledge_base.query(
                question=request.question,
                countries=request.countries,
                max_results=request.max_results,
                min_confidence=request.min_confidence
            )

            processing_time = int((datetime.now() - start_time).total_seconds() * 1000)

            # Converter fontes
            sources = []
            for source in response.sources:
                sources.append(SourceResponse(
                    document_title=source.document_title,
                    page_number=source.page_number,
                    section=source.section,
                    confidence=source.confidence,
                    relevant_text=source.relevant_text
                ))

            return QueryResponse(
                answer=response.answer,
                confidence_score=response.confidence_score,
                sources=sources,
                search_results_count=response.search_results_count,
                processing_time_ms=processing_time,
                related_topics=response.related_topics,
                suggested_countries=response.suggested_countries
            )

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao processar consulta: {str(e)}"
            )


    @app.get("/countries", response_model=List[str])
    async def list_countries():
        """Lista países disponíveis na base de conhecimento."""
        if not knowledge_base:
            raise HTTPException(status_code=503, detail="Base de conhecimento não disponível")

        try:
            countries = knowledge_base.list_countries()
            return countries
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro ao listar países: {str(e)}")


    @app.get("/topics", response_model=List[str])
    async def list_topics():
        """Lista tópicos disponíveis na base de conhecimento."""
        if not knowledge_base:
            raise HTTPException(status_code=503, detail="Base de conhecimento não disponível")

        try:
            topics = knowledge_base.list_topics()
            return topics
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro ao listar tópicos: {str(e)}")


    @app.post("/setup", response_model=dict)
    async def setup_system():
        """Configura o sistema processando documentos."""
        global knowledge_base

        if not BACKEND_AVAILABLE:
            raise HTTPException(status_code=503, detail="Backend não disponível")

        try:
            if not knowledge_base:
                knowledge_base = TaxKnowledgeBase()

            setup_report = knowledge_base.setup(process_documents=True)

            return {
                "message": "Sistema configurado com sucesso" if setup_report.get("ready_for_queries") else "Sistema configurado com limitações",
                "report": setup_report
            }

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro na configuração: {str(e)}")


def create_app():
    """Factory function para criar app FastAPI."""
    if not FASTAPI_AVAILABLE:
        raise RuntimeError("FastAPI não disponível. Execute: pip install fastapi uvicorn")

    return app


def run_server(host: str = "0.0.0.0", port: int = 8000, reload: bool = True):
    """Executa o servidor web."""
    if not FASTAPI_AVAILABLE:
        print("❌ FastAPI não disponível. Execute: pip install fastapi uvicorn")
        return

    try:
        import uvicorn
        print(f"🚀 Iniciando servidor web em http://{host}:{port}")
        print(f"📖 Documentação: http://{host}:{port}/docs")
        
        uvicorn.run(
            "api.web_server:app",
            host=host,
            port=port,
            reload=reload,
            log_level="info"
        )
    except ImportError:
        print("❌ Uvicorn não disponível. Execute: pip install uvicorn")
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")


if __name__ == "__main__":
    # Executar servidor diretamente
    run_server()
else:
    # Para uso com uvicorn command line
    if FASTAPI_AVAILABLE:
        # Garantir que app está disponível para import
        pass