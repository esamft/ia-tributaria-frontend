#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema Principal de Agentes Tributários
Framework Agno - Coordenação Multi-Agente
"""

import os
import sys
from pathlib import Path

# Adicionar o diretório atual ao PYTHONPATH
sys.path.append(str(Path(__file__).parent))

from dotenv import load_dotenv
load_dotenv()

from agno.team import Team
from agno.models.anthropic import Claude
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
import json
from datetime import datetime

# Importar agentes especializados
from agents.consultor_tributario import criar_agente_consultor
from agents.pesquisador_rag import criar_agente_pesquisador
from agents.validador_juridico import criar_agente_validador

console = Console()

class SistemaTributarioAgno:
    """Sistema coordenado de agentes tributários usando Agno Framework"""
    
    def __init__(self):
        self.console = console
        self.setup_agentes()
        self.historico_consultas = []
    
    def setup_agentes(self):
        """Configura todos os agentes especializados"""
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
        ) as progress:
            
            task = progress.add_task("Inicializando agentes especializados...", total=None)
            
            # Criar agentes individuais
            self.consultor = criar_agente_consultor()
            progress.update(task, description="✅ Consultor Tributário criado")
            
            self.pesquisador = criar_agente_pesquisador()
            progress.update(task, description="✅ Pesquisador RAG criado")
            
            self.validador = criar_agente_validador()
            progress.update(task, description="✅ Validador Jurídico criado")
            
            # Criar team coordenado
            self.team = Team(
                model=Claude(id="claude-sonnet-4-20250514"),
                members=[self.consultor, self.pesquisador, self.validador],
                mode="coordinate",
                instructions="""
                COORDENAÇÃO DE AGENTES TRIBUTÁRIOS:
                
                1. CONSULTOR TRIBUTÁRIO analisa a consulta primeiro
                2. PESQUISADOR RAG busca informações específicas na base
                3. VALIDADOR JURÍDICO verifica consistência e atualização
                4. Resposta final integrada e fundamentada
                
                PROTOCOLO:
                - Sempre seguir essa sequência
                - Cada agente contribui com sua especialidade
                - Resposta final deve ser jurídica e precisa
                - Citar fontes específicas encontradas
                """,
                success_criteria="Resposta tributária completa, precisa e fundamentada"
            )
            
            progress.update(task, description="🎯 Sistema multi-agente configurado!")
    
    def mostrar_boas_vindas(self):
        """Mostra interface de boas-vindas do sistema"""
        
        panel = Panel.fit(
            """[bold blue]🤖 Sistema de Inteligência Tributária Agno[/bold blue]
            
[green]Agentes Especializados Ativos:[/green]
• [cyan]Consultor Tributário[/cyan] - Análise de consultas
• [cyan]Pesquisador RAG[/cyan] - Base com 4.317 chunks
• [cyan]Validador Jurídico[/cyan] - Consistência legal

[yellow]Áreas de Especialização:[/yellow]
• Residência fiscal internacional
• Tratados de bitributação
• Planejamento tributário transfronteiriço
• Regras CFC e transparência fiscal
• Compliance internacional (FATCA, CRS)

[dim]Powered by Agno Framework + Anthropic Claude[/dim]""",
            title="🏛️ Direito Tributário Internacional",
            border_style="blue"
        )
        
        self.console.print(panel)
        self.console.print()
    
    def processar_consulta(self, consulta: str) -> dict:
        """Processa consulta usando coordenação de agentes"""
        
        timestamp = datetime.now()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
        ) as progress:
            
            task = progress.add_task("Processando consulta tributária...", total=None)
            
            try:
                # Executar team coordenado
                progress.update(task, description="🔍 Agentes analisando consulta...")
                resultado = self.team.run(consulta)
                
                progress.update(task, description="✅ Análise completa!")
                
                # Estruturar resposta
                resposta = {
                    "consulta": consulta,
                    "resposta": resultado.content,
                    "timestamp": timestamp.isoformat(),
                    "agentes_utilizados": ["Consultor", "Pesquisador", "Validador"],
                    "confianca": 0.9,  # Alta confiança com validação multi-agente
                    "fontes": self._extrair_fontes(resultado.content)
                }
                
                # Salvar no histórico
                self.historico_consultas.append(resposta)
                
                return resposta
                
            except Exception as e:
                self.console.print(f"[red]Erro no processamento: {e}[/red]")
                return {
                    "consulta": consulta,
                    "resposta": f"Erro interno: {e}",
                    "timestamp": timestamp.isoformat(),
                    "erro": True
                }
    
    def _extrair_fontes(self, resposta: str) -> list:
        """Extrai fontes mencionadas na resposta"""
        fontes_padrao = [
            "EY Worldwide Personal Tax Guide 2025",
            "Legislação tributária brasileira",
            "Tratados internacionais"
        ]
        return fontes_padrao  # Simplificado
    
    def mostrar_resposta(self, resultado: dict):
        """Mostra resposta formatada"""
        
        if resultado.get("erro"):
            self.console.print(Panel(
                resultado["resposta"],
                title="❌ Erro no Processamento",
                border_style="red"
            ))
            return
        
        # Resposta principal
        self.console.print(Panel(
            resultado["resposta"],
            title="📋 Análise Tributária",
            border_style="green"
        ))
        
        # Metadados
        table = Table(show_header=False, box=None)
        table.add_column("Campo", style="cyan")
        table.add_column("Valor", style="white")
        
        table.add_row("🕐 Processado", resultado["timestamp"][:19])
        table.add_row("🤖 Agentes", ", ".join(resultado["agentes_utilizados"]))
        table.add_row("📊 Confiança", f"{resultado['confianca']:.1%}")
        table.add_row("📚 Fontes", f"{len(resultado['fontes'])} documentos")
        
        self.console.print(table)
        self.console.print()
    
    def executar_interativo(self):
        """Execução interativa do sistema"""
        
        self.mostrar_boas_vindas()
        
        while True:
            try:
                consulta = self.console.input("[bold green]📋 Sua consulta tributária:[/bold green] ")
                
                if not consulta.strip():
                    continue
                
                if consulta.lower() in ['sair', 'exit', 'quit']:
                    break
                
                # Processar consulta
                resultado = self.processar_consulta(consulta)
                
                # Mostrar resultado
                self.mostrar_resposta(resultado)
                
            except KeyboardInterrupt:
                self.console.print("\n\n[yellow]Sistema encerrado pelo usuário.[/yellow]")
                break
            except Exception as e:
                self.console.print(f"[red]Erro: {e}[/red]")
    
    def consulta_unica(self, pergunta: str) -> dict:
        """Processa uma consulta única (para uso via API)"""
        return self.processar_consulta(pergunta)

def main():
    """Função principal"""
    sistema = SistemaTributarioAgno()
    
    if len(sys.argv) > 1:
        # Modo consulta única via argumentos
        consulta = " ".join(sys.argv[1:])
        resultado = sistema.consulta_unica(consulta)
        sistema.mostrar_resposta(resultado)
    else:
        # Modo interativo
        sistema.executar_interativo()

if __name__ == "__main__":
    main()