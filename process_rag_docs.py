#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Processa documentos do RAG Tributária e integra à base de conhecimento
"""

import os
import json
import PyPDF2
import re
from datetime import datetime
from typing import List, Dict, Any

def read_pdf(file_path: str) -> str:
    """Lê conteúdo de um arquivo PDF"""
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        print(f"❌ Erro ao ler PDF {file_path}: {e}")
        return ""

def read_txt(file_path: str) -> str:
    """Lê conteúdo de um arquivo de texto"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            return file.read().strip()
    except Exception as e:
        print(f"❌ Erro ao ler TXT {file_path}: {e}")
        return ""

def extract_document_metadata(filename: str, content: str) -> Dict[str, Any]:
    """Extrai metadados do documento baseado no nome e conteúdo"""
    metadata = {
        "filename": filename,
        "type": "tributario",
        "source": "RAG Tributária",
        "processed_date": datetime.now().isoformat(),
        "topics": [],
        "country": "Brasil",
        "language": "pt-BR"
    }
    
    # Identifica tópicos principais baseado no nome do arquivo
    topics_map = {
        "fatca": ["FATCA", "Compliance", "Conformidade Fiscal"],
        "crs": ["CRS", "Common Reporting Standard", "Troca de Informações"],
        "14.754": ["Lei 14.754/2023", "CFC", "Controlled Foreign Company"],
        "beps": ["BEPS", "Base Erosion", "Profit Shifting"],
        "offshore": ["Offshore", "Planejamento Patrimonial", "Estruturas Internacionais"],
        "tributacao": ["Tributação Internacional", "Imposto de Renda", "Direito Tributário"]
    }
    
    filename_lower = filename.lower()
    for key, topics in topics_map.items():
        if key in filename_lower:
            metadata["topics"].extend(topics)
    
    # Se não encontrou tópicos específicos, usa genéricos
    if not metadata["topics"]:
        metadata["topics"] = ["Tributação Internacional", "Direito Tributário"]
    
    # Identifica se é PDF ou TXT
    metadata["format"] = "PDF" if filename.endswith('.pdf') else "TXT"
    
    # Estima tamanho do conteúdo
    metadata["content_size"] = len(content)
    metadata["estimated_pages"] = max(1, len(content) // 2000) if content else 1
    
    return metadata

def chunk_document(content: str, chunk_size: int = 1500, overlap: int = 200) -> List[str]:
    """Divide o documento em chunks para processamento RAG"""
    if not content or len(content) < chunk_size:
        return [content] if content else []
    
    chunks = []
    start = 0
    
    while start < len(content):
        end = start + chunk_size
        
        # Se não é o último chunk, tenta quebrar em uma frase completa
        if end < len(content):
            # Procura por quebras naturais (. ! ? \n)
            for i in range(end, max(start + chunk_size - 200, start), -1):
                if content[i] in '.!?\n':
                    end = i + 1
                    break
        
        chunk = content[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        start = end - overlap if end < len(content) else end
    
    return chunks

def process_rag_documents():
    """Processa todos os documentos do RAG Tributária"""
    
    docs_dir = "/Users/esausamuellimafeitosa/meus-projetos-claude/projetos-python/sistema-agentes-tributarios/data/rag_docs"
    output_dir = "/Users/esausamuellimafeitosa/meus-projetos-claude/projetos-python/sistema-agentes-tributarios/data/processed_rag"
    
    # Cria diretório de saída
    os.makedirs(output_dir, exist_ok=True)
    
    processed_documents = []
    total_chunks = 0
    
    print("🔄 Iniciando processamento dos documentos RAG Tributária...")
    print(f"📁 Origem: {docs_dir}")
    print(f"📁 Destino: {output_dir}")
    print("=" * 60)
    
    # Lista arquivos
    if not os.path.exists(docs_dir):
        print(f"❌ Diretório não encontrado: {docs_dir}")
        return
    
    files = [f for f in os.listdir(docs_dir) if f.endswith(('.pdf', '.txt'))]
    
    if not files:
        print("❌ Nenhum arquivo encontrado para processar")
        return
    
    print(f"📋 Encontrados {len(files)} arquivos para processar")
    print()
    
    for filename in files:
        file_path = os.path.join(docs_dir, filename)
        print(f"🔄 Processando: {filename}")
        
        # Lê conteúdo do arquivo
        if filename.endswith('.pdf'):
            content = read_pdf(file_path)
        else:
            content = read_txt(file_path)
        
        if not content:
            print(f"⚠️  Arquivo vazio ou não foi possível ler: {filename}")
            continue
        
        # Extrai metadados
        metadata = extract_document_metadata(filename, content)
        
        # Divide em chunks
        chunks = chunk_document(content)
        
        # Prepara documento processado
        processed_doc = {
            "metadata": metadata,
            "content": content,
            "chunks": chunks,
            "chunk_count": len(chunks)
        }
        
        # Salva documento processado
        output_filename = f"{os.path.splitext(filename)[0]}_processed.json"
        output_path = os.path.join(output_dir, output_filename)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(processed_doc, f, ensure_ascii=False, indent=2)
        
        processed_documents.append({
            "filename": filename,
            "processed_filename": output_filename,
            "chunks": len(chunks),
            "size": len(content),
            "topics": metadata["topics"]
        })
        
        total_chunks += len(chunks)
        
        print(f"✅ {filename}")
        print(f"   📄 {len(chunks)} chunks gerados")
        print(f"   📊 {len(content):,} caracteres")
        print(f"   🏷️  Tópicos: {', '.join(metadata['topics'][:3])}")
        print()
    
    # Cria índice geral
    index = {
        "processed_date": datetime.now().isoformat(),
        "total_documents": len(processed_documents),
        "total_chunks": total_chunks,
        "documents": processed_documents
    }
    
    index_path = os.path.join(output_dir, "index.json")
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
    
    print("=" * 60)
    print("🎉 PROCESSAMENTO CONCLUÍDO!")
    print(f"📈 Estatísticas:")
    print(f"   • {len(processed_documents)} documentos processados")
    print(f"   • {total_chunks} chunks gerados")
    print(f"   • Arquivos salvos em: {output_dir}")
    print(f"   • Índice criado: {index_path}")
    print()
    
    print("📋 Resumo por documento:")
    for doc in processed_documents:
        print(f"   • {doc['filename']}: {doc['chunks']} chunks, {doc['size']:,} chars")
    
    print()
    print("🚀 Próximos passos:")
    print("   1. Integrar chunks ao sistema ChromaDB")
    print("   2. Atualizar base de conhecimento do agente")
    print("   3. Testar consultas com os novos documentos")
    
    return processed_documents

if __name__ == "__main__":
    try:
        process_rag_documents()
    except KeyboardInterrupt:
        print("\n⚠️ Processamento interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro durante processamento: {e}")