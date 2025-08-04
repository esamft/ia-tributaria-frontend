# Base de Conhecimento - Sistema Tributário

## 📄 Documentos Fonte

### EY_Worldwide_Personal_Tax_Guide_2025.pdf
- **Tamanho**: ~12.6MB
- **Fonte**: EY (Ernst & Young)
- **Descrição**: Guia mundial de tributação pessoal e imigração
- **Uso**: Base principal de conhecimento para o agente RAG
- **Status**: ✅ Pronto para processamento

### EY_Guide_backup.pdf
- **Tamanho**: ~12.6MB
- **Fonte**: EY (Ernst & Young) - versão backup
- **Descrição**: Cópia de segurança do guia principal
- **Status**: ✅ Backup disponível

### livro_tributacao_internacional.md
- **Tamanho**: ~500KB (estimado)
- **Fonte**: "O Estrategista" - 40 anos de experiência
- **Descrição**: Livro completo sobre estratégias tributárias internacionais
- **Conteúdo**: Fundamentos, legislação brasileira, guia global por país
- **Status**: ✅ Fonte complementar de alta qualidade

### estrutura_expandida.md
- **Fonte**: Estrutura detalhada do livro de tributação
- **Descrição**: Índice expandido com capítulos e subcapítulos
- **Uso**: Referência para organização do conhecimento
- **Status**: ✅ Guia estrutural

### compass_artifact_wf-*.md
- **Fonte**: Relatório de Pesquisa 2024-2025
- **Descrição**: Análise de tendências e lacunas regulatórias
- **Conteúdo**: Jurisdições emergentes, criptoativos, OCDE Pilar 2
- **Status**: ✅ Informações atualizadas

## 🗃️ Estrutura de Dados

```
data/
├── EY_Worldwide_Personal_Tax_Guide_2025.pdf    # Documento fonte principal
├── chroma_db/                                  # Base vetorial ChromaDB (gerada automaticamente)
├── processed/                                  # Chunks processados (futuro)
├── backup/                                     # Backups da base (futuro)
└── uploads/                                    # Novos documentos (futuro)
```

## 🔄 Processamento

O PDF será processado pelo sistema para:
1. Extração de texto por páginas
2. Chunking inteligente (1200 caracteres + overlap 200)
3. Detecção automática de país/jurisdição
4. Geração de embeddings (OpenAI text-embedding-3-small)
5. Armazenamento em ChromaDB com metadados estruturados

## 📊 Metadados Esperados

Cada chunk terá:
- **país**: Jurisdição identificada automaticamente
- **tópico**: Residência, Tributação, Imigração, etc.
- **página**: Referência no documento original
- **tipo**: Seção, tabela, caso prático, etc.
- **confiança**: Score de qualidade da extração