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
    const { messages, countries, selectedDatabases } = await req.json()
    
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
      // SEMPRE chamar o backend - Sistema Hierárquico decide tudo
      const response = await fetch(`${backendUrl}/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question: lastMessage.content,
          countries: countries || [],
          selectedDatabases: selectedDatabases || [],
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
      
      // Se o backend não estiver disponível, retornar erro claro
      return NextResponse.json({
        content: "❌ **Sistema Temporariamente Indisponível**\n\nO sistema de agentes especializados não está disponível no momento. Por favor, tente novamente em alguns instantes.\n\nSe o problema persistir, verifique se o backend Python está executando.",
        sources: [],
        confidence: 0.0,
        processingTime: 0,
        searchResults: 0
      })
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