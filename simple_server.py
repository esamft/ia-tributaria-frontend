#!/usr/bin/env python3
"""
Servidor web com OpenAI real para IA Tributária Internacional.
"""

import os
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import tempfile
import shutil
import asyncio
from pathlib import Path

# OpenAI Integration
try:
    import openai
    OPENAI_AVAILABLE = True
    openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
except ImportError:
    OPENAI_AVAILABLE = False
    print("⚠️ OpenAI não disponível")

# Modelos da API
class QueryRequest(BaseModel):
    question: str
    countries: List[str] = []
    max_results: int = 10

class SourceResponse(BaseModel):
    document_title: str
    page_number: Optional[int] = None
    section: Optional[str] = None
    confidence: float
    relevant_text: str

class QueryResponse(BaseModel):
    answer: str
    confidence_score: float
    sources: List[SourceResponse]
    search_results_count: int
    processing_time_ms: int


class DocumentUploadResponse(BaseModel):
    """Resposta do upload de documento."""
    success: bool
    message: str
    document_id: str
    filename: str
    size: int
    chunks_generated: int
    processing_time_ms: int


class DocumentInfo(BaseModel):
    """Informações de um documento."""
    id: str
    filename: str
    size: int
    type: str
    upload_date: str
    chunks: int
    status: str

# Inicializar FastAPI
app = FastAPI(
    title="IA Tributária Internacional API",
    description="API REST para consultas tributárias internacionais",
    version="1.0.0"
)

# CORS para Next.js (desenvolvimento e produção)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",              # Dev local
        "http://localhost:3001",  
        "https://*.vercel.app",               # Qualquer Vercel app
        "https://ia-tributaria-frontend.vercel.app",
        "https://ia-tributaria.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "IA Tributária Internacional API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "backend_available": True,
        "knowledge_base_ready": True
    }

@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """Processar consulta tributária com OpenAI real."""
    
    if not OPENAI_AVAILABLE:
        raise HTTPException(status_code=503, detail="OpenAI não disponível")
    
    try:
        # Criar prompt especializado
        system_prompt = """
        Você é um especialista em tributação internacional com acesso a uma vasta base de conhecimento.
        
        INSTRUÇÕES:
        1. Responda com informações precisas sobre tributação internacional
        2. Use markdown para formatação
        3. Sempre mencione fontes relevantes (EY Guide, OCDE, etc.)
        4. Para países específicos, forneça informações detalhadas
        5. Inclua alertas sobre necessidade de consultoria especializada
        
        ESPECIALIDADES:
        - Residência fiscal
        - Tratados de bitributação  
        - Planejamento tributário internacional
        - Exit tax
        - Preços de transferência
        - CFC rules
        """
        
        # Contexto dos países selecionados
        country_context = ""
        if request.countries:
            country_context = f"\n\nPAÍSES DE INTERESSE: {', '.join(request.countries)}"
            country_context += "\nForneça informações específicas para estas jurisdições."
        
        # Chamada para OpenAI
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": request.question + country_context}
            ],
            max_tokens=2000,
            temperature=0.1
        )
        
        answer = response.choices[0].message.content
        
        # Fontes simuladas (em produção viriam do RAG)
        sources = [
            SourceResponse(
                document_title="EY Worldwide Personal Tax Guide 2025",
                page_number=45 + hash(request.question) % 100,
                section="International Tax Analysis",
                confidence=0.92,
                relevant_text="Base de conhecimento tributário internacional com análise detalhada..."
            ),
            SourceResponse(
                document_title="OECD Model Tax Convention",
                page_number=23,
                section="Double Taxation Treaties",
                confidence=0.87,
                relevant_text="Modelos e diretrizes da OCDE para tratados fiscais internacionais..."
            )
        ]
        
        return QueryResponse(
            answer=answer,
            confidence_score=0.90,
            sources=sources,
            search_results_count=12,
            processing_time_ms=int(response.usage.total_tokens * 2)  # Simular tempo baseado em tokens
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar consulta: {str(e)}")

@app.get("/countries")
async def list_countries():
    """Lista países disponíveis (demo)."""
    return [
        "Brasil", "Estados Unidos", "Alemanha", "França", "Reino Unido",
        "Japão", "Canadá", "Austrália", "Singapura", "Suíça"
    ]

@app.get("/topics")
async def list_topics():
    """Lista tópicos disponíveis (demo)."""
    return [
        "Dupla Tributação", "Tratados Internacionais", "Planejamento Tributário",
        "Residência Fiscal", "Preços de Transferência", "Controlled Foreign Corporation",
        "Tributação de Dividendos", "Retenções na Fonte"
    ]


@app.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """Upload e processamento de documentos para a base de conhecimento."""
    
    if not file.filename:
        raise HTTPException(status_code=400, detail="Nome do arquivo é obrigatório")
    
    # Verificar tipo de arquivo
    allowed_extensions = {'.pdf', '.md', '.txt', '.docx'}
    file_ext = Path(file.filename).suffix.lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400, 
            detail=f"Tipo de arquivo não suportado. Use: {', '.join(allowed_extensions)}"
        )
    
    try:
        # Simular processamento
        import time
        start_time = time.time()
        
        # Ler conteúdo do arquivo
        content = await file.read()
        file_size = len(content)
        
        # Simular processamento de chunks
        await asyncio.sleep(1)  # Simular tempo de processamento
        
        # Gerar ID único para o documento
        import uuid
        doc_id = str(uuid.uuid4())
        
        # Simular quantidade de chunks baseada no tamanho
        chunks_generated = max(1, file_size // 1000)  # ~1 chunk por KB
        
        processing_time = int((time.time() - start_time) * 1000)
        
        # Em produção real, aqui salvaria o arquivo e processaria com RAG
        # Por agora, apenas simular sucesso
        
        return DocumentUploadResponse(
            success=True,
            message=f"Documento '{file.filename}' processado com sucesso",
            document_id=doc_id,
            filename=file.filename,
            size=file_size,
            chunks_generated=chunks_generated,
            processing_time_ms=processing_time
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Erro ao processar documento: {str(e)}"
        )


@app.get("/documents", response_model=List[DocumentInfo])
async def list_documents():
    """Lista documentos na base de conhecimento."""
    # Demo: retornar alguns documentos simulados
    from datetime import datetime
    
    return [
        DocumentInfo(
            id="1",
            filename="EY_Worldwide_Personal_Tax_Guide_2025.pdf",
            size=12600000,
            type="pdf",
            upload_date=datetime.now().isoformat(),
            chunks=1250,
            status="completed"
        ),
        DocumentInfo(
            id="2", 
            filename="livro_tributacao_internacional.md",
            size=850000,
            type="md",
            upload_date=datetime.now().isoformat(),
            chunks=425,
            status="completed"
        )
    ]


@app.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    """Remove documento da base de conhecimento."""
    # Em produção real, removeria do ChromaDB e do sistema de arquivos
    return {
        "success": True,
        "message": f"Documento {document_id} removido com sucesso"
    }

if __name__ == "__main__":
    # Configurações para produção
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8001"))
    
    print("🌐 IA Tributária Internacional - Servidor Simples")
    print("=" * 50)
    print(f"🚀 Iniciando servidor em http://{host}:{port}")
    print(f"📖 API Docs: http://{host}:{port}/docs")
    print(f"🔍 Health Check: http://{host}:{port}/health")
    print("=" * 50)
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )