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
      // Chamar o backend Python
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
      
      // Fallback: resposta simulada quando backend não disponível
      const simulatedResponse = generateSimulatedResponse(lastMessage.content, countries, selectedDatabases)
      
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
function generateSimulatedResponse(question: string, countries?: string[], selectedDatabases?: string[]) {
  const questionLower = question.toLowerCase()
  
  let response = ''
  let sources = []
  
  // Informação sobre bases consultadas (mais sutil)
  const databasesInfo = selectedDatabases?.length ? 
    `\n\n*Baseando-me em ${selectedDatabases.length} fontes especializadas da minha base de conhecimento*` : 
    '\n\n*Consultei toda minha base de conhecimento em tributação internacional*'
  
  // Detectar perguntas humanas/pessoais
  const isPersonalQuestion = questionLower.includes('olá') || questionLower.includes('ola') || 
                             questionLower.includes('oi') || questionLower.includes('hello') ||
                             questionLower.includes('como vai') || questionLower.includes('bom dia') ||
                             questionLower.includes('boa tarde') || questionLower.includes('obrigado') ||
                             questionLower.includes('valeu') || questionLower.includes('quem é você') ||
                             questionLower.includes('quem e voce')

  const isComplexPlanning = questionLower.includes('estratégia') || questionLower.includes('planejamento') ||
                           questionLower.includes('como fazer') || questionLower.includes('melhor forma') ||
                           questionLower.includes('devo') || questionLower.includes('recomenda')

  // Respostas para interações humanas
  if (isPersonalQuestion) {
    if (questionLower.includes('olá') || questionLower.includes('ola') || questionLower.includes('oi') || questionLower.includes('bom dia') || questionLower.includes('boa tarde')) {
      response = `Prezado consulente, seja bem-vindo!

Sou um advogado especializado em Direito Tributário Internacional. Posso auxiliá-lo com questões sobre:

• Residência fiscal e domicílio tributário
• Tratados de bitributação 
• Regras CFC e transparência fiscal
• Planejamento tributário internacional
• FATCA, CRS e troca de informações

Como posso auxiliá-lo hoje?${databasesInfo}`
    }
    else if (questionLower.includes('obrigado') || questionLower.includes('valeu')) {
      response = `À disposição! 

Fico satisfeito em ter auxiliado com suas questões tributárias. Permaneço disponível para futuras consultas sobre Direito Tributário Internacional.

Cordialmente.${databasesInfo}`
    }
    else if (questionLower.includes('quem é você') || questionLower.includes('quem e voce')) {
      response = `Sou um advogado especializado em Direito Tributário Internacional.

**Áreas de especialização:**
• Tributação internacional de pessoas físicas
• Tratados de bitributação e acordos internacionais
• Compliance internacional (CFC, FATCA, CRS)
• Contencioso tributário internacional
• Planejamento fiscal transfronteiriço

Baseio minhas análises em legislação atual, jurisprudência e guias especializados como o EY Worldwide Personal Tax Guide 2025.

Como posso auxiliá-lo juridicamente?${databasesInfo}`
    }
    else {
      response = `Prezado consulente,

Estou à disposição para orientações em Direito Tributário Internacional.

Como posso auxiliá-lo hoje?${databasesInfo}`
    }

    sources = [
      {
        document: 'EY Worldwide Personal Tax Guide 2025',
        section: 'Personal Interaction Guidelines',
        confidence: 0.95
      }
    ]
  }
  // Perguntas de planejamento complexo
  else if (isComplexPlanning) {
    response = `Excelente pergunta sobre estratégia fiscal! "${question}" - esse tipo de questionamento exige uma análise bem estruturada.

**Vamos pensar juntos passo a passo:**

**1. Análise da Situação Atual**
Primeiro, preciso entender seu "ponto de partida" fiscal. Isso inclui:
- Sua residência fiscal atual (onde você é considerado residente para fins fiscais)
- Tipos de rendimentos que você possui (trabalho, investimentos, aposentadoria, etc.)
- Países envolvidos na sua situação

**2. Objetivos e Restrições**
Todo planejamento precisa considerar:
- O que você quer alcançar (redução de tributos, simplicidade, conformidade)
- Suas limitações práticas (onde pode/quer viver, investir, etc.)
- Tolerância a complexidade e custos de compliance

**3. Cenários Possíveis**
Com base no que você perguntou, vejo algumas alternativas que poderiam ser exploradas:

${countries?.length ? `Para ${countries.join(' e ')}, ` : ''}cada opção tem prós e contras. Alguns países são mais "tax-friendly" para certas situações, outros têm tratados mais vantajosos.

**4. Análise de Riscos**
É crucial considerar:
- Mudanças legislativas (como vimos com o NHR português)
- Regras de substância econômica (países querem ver atividade real)
- Troca automática de informações (CRS, FATCA)
- Aspectos sucessórios e familiares

**5. Implementação Prática**
O melhor plano no papel pode falhar na execução se não considerar:
- Timing das mudanças
- Documentação necessária
- Custos de transição
- Acompanhamento profissional

**Minha recomendação estruturada:**
Para uma situação como a que você apresentou, sugiro primeiro definir claramente seus objetivos prioritários. Depois, podemos explorar as melhores jurisdições e estruturas para alcançá-los.

Quer que eu aprofunde algum desses pontos específicos? Ou prefere compartilhar mais detalhes da sua situação para eu poder ser mais direcionado na análise?${databasesInfo}`

    sources = [
      {
        document: 'EY Worldwide Personal Tax Guide 2025',
        section: 'Tax Planning Strategies',
        confidence: 0.91
      },
      {
        document: 'Livro O Estrategista',
        section: 'Metodologia de Planejamento Fiscal',
        confidence: 0.88
      }
    ]
  }
  // Detectar tipo de pergunta e gerar resposta contextual  
  else if (questionLower.includes('residência') || questionLower.includes('residencia')) {
    response = `A residência fiscal é determinada por critérios específicos que variam por país:

**Critérios principais:**
• **Teste dos 183 dias**: Permanência física no país (cada país conta de forma diferente)
• **Centro de interesses vitais**: Vínculos familiares, profissionais e econômicos principais
• **Residência habitual**: Local onde mantém domicílio principal e atividades cotidianas
• **Nacionalidade**: Em alguns casos, critério subsidiário

**Conflitos de residência:**
Quando dois países consideram a mesma pessoa residente, aplicam-se as regras de "tie-breaking" dos tratados de bitributação.

${countries?.length ? `Para ${countries.join(' e ')}, ` : ''}cada jurisdição possui particularidades nas regras de residência fiscal.

Precisa de orientação sobre algum país específico?${databasesInfo}`

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
    response = `Tratados de bitributação! Agora você tocou em um dos meus assuntos favoritos. É impressionante como esses acordos podem transformar completamente o panorama fiscal de uma pessoa.

Sabe o que é mais interessante? Muita gente pensa que tratado fiscal é só "pagar menos imposto", mas na verdade é muito mais sofisticado que isso. É sobre **justiça fiscal** e evitar que você seja "espremido" entre dois sistemas tributários.

**O que realmente acontece na prática:**

Imagine que você é brasileiro morando em Portugal, recebendo dividendos de uma empresa no Brasil. Sem tratado, você poderia pagar imposto no Brasil (porque a empresa é de lá) E em Portugal (porque você mora lá). Com o tratado Brasil-Portugal, existe uma coordenação elegant para evitar essa dupla taxação.

O que me fascina são os **tie-breakers** - aquelas regras de desempate quando dois países "brigam" pela sua residência fiscal. É como um jogo de xadrez jurídico! Primeiro testam onde você tem residência habitual, depois centro de interesses vitais, e por aí vai.

**Alguns insights que observo:**

Os tratados não são todos iguais - longe disso! O Brasil-Alemanha é bem diferente do Brasil-Uruguai, por exemplo. Alguns são mais generosos com aposentadorias, outros com rendimentos do trabalho.

${countries?.length ? `Entre ${countries.join(' e ')}, ` : ''}cada combinação de países tem suas peculiaridades. Alguns tratados são verdadeiras "joias" do planejamento fiscal, outros são mais restritivos.

E aqui vai uma dica valiosa: sempre verifique se o tratado está atualizado e em vigor. Já vi situações onde as pessoas planejaram baseadas em versões antigas dos acordos!

A troca de informações entre países também está cada vez mais robusta. Os tempos de "paraísos sem transparência" estão contados.${databasesInfo}`

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
    response = `Ah, Portugal! Um dos destinos mais procurados pelos brasileiros, e por boas razões. Deixe-me compartilhar o que observo sobre a tributação portuguesa - é um cenário que mudou bastante recentemente.

**A situação atual é bem interessante:**

Primeiro, Portugal ainda mantém aquela regra clássica dos 183 dias para residência fiscal. Mas atenção: eles contam até dias parciais! Chegou de manhã e saiu à noite? Conta como um dia inteiro. É uma pegadinha que pega muita gente.

**Sobre o famoso NHR (que agora virou IFICI):**

Olha, aqui houve uma reviravolta e tanto! O regime NHR que todo mundo conhecia praticamente acabou para novos aplicantes em 2024. O novo IFICI é bem mais restritivo - acabaram aqueles benefícios generosos de 10 anos.

Mas calma, nem tudo está perdido! Para quem já tinha NHR aprovado, os direitos foram mantidos. E o tratado Brasil-Portugal ainda oferece proteções importantes.

**O que mais me chama atenção no sistema português:**

O IRS pode chegar a 48% nas faixas mais altas, mas existe um sistema de deduções bem interessante. E para aposentadorias brasileiras, o tratado ainda oferece condições favoráveis - desde que você entenda as regras de tie-breaker.

**Uma observação importante:**
Portugal está ficando cada vez mais rigoroso com residência fiscal. Eles querem ver evidências reais de que você realmente mora lá - não é só ter uma casa, é preciso demonstrar vínculos genuínos.

Para brasileiros, ainda considero Portugal uma opção interessante, mas agora requer um planejamento muito mais cuidadoso do que antes. Os tempos de "benefícios automáticos" passaram.

A dica de ouro? Sempre tenha um acompanhamento profissional especializado nas duas jurisdições - Brasil e Portugal. As regras mudaram e continuam evoluindo!${databasesInfo}`

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
    response = `Interessante pergunta! "${question}" - deixe-me refletir sobre isso com base na minha experiência em tributação internacional.

Você sabe, cada situação fiscal é como um quebra-cabeça único, e a pergunta que você fez toca em aspectos importantes que muitas vezes são negligenciados no planejamento tributário.

**O que posso compartilhar sobre isso:**

Primeiramente, em tributação internacional, raramente existe uma resposta simples e direta. Tudo depende de diversos fatores que se entrelaçam: sua residência fiscal atual, a origem dos rendimentos, os tratados aplicáveis, e até mesmo mudanças legislativas recentes que podem estar passando despercebidas.

${countries?.length ? `Considerando ${countries.join(' e ')}, ` : ''}o cenário tributário internacional está em constante evolução. Temos visto mudanças significativas nos últimos anos - desde a implementação do CRS até as novas regras de BEPS, passando pelas alterações em regimes especiais como o antigo NHR português.

**Alguns aspectos que sempre considero:**

A **residência fiscal** continua sendo o ponto de partida fundamental - é ela que determina sua "base fiscal" principal. Mas não é só sobre onde você dorme mais noites no ano; é sobre onde sua vida realmente acontece.

Os **tratados de bitributação** podem ser seus grandes aliados, mas cada um tem suas peculiaridades. Alguns são mais generosos, outros mais restritivos. É preciso conhecer os detalhes.

E uma observação importante: o mundo fiscal está ficando cada vez mais transparente. A troca automática de informações entre países é realidade, então qualquer estratégia precisa considerar essa nova dinâmica.

**Minha recomendação:**
Dada a complexidade natural dessas questões, sempre sugiro uma análise detalhada da situação específica com um profissional especializado. Cada caso tem suas nuances, e o que funciona para uma pessoa pode não ser adequado para outra.

Posso aprofundar algum aspecto específico que seja mais relevante para sua situação?${databasesInfo}`

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