# Sistema de Agentes IA para Tributação Internacional

Sistema multi-agente especializado em consultas tributárias internacionais usando RAG (Retrieval-Augmented Generation).

## 🚀 Início Rápido

```bash
# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Mac/Linux

# Instalar dependências
pip install -r requirements.txt

# Configurar environment
cp .env.example .env
# Editar .env com suas API keys

# Executar sistema
python main.py
```

## 📁 Estrutura do Projeto

```
sistema-agentes-tributarios/
├── agents/           # Agentes especializados
├── tools/            # Ferramentas customizadas  
├── models/           # Estruturas Pydantic
├── data/             # Persistência e base de conhecimento
├── ui/               # Interface Streamlit
├── core/             # Orquestrador principal
├── tests/            # Testes automatizados
├── main.py           # Entry point
└── DOCUMENTACAO.md   # Documentação técnica completa
```

## 🤖 Agentes Implementados

- **Consultor Tributário (Nível 2)**: Consultas baseadas em RAG
- *Futuros*: Gestor de Conhecimento, Analista Comparativo, Monitor Regulatório

## 📊 Base de Conhecimento

- EY Worldwide Personal Tax and Immigration Guide
- Legislação tributária por país
- Tratados de bitributação
- Casos práticos

## 🔧 Tecnologias

- **Framework**: Agno
- **IA**: OpenAI GPT-4o, Anthropic Claude
- **RAG**: ChromaDB + embeddings
- **Interface**: Streamlit
- **Dados**: Pydantic + JSON

## 📝 Status

- [x] Estrutura inicial criada
- [ ] Agente Consultor implementado
- [ ] Interface web desenvolvida
- [ ] Base de conhecimento processada

Consulte `DOCUMENTACAO.md` para detalhes técnicos completos.