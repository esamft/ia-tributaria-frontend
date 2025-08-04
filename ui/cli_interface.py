"""
Interface Rich CLI para o Sistema de Agentes Tributários.
Interface elegante e profissional para consultas tributárias.
"""

import os
import sys
from typing import List, Dict, Any, Optional
from datetime import datetime

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.prompt import Prompt, Confirm
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.layout import Layout
    from rich.text import Text
    from rich.markdown import Markdown
    from rich.rule import Rule
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("⚠️ Rich não disponível. Interface simplificada.")

from ..core.knowledge_base import TaxKnowledgeBase
from ..models.query import QueryType


class TaxSystemCLI:
    """Interface CLI Rica para Sistema de Agentes Tributários."""
    
    def __init__(self, knowledge_base: Optional[TaxKnowledgeBase] = None):
        """
        Inicializa interface CLI.
        
        Args:
            knowledge_base: Base de conhecimento (opcional)
        """
        if not RICH_AVAILABLE:
            print("❌ Rich não instalado. Execute: pip install rich")
            sys.exit(1)
        
        self.console = Console()
        self.knowledge_base = knowledge_base or TaxKnowledgeBase()
        
        # Estado da sessão
        self.session_history = []
        self.current_countries = []
        self.system_ready = False
    
    def start(self):
        """Inicia a interface CLI."""
        self._show_welcome()
        
        # Verificar status do sistema
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("Verificando sistema...", total=None)
            
            health = self.knowledge_base.health_check()
            self.system_ready = health["status"] in ["healthy", "warning"]
            
            progress.update(task, description="Sistema verificado")
        
        self._show_system_status(health)
        
        if not self.system_ready:
            if Confirm.ask("Deseja configurar o sistema agora?", console=self.console):
                self._setup_system()
        
        # Loop principal
        self._main_loop()
    
    def _show_welcome(self):
        """Exibe tela de boas-vindas."""
        welcome_text = """
# 🤖 Sistema de Agentes Tributários

**Especialista em Tributação Internacional**
*Powered by Agno Framework • Base RAG com EY Guide*

---

### Capacidades:
• Consultas sobre tributação pessoal internacional
• Comparação entre jurisdições fiscais  
• Planejamento tributário estratégico
• Base de conhecimento atualizada (2024-2025)

### Fontes:
• EY Worldwide Personal Tax Guide 2025
• Livro "O Estrategista" (40 anos experiência)
• Relatórios de tendências atuais
"""
        
        self.console.print(Panel(
            Markdown(welcome_text),
            title="[bold blue]Bem-vindo[/bold blue]",
            border_style="blue"
        ))
    
    def _show_system_status(self, health: Dict[str, Any]):
        """Exibe status do sistema."""
        # Determinar cor baseada no status
        status_colors = {
            "healthy": "green",
            "warning": "yellow", 
            "degraded": "orange",
            "critical": "red",
            "error": "red"
        }
        
        status_color = status_colors.get(health["status"], "white")
        status_text = health["status"].upper()
        
        # Obter estatísticas
        system_stats = self.knowledge_base.get_system_status()
        
        # Criar tabela de status
        status_table = Table(title="Status do Sistema", show_header=True)
        status_table.add_column("Componente", style="cyan")
        status_table.add_column("Status", justify="center")
        status_table.add_column("Detalhes", style="dim")
        
        # Sistema geral
        status_table.add_row(
            "Sistema",
            f"[{status_color}]{status_text}[/{status_color}]",
            "✅ Operacional" if self.system_ready else "⚠️ Requer configuração"
        )
        
        # Vector Store
        vs_stats = system_stats.get("vector_store", {})
        chunks_count = vs_stats.get("total_chunks", 0)
        status_table.add_row(
            "Base Vetorial",
            "✅ OK" if chunks_count > 0 else "❌ Vazia",
            f"{chunks_count:,} chunks • {vs_stats.get('unique_documents', 0)} documentos"
        )
        
        # Documentos
        doc_stats = system_stats.get("documents", {})
        status_table.add_row(
            "Documentos",
            f"✅ {doc_stats.get('files_processed', 0)}/{doc_stats.get('files_available', 0)}",
            f"{doc_stats.get('countries_covered', 0)} países • {doc_stats.get('topics_covered', 0)} tópicos"
        )
        
        # Agente
        agent_stats = system_stats.get("agent", {})
        agno_status = "✅ Agno" if agent_stats.get("agno_enabled") else "⚠️ Simplificado"
        status_table.add_row(
            "Agente RAG",
            agno_status,
            f"Nível {agent_stats.get('level', 'N/A')}"
        )
        
        self.console.print(status_table)
        
        # Mostrar problemas se existirem
        if health.get("issues"):
            self.console.print("\n[yellow]⚠️ Problemas identificados:[/yellow]")
            for issue in health["issues"]:
                self.console.print(f"  • {issue}")
        
        if health.get("recommendations"):
            self.console.print("\n[blue]💡 Recomendações:[/blue]")
            for rec in health["recommendations"]:
                self.console.print(f"  • {rec}")
    
    def _setup_system(self):
        """Configura o sistema processando documentos."""
        self.console.print("\n[bold blue]⚙️ Configurando Sistema[/bold blue]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("Processando documentos...", total=None)
            
            try:
                setup_report = self.knowledge_base.setup(process_documents=True)
                
                if setup_report.get("ready_for_queries"):
                    progress.update(task, description="✅ Sistema configurado com sucesso")
                    self.system_ready = True
                    
                    # Mostrar resumo
                    proc_report = setup_report.get("processing_report", {})
                    self.console.print(f"\n✅ Processados: {proc_report.get('documents_processed', 0)} documentos")
                    self.console.print(f"🧩 Total: {proc_report.get('total_chunks', 0)} chunks criados")
                else:
                    progress.update(task, description="⚠️ Configuração com problemas")
                    self.console.print("\n[yellow]⚠️ Sistema configurado mas com limitações[/yellow]")
                    
            except Exception as e:
                progress.update(task, description="❌ Erro na configuração")
                self.console.print(f"\n[red]❌ Erro: {str(e)}[/red]")
    
    def _main_loop(self):
        """Loop principal da interface."""
        self.console.print(Rule("[bold green]Sistema Pronto[/bold green]"))
        
        while True:
            try:
                # Menu principal
                self.console.print("")
                command = Prompt.ask(
                    "[bold cyan]Sistema Tributário[/bold cyan]",
                    choices=["consulta", "status", "docs", "config", "ajuda", "sair"],
                    default="consulta"
                )
                
                if command == "consulta":
                    self._handle_query()
                elif command == "status":
                    self._show_detailed_status()
                elif command == "docs":
                    self._manage_documents()
                elif command == "config":
                    self._system_config()
                elif command == "ajuda":
                    self._show_help()
                elif command == "sair":
                    self._goodbye()
                    break
                    
            except KeyboardInterrupt:
                self.console.print("\n\n[yellow]Saindo...[/yellow]")
                break
            except Exception as e:
                self.console.print(f"\n[red]Erro: {str(e)}[/red]")
    
    def _handle_query(self):
        """Processa consulta do usuário."""
        if not self.system_ready:
            self.console.print("[red]❌ Sistema não está pronto. Execute a configuração primeiro.[/red]")
            return
        
        self.console.print(Rule("[cyan]Nova Consulta[/cyan]"))
        
        # Obter pergunta
        question = Prompt.ask("\n[bold]Sua pergunta tributária[/bold]")
        
        if not question.strip():
            return
        
        # Filtros opcionais
        self.console.print("\n[dim]Filtros opcionais (Enter para pular):[/dim]")
        
        countries_input = Prompt.ask("Países específicos (separados por vírgula)", default="")
        countries = [c.strip() for c in countries_input.split(",")] if countries_input else []
        
        # Processar consulta
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task = progress.add_task("Processando consulta...", total=None)
            
            try:
                response = self.knowledge_base.query(
                    question=question,
                    countries=countries
                )
                
                progress.update(task, description="✅ Consulta processada")
                
                # Exibir resposta
                self._display_response(response)
                
                # Salvar no histórico
                self.session_history.append({
                    "question": question,
                    "countries": countries,
                    "timestamp": datetime.now().isoformat(),
                    "confidence": response.confidence_score
                })
                
            except Exception as e:
                progress.update(task, description="❌ Erro na consulta")
                self.console.print(f"\n[red]Erro: {str(e)}[/red]")
    
    def _display_response(self, response):
        """Exibe resposta formatada."""
        self.console.print(Rule("[green]Resposta[/green]"))
        
        # Resposta principal
        confidence_color = "green" if response.confidence_score > 0.8 else "yellow" if response.confidence_score > 0.6 else "red"
        
        self.console.print(Panel(
            response.answer,
            title=f"[bold]Resposta (Confiança: [{confidence_color}]{response.confidence_score:.1%}[/{confidence_color}])[/bold]",
            border_style="green"
        ))
        
        # Fontes
        if response.sources:
            sources_table = Table(title="📚 Fontes Citadas", show_header=True)
            sources_table.add_column("#", width=3)
            sources_table.add_column("Documento", style="cyan")
            sources_table.add_column("Referência", style="dim")
            sources_table.add_column("Confiança", justify="center")
            
            for i, source in enumerate(response.sources, 1):
                ref_parts = []
                if source.page_number:
                    ref_parts.append(f"p. {source.page_number}")
                if source.section:
                    ref_parts.append(source.section[:30] + "..." if len(source.section) > 30 else source.section)
                
                reference = " • ".join(ref_parts) if ref_parts else "N/A"
                
                sources_table.add_row(
                    str(i),
                    source.document_title,
                    reference,
                    f"{source.confidence:.1%}"
                )
            
            self.console.print(sources_table)
        
        # Informações complementares
        if response.related_topics or response.suggested_countries:
            info_text = ""
            
            if response.related_topics:
                info_text += f"🔗 **Tópicos relacionados:** {', '.join(response.related_topics[:5])}\n"
            
            if response.suggested_countries:
                info_text += f"🌍 **Países sugeridos:** {', '.join(response.suggested_countries[:5])}\n"
            
            if info_text:
                self.console.print(Panel(
                    Markdown(info_text),
                    title="[dim]Informações Complementares[/dim]",
                    border_style="dim"
                ))
        
        # Métricas
        self.console.print(f"\n[dim]⏱️ Processado em {response.processing_time_ms}ms • {response.search_results_count} chunks analisados[/dim]")
    
    def _show_detailed_status(self):
        """Exibe status detalhado do sistema."""
        status = self.knowledge_base.get_system_status()
        
        self.console.print(Rule("[cyan]Status Detalhado[/cyan]"))
        
        # Estatísticas principais
        main_stats = Table(title="Estatísticas Principais")
        main_stats.add_column("Métrica", style="cyan")
        main_stats.add_column("Valor", justify="right")
        
        vs_stats = status.get("vector_store", {})
        doc_stats = status.get("documents", {})
        
        main_stats.add_row("Total de Chunks", f"{vs_stats.get('total_chunks', 0):,}")
        main_stats.add_row("Documentos Únicos", str(vs_stats.get('unique_documents', 0)))
        main_stats.add_row("Países Cobertos", str(doc_stats.get('countries_covered', 0)))
        main_stats.add_row("Tópicos Cobertos", str(doc_stats.get('topics_covered', 0)))
        main_stats.add_row("Consultas na Sessão", str(len(self.session_history)))
        
        self.console.print(main_stats)
        
        # Países disponíveis
        if doc_stats.get('countries_list'):
            countries_text = ", ".join(doc_stats['countries_list'][:15])
            if len(doc_stats['countries_list']) > 15:
                countries_text += f" (e mais {len(doc_stats['countries_list']) - 15})"
            
            self.console.print(Panel(
                countries_text,
                title="🌍 Países na Base de Conhecimento",
                border_style="blue"
            ))
    
    def _manage_documents(self):
        """Gerencia documentos do sistema."""
        self.console.print(Rule("[cyan]Gerenciar Documentos[/cyan]"))
        
        docs = self.knowledge_base.document_manager.list_available_documents()
        
        if not docs:
            self.console.print("[yellow]Nenhum documento encontrado.[/yellow]")
            return
        
        # Tabela de documentos
        docs_table = Table(title="Documentos Disponíveis", show_header=True)
        docs_table.add_column("Nome", style="cyan")
        docs_table.add_column("Tipo", justify="center")
        docs_table.add_column("Tamanho", justify="right")
        docs_table.add_column("Status", justify="center")
        docs_table.add_column("Chunks", justify="right")
        
        for doc in docs:
            status = "✅ Processado" if doc["is_processed"] else "⏳ Pendente"
            chunks = str(doc.get("chunks_count", 0)) if doc["is_processed"] else "-"
            
            docs_table.add_row(
                doc["name"],
                doc["type"].upper(),
                f"{doc['size_mb']:.1f} MB",
                status,
                chunks
            )
        
        self.console.print(docs_table)
        
        # Ações disponíveis
        action = Prompt.ask(
            "Ação",
            choices=["processar", "reprocessar", "remover", "voltar"],
            default="voltar"
        )
        
        if action == "processar":
            pending = [doc for doc in docs if not doc["is_processed"]]
            if pending:
                self._process_pending_documents(pending)
            else:
                self.console.print("[yellow]Todos os documentos já foram processados.[/yellow]")
        
        elif action in ["reprocessar", "remover"]:
            processed = [doc for doc in docs if doc["is_processed"]]
            if processed:
                doc_names = [doc["name"] for doc in processed]
                selected = Prompt.ask("Documento", choices=doc_names)
                
                if action == "reprocessar":
                    self._reprocess_document(selected)
                else:
                    self._remove_document(selected)
            else:
                self.console.print("[yellow]Nenhum documento processado disponível.[/yellow]")
    
    def _process_pending_documents(self, pending_docs: List[Dict]):
        """Processa documentos pendentes."""
        self.console.print(f"\n[blue]Processando {len(pending_docs)} documento(s)...[/blue]")
        
        with Progress(console=self.console) as progress:
            task = progress.add_task("Processando...", total=len(pending_docs))
            
            for doc in pending_docs:
                progress.update(task, description=f"Processando {doc['name']}")
                
                try:
                    result = self.knowledge_base.document_manager.process_single_document(
                        self.knowledge_base.data_path / doc['name']
                    )
                    
                    if result["success"]:
                        self.console.print(f"✅ {doc['name']}: {result['chunks_count']} chunks")
                    else:
                        self.console.print(f"❌ {doc['name']}: {result.get('error', 'Falha')}")
                        
                except Exception as e:
                    self.console.print(f"❌ {doc['name']}: {str(e)}")
                
                progress.advance(task)
        
        self.console.print("\n[green]✅ Processamento concluído[/green]")
    
    def _reprocess_document(self, doc_name: str):
        """Reprocessa um documento."""
        if Confirm.ask(f"Reprocessar '{doc_name}'?", console=self.console):
            with Progress(console=self.console) as progress:
                task = progress.add_task(f"Reprocessando {doc_name}...", total=None)
                
                try:
                    result = self.knowledge_base.reprocess_document(
                        str(self.knowledge_base.data_path / doc_name)
                    )
                    
                    if result["success"]:
                        self.console.print(f"✅ {doc_name} reprocessado: {result['chunks_count']} chunks")
                    else:
                        self.console.print(f"❌ Erro: {result.get('error')}")
                        
                except Exception as e:
                    self.console.print(f"❌ Erro: {str(e)}")
    
    def _remove_document(self, doc_name: str):
        """Remove um documento."""
        if Confirm.ask(f"Remover '{doc_name}' permanentemente?", console=self.console):
            try:
                success = self.knowledge_base.remove_document(doc_name)
                if success:
                    self.console.print(f"✅ {doc_name} removido")
                else:
                    self.console.print(f"❌ Erro ao remover {doc_name}")
            except Exception as e:
                self.console.print(f"❌ Erro: {str(e)}")
    
    def _system_config(self):
        """Configurações do sistema."""
        self.console.print(Rule("[cyan]Configurações[/cyan]"))
        
        config_action = Prompt.ask(
            "Configuração",
            choices=["setup", "backup", "reset", "health", "voltar"],
            default="voltar"
        )
        
        if config_action == "setup":
            self._setup_system()
        elif config_action == "backup":
            self._backup_system()
        elif config_action == "reset":
            self._reset_system()
        elif config_action == "health":
            health = self.knowledge_base.health_check()
            self._show_system_status(health)
    
    def _backup_system(self):
        """Faz backup do sistema."""
        if Confirm.ask("Fazer backup do sistema?", console=self.console):
            with Progress(console=self.console) as progress:
                task = progress.add_task("Criando backup...", total=None)
                
                try:
                    success = self.knowledge_base.backup_system()
                    if success:
                        self.console.print("✅ Backup criado com sucesso")
                    else:
                        self.console.print("❌ Falha no backup")
                except Exception as e:
                    self.console.print(f"❌ Erro: {str(e)}")
    
    def _reset_system(self):
        """Reseta o sistema."""
        self.console.print("[red]⚠️ ATENÇÃO: Esta operação apagará todos os dados processados![/red]")
        
        if Confirm.ask("Tem certeza que deseja resetar o sistema?", console=self.console):
            if Confirm.ask("CONFIRMAÇÃO FINAL: Apagar todos os dados?", console=self.console):
                try:
                    success = self.knowledge_base.reset_system()
                    if success:
                        self.console.print("✅ Sistema resetado")
                        self.system_ready = False
                        self.session_history = []
                    else:
                        self.console.print("❌ Falha no reset")
                except Exception as e:
                    self.console.print(f"❌ Erro: {str(e)}")
    
    def _show_help(self):
        """Exibe ajuda do sistema."""
        help_text = """
# 📋 Ajuda - Sistema de Agentes Tributários

## Comandos Principais:

### 🔍 **consulta** (padrão)
Faz consultas sobre tributação internacional
- Perguntas em linguagem natural
- Filtros por país opcionais
- Respostas com citações das fontes

### 📊 **status**
Exibe status detalhado do sistema
- Estatísticas da base de conhecimento
- Países e tópicos disponíveis
- Histórico da sessão

### 📄 **docs**
Gerencia documentos da base
- Lista documentos disponíveis
- Processa documentos pendentes
- Reprocessa ou remove documentos

### ⚙️ **config**
Configurações do sistema
- Setup inicial
- Backup e restore
- Reset do sistema
- Verificação de saúde

---

## Exemplos de Consultas:

• "Quais são os requisitos para residência fiscal em Portugal?"
• "Compare tributação entre Brasil e Portugal"
• "Como funciona o exit tax brasileiro?"
• "Tratado de bitributação Brasil-EUA tie-breaker"

---

## Dicas:
- Use países específicos para respostas mais precisas
- Consulte o **status** para ver países disponíveis
- Execute **config → setup** se o sistema não estiver pronto
"""
        
        self.console.print(Panel(
            Markdown(help_text),
            title="[bold blue]Ajuda[/bold blue]",
            border_style="blue"
        ))
    
    def _goodbye(self):
        """Mensagem de despedida."""
        if self.session_history:
            self.console.print(f"\n[dim]Sessão: {len(self.session_history)} consulta(s) realizadas[/dim]")
        
        goodbye_text = """
# 👋 Até logo!

Obrigado por usar o **Sistema de Agentes Tributários**.

Para questões específicas, sempre consulte um profissional 
qualificado em tributação internacional.

---
*Powered by Agno Framework*
"""
        
        self.console.print(Panel(
            Markdown(goodbye_text),
            title="[bold green]Despedida[/bold green]",
            border_style="green"
        ))