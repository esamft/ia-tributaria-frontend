'use client'

import { useState, useRef, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Separator } from '@/components/ui/separator'
import { 
  Send, 
  Bot, 
  User, 
  Scale, 
  Globe, 
  BookOpen,
  Settings,
  MessageSquare,
  FileText,
  Clock,
  Filter
} from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { ThemeToggle } from './theme-toggle'
import { KnowledgeManager } from './knowledge-manager'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  sources?: Source[]
  confidence?: number
}

interface Source {
  document: string
  page?: number
  section?: string
  confidence: number
}

export function TaxChatInterface() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: 'Olá! Sou sua IA especialista em tributação internacional. Posso ajudá-lo com consultas sobre residência fiscal, tratados de bitributação, planejamento tributário e muito mais. Como posso ajudá-lo hoje?',
      timestamp: new Date(),
      confidence: 1.0
    }
  ])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [selectedCountries, setSelectedCountries] = useState<string[]>([])
  const scrollAreaRef = useRef<HTMLDivElement>(null)

  const countries = [
    { code: 'pt', name: 'Portugal', flag: '🇵🇹' },
    { code: 'br', name: 'Brasil', flag: '🇧🇷' },
    { code: 'es', name: 'Espanha', flag: '🇪🇸' },
    { code: 'us', name: 'EUA', flag: '🇺🇸' },
    { code: 'ch', name: 'Suíça', flag: '🇨🇭' },
    { code: 'ie', name: 'Irlanda', flag: '🇮🇪' },
  ]

  useEffect(() => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight
    }
  }, [messages])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input.trim(),
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    try {
      // Chamar nossa API interna que se conecta ao backend Python
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          messages: [...messages, userMessage],
          countries: selectedCountries
        })
      })

      if (!response.ok) {
        throw new Error('Erro na resposta da API')
      }

      const data = await response.json()

      if (data.error) {
        throw new Error(data.message || 'Erro desconhecido')
      }

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.content,
        timestamp: new Date(),
        sources: data.sources?.map((source: any) => ({
          document: source.document,
          page: source.page,
          section: source.section,
          confidence: source.confidence
        })) || [],
        confidence: data.confidence
      }

      setMessages(prev => [...prev, assistantMessage])
    } catch (error) {
      console.error('Erro ao enviar mensagem:', error)
      
      // Mensagem de erro para o usuário
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: '❌ Desculpe, ocorreu um erro ao processar sua consulta. Tente novamente em alguns instantes.\n\nSe o problema persistir, verifique se o backend Python está executando ou entre em contato com o suporte.',
        timestamp: new Date(),
        confidence: 0
      }
      
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const toggleCountry = (countryCode: string) => {
    setSelectedCountries(prev => 
      prev.includes(countryCode) 
        ? prev.filter(c => c !== countryCode)
        : [...prev, countryCode]
    )
  }

  return (
    <div className="flex h-full bg-background">
      {/* Sidebar */}
      <div className="w-80 border-r border-border bg-card flex flex-col">
        {/* Header */}
        <div className="p-6 border-b border-border">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-10 h-10 rounded-lg bg-primary flex items-center justify-center">
              <Scale className="w-6 h-6 text-primary-foreground" />
            </div>
            <div>
              <h1 className="text-xl font-serif font-bold text-foreground">
                IA Tributária
              </h1>
              <p className="text-sm text-muted-foreground">
                Especialista Internacional
              </p>
            </div>
          </div>
        </div>

        {/* Country Filters */}
        <div className="p-4 border-b border-border">
          <div className="flex items-center gap-2 mb-3">
            <Filter className="w-4 h-4 text-muted-foreground" />
            <span className="text-sm font-medium text-foreground">
              Filtrar por País
            </span>
          </div>
          <div className="grid grid-cols-2 gap-2">
            {countries.map(country => (
              <Button
                key={country.code}
                variant={selectedCountries.includes(country.code) ? "default" : "outline"}
                size="sm"
                onClick={() => toggleCountry(country.code)}
                className="justify-start gap-2 h-8"
              >
                <span className="text-base">{country.flag}</span>
                <span className="text-xs">{country.name}</span>
              </Button>
            ))}
          </div>
        </div>

        {/* Quick Actions */}
        <div className="p-4 space-y-2">
          <h3 className="text-sm font-medium text-foreground mb-3">
            Consultas Rápidas
          </h3>
          <Button variant="ghost" size="sm" className="w-full justify-start gap-2">
            <Globe className="w-4 h-4" />
            Residência Fiscal
          </Button>
          <Button variant="ghost" size="sm" className="w-full justify-start gap-2">
            <FileText className="w-4 h-4" />
            Tratados Fiscais
          </Button>
          <Button variant="ghost" size="sm" className="w-full justify-start gap-2">
            <BookOpen className="w-4 h-4" />
            Planejamento
          </Button>
          <Button variant="ghost" size="sm" className="w-full justify-start gap-2">
            <Settings className="w-4 h-4" />
            Exit Tax
          </Button>
        </div>

        {/* Knowledge Manager */}
        <div className="p-4 border-t border-border">
          <KnowledgeManager />
        </div>

        {/* Stats */}
        <div className="mt-auto p-4 border-t border-border">
          <div className="grid grid-cols-2 gap-4 text-center">
            <div>
              <div className="text-lg font-bold text-primary">{messages.length - 1}</div>
              <div className="text-xs text-muted-foreground">Consultas</div>
            </div>
            <div>
              <div className="text-lg font-bold text-accent">25</div>
              <div className="text-xs text-muted-foreground">Países</div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Chat Header */}
        <div className="p-4 border-b border-border bg-card/50">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
                <Bot className="w-5 h-5 text-primary" />
              </div>
              <div>
                <h2 className="text-lg font-medium text-foreground">
                  Consulta Tributária
                </h2>
                <p className="text-sm text-muted-foreground">
                  Base: EY Guide 2025 • O Estrategista • Tendências 2024-25
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              {selectedCountries.length > 0 && (
                <div className="flex gap-1">
                  {selectedCountries.map(code => {
                    const country = countries.find(c => c.code === code)
                    return (
                      <span key={code} className="text-base">
                        {country?.flag}
                      </span>
                    )
                  })}
                </div>
              )}
              <ThemeToggle />
            </div>
          </div>
        </div>

        {/* Messages */}
        <ScrollArea className="flex-1 p-4" ref={scrollAreaRef}>
          <div className="space-y-6 max-w-4xl mx-auto">
            <AnimatePresence>
              {messages.map((message) => (
                <motion.div
                  key={message.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  transition={{ duration: 0.3 }}
                  className={`flex gap-4 ${
                    message.role === 'user' ? 'flex-row-reverse' : 'flex-row'
                  }`}
                >
                  <Avatar className="w-8 h-8 mt-1">
                    <AvatarFallback className={
                      message.role === 'user' 
                        ? 'bg-secondary text-secondary-foreground' 
                        : 'bg-primary text-primary-foreground'
                    }>
                      {message.role === 'user' ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
                    </AvatarFallback>
                  </Avatar>

                  <div className={`flex-1 max-w-[80%] ${
                    message.role === 'user' ? 'text-right' : 'text-left'
                  }`}>
                    <Card className={
                      message.role === 'user'
                        ? 'bg-primary text-primary-foreground'
                        : 'bg-card'
                    }>
                      <CardContent className="p-4">
                        <div className="whitespace-pre-wrap text-sm leading-relaxed">
                          {message.content}
                        </div>
                        
                        {message.sources && message.sources.length > 0 && (
                          <div className="mt-4 pt-3 border-t border-border/50">
                            <div className="text-xs font-medium text-muted-foreground mb-2">
                              📚 Fontes Citadas:
                            </div>
                            <div className="space-y-1">
                              {message.sources.map((source, idx) => (
                                <div key={idx} className="text-xs text-muted-foreground">
                                  <span className="font-medium">{idx + 1}.</span>{' '}
                                  {source.document}
                                  {source.page && `, página ${source.page}`}
                                  {source.section && ` - ${source.section}`}
                                  <span className="ml-2 text-accent">
                                    ({(source.confidence * 100).toFixed(0)}%)
                                  </span>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                      </CardContent>
                    </Card>
                    
                    <div className="flex items-center gap-2 mt-2 text-xs text-muted-foreground">
                      <Clock className="w-3 h-3" />
                      {message.timestamp.toLocaleTimeString('pt-BR', { 
                        hour: '2-digit', 
                        minute: '2-digit' 
                      })}
                      {message.confidence && (
                        <>
                          <Separator orientation="vertical" className="h-3" />
                          <span>
                            Confiança: {(message.confidence * 100).toFixed(0)}%
                          </span>
                        </>
                      )}
                    </div>
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>

            {isLoading && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex gap-4"
              >
                <Avatar className="w-8 h-8 mt-1">
                  <AvatarFallback className="bg-primary text-primary-foreground">
                    <Bot className="w-4 h-4" />
                  </AvatarFallback>
                </Avatar>
                <Card className="bg-card">
                  <CardContent className="p-4">
                    <div className="flex items-center gap-2 text-sm text-muted-foreground">
                      <div className="w-2 h-2 bg-primary rounded-full animate-pulse" />
                      <div className="w-2 h-2 bg-primary rounded-full animate-pulse" style={{ animationDelay: '0.2s' }} />
                      <div className="w-2 h-2 bg-primary rounded-full animate-pulse" style={{ animationDelay: '0.4s' }} />
                      <span className="ml-2">Analisando base de conhecimento...</span>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            )}
          </div>
        </ScrollArea>

        {/* Input Form */}
        <div className="p-4 border-t border-border bg-card/50">
          <form onSubmit={handleSubmit} className="max-w-4xl mx-auto">
            <div className="flex gap-2">
              <Input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Digite sua pergunta sobre tributação internacional..."
                className="flex-1"
                disabled={isLoading}
              />
              <Button 
                type="submit" 
                disabled={!input.trim() || isLoading}
                className="px-6"
              >
                <Send className="w-4 h-4" />
              </Button>
            </div>
            <div className="flex items-center justify-between mt-2 text-xs text-muted-foreground">
              <span>
                💡 Exemplos: "Residência fiscal Portugal", "Tratado Brasil-EUA", "Exit tax brasileiro"
              </span>
              <span>
                Powered by IA • {selectedCountries.length > 0 && `Filtros: ${selectedCountries.length} país(es)`}
              </span>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}