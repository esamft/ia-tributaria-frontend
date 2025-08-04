"""
Sistema de armazenamento vetorial com ChromaDB.
Otimizado para consultas tributárias com metadados estruturados.
"""

import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import json

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from ..models.chunk import Chunk
from ..models.query import TaxQuery


class TaxVectorStore:
    """Armazenamento vetorial especializado para tributação internacional."""
    
    def __init__(self, 
                 db_path: str = "./data/chroma_db",
                 collection_name: str = "tax_knowledge",
                 embedding_model: str = "text-embedding-3-small"):
        """
        Inicializa o store vetorial.
        
        Args:
            db_path: Caminho para o banco ChromaDB
            collection_name: Nome da coleção
            embedding_model: Modelo de embeddings OpenAI
        """
        if not CHROMADB_AVAILABLE:
            raise ImportError("ChromaDB não instalado. Execute: pip install chromadb")
        
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI não instalado. Execute: pip install openai")
        
        self.db_path = Path(db_path)
        self.collection_name = collection_name
        self.embedding_model = embedding_model
        
        # Configurar OpenAI
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY não configurada no .env")
        
        self.openai_client = openai.OpenAI()
        
        # Inicializar ChromaDB
        self._initialize_chromadb()
    
    def _initialize_chromadb(self):
        """Inicializa o cliente ChromaDB e coleção."""
        # Criar diretório se não existir
        self.db_path.mkdir(parents=True, exist_ok=True)
        
        # Configurar ChromaDB para persistência
        self.client = chromadb.PersistentClient(
            path=str(self.db_path),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Obter ou criar coleção
        try:
            self.collection = self.client.get_collection(
                name=self.collection_name
            )
            print(f"✅ Coleção '{self.collection_name}' carregada")
        except:
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={
                    "description": "Base de conhecimento tributário internacional",
                    "embedding_model": self.embedding_model,
                    "created_at": datetime.now().isoformat()
                }
            )
            print(f"✅ Coleção '{self.collection_name}' criada")
    
    def add_chunks(self, chunks: List[Chunk]) -> bool:
        """
        Adiciona chunks à base vetorial.
        
        Args:
            chunks: Lista de chunks para adicionar
            
        Returns:
            bool: Sucesso da operação
        """
        if not chunks:
            return True
        
        try:
            # Preparar dados para ChromaDB
            ids = []
            documents = []
            metadatas = []
            embeddings = []
            
            for chunk in chunks:
                # Gerar embedding
                embedding = self._generate_embedding(chunk.text)
                
                # Preparar metadados para ChromaDB
                metadata = {
                    "document_id": chunk.metadata.document_id,
                    "page_number": chunk.metadata.page_number or 0,
                    "section": chunk.metadata.section or "",
                    "countries": ",".join(chunk.metadata.detected_countries),
                    "topics": ",".join(chunk.metadata.detected_topics),
                    "has_numbers": chunk.metadata.has_numbers,
                    "has_dates": chunk.metadata.has_dates,
                    "has_legal_refs": chunk.metadata.has_legal_refs,
                    "text_quality": chunk.metadata.text_quality,
                    "information_density": chunk.metadata.information_density,
                    "created_at": chunk.created_at.isoformat(),
                    "char_length": len(chunk.text)
                }
                
                ids.append(chunk.id)
                documents.append(chunk.text)
                metadatas.append(metadata)
                embeddings.append(embedding)
            
            # Adicionar à coleção
            self.collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas,
                embeddings=embeddings
            )
            
            print(f"✅ {len(chunks)} chunks adicionados à base vetorial")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao adicionar chunks: {str(e)}")
            return False
    
    def search(self, 
               query: TaxQuery, 
               n_results: int = 10) -> List[Dict[str, Any]]:
        """
        Busca chunks relevantes para uma query.
        
        Args:
            query: Query estruturada
            n_results: Número máximo de resultados
            
        Returns:
            List[Dict]: Chunks encontrados com scores
        """
        try:
            # Gerar embedding da query
            query_embedding = self._generate_embedding(query.question)
            
            # Preparar filtros de metadados
            where_filters = self._build_metadata_filters(query)
            
            # Executar busca
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=min(n_results, 50),  # Máximo 50 resultados
                where=where_filters if where_filters else None,
                include=["documents", "metadatas", "distances"]
            )
            
            # Processar resultados
            processed_results = []
            
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    metadata = results['metadatas'][0][i]
                    distance = results['distances'][0][i]
                    
                    # Converter distância em score de similaridade (0-1)
                    similarity_score = max(0, 1 - distance)
                    
                    # Aplicar boost baseado em filtros da query
                    boost_score = self._calculate_relevance_boost(metadata, query)
                    final_score = min(1.0, similarity_score + boost_score)
                    
                    processed_results.append({
                        "text": doc,
                        "metadata": metadata,
                        "similarity_score": similarity_score,
                        "relevance_score": final_score,
                        "distance": distance
                    })
            
            # Ordenar por relevância final
            processed_results.sort(key=lambda x: x["relevance_score"], reverse=True)
            
            return processed_results
            
        except Exception as e:
            print(f"❌ Erro na busca: {str(e)}")
            return []
    
    def _generate_embedding(self, text: str) -> List[float]:
        """Gera embedding usando OpenAI."""
        try:
            response = self.openai_client.embeddings.create(
                input=text,
                model=self.embedding_model
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"❌ Erro ao gerar embedding: {str(e)}")
            # Retornar embedding dummy em caso de erro
            return [0.0] * 1536  # text-embedding-3-small tem 1536 dimensões
    
    def _build_metadata_filters(self, query: TaxQuery) -> Optional[Dict[str, Any]]:
        """Constrói filtros de metadados baseados na query."""
        filters = {}
        
        # Filtro por países
        if query.target_countries:
            country_conditions = []
            for country in query.target_countries:
                country_conditions.append({
                    "countries": {"$contains": country}
                })
            if len(country_conditions) == 1:
                filters.update(country_conditions[0])
            else:
                filters["$or"] = country_conditions
        
        # Filtro por qualidade mínima
        if query.min_confidence > 0:
            filters["text_quality"] = {"$gte": query.min_confidence}
        
        # Filtro por densidade de informação
        filters["information_density"] = {"$gte": 0.3}
        
        return filters if filters else None
    
    def _calculate_relevance_boost(self, metadata: Dict[str, Any], query: TaxQuery) -> float:
        """Calcula boost de relevância baseado em correspondências."""
        boost = 0.0
        
        # Boost por países correspondentes
        if query.target_countries:
            chunk_countries = metadata.get("countries", "").split(",")
            matching_countries = set(query.target_countries) & set(chunk_countries)
            if matching_countries:
                boost += 0.2 * (len(matching_countries) / len(query.target_countries))
        
        # Boost por características especiais
        if metadata.get("has_numbers") and any(char.isdigit() for char in query.question):
            boost += 0.1
        
        if metadata.get("has_legal_refs") and any(term in query.question.lower() 
                                                 for term in ["lei", "artigo", "decreto"]):
            boost += 0.1
        
        # Boost por qualidade alta
        if metadata.get("text_quality", 0) > 0.8:
            boost += 0.05
        
        return boost
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas da coleção."""
        try:
            count = self.collection.count()
            
            # Buscar alguns metadados para estatísticas
            sample = self.collection.get(limit=min(100, count))
            
            countries = set()
            topics = set()
            documents = set()
            
            if sample['metadatas']:
                for metadata in sample['metadatas']:
                    if metadata.get('countries'):
                        countries.update(metadata['countries'].split(','))
                    if metadata.get('topics'):
                        topics.update(metadata['topics'].split(','))
                    if metadata.get('document_id'):
                        documents.add(metadata['document_id'])
            
            return {
                "total_chunks": count,
                "unique_documents": len(documents),
                "countries_covered": len([c for c in countries if c.strip()]),
                "topics_covered": len([t for t in topics if t.strip()]),
                "collection_name": self.collection_name,
                "embedding_model": self.embedding_model,
                "db_path": str(self.db_path)
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def delete_document(self, document_id: str) -> bool:
        """Remove todos os chunks de um documento."""
        try:
            # Buscar chunks do documento
            results = self.collection.get(
                where={"document_id": document_id}
            )
            
            if results['ids']:
                self.collection.delete(ids=results['ids'])
                print(f"✅ {len(results['ids'])} chunks do documento '{document_id}' removidos")
                return True
            else:
                print(f"⚠️ Nenhum chunk encontrado para documento '{document_id}'")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao deletar documento: {str(e)}")
            return False
    
    def reset_collection(self) -> bool:
        """Reseta a coleção (apaga todos os dados)."""
        try:
            self.client.delete_collection(self.collection_name)
            self._initialize_chromadb()
            print("✅ Coleção resetada com sucesso")
            return True
        except Exception as e:
            print(f"❌ Erro ao resetar coleção: {str(e)}")
            return False
    
    def backup_collection(self, backup_path: str) -> bool:
        """Faz backup da coleção."""
        try:
            backup_dir = Path(backup_path)
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Exportar todos os dados
            all_data = self.collection.get()
            
            backup_file = backup_dir / f"tax_knowledge_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "collection_name": self.collection_name,
                    "embedding_model": self.embedding_model,
                    "backup_date": datetime.now().isoformat(),
                    "data": all_data
                }, f, ensure_ascii=False, indent=2)
            
            print(f"✅ Backup salvo em: {backup_file}")
            return True
            
        except Exception as e:
            print(f"❌ Erro no backup: {str(e)}")
            return False