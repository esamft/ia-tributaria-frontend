#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integra documentos processados do RAG Tributária ao ChromaDB
"""

import os
import json
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any
import hashlib
from datetime import datetime

def generate_chunk_id(content: str, metadata: Dict[str, Any], chunk_index: int) -> str:
    """Gera um ID único para o chunk baseado no conteúdo, metadados e índice"""
    source_string = f"{metadata.get('filename', '')}{chunk_index}{content[:100]}"
    return hashlib.md5(source_string.encode()).hexdigest()

def load_processed_documents(processed_dir: str) -> List[Dict[str, Any]]:
    """Carrega documentos processados do diretório"""
    documents = []
    
    if not os.path.exists(processed_dir):
        print(f"❌ Diretório não encontrado: {processed_dir}")
        return documents
    
    # Carrega índice
    index_path = os.path.join(processed_dir, "index.json")
    if not os.path.exists(index_path):
        print(f"❌ Arquivo de índice não encontrado: {index_path}")
        return documents
    
    with open(index_path, 'r', encoding='utf-8') as f:
        index = json.load(f)
    
    print(f"📋 Carregando {index['total_documents']} documentos processados...")
    
    for doc_info in index['documents']:
        processed_file = os.path.join(processed_dir, doc_info['processed_filename'])
        
        if os.path.exists(processed_file):
            with open(processed_file, 'r', encoding='utf-8') as f:
                doc_data = json.load(f)
                documents.append(doc_data)
                print(f"✅ Carregado: {doc_info['filename']} ({doc_info['chunks']} chunks)")
        else:
            print(f"⚠️  Arquivo não encontrado: {processed_file}")
    
    return documents

def setup_chromadb(persist_dir: str = None) -> chromadb.Collection:
    """Configura e retorna a coleção ChromaDB"""
    
    if not persist_dir:
        persist_dir = "/Users/esausamuellimafeitosa/meus-projetos-claude/projetos-python/sistema-agentes-tributarios/data/chromadb"
    
    # Cria diretório se não existir
    os.makedirs(persist_dir, exist_ok=True)
    
    print(f"🔧 Configurando ChromaDB em: {persist_dir}")
    
    # Configura cliente ChromaDB
    client = chromadb.PersistentClient(path=persist_dir)
    
    # Cria ou obtém coleção
    collection_name = "tributacao_internacional_rag"
    
    try:
        # Tenta obter coleção existente
        collection = client.get_collection(collection_name)
        print(f"📚 Coleção existente encontrada: {collection_name}")
    except:
        # Cria nova coleção
        collection = client.create_collection(
            name=collection_name,
            metadata={"description": "Base de conhecimento tributária com documentos RAG"}
        )
        print(f"🆕 Nova coleção criada: {collection_name}")
    
    return collection

def add_documents_to_chromadb(collection: chromadb.Collection, documents: List[Dict[str, Any]]) -> Dict[str, int]:
    """Adiciona documentos à coleção ChromaDB"""
    
    stats = {
        "total_chunks": 0,
        "added_chunks": 0,
        "skipped_chunks": 0,
        "error_chunks": 0
    }
    
    print("🔄 Integrando documentos ao ChromaDB...")
    print("=" * 50)
    
    for doc in documents:
        filename = doc['metadata']['filename']
        chunks = doc['chunks']
        metadata = doc['metadata']
        
        print(f"📄 Processando: {filename}")
        print(f"   📊 {len(chunks)} chunks para adicionar")
        
        # Prepara dados para o batch
        chunk_ids = []
        chunk_documents = []
        chunk_metadatas = []
        
        for i, chunk_content in enumerate(chunks):
            if not chunk_content.strip():
                continue
                
            # Gera ID único para o chunk
            chunk_id = generate_chunk_id(chunk_content, metadata, i)
            
            # Metadados do chunk
            chunk_metadata = {
                "source_document": filename,
                "chunk_index": i,
                "document_type": metadata.get("type", "tributario"),
                "topics": json.dumps(metadata.get("topics", [])),
                "country": metadata.get("country", "Brasil"),
                "language": metadata.get("language", "pt-BR"),
                "processed_date": metadata.get("processed_date"),
                "format": metadata.get("format", "TXT"),
                "content_size": len(chunk_content)
            }
            
            chunk_ids.append(chunk_id)
            chunk_documents.append(chunk_content)
            chunk_metadatas.append(chunk_metadata)
            
            stats["total_chunks"] += 1
        
        if chunk_ids:
            try:
                # Adiciona chunks em batch
                collection.add(
                    ids=chunk_ids,
                    documents=chunk_documents,
                    metadatas=chunk_metadatas
                )
                
                stats["added_chunks"] += len(chunk_ids)
                print(f"   ✅ {len(chunk_ids)} chunks adicionados com sucesso")
                
            except Exception as e:
                print(f"   ❌ Erro ao adicionar chunks: {e}")
                stats["error_chunks"] += len(chunk_ids)
        else:
            print(f"   ⚠️  Nenhum chunk válido encontrado")
        
        print()
    
    return stats

def integrate_rag_to_chromadb():
    """Função principal para integrar RAG ao ChromaDB"""
    
    print("🚀 INTEGRAÇÃO RAG TRIBUTÁRIA → ChromaDB")
    print("=" * 60)
    
    # Diretórios
    processed_dir = "/Users/esausamuellimafeitosa/meus-projetos-claude/projetos-python/sistema-agentes-tributarios/data/processed_rag"
    chromadb_dir = "/Users/esausamuellimafeitosa/meus-projetos-claude/projetos-python/sistema-agentes-tributarios/data/chromadb"
    
    try:
        # 1. Carrega documentos processados
        documents = load_processed_documents(processed_dir)
        
        if not documents:
            print("❌ Nenhum documento foi carregado. Verifique o processamento anterior.")
            return
        
        print(f"📚 {len(documents)} documentos carregados")
        print()
        
        # 2. Configura ChromaDB
        collection = setup_chromadb(chromadb_dir)
        print()
        
        # 3. Adiciona documentos
        stats = add_documents_to_chromadb(collection, documents)
        
        # 4. Mostra estatísticas finais
        print("=" * 60)
        print("🎉 INTEGRAÇÃO CONCLUÍDA!")
        print(f"📊 Estatísticas:")
        print(f"   • Total de chunks processados: {stats['total_chunks']}")
        print(f"   • Chunks adicionados: {stats['added_chunks']}")
        print(f"   • Chunks com erro: {stats['error_chunks']}")
        print(f"   • Taxa de sucesso: {(stats['added_chunks']/stats['total_chunks']*100):.1f}%")
        print()
        
        # 5. Verifica estado final da coleção
        total_items = collection.count()
        print(f"🗄️  Estado da base de conhecimento:")
        print(f"   • Total de chunks na base: {total_items}")
        print(f"   • Localização: {chromadb_dir}")
        print()
        
        # 6. Teste rápido de busca
        print("🔍 Teste rápido de busca:")
        try:
            results = collection.query(
                query_texts=["tributação internacional"],
                n_results=3
            )
            
            if results['documents'] and results['documents'][0]:
                print(f"   ✅ Busca funcionando - {len(results['documents'][0])} resultados encontrados")
                for i, doc in enumerate(results['documents'][0][:2]):
                    preview = doc[:100] + "..." if len(doc) > 100 else doc
                    print(f"   📄 {i+1}: {preview}")
            else:
                print("   ⚠️  Busca retornou resultados vazios")
                
        except Exception as e:
            print(f"   ❌ Erro no teste de busca: {e}")
        
        print()
        print("🚀 Próximos passos:")
        print("   1. Testar consultas no sistema de agentes")
        print("   2. Verificar qualidade das respostas")
        print("   3. Ajustar parâmetros se necessário")
        
    except KeyboardInterrupt:
        print("\n⚠️ Integração interrompida pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro durante integração: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    integrate_rag_to_chromadb()