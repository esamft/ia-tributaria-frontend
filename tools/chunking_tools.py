"""
Ferramentas de chunking inteligente para documentos tributários.
Preserva contexto semântico e estrutura hierárquica.
"""

import re
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

from ..models.document import Document
from ..models.chunk import Chunk, ChunkMetadata


class ChunkingTools:
    """Ferramentas especializadas para chunking de documentos tributários."""
    
    def __init__(self, 
                 chunk_size: int = 1200,
                 overlap_size: int = 200,
                 min_chunk_size: int = 100):
        """
        Inicializa ferramentas de chunking.
        
        Args:
            chunk_size: Tamanho máximo do chunk em caracteres
            overlap_size: Sobreposição entre chunks em caracteres
            min_chunk_size: Tamanho mínimo do chunk em caracteres
        """
        self.chunk_size = chunk_size
        self.overlap_size = overlap_size
        self.min_chunk_size = min_chunk_size
        
        # Padrões para quebras semânticas
        self.section_breaks = [
            r'\n#{1,6}\s+',           # Headers Markdown
            r'\n\[PÁGINA \d+\]',      # Marcadores de página
            r'\n\d+\.\s+[A-Z]',       # Numeração de seções
            r'\nChapter \d+',         # Capítulos
            r'\nPART [IVX]+',         # Partes
            r'\n[A-Z\s]{10,}\n',      # Títulos em maiúsculas
        ]
        
        # Padrões para quebras de parágrafos
        self.paragraph_breaks = [
            r'\n\n',                  # Quebra dupla
            r'\.\s+(?=[A-Z])',        # Final de frase + maiúscula
            r':\s*\n',                # Dois pontos + quebra
            r';\s*\n',                # Ponto e vírgula + quebra
        ]
        
        # Indicadores de contexto tributário
        self.context_indicators = {
            'countries': r'\b(portugal|brasil|espanha|usa|reino unido|suiça|singapura)\b',
            'tax_rates': r'\d+%|\d+\.\d+%',
            'monetary': r'[€$£¥₹]\s*\d+|USD|EUR|GBP|BRL',
            'legal_refs': r'(artigo|art\.|lei nº|decreto|portaria)\s*\d+',
            'dates': r'\d{1,2}[-/]\d{1,2}[-/]\d{4}|\d{4}[-/]\d{1,2}[-/]\d{1,2}',
            'tax_terms': r'\b(residen[ct]e|fiscal|tribut|imposto|tax|treaty|acordo)\b'
        }
    
    def create_chunks(self, document: Document) -> List[Chunk]:
        """
        Cria chunks inteligentes de um documento.
        
        Args:
            document: Documento a ser fragmentado
            
        Returns:
            List[Chunk]: Lista de chunks gerados
        """
        text = document.content
        
        # Dividir em chunks candidatos
        raw_chunks = self._split_into_raw_chunks(text)
        
        # Processar e enriquecer chunks
        processed_chunks = []
        
        for i, raw_chunk in enumerate(raw_chunks):
            chunk_metadata = self._analyze_chunk(raw_chunk, document, i)
            
            chunk = Chunk(
                id=self._generate_chunk_id(document.id, i),
                text=raw_chunk,
                metadata=chunk_metadata
            )
            
            processed_chunks.append(chunk)
        
        return processed_chunks
    
    def _split_into_raw_chunks(self, text: str) -> List[str]:
        """Divide texto em chunks preservando contexto semântico."""
        chunks = []
        current_pos = 0
        
        while current_pos < len(text):
            # Determinar fim do chunk atual
            chunk_end = min(current_pos + self.chunk_size, len(text))
            
            # Tentar quebrar em posição semântica apropriada
            optimal_break = self._find_optimal_break(text, current_pos, chunk_end)
            
            if optimal_break > current_pos:
                chunk_end = optimal_break
            
            # Extrair chunk com overlap
            if current_pos > 0:
                # Adicionar overlap do chunk anterior
                chunk_start = max(0, current_pos - self.overlap_size)
                chunk_text = text[chunk_start:chunk_end]
                
                # Marcar onde começa o conteúdo novo
                new_content_start = current_pos - chunk_start
                if new_content_start > 0:
                    chunk_text = "[...] " + chunk_text[new_content_start:]
            else:
                chunk_text = text[current_pos:chunk_end]
            
            # Validar tamanho mínimo
            if len(chunk_text.strip()) >= self.min_chunk_size:
                chunks.append(chunk_text.strip())
            
            # Avançar posição
            current_pos = chunk_end
            
            # Evitar loop infinito
            if chunk_end == current_pos and current_pos < len(text):
                current_pos += 1
        
        return chunks
    
    def _find_optimal_break(self, text: str, start: int, max_end: int) -> int:
        """Encontra posição ótima para quebra do chunk."""
        
        # Primeira prioridade: quebras de seção
        for pattern in self.section_breaks:
            matches = list(re.finditer(pattern, text[start:max_end], re.IGNORECASE))
            if matches:
                # Usar a última quebra de seção no range
                return start + matches[-1].start()
        
        # Segunda prioridade: quebras de parágrafo
        for pattern in self.paragraph_breaks:
            matches = list(re.finditer(pattern, text[start:max_end]))
            if matches:
                # Usar quebra de parágrafo mais próxima do final
                for match in reversed(matches):
                    break_pos = start + match.end()
                    if break_pos > start + (self.chunk_size * 0.7):  # Pelo menos 70% do tamanho
                        return break_pos
        
        # Terceira prioridade: quebra de frase
        sentence_breaks = list(re.finditer(r'\.\s+', text[start:max_end]))
        if sentence_breaks:
            for match in reversed(sentence_breaks):
                break_pos = start + match.end()
                if break_pos > start + (self.chunk_size * 0.6):  # Pelo menos 60% do tamanho
                    return break_pos
        
        # Última opção: quebra de palavra
        word_breaks = list(re.finditer(r'\s+', text[start:max_end]))
        if word_breaks:
            for match in reversed(word_breaks):
                break_pos = start + match.start()
                if break_pos > start + (self.chunk_size * 0.5):  # Pelo menos 50% do tamanho
                    return break_pos
        
        # Se não encontrar quebra adequada, usar posição máxima
        return max_end
    
    def _analyze_chunk(self, chunk_text: str, document: Document, chunk_index: int) -> ChunkMetadata:
        """Analisa e enriquece metadados do chunk."""
        
        # Detectar países mencionados
        detected_countries = self._detect_entities(chunk_text, 'countries')
        
        # Detectar tópicos tributários
        detected_topics = self._detect_chunk_topics(chunk_text)
        
        # Detectar página (se disponível)
        page_number = self._extract_page_number(chunk_text)
        
        # Detectar seção
        section = self._extract_section_info(chunk_text)
        
        # Analisar características do conteúdo
        has_numbers = bool(re.search(r'\d+', chunk_text))
        has_dates = bool(re.search(self.context_indicators['dates'], chunk_text, re.IGNORECASE))
        has_legal_refs = bool(re.search(self.context_indicators['legal_refs'], chunk_text, re.IGNORECASE))
        
        # Calcular qualidade e densidade de informação
        text_quality = self._calculate_text_quality(chunk_text)
        info_density = self._calculate_information_density(chunk_text)
        
        # Calcular posição no documento original
        start_char = chunk_index * (self.chunk_size - self.overlap_size)
        end_char = start_char + len(chunk_text)
        
        return ChunkMetadata(
            document_id=document.id,
            page_number=page_number,
            section=section,
            start_char=start_char,
            end_char=end_char,
            detected_countries=detected_countries,
            detected_topics=detected_topics,
            has_numbers=has_numbers,
            has_dates=has_dates,
            has_legal_refs=has_legal_refs,
            text_quality=text_quality,
            information_density=info_density
        )
    
    def _detect_entities(self, text: str, entity_type: str) -> List[str]:
        """Detecta entidades específicas no texto."""
        entities = []
        text_lower = text.lower()
        
        if entity_type == 'countries':
            country_patterns = {
                'portugal': ['portugal', 'português'],
                'brasil': ['brasil', 'brazil', 'brasileiro'],
                'espanha': ['espanha', 'spain'],
                'reino_unido': ['reino unido', 'uk', 'britain'],
                'estados_unidos': ['estados unidos', 'usa', 'us '],
                'suica': ['suíça', 'switzerland'],
                'singapura': ['singapura', 'singapore'],
                'malta': ['malta'],
                'chipre': ['chipre', 'cyprus'],
                'irlanda': ['irlanda', 'ireland']
            }
            
            for country, patterns in country_patterns.items():
                if any(pattern in text_lower for pattern in patterns):
                    entities.append(country)
        
        return entities
    
    def _detect_chunk_topics(self, text: str) -> List[str]:
        """Detecta tópicos tributários no chunk específico."""
        topics = []
        text_lower = text.lower()
        
        topic_patterns = {
            'residencia_fiscal': ['residência fiscal', 'tax residence'],
            'tributacao_renda': ['imposto de renda', 'income tax'],
            'ganhos_capital': ['ganhos de capital', 'capital gains'],
            'dividendos': ['dividendos', 'dividends'],
            'tratados': ['tratado', 'treaty'],
            'compliance': ['compliance', 'declaração'],
            'planejamento': ['planejamento', 'planning'],
            'imigracao': ['imigração', 'immigration', 'visto'],
            'offshore': ['offshore', 'holding']
        }
        
        for topic, patterns in topic_patterns.items():
            if any(pattern in text_lower for pattern in patterns):
                topics.append(topic)
        
        return topics
    
    def _extract_page_number(self, text: str) -> Optional[int]:
        """Extrai número da página do texto."""
        page_match = re.search(r'\[PÁGINA (\d+)\]', text)
        if page_match:
            return int(page_match.group(1))
        return None
    
    def _extract_section_info(self, text: str) -> Optional[str]:
        """Extrai informação da seção do texto."""
        # Procurar headers Markdown
        header_match = re.search(r'^#{1,6}\s+(.+)$', text, re.MULTILINE)
        if header_match:
            return header_match.group(1).strip()
        
        # Procurar numeração de seções
        section_match = re.search(r'^\d+\.\s+([A-Z][^:\n]+)', text, re.MULTILINE)
        if section_match:
            return section_match.group(1).strip()
        
        return None
    
    def _calculate_text_quality(self, text: str) -> float:
        """Calcula qualidade do texto do chunk."""
        if not text:
            return 0.0
        
        score = 1.0
        
        # Penalizar texto muito curto
        if len(text) < 200:
            score *= 0.7
        
        # Penalizar muitos caracteres especiais
        special_chars = len(re.findall(r'[^\w\s\.\,\;\:\!\?\(\)\-\%\$€£]', text))
        if special_chars > len(text) * 0.15:
            score *= 0.6
        
        # Bonificar presença de estrutura
        if re.search(r'^\d+\.', text, re.MULTILINE):  # Listas numeradas
            score *= 1.1
        
        if re.search(r'[A-Z][a-z]+:', text):  # Rótulos
            score *= 1.05
        
        # Penalizar texto fragmentado
        if text.startswith('[...]') or 'ERRO:' in text:
            score *= 0.8
        
        return min(score, 1.0)
    
    def _calculate_information_density(self, text: str) -> float:
        """Calcula densidade de informação do chunk."""
        if not text:
            return 0.0
        
        density = 0.3  # Base
        
        # Bonificar presença de indicadores de contexto
        for indicator_type, pattern in self.context_indicators.items():
            if re.search(pattern, text, re.IGNORECASE):
                density += 0.1
        
        # Bonificar texto substantivo vs. conectivos
        words = text.split()
        if words:
            substantive_words = len([w for w in words if len(w) > 3])
            density += 0.3 * (substantive_words / len(words))
        
        return min(density, 1.0)
    
    def _generate_chunk_id(self, document_id: str, chunk_index: int) -> str:
        """Gera ID único para o chunk."""
        return f"{document_id}_chunk_{chunk_index:04d}"
    
    def optimize_chunks(self, chunks: List[Chunk]) -> List[Chunk]:
        """Otimiza lista de chunks removendo duplicatas e melhorando qualidade."""
        optimized = []
        seen_content = set()
        
        for chunk in chunks:
            # Criar hash do conteúdo para detectar duplicatas
            content_hash = hash(chunk.text[:200])  # Usar primeiros 200 chars
            
            if content_hash not in seen_content and chunk.metadata.text_quality > 0.3:
                seen_content.add(content_hash)
                optimized.append(chunk)
        
        return optimized
    
    def merge_small_chunks(self, chunks: List[Chunk]) -> List[Chunk]:
        """Combina chunks muito pequenos com adjacentes."""
        if not chunks:
            return []
        
        merged = []
        current_chunk = chunks[0]
        
        for next_chunk in chunks[1:]:
            # Se chunk atual é muito pequeno, tentar combinar
            if (len(current_chunk.text) < self.min_chunk_size and 
                len(current_chunk.text + next_chunk.text) <= self.chunk_size * 1.2):
                
                # Combinar textos
                combined_text = current_chunk.text + "\n\n" + next_chunk.text
                
                # Usar metadados do chunk com maior densidade de informação
                if next_chunk.metadata.information_density > current_chunk.metadata.information_density:
                    combined_metadata = next_chunk.metadata
                else:
                    combined_metadata = current_chunk.metadata
                
                combined_metadata.end_char = next_chunk.metadata.end_char
                
                # Criar chunk combinado
                current_chunk = Chunk(
                    id=current_chunk.id,  # Manter ID original
                    text=combined_text,
                    metadata=combined_metadata
                )
            else:
                # Adicionar chunk atual e avançar
                merged.append(current_chunk)
                current_chunk = next_chunk
        
        # Adicionar último chunk
        merged.append(current_chunk)
        
        return merged