"""
Base de conhecimento integrada do sistema tributário.
Orquestra processamento, armazenamento e consulta.
"""

from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

from .vector_store import TaxVectorStore
from .document_manager import DocumentManager
from ..agents.tax_consultant import TaxConsultantAgent
from ..models.query import TaxQuery, QueryResponse


class TaxKnowledgeBase:
    """
    Base de conhecimento integrada para tributação internacional.
    Ponto central de acesso ao sistema RAG.
    """
    
    def __init__(self, data_path: str = "./data"):
        """
        Inicializa a base de conhecimento.
        
        Args:
            data_path: Caminho para os dados
        """
        self.data_path = Path(data_path)
        
        # Inicializar componentes core
        print("🚀 Inicializando Base de Conhecimento Tributário...")
        
        # Vector Store
        self.vector_store = TaxVectorStore(
            db_path=str(self.data_path / "chroma_db")
        )
        
        # Document Manager
        self.document_manager = DocumentManager(
            data_path=str(self.data_path),
            vector_store=self.vector_store
        )
        
        # Agente Consultor
        self.tax_consultant = TaxConsultantAgent(
            vector_store=self.vector_store
        )
        
        print("✅ Base de conhecimento inicializada")
    
    def setup(self, process_documents: bool = True) -> Dict[str, Any]:
        """
        Configura a base de conhecimento processando documentos.
        
        Args:
            process_documents: Se deve processar documentos automaticamente
            
        Returns:
            Dict: Relatório da configuração
        """
        print("⚙️ Configurando base de conhecimento...")
        
        setup_report = {
            "started_at": datetime.now().isoformat(),
            "documents_processed": False,
            "processing_report": None,
            "final_stats": None,
            "ready_for_queries": False
        }
        
        try:
            if process_documents:
                # Processar todos os documentos
                processing_report = self.document_manager.process_all_documents()
                setup_report["documents_processed"] = True
                setup_report["processing_report"] = processing_report
            
            # Obter estatísticas finais
            final_stats = self.get_system_status()
            setup_report["final_stats"] = final_stats
            
            # Verificar se está pronto para consultas
            ready = final_stats["vector_store"]["total_chunks"] > 0
            setup_report["ready_for_queries"] = ready
            
            if ready:
                print("✅ Base de conhecimento configurada e pronta para consultas!")
            else:
                print("⚠️ Base de conhecimento configurada, mas sem dados para consulta")
            
            setup_report["completed_at"] = datetime.now().isoformat()
            return setup_report
            
        except Exception as e:
            setup_report["error"] = str(e)
            print(f"❌ Erro na configuração: {e}")
            return setup_report
    
    def query(self, 
              question: str,
              countries: List[str] = None,
              **kwargs) -> QueryResponse:
        """
        Realiza consulta na base de conhecimento.
        
        Args:
            question: Pergunta do usuário
            countries: Países específicos
            **kwargs: Parâmetros adicionais
            
        Returns:
            QueryResponse: Resposta estruturada
        """
        return self.tax_consultant.query(
            question=question,
            countries=countries or [],
            **kwargs
        )
    
    def quick_query(self, question: str) -> str:
        """
        Consulta rápida retornando apenas o texto da resposta.
        
        Args:
            question: Pergunta do usuário
            
        Returns:
            str: Resposta formatada
        """
        response = self.query(question)
        return response.format_for_cli()
    
    def add_documents(self, file_paths: List[str]) -> Dict[str, Any]:
        """
        Adiciona novos documentos à base.
        
        Args:
            file_paths: Lista de caminhos dos arquivos
            
        Returns:
            Dict: Relatório do processamento
        """
        report = {
            "processed": [],
            "failed": [],
            "total_new_chunks": 0
        }
        
        for file_path in file_paths:
            try:
                result = self.document_manager.process_single_document(Path(file_path))
                if result["success"]:
                    report["processed"].append({
                        "file": file_path,
                        "chunks": result["chunks_count"]
                    })
                    report["total_new_chunks"] += result["chunks_count"]
                else:
                    report["failed"].append({
                        "file": file_path,
                        "error": result.get("error", "Processo falhou")
                    })
            except Exception as e:
                report["failed"].append({
                    "file": file_path,
                    "error": str(e)
                })
        
        return report
    
    def remove_document(self, document_name: str) -> bool:
        """
        Remove documento da base.
        
        Args:
            document_name: Nome do documento
            
        Returns:
            bool: Sucesso da operação
        """
        return self.document_manager.remove_document(document_name)
    
    def reprocess_document(self, file_path: str) -> Dict[str, Any]:
        """
        Reprocessa um documento específico.
        
        Args:
            file_path: Caminho do arquivo
            
        Returns:
            Dict: Resultado do reprocessamento
        """
        return self.document_manager.reprocess_document(Path(file_path))
    
    def get_system_status(self) -> Dict[str, Any]:
        """Retorna status completo do sistema."""
        
        # Status do processamento de documentos
        doc_status = self.document_manager.get_processing_status()
        
        # Status do vector store
        vs_stats = self.vector_store.get_collection_stats()
        
        # Status do agente
        agent_status = self.tax_consultant.get_status()
        
        # Documentos disponíveis
        available_docs = self.document_manager.list_available_documents()
        
        return {
            "system_ready": vs_stats.get("total_chunks", 0) > 0,
            "documents": doc_status,
            "vector_store": vs_stats,
            "agent": agent_status,
            "available_documents": len(available_docs),
            "last_updated": datetime.now().isoformat()
        }
    
    def search_knowledge(self, 
                        query_text: str,
                        countries: List[str] = None,
                        max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Busca direta na base vetorial (sem agente).
        
        Args:
            query_text: Texto da busca
            countries: Filtro de países
            max_results: Máximo de resultados
            
        Returns:
            List[Dict]: Resultados da busca
        """
        query = TaxQuery(
            question=query_text,
            target_countries=countries or [],
            max_results=max_results
        )
        
        return self.vector_store.search(query, n_results=max_results)
    
    def get_document_info(self, document_name: str) -> Optional[Dict[str, Any]]:
        """
        Obtém informações de um documento específico.
        
        Args:
            document_name: Nome do documento
            
        Returns:
            Dict: Informações do documento ou None
        """
        available_docs = self.document_manager.list_available_documents()
        
        for doc in available_docs:
            if doc["name"] == document_name:
                return doc
        
        return None
    
    def list_countries(self) -> List[str]:
        """Lista países disponíveis na base."""
        status = self.get_system_status()
        return status["documents"].get("countries_list", [])
    
    def list_topics(self) -> List[str]:
        """Lista tópicos disponíveis na base.""" 
        status = self.get_system_status()
        return status["documents"].get("topics_list", [])
    
    def backup_system(self, backup_path: str = None) -> bool:
        """
        Faz backup completo do sistema.
        
        Args:
            backup_path: Caminho do backup (opcional)
            
        Returns:
            bool: Sucesso da operação
        """
        if not backup_path:
            backup_path = str(self.data_path / "backup")
        
        try:
            # Backup do vector store
            vs_backup = self.vector_store.backup_collection(backup_path)
            
            if vs_backup:
                print(f"✅ Backup do sistema salvo em: {backup_path}")
                return True
            else:
                print("❌ Falha no backup do sistema")
                return False
                
        except Exception as e:
            print(f"❌ Erro no backup: {str(e)}")
            return False
    
    def reset_system(self) -> bool:
        """
        Reseta completamente o sistema (apaga todos os dados).
        CUIDADO: Operação irreversível!
        
        Returns:
            bool: Sucesso da operação
        """
        try:
            # Reset do vector store
            vs_reset = self.vector_store.reset_collection()
            
            # Limpar registro de documentos processados
            if hasattr(self.document_manager, 'processed_docs'):
                self.document_manager.processed_docs = {}
                self.document_manager._save_processed_docs()
            
            if vs_reset:
                print("✅ Sistema resetado com sucesso")
                return True
            else:
                print("❌ Falha no reset do sistema")
                return False
                
        except Exception as e:
            print(f"❌ Erro no reset: {str(e)}")
            return False
    
    def health_check(self) -> Dict[str, Any]:
        """Verifica saúde do sistema."""
        health = {
            "status": "healthy",
            "issues": [],
            "recommendations": []
        }
        
        try:
            # Verificar vector store
            vs_stats = self.vector_store.get_collection_stats()
            if vs_stats.get("total_chunks", 0) == 0:
                health["issues"].append("Nenhum documento processado na base vetorial")
                health["recommendations"].append("Execute setup() para processar documentos")
                health["status"] = "warning"
            
            # Verificar documentos disponíveis
            available_docs = self.document_manager.list_available_documents()
            unprocessed = [doc for doc in available_docs if not doc["is_processed"]]
            
            if unprocessed:
                health["issues"].append(f"{len(unprocessed)} documentos não processados")
                health["recommendations"].append("Processe documentos pendentes")
            
            # Verificar agente
            agent_status = self.tax_consultant.get_status()
            if not agent_status.get("agno_enabled"):
                health["issues"].append("Agente Agno não disponível")
                health["recommendations"].append("Instale Agno para funcionalidade completa")
            
            # Determinar status final
            if health["issues"] and health["status"] != "warning":
                health["status"] = "degraded" if vs_stats.get("total_chunks", 0) > 0 else "critical"
                
        except Exception as e:
            health["status"] = "error"
            health["issues"].append(f"Erro na verificação: {str(e)}")
        
        return health