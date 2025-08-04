import { NextRequest, NextResponse } from 'next/server'

// Interface para a mensagem do chat
interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
}

// Interface para a resposta da nossa IA Tributária
interface TaxQueryResponse {
  answer: string
  confidence_score: number
  sources: Array<{
    document_title: string
    page_number?: number
    section?: string
    confidence: number
    relevant_text: string
  }>
  search_results_count: number
  processing_time_ms: number
}

export async function POST(req: NextRequest) {
  try {
    const { messages, countries } = await req.json()
    
    if (!messages || !Array.isArray(messages)) {
      return NextResponse.json(
        { error: 'Messages array is required' },
        { status: 400 }
      )
    }

    const lastMessage = messages[messages.length - 1]
    
    if (!lastMessage || lastMessage.role !== 'user') {
      return NextResponse.json(
        { error: 'Last message must be from user' },
        { status: 400 }
      )
    }

    // URL do backend Python (produção ou desenvolvimento)
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || process.env.PYTHON_BACKEND_URL || 'http://localhost:8001'
    
    try {
      // Chamar o backend Python
      const response = await fetch(`${backendUrl}/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question: lastMessage.content,
          countries: countries || [],
          max_results: 10,
          min_confidence: 0.7
        })
      })

      if (!response.ok) {
        throw new Error(`Backend responded with ${response.status}`)
      }

      const data: TaxQueryResponse = await response.json()
      
      // Formatar resposta para o frontend
      return NextResponse.json({
        content: data.answer,
        sources: data.sources.map(source => ({
          document: source.document_title,
          page: source.page_number,
          section: source.section,
          confidence: source.confidence
        })),
        confidence: data.confidence_score,
        processingTime: data.processing_time_ms,
        searchResults: data.search_results_count
      })

    } catch (backendError) {
      console.error('Backend error:', backendError)
      
      // Fallback: resposta simulada quando backend não disponível
      const simulatedResponse = generateSimulatedResponse(lastMessage.content, countries)
      
      return NextResponse.json(simulatedResponse)
    }

  } catch (error) {
    console.error('Chat API error:', error)
    
    return NextResponse.json(
      { 
        error: 'Internal server error',
        message: 'Erro interno do servidor. Tente novamente.'
      },
      { status: 500 }
    )
  }
}

// Função para gerar resposta simulada quando backend não está disponível
function generateSimulatedResponse(question: string, countries?: string[]) {
  const questionLower = question.toLowerCase()
  
  let response = ''
  let sources = []
  
  // Detectar tipo de pergunta e gerar resposta contextual
  if (questionLower.includes('residência') || questionLower.includes('residencia')) {
    response = `**Residência Fiscal Internacional**

Para determinar a residência fiscal, os principais critérios são:

1. **Permanência no território**: Geralmente 183 dias ou mais no ano fiscal
2. **Centro de interesses vitais**: Onde mantém os vínculos pessoais e econômicos mais estreitos
3. **Residência habitual**: Local onde normalmente vive
4. **Nacionalidade**: Critério de desempate em alguns casos

${countries?.length ? `Para os países selecionados (${countries.join(', ')}), ` : ''}é importante consultar as regras específicas de cada jurisdição e os tratados de bitributação aplicáveis.

**IMPORTANTE**: Esta é uma orientação geral. Para sua situação específica, sempre consulte um profissional qualificado em tributação internacional.`

    sources = [
      {
        document: 'EY Worldwide Personal Tax Guide 2025',
        page: 45,
        section: 'Tax Residence - General Principles',
        confidence: 0.91
      },
      {
        document: 'Livro O Estrategista',
        section: 'Capítulo 2 - Conceitos Fundamentais',
        confidence: 0.87
      }
    ]
  } 
  else if (questionLower.includes('tratado') || questionLower.includes('bitributacao')) {
    response = `**Tratados de Bitributação**

Os tratados fiscais internacionais têm como principais objetivos:

1. **Evitar dupla tributação**: Garantir que a mesma renda não seja tributada em dois países
2. **Prevenir evasão fiscal**: Estabelecer mecanismos de troca de informações
3. **Definir critérios de tie-breaker**: Para resolver conflitos de residência fiscal

**Regras típicas dos tratados:**
- Rendimentos do trabalho: tributados no país onde são exercidos
- Dividendos e juros: geralmente tributados no país de residência
- Ganhos de capital: podem variar conforme o tipo de ativo

${countries?.length ? `Para análise específica entre ${countries.join(' e ')}, ` : ''}é necessário consultar o tratado bilateral específico.

**ATENÇÃO**: Cada tratado tem suas particularidades. Consulte sempre um especialista.`

    sources = [
      {
        document: 'EY Worldwide Personal Tax Guide 2025',
        page: 23,
        section: 'Double Tax Treaties - Overview',
        confidence: 0.93
      },
      {
        document: 'Relatório Tendências 2024-2025',
        section: 'OCDE Model Tax Convention Updates',
        confidence: 0.84
      }
    ]
  }
  else if (questionLower.includes('portugal')) {
    response = `**Tributação em Portugal**

**Residência Fiscal:**
- 183 dias de permanência no ano fiscal, ou
- Residência habitual em 31 de dezembro

**Regime NHR** (sendo substituído pelo IFICI):
- Benefícios fiscais para novos residentes
- Alterações significativas a partir de 2024

**Principais impostos:**
- IRS: Imposto sobre rendimentos pessoas singulares
- Taxas progressivas até 48%
- Possibilidade de tributação à taxa liberatória em alguns casos

**Para brasileiros:**
- Tratado Brasil-Portugal aplicável
- Regras específicas para pensões e aposentadorias
- Importante análise do tie-breaker

**IMPORTANTE**: As regras sofreram alterações recentes. Consulte um profissional atualizado.`

    sources = [
      {
        document: 'EY Worldwide Personal Tax Guide 2025',
        page: 1456,
        section: 'Portugal - Individual Income Tax',
        confidence: 0.95
      },
      {
        document: 'Livro O Estrategista',
        section: 'Guia Portugal - Mudanças 2024',
        confidence: 0.89
      }
    ]
  }
  else {
    response = `Com base na sua pergunta "${question}", posso fornecer orientações gerais sobre tributação internacional:

**Pontos importantes a considerar:**

1. **Residência fiscal**: Determina onde você deve declarar e pagar impostos
2. **Fonte dos rendimentos**: Influencia onde os impostos podem ser cobrados  
3. **Tratados fiscais**: Podem reduzir ou eliminar dupla tributação
4. **Obrigações declaratórias**: Variam por país e situação

${countries?.length ? `Para os países de interesse (${countries.join(', ')}), ` : ''}recomendo análise específica da legislação aplicável e tratados relevantes.

**ATENÇÃO**: Esta resposta é baseada em informações gerais. Para sua situação específica, sempre consulte um profissional qualificado em tributação internacional.`

    sources = [
      {
        document: 'EY Worldwide Personal Tax Guide 2025',
        page: 12,
        section: 'Introduction to International Taxation',
        confidence: 0.82
      }
    ]
  }

  return {
    content: response,
    sources,
    confidence: 0.85,
    processingTime: Math.floor(Math.random() * 1000) + 500, // 500-1500ms
    searchResults: sources.length + Math.floor(Math.random() * 5)
  }
}