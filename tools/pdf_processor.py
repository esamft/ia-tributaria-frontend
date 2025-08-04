"""
Processador especializado para documentos PDF tributários.
Extração inteligente com preservação de estrutura.
"""

import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from pydantic import BaseModel

try:
    import pypdf
    from pypdf import PdfReader
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

from ..models.document import Document, DocumentMetadata, DocumentType, SourceType


class PDFPageInfo(BaseModel):
    """Informações de uma página PDF."""
    page_number: int
    text: str
    char_count: int
    has_tables: bool = False
    has_headers: bool = False
    quality_score: float = 1.0


class PDFProcessor:
    """Processador de documentos PDF para base tributária."""
    
    def __init__(self):
        """Inicializa o processador PDF."""
        if not PDF_AVAILABLE:
            raise ImportError(
                "pypdf não instalado. Execute: pip install pypdf"
            )
        
        # Padrões para detecção de estrutura
        self.header_patterns = [
            r'^[A-Z\s]{10,}$',  # Cabeçalhos em maiúsculas
            r'^\d+\.\s+[A-Z]',  # Numeração de seções
            r'^Chapter \d+',     # Capítulos
            r'^PART [IVX]+',     # Partes
        ]
        
        self.table_indicators = [
            r'\s+\|\s+',        # Separadores de tabela
            r'\d+%\s+\d+%',     # Percentuais em sequência
            r'USD\s+EUR\s+',    # Moedas em sequência
        ]
        
        # Padrões de limpeza
        self.noise_patterns = [
            r'\f',               # Form feed
            r'\x0c',             # Page break
            r'^\s*\d+\s*$',      # Números de página sozinhos
            r'^Page \d+ of \d+', # "Page X of Y"
            r'©.*\d{4}',         # Copyright
        ]
    
    def process_pdf(self, file_path: Path) -> Document:
        """
        Processa um arquivo PDF completo.
        
        Args:
            file_path: Caminho para o arquivo PDF
            
        Returns:
            Document: Documento processado com metadados
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
        
        # Extrair conteúdo página por página
        pages_info = self._extract_pages(file_path)
        
        # Combinar texto de todas as páginas
        full_text = self._combine_pages_text(pages_info)
        
        # Gerar metadados
        metadata = self._generate_metadata(file_path, pages_info, full_text)
        
        # Criar documento
        document = Document(
            id=self._generate_document_id(file_path),
            file_path=file_path,
            content=full_text,
            metadata=metadata
        )
        
        return document
    
    def _extract_pages(self, file_path: Path) -> List[PDFPageInfo]:
        """Extrai informações de todas as páginas."""
        pages_info = []
        
        try:
            with open(file_path, 'rb') as file:
                reader = PdfReader(file)
                
                for page_num, page in enumerate(reader.pages, 1):
                    try:
                        # Extrair texto da página
                        raw_text = page.extract_text()
                        cleaned_text = self._clean_page_text(raw_text)
                        
                        # Analisar características da página
                        page_info = PDFPageInfo(
                            page_number=page_num,
                            text=cleaned_text,
                            char_count=len(cleaned_text),
                            has_tables=self._detect_tables(cleaned_text),
                            has_headers=self._detect_headers(cleaned_text),
                            quality_score=self._calculate_quality_score(cleaned_text)
                        )
                        
                        pages_info.append(page_info)
                        
                    except Exception as e:
                        # Página com problema - criar placeholder
                        placeholder = PDFPageInfo(
                            page_number=page_num,
                            text=f"[ERRO: Página {page_num} não pôde ser processada: {str(e)}]",
                            char_count=0,
                            quality_score=0.0
                        )
                        pages_info.append(placeholder)
                        
        except Exception as e:
            raise Exception(f"Erro ao processar PDF {file_path}: {str(e)}")
        
        return pages_info
    
    def _clean_page_text(self, raw_text: str) -> str:
        """Limpa texto extraído de uma página."""
        if not raw_text:
            return ""
        
        text = raw_text
        
        # Remover padrões de ruído
        for pattern in self.noise_patterns:
            text = re.sub(pattern, '', text, flags=re.MULTILINE)
        
        # Normalizar espaços em branco
        text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)  # Múltiplas quebras
        text = re.sub(r' +', ' ', text)                # Espaços múltiplos
        text = re.sub(r'\n ', '\n', text)              # Espaços no início de linha
        
        # Remover linhas muito curtas (provavelmente ruído)
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            # Manter linha se: não vazia, tem mais que 3 chars, ou contém números/símbolos importantes
            if line and (len(line) > 3 or re.search(r'[\d%$€£]', line)):
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def _detect_tables(self, text: str) -> bool:
        """Detecta se o texto contém tabelas."""
        for pattern in self.table_indicators:
            if re.search(pattern, text):
                return True
        return False
    
    def _detect_headers(self, text: str) -> bool:
        """Detecta se o texto contém cabeçalhos estruturados."""
        lines = text.split('\n')[:5]  # Verificar primeiras linhas
        
        for line in lines:
            for pattern in self.header_patterns:
                if re.match(pattern, line.strip()):
                    return True
        return False
    
    def _calculate_quality_score(self, text: str) -> float:
        """Calcula score de qualidade do texto extraído."""
        if not text:
            return 0.0
        
        score = 1.0
        
        # Penalizar texto muito curto
        if len(text) < 100:
            score *= 0.5
        
        # Penalizar muitos caracteres especiais (pode indicar erro de OCR)
        special_chars = len(re.findall(r'[^\w\s\.\,\;\:\!\?\(\)\-]', text))
        if special_chars > len(text) * 0.1:  # Mais de 10% caracteres especiais
            score *= 0.7
        
        # Bonificar texto bem estruturado
        if re.search(r'\d+\.\d+', text):  # Numeração de seções
            score *= 1.1
        
        if re.search(r'[A-Z][a-z]+:', text):  # Rótulos/títulos
            score *= 1.1
        
        return min(score, 1.0)
    
    def _combine_pages_text(self, pages_info: List[PDFPageInfo]) -> str:
        """Combina texto de todas as páginas com marcadores."""
        combined_parts = []
        
        for page_info in pages_info:
            if page_info.text and page_info.quality_score > 0.3:
                # Adicionar marcador de página
                page_marker = f"\n\n[PÁGINA {page_info.page_number}]\n"
                combined_parts.append(page_marker + page_info.text)
        
        return '\n'.join(combined_parts)
    
    def _generate_metadata(self, file_path: Path, pages_info: List[PDFPageInfo], 
                          full_text: str) -> DocumentMetadata:
        """Gera metadados baseados no conteúdo do PDF."""
        
        # Detectar tipo de documento pelo nome do arquivo
        filename = file_path.stem.lower()
        doc_type = DocumentType.GUIDE  # Default
        
        if "guide" in filename or "manual" in filename:
            doc_type = DocumentType.GUIDE
        elif "book" in filename or "livro" in filename:
            doc_type = DocumentType.BOOK
        elif "report" in filename or "relatorio" in filename:
            doc_type = DocumentType.REPORT
        
        # Detectar autor/fonte
        author = None
        if "ey" in filename:
            author = "Ernst & Young"
        elif "pwc" in filename:
            author = "PricewaterhouseCoopers"
        elif "deloitte" in filename:
            author = "Deloitte"
        elif "kpmg" in filename:
            author = "KPMG"
        
        # Calcular estatísticas
        total_pages = len([p for p in pages_info if p.quality_score > 0])
        avg_quality = sum(p.quality_score for p in pages_info) / len(pages_info) if pages_info else 0
        file_size_mb = file_path.stat().st_size / (1024 * 1024)
        
        # Detectar países mencionados (básico)
        detected_countries = self._detect_countries_in_text(full_text)
        
        # Detectar tópicos tributários
        detected_topics = self._detect_tax_topics(full_text)
        
        return DocumentMetadata(
            title=file_path.stem.replace('_', ' ').title(),
            author=author,
            document_type=doc_type,
            source_type=SourceType.PDF,
            countries=detected_countries,
            topics=detected_topics,
            total_pages=total_pages,
            file_size_mb=round(file_size_mb, 2),
            confidence_level=avg_quality,
            official_source=author is not None,
            keywords=detected_topics + detected_countries
        )
    
    def _detect_countries_in_text(self, text: str) -> List[str]:
        """Detecta países mencionados no texto."""
        countries = []
        text_lower = text.lower()
        
        # Lista de países com variações
        country_patterns = {
            'portugal': ['portugal', 'portuguese'],
            'brasil': ['brazil', 'brasil', 'brazilian'],
            'espanha': ['spain', 'spanish', 'españa'],
            'reino_unido': ['united kingdom', 'uk', 'britain', 'england'],
            'estados_unidos': ['united states', 'usa', 'us ', 'america'],
            'suica': ['switzerland', 'swiss'],
            'singapura': ['singapore'],
            'hong_kong': ['hong kong'],
            'malta': ['malta'],
            'chipre': ['cyprus'],
            'irlanda': ['ireland', 'irish'],
            'luxemburgo': ['luxembourg'],
            'panama': ['panama'],
            'uruguai': ['uruguay'],
            'paraguai': ['paraguay']
        }
        
        for country, patterns in country_patterns.items():
            if any(pattern in text_lower for pattern in patterns):
                countries.append(country)
        
        return countries[:10]  # Limitar a 10 países
    
    def _detect_tax_topics(self, text: str) -> List[str]:
        """Detecta tópicos tributários no texto."""
        topics = []
        text_lower = text.lower()
        
        topic_patterns = {
            'residencia_fiscal': ['tax residence', 'fiscal residence', 'residência'],
            'tributacao_renda': ['income tax', 'personal tax', 'individual tax'],
            'ganhos_capital': ['capital gains', 'cgt'],
            'dividendos': ['dividends', 'dividend tax'],
            'tratados': ['treaty', 'agreement', 'acordo'],
            'compliance': ['compliance', 'reporting', 'declaração'],
            'planejamento': ['planning', 'optimization', 'planejamento'],
            'imigracao': ['immigration', 'visa', 'residence permit'],
            'offshore': ['offshore', 'holding'],
            'criptomoedas': ['crypto', 'bitcoin', 'digital assets', 'criptomoeda']
        }
        
        for topic, patterns in topic_patterns.items():
            if any(pattern in text_lower for pattern in patterns):
                topics.append(topic)
        
        return topics
    
    def _generate_document_id(self, file_path: Path) -> str:
        """Gera ID único para o documento."""
        # Usar nome do arquivo como base
        base_name = file_path.stem.lower()
        # Limpar caracteres especiais
        clean_name = re.sub(r'[^\w\-]', '_', base_name)
        return clean_name
    
    def get_page_text(self, file_path: Path, page_number: int) -> Optional[str]:
        """Extrai texto de uma página específica."""
        try:
            with open(file_path, 'rb') as file:
                reader = PdfReader(file)
                if 1 <= page_number <= len(reader.pages):
                    page = reader.pages[page_number - 1]
                    raw_text = page.extract_text()
                    return self._clean_page_text(raw_text)
        except Exception:
            pass
        return None