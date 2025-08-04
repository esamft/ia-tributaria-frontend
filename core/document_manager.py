"""
Gerenciador de documentos para o sistema tributário.
Processa PDFs e Markdowns, gera chunks e alimenta vector store.
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from ..models.document import Document
from ..models.chunk import Chunk
from ..tools.pdf_processor import PDFProcessor
from ..tools.markdown_processor import MarkdownProcessor
from ..tools.chunking_tools import ChunkingTools
from .vector_store import TaxVectorStore


class DocumentManager:
    """Gerenciador central de documentos da base tributária."""
    
    def __init__(self, 
                 data_path: str = "./data",
                 vector_store: Optional[TaxVectorStore] = None):
        """
        Inicializa o gerenciador de documentos.
        
        Args:
            data_path: Caminho para dados
            vector_store: Store vetorial (opcional)
        """
        self.data_path = Path(data_path)
        self.processed_docs_file = self.data_path / "processed_documents.json"
        
        # Inicializar processadores
        self.pdf_processor = PDFProcessor()
        self.markdown_processor = MarkdownProcessor()
        self.chunking_tools = ChunkingTools()
        
        # Vector store
        self.vector_store = vector_store or TaxVectorStore()
        
        # Carregar registro de documentos processados
        self.processed_docs = self._load_processed_docs()
    
    def process_all_documents(self) -> Dict[str, Any]:
        """
        Processa todos os documentos na pasta data.
        
        Returns:
            Dict: Relatório do processamento
        """
        report = {
            "started_at": datetime.now().isoformat(),
            "documents_found": 0,
            "documents_processed": 0,
            "documents_skipped": 0,
            "total_chunks": 0,
            "errors": [],
            "processed_files": []
        }
        
        print("🚀 Iniciando processamento de documentos...")
        
        # Encontrar arquivos para processar
        pdf_files = list(self.data_path.glob("*.pdf"))
        md_files = list(self.data_path.glob("*.md"))
        
        all_files = pdf_files + md_files
        report["documents_found"] = len(all_files)
        
        if not all_files:
            print("⚠️ Nenhum documento encontrado para processar")
            return report
        
        # Processar cada arquivo
        for file_path in all_files:
            try:
                result = self.process_single_document(file_path)
                
                if result["success"]:
                    report["documents_processed"] += 1
                    report["total_chunks"] += result["chunks_count"]
                    report["processed_files"].append({
                        "file": str(file_path),
                        "type": result["document_type"],
                        "chunks": result["chunks_count"],
                        "processing_time": result["processing_time"]
                    })
                    print(f"✅ {file_path.name}: {result['chunks_count']} chunks")\n                else:
                    report["documents_skipped"] += 1
                    if result.get("error"):
                        report["errors"].append({
                            "file": str(file_path),
                            "error": result["error"]
                        })
                    print(f"⏭️ {file_path.name}: {result.get('reason', 'Pulado')}")
                    
            except Exception as e:
                report["errors"].append({
                    "file": str(file_path),
                    "error": str(e)
                })
                print(f"❌ Erro processando {file_path.name}: {str(e)}")
        
        # Salvar registro atualizado
        self._save_processed_docs()
        
        report["completed_at"] = datetime.now().isoformat()
        
        # Exibir relatório final
        self._print_processing_report(report)
        
        return report
    
    def process_single_document(self, file_path: Path) -> Dict[str, Any]:
        """
        Processa um único documento.
        
        Args:
            file_path: Caminho do arquivo
            
        Returns:
            Dict: Resultado do processamento
        """
        start_time = datetime.now()
        
        # Verificar se já foi processado
        file_key = str(file_path.name)
        if file_key in self.processed_docs:
            return {
                "success": False,
                "reason": "Já processado anteriormente",
                "processed_at": self.processed_docs[file_key]["processed_at"]
            }
        
        try:
            # Detectar tipo e processar
            if file_path.suffix.lower() == '.pdf':
                document = self.pdf_processor.process_pdf(file_path)
            elif file_path.suffix.lower() == '.md':
                document = self.markdown_processor.process_markdown(file_path)
            else:
                return {
                    "success": False,
                    "error": f"Tipo de arquivo não suportado: {file_path.suffix}"
                }
            
            # Gerar chunks
            chunks = self.chunking_tools.create_chunks(document)
            
            # Otimizar chunks
            optimized_chunks = self.chunking_tools.optimize_chunks(chunks)
            merged_chunks = self.chunking_tools.merge_small_chunks(optimized_chunks)
            
            # Adicionar ao vector store
            success = self.vector_store.add_chunks(merged_chunks)
            
            if success:
                # Registrar como processado
                self.processed_docs[file_key] = {
                    "document_id": document.id,
                    "file_path": str(file_path),
                    "document_type": document.metadata.document_type.value,
                    "source_type": document.metadata.source_type.value,
                    "chunks_count": len(merged_chunks),
                    "processed_at": datetime.now().isoformat(),
                    "file_size_mb": document.metadata.file_size_mb,
                    "countries": document.metadata.countries,
                    "topics": document.metadata.topics
                }
                
                # Atualizar documento com info dos chunks
                document.chunks_count = len(merged_chunks)
                document.embedded = True
                
                processing_time = (datetime.now() - start_time).total_seconds()
                
                return {
                    "success": True,
                    "document_id": document.id,
                    "document_type": document.metadata.document_type.value,
                    "chunks_count": len(merged_chunks),
                    "processing_time": f"{processing_time:.2f}s"
                }
            else:
                return {
                    "success": False,
                    "error": "Falha ao adicionar chunks ao vector store"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def reprocess_document(self, file_path: Path) -> Dict[str, Any]:
        """
        Reprocessa um documento (remove e processa novamente).
        
        Args:
            file_path: Caminho do arquivo
            
        Returns:
            Dict: Resultado do reprocessamento
        """
        file_key = str(file_path.name)
        
        # Remover do vector store se existir
        if file_key in self.processed_docs:
            document_id = self.processed_docs[file_key]["document_id"]
            self.vector_store.delete_document(document_id)
            del self.processed_docs[file_key]
            print(f"🗑️ Documento {file_key} removido para reprocessamento")
        
        # Processar novamente
        return self.process_single_document(file_path)
    
    def get_processing_status(self) -> Dict[str, Any]:
        """Retorna status do processamento de documentos."""
        
        # Contar arquivos disponíveis
        pdf_files = list(self.data_path.glob("*.pdf"))
        md_files = list(self.data_path.glob("*.md"))
        total_available = len(pdf_files) + len(md_files)
        
        # Estatísticas dos processados
        processed_count = len(self.processed_docs)
        total_chunks = sum(doc.get("chunks_count", 0) for doc in self.processed_docs.values())
        
        # Agrupar por tipo
        by_type = {}
        for doc_info in self.processed_docs.values():
            doc_type = doc_info.get("document_type", "unknown")
            if doc_type not in by_type:
                by_type[doc_type] = {"count": 0, "chunks": 0}
            by_type[doc_type]["count"] += 1
            by_type[doc_type]["chunks"] += doc_info.get("chunks_count", 0)
        
        # Países cobertos
        all_countries = set()
        for doc_info in self.processed_docs.values():
            all_countries.update(doc_info.get("countries", []))
        
        # Tópicos cobertos
        all_topics = set()
        for doc_info in self.processed_docs.values():
            all_topics.update(doc_info.get("topics", []))
        
        return {
            "files_available": total_available,
            "files_processed": processed_count,
            "files_pending": total_available - processed_count,
            "total_chunks": total_chunks,
            "by_document_type": by_type,
            "countries_covered": len(all_countries),
            "topics_covered": len(all_topics),
            "countries_list": sorted(list(all_countries)),
            "topics_list": sorted(list(all_topics)),
            "vector_store_stats": self.vector_store.get_collection_stats()
        }
    
    def _load_processed_docs(self) -> Dict[str, Any]:
        """Carrega registro de documentos processados."""
        if self.processed_docs_file.exists():
            try:
                with open(self.processed_docs_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ Erro ao carregar registro de documentos: {e}")
        return {}
    
    def _save_processed_docs(self):
        """Salva registro de documentos processados."""
        try:
            with open(self.processed_docs_file, 'w', encoding='utf-8') as f:
                json.dump(self.processed_docs, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ Erro ao salvar registro de documentos: {e}")
    
    def _print_processing_report(self, report: Dict[str, Any]):
        """Exibe relatório de processamento formatado."""
        print("\n" + "="*60)
        print("📊 RELATÓRIO DE PROCESSAMENTO")
        print("="*60)
        print(f"📁 Documentos encontrados: {report['documents_found']}")
        print(f"✅ Documentos processados: {report['documents_processed']}")
        print(f"⏭️ Documentos pulados: {report['documents_skipped']}")
        print(f"🧩 Total de chunks: {report['total_chunks']}")
        
        if report['errors']:
            print(f"❌ Erros: {len(report['errors'])}")
            for error in report['errors']:
                print(f"   • {error['file']}: {error['error']}")
        
        if report['processed_files']:
            print("\n📋 ARQUIVOS PROCESSADOS:")
            for file_info in report['processed_files']:
                print(f"   • {Path(file_info['file']).name}")
                print(f"     Tipo: {file_info['type']}")
                print(f"     Chunks: {file_info['chunks']}")
                print(f"     Tempo: {file_info['processing_time']}")
        
        # Estatísticas do vector store
        vs_stats = self.vector_store.get_collection_stats()
        print(f"\n🗂️ VECTOR STORE:")
        print(f"   • Total chunks: {vs_stats.get('total_chunks', 0)}")
        print(f"   • Documentos únicos: {vs_stats.get('unique_documents', 0)}")
        print(f"   • Países cobertos: {vs_stats.get('countries_covered', 0)}")
        print(f"   • Tópicos cobertos: {vs_stats.get('topics_covered', 0)}")
        
        print("="*60)
    
    def list_available_documents(self) -> List[Dict[str, Any]]:
        """Lista documentos disponíveis para processamento."""
        documents = []
        
        pdf_files = list(self.data_path.glob("*.pdf"))
        md_files = list(self.data_path.glob("*.md"))
        
        for file_path in pdf_files + md_files:
            file_key = str(file_path.name)
            is_processed = file_key in self.processed_docs
            
            doc_info = {
                "name": file_path.name,
                "path": str(file_path),
                "type": file_path.suffix.lower(),
                "size_mb": round(file_path.stat().st_size / (1024 * 1024), 2),
                "is_processed": is_processed
            }
            
            if is_processed:
                processed_info = self.processed_docs[file_key]
                doc_info.update({
                    "document_id": processed_info.get("document_id"),
                    "chunks_count": processed_info.get("chunks_count"),
                    "processed_at": processed_info.get("processed_at"),
                    "countries": processed_info.get("countries", []),
                    "topics": processed_info.get("topics", [])
                })
            
            documents.append(doc_info)
        
        return sorted(documents, key=lambda x: x["name"])
    
    def remove_document(self, document_name: str) -> bool:
        """
        Remove documento do sistema (vector store + registro).
        
        Args:
            document_name: Nome do arquivo
            
        Returns:
            bool: Sucesso da operação
        """
        if document_name in self.processed_docs:
            try:
                document_id = self.processed_docs[document_name]["document_id"]
                
                # Remover do vector store
                if self.vector_store.delete_document(document_id):
                    # Remover do registro
                    del self.processed_docs[document_name]
                    self._save_processed_docs()
                    print(f"✅ Documento '{document_name}' removido com sucesso")
                    return True
                else:
                    print(f"❌ Erro ao remover '{document_name}' do vector store")
                    return False
                    
            except Exception as e:
                print(f"❌ Erro ao remover documento: {str(e)}")
                return False
        else:
            print(f"⚠️ Documento '{document_name}' não encontrado no registro")
            return False