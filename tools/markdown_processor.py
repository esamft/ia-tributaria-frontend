"""
Processador especializado para documentos Markdown tributários.
Preserva estrutura hierárquica e metadados.
"""

import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

from ..models.document import Document, DocumentMetadata, DocumentType, SourceType


class MarkdownSection:
    """Representa uma seção do documento Markdown."""
    
    def __init__(self, title: str, level: int, content: str, line_start: int):
        self.title = title
        self.level = level  # 1-6 (H1-H6)
        self.content = content
        self.line_start = line_start
        self.subsections: List['MarkdownSection'] = []


class MarkdownProcessor:
    """Processador de documentos Markdown para base tributária."""
    
    def __init__(self):
        """Inicializa o processador Markdown."""
        
        # Padrões de detecção
        self.header_pattern = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)
        self.code_block_pattern = re.compile(r'```[\s\S]*?```', re.MULTILINE)
        self.inline_code_pattern = re.compile(r'`[^`]+`')
        self.link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
        self.emphasis_pattern = re.compile(r'\*\*([^*]+)\*\*|__([^_]+)__|\*([^*]+)\*|_([^_]+)_')
        
        # Padrões tributários específicos
        self.tax_terms = {
            'residencia': r'\b(resid[eê]ncia|fiscal|domicilio)\b',
            'tributacao': r'\b(tribut|imposto|tax|fiscal)\b',
            'tratado': r'\b(tratado|treaty|acordo)\b',
            'compliance': r'\b(compliance|declaração|reporting)\b',
            'planejamento': r'\b(planejamento|planning|otimiz)\b',
            'pais': r'\b(brasil|portugal|espanha|usa|reino unido|suiça)\b'
        }
    
    def process_markdown(self, file_path: Path) -> Document:
        """
        Processa um arquivo Markdown completo.
        
        Args:
            file_path: Caminho para o arquivo Markdown
            
        Returns:
            Document: Documento processado com metadados
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
        
        # Ler conteúdo do arquivo
        with open(file_path, 'r', encoding='utf-8') as f:
            raw_content = f.read()
        
        # Processar estrutura hierárquica
        sections = self._parse_sections(raw_content)
        
        # Limpar e estruturar conteúdo
        cleaned_content = self._clean_content(raw_content)
        
        # Gerar metadados
        metadata = self._generate_metadata(file_path, raw_content, sections)
        
        # Criar documento
        document = Document(
            id=self._generate_document_id(file_path),
            file_path=file_path,
            content=cleaned_content,
            metadata=metadata
        )
        
        return document
    
    def _parse_sections(self, content: str) -> List[MarkdownSection]:
        """Analisa estrutura hierárquica do Markdown."""
        sections = []
        lines = content.split('\n')
        current_section = None
        section_content = []
        
        for i, line in enumerate(lines):
            header_match = re.match(r'^(#{1,6})\s+(.+)$', line)
            
            if header_match:
                # Salvar seção anterior se existir
                if current_section:
                    current_section.content = '\n'.join(section_content).strip()
                    sections.append(current_section)
                
                # Criar nova seção
                level = len(header_match.group(1))
                title = header_match.group(2).strip()
                current_section = MarkdownSection(title, level, "", i + 1)
                section_content = []
            else:
                # Adicionar linha ao conteúdo da seção atual
                if current_section:
                    section_content.append(line)
        
        # Adicionar última seção
        if current_section:
            current_section.content = '\n'.join(section_content).strip()
            sections.append(current_section)
        
        return sections
    
    def _clean_content(self, content: str) -> str:
        """Limpa e normaliza conteúdo Markdown."""
        
        # Remover múltiplas linhas em branco
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
        
        # Normalizar espaços
        content = re.sub(r'[ \t]+', ' ', content)
        
        # Remover trailing whitespace
        lines = content.split('\n')
        cleaned_lines = [line.rstrip() for line in lines]
        
        # Remover linhas vazias no início e fim
        while cleaned_lines and not cleaned_lines[0].strip():
            cleaned_lines.pop(0)
        while cleaned_lines and not cleaned_lines[-1].strip():
            cleaned_lines.pop()
        
        return '\n'.join(cleaned_lines)
    
    def _generate_metadata(self, file_path: Path, content: str, 
                          sections: List[MarkdownSection]) -> DocumentMetadata:
        """Gera metadados baseados no conteúdo Markdown."""
        
        # Detectar tipo de documento
        doc_type = self._detect_document_type(file_path, content)
        
        # Extrair título (primeira linha ou nome do arquivo)
        title = self._extract_title(content, file_path)
        
        # Detectar autor
        author = self._detect_author(content)
        
        # Análise de conteúdo
        countries = self._detect_countries(content)
        topics = self._detect_topics(content)
        keywords = self._extract_keywords(content)
        
        # Estatísticas
        file_size_mb = file_path.stat().st_size / (1024 * 1024)
        word_count = len(content.split())
        
        # Calcular confiança baseada na estrutura e conteúdo
        confidence = self._calculate_confidence(content, sections)
        
        return DocumentMetadata(
            title=title,
            author=author,
            document_type=doc_type,
            source_type=SourceType.MARKDOWN,
            countries=countries,
            topics=topics,
            keywords=keywords,
            file_size_mb=round(file_size_mb, 3),
            confidence_level=confidence,
            official_source=self._is_official_source(content, author)
        )
    
    def _detect_document_type(self, file_path: Path, content: str) -> DocumentType:
        """Detecta tipo de documento baseado no nome e conteúdo."""
        filename = file_path.stem.lower()
        content_lower = content.lower()
        
        if any(term in filename for term in ['livro', 'book']):
            return DocumentType.BOOK
        elif any(term in filename for term in ['relatorio', 'report', 'pesquisa']):
            return DocumentType.REPORT
        elif any(term in filename for term in ['estrutura', 'indice', 'sumario']):
            return DocumentType.STRUCTURE
        elif any(term in content_lower for term in ['capítulo', 'chapter', 'parte']):
            return DocumentType.BOOK
        else:
            return DocumentType.GUIDE
    
    def _extract_title(self, content: str, file_path: Path) -> str:
        """Extrai título do documento."""
        lines = content.split('\n')
        
        # Procurar primeiro header H1
        for line in lines[:10]:  # Verificar primeiras 10 linhas
            if line.startswith('# '):
                return line[2:].strip()
        
        # Procurar linha com texto em maiúsculas
        for line in lines[:5]:
            if line.isupper() and len(line.strip()) > 10:
                return line.strip().title()
        
        # Usar nome do arquivo como fallback
        return file_path.stem.replace('_', ' ').replace('-', ' ').title()
    
    def _detect_author(self, content: str) -> Optional[str]:
        """Detecta autor do documento."""
        content_lower = content.lower()
        
        # Padrões de autor
        author_patterns = [
            r'autor[:\s]+([^\n]+)',
            r'por[:\s]+([^\n]+)',
            r'by[:\s]+([^\n]+)',
            r'estrategista'  # Específico para o livro
        ]
        
        for pattern in author_patterns:
            match = re.search(pattern, content_lower)
            if match:
                if pattern == 'estrategista':
                    return "O Estrategista"
                else:
                    return match.group(1).strip().title()
        
        return None
    
    def _detect_countries(self, content: str) -> List[str]:
        """Detecta países mencionados no conteúdo."""
        content_lower = content.lower()
        countries = []
        
        country_patterns = {
            'portugal': ['portugal', 'português', 'lusitano'],
            'brasil': ['brasil', 'brazil', 'brasileiro'],
            'espanha': ['espanha', 'spain', 'espanhol'],
            'reino_unido': ['reino unido', 'uk', 'inglaterra', 'britain'],
            'estados_unidos': ['estados unidos', 'usa', 'américa', 'eua'],
            'suica': ['suíça', 'switzerland', 'swiss'],
            'singapura': ['singapura', 'singapore'],
            'hong_kong': ['hong kong'],
            'malta': ['malta'],
            'chipre': ['chipre', 'cyprus'],
            'irlanda': ['irlanda', 'ireland'],
            'uruguai': ['uruguai', 'uruguay'],
            'panama': ['panama', 'panamá'],
            'paraguai': ['paraguai', 'paraguay'],
            'emirados_arabes': ['emirados', 'uae', 'dubai']
        }
        
        for country, patterns in country_patterns.items():
            if any(pattern in content_lower for pattern in patterns):
                countries.append(country)
        
        return countries
    
    def _detect_topics(self, content: str) -> List[str]:
        """Detecta tópicos tributários no conteúdo."""
        content_lower = content.lower()
        topics = []
        
        topic_patterns = {
            'residencia_fiscal': ['residência fiscal', 'residencia fiscal', 'tax residence'],
            'tributacao_renda': ['imposto de renda', 'income tax', 'tributação'],
            'ganhos_capital': ['ganhos de capital', 'capital gains', 'cgt'],
            'dividendos': ['dividendos', 'dividends'],
            'tratados': ['tratado', 'treaty', 'acordo fiscal'],
            'compliance': ['compliance', 'declaração', 'obrigações'],
            'planejamento': ['planejamento tributário', 'tax planning', 'otimização'],
            'imigracao': ['imigração', 'immigration', 'visto'],
            'offshore': ['offshore', 'holding', 'estrutura'],
            'exit_tax': ['exit tax', 'imposto de saída'],
            'crs': ['crs', 'common reporting standard'],
            'fatca': ['fatca'],
            'criptomoedas': ['criptomoeda', 'crypto', 'bitcoin', 'blockchain'],
            'nhr': ['nhr', 'residente não habitual'],
            'golden_visa': ['golden visa', 'visto gold']
        }
        
        for topic, patterns in topic_patterns.items():
            if any(pattern in content_lower for pattern in patterns):
                topics.append(topic)
        
        return topics
    
    def _extract_keywords(self, content: str) -> List[str]:
        """Extrai palavras-chave relevantes."""
        keywords = set()
        content_lower = content.lower()
        
        # Termos tributários específicos
        tax_keywords = [
            'tributação', 'imposto', 'fiscal', 'tax', 'revenue',
            'alíquota', 'isenção', 'dedução', 'crédito',
            'offshore', 'onshore', 'compliance', 'planning',
            'residence', 'domicile', 'treaty', 'agreement'
        ]
        
        for keyword in tax_keywords:
            if keyword in content_lower:
                keywords.add(keyword)
        
        # Adicionar países e tópicos detectados
        keywords.update(self._detect_countries(content))
        keywords.update(self._detect_topics(content))
        
        return list(keywords)[:20]  # Limitar a 20 keywords
    
    def _calculate_confidence(self, content: str, sections: List[MarkdownSection]) -> float:
        """Calcula nível de confiança do documento."""
        score = 0.7  # Base
        
        # Bonificar estrutura bem organizada
        if len(sections) > 5:
            score += 0.1
        
        # Bonificar presença de headers hierárquicos
        if any(s.level <= 2 for s in sections):
            score += 0.1
        
        # Bonificar conteúdo substantivo
        if len(content) > 10000:  # Mais de 10k caracteres
            score += 0.1
        
        # Bonificar termos técnicos
        technical_terms = ['lei', 'artigo', 'decreto', 'regulamento', 'instrução']
        if any(term in content.lower() for term in technical_terms):
            score += 0.1
        
        return min(score, 1.0)
    
    def _is_official_source(self, content: str, author: Optional[str]) -> bool:
        """Determina se é fonte oficial."""
        if author and any(term in author.lower() for term in ['governo', 'receita', 'ministry']):
            return True
        
        official_indicators = ['lei nº', 'decreto', 'portaria', 'instrução normativa']
        return any(indicator in content.lower() for indicator in official_indicators)
    
    def _generate_document_id(self, file_path: Path) -> str:
        """Gera ID único para o documento."""
        base_name = file_path.stem.lower()
        return re.sub(r'[^\w\-]', '_', base_name)
    
    def get_section_content(self, content: str, section_title: str) -> Optional[str]:
        """Extrai conteúdo de uma seção específica."""
        sections = self._parse_sections(content)
        
        for section in sections:
            if section_title.lower() in section.title.lower():
                return section.content
        
        return None
    
    def get_table_of_contents(self, content: str) -> List[Dict[str, Any]]:
        """Gera índice do documento."""
        sections = self._parse_sections(content)
        toc = []
        
        for section in sections:
            toc.append({
                'title': section.title,
                'level': section.level,
                'line_start': section.line_start,
                'content_length': len(section.content)
            })
        
        return toc