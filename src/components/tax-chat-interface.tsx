'use client'

import { useState, useRef, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { ScrollArea } from '@/components/ui/scroll-area'
import { 
  Send, 
  Bot, 
  User, 
  Menu,
  Plus,
  ExternalLink,
  Copy,
  RefreshCw,
  Download,
  Check,
  Database,
  Settings
} from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { ThemeToggle } from './theme-toggle'
import { DatabaseSelector } from './database-selector'
import Image from 'next/image'

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

interface Conversation {
  id: string
  title: string
  lastMessage: string
  timestamp: Date
}

export function TaxChatInterface() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [sidebarOpen, setSidebarOpen] = useState(true) // Sidebar aberta por padrão
  const [databaseSelectorOpen, setDatabaseSelectorOpen] = useState(false)
  const [selectedDatabases, setSelectedDatabases] = useState<string[]>([
    'ey-worldwide-personal-tax-guide-2025',
    'tributacao-internacional-pdf',
    'lei-14754-2023-parte1',
    'lei-14754-2023-novo-regime',
    'l14754-complementar',
    'fatca-crs-ipld',
    'fatca-crs-ipld1'
  ])
  const [conversations] = useState<Conversation[]>([
    {
      id: '1',
      title: 'Residência Fiscal Portugal',
      lastMessage: 'Quais são os requisitos para...',
      timestamp: new Date(Date.now() - 86400000)
    },
    {
      id: '2', 
      title: 'Tratado Brasil-EUA',
      lastMessage: 'Como funciona o tie-breaker...',
      timestamp: new Date(Date.now() - 172800000)
    },
    {
      id: '3',
      title: 'Exit Tax Brasileiro',
      lastMessage: 'Quando se aplica o exit tax...',
      timestamp: new Date(Date.now() - 259200000)
    },
    {
      id: '4',
      title: 'Planejamento Fiscal Internacional',
      lastMessage: 'Estratégias para otimização...',
      timestamp: new Date(Date.now() - 345600000)
    }
  ])
  const [activeConversation, setActiveConversation] = useState<string | null>(null)
  const scrollAreaRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight
    }
  }, [messages])

  // Atalhos de teclado
  useEffect(() => {
    const handleKeyboard = (e: KeyboardEvent) => {
      // Ctrl/Cmd + K = Nova conversa
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault()
        startNewConversation()
      }
      
      // Ctrl/Cmd + B = Toggle sidebar
      if ((e.ctrlKey || e.metaKey) && e.key === 'b') {
        e.preventDefault()
        setSidebarOpen(!sidebarOpen)
      }

      // Escape = Fechar sidebar se estiver aberta
      if (e.key === 'Escape' && sidebarOpen) {
        setSidebarOpen(false)
      }
    }

    document.addEventListener('keydown', handleKeyboard)
    return () => document.removeEventListener('keydown', handleKeyboard)
  }, [sidebarOpen])

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
          selectedDatabases: selectedDatabases
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
        sources: data.sources?.map((source: Source) => ({
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

  const startNewConversation = () => {
    setMessages([])
    setActiveConversation(null)
    setSidebarOpen(false)
  }

  const [copiedMessageId, setCopiedMessageId] = useState<string | null>(null)

  const copyMessage = (content: string, messageId: string) => {
    navigator.clipboard.writeText(content)
    setCopiedMessageId(messageId)
    setTimeout(() => setCopiedMessageId(null), 2000)
  }

  const regenerateResponse = async (messageId: string) => {
    const messageIndex = messages.findIndex(m => m.id === messageId)
    if (messageIndex === -1) return
    
    // Remove a resposta atual e reprocessa
    const messagesUpToUser = messages.slice(0, messageIndex)
    setMessages(messagesUpToUser)
    
    const lastUserMessage = messagesUpToUser[messagesUpToUser.length - 1]
    if (lastUserMessage) {
      setIsLoading(true)
      // Aqui você chamaria a API novamente
      setTimeout(() => {
        setMessages(prev => [...prev, {
          id: Date.now().toString(),
          role: 'assistant',
          content: 'Resposta regenerada: ' + lastUserMessage.content,
          timestamp: new Date()
        }])
        setIsLoading(false)
      }, 1000)
    }
  }

  const exportMessage = (content: string) => {
    const blob = new Blob([content], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'resposta-tributaria.txt'
    a.click()
    URL.revokeObjectURL(url)
  }


  return (
    <div className="flex h-full bg-background">
      {/* Sidebar - ChatGPT Style */}
      <div className={`${sidebarOpen ? 'w-64' : 'w-0'} transition-all duration-300 bg-muted/30 border-r border-border/50 flex flex-col overflow-hidden`}>
        {sidebarOpen && (
          <>
            {/* Sidebar Header */}
            <div className="p-3">
              <Button
                onClick={startNewConversation}
                className="w-full justify-start gap-2 h-10"
                variant="outline"
              >
                <Plus className="w-4 h-4" />
                Nova conversa
              </Button>
            </div>

            {/* Conversation History */}
            <ScrollArea className="flex-1 px-2">
              <div className="space-y-1">
                {conversations.map((conv) => (
                  <button
                    key={conv.id}
                    onClick={() => setActiveConversation(conv.id)}
                    className={`w-full text-left p-3 rounded-lg hover:bg-accent/50 transition-colors group ${
                      activeConversation === conv.id ? 'bg-accent' : ''
                    }`}
                  >
                    <div className="font-medium text-sm truncate mb-1">
                      {conv.title}
                    </div>
                    <div className="text-xs text-muted-foreground truncate">
                      {conv.lastMessage}
                    </div>
                  </button>
                ))}
              </div>
            </ScrollArea>

            {/* Sidebar Footer */}
            <div className="p-3 border-t border-border/50">
              <div className="text-xs text-muted-foreground">
                Powered by OpenAI
              </div>
            </div>
          </>
        )}
      </div>

      {/* Main Chat Area - ChatGPT Style */}
      <div className="flex-1 flex flex-col relative">
        {/* Top Header with System Name */}
        <div className="absolute top-4 right-6 z-10">
          <div className="flex items-center gap-3">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setDatabaseSelectorOpen(true)}
              className="gap-2 text-xs"
            >
              <Database className="w-3 h-3" />
              Bases ({selectedDatabases.length})
            </Button>
            <span className="text-sm font-medium text-muted-foreground">
              Inteligência Tributária
            </span>
            <ThemeToggle />
          </div>
        </div>

        {/* Chat Toggle Button */}
        <div className="absolute top-4 left-4 z-10">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="w-8 h-8 p-0"
          >
            <Menu className="w-4 h-4" />
          </Button>
        </div>

        {/* Messages Area - Centralized ChatGPT Style */}
        <ScrollArea className="flex-1 pt-16" ref={scrollAreaRef}>
          <div className="max-w-3xl mx-auto px-4">
            {messages.length === 0 ? (
              /* ChatGPT Welcome Screen - Logo Only */
              <div className="flex flex-col items-center justify-center min-h-[calc(100vh-200px)]">
                <div>
                  <Image
                    src="/logo.png"
                    alt="Inteligência Tributária"
                    width={200}
                    height={100}
                    className="opacity-80"
                    priority
                  />
                </div>
              </div>
            ) : (
              /* Messages - ChatGPT Style */
              <div className="space-y-6 py-8">
                <AnimatePresence>
                  {messages.map((message) => (
                    <motion.div
                      key={message.id}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="group"
                    >
                      <div className={`flex gap-4 ${
                        message.role === 'user' ? 'justify-end' : 'justify-start'
                      }`}>
                        {message.role === 'assistant' && (
                          <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0 mt-1">
                            <Bot className="w-4 h-4 text-primary" />
                          </div>
                        )}
                        
                        <div className={`max-w-[75%] ${
                          message.role === 'user' ? 'bg-primary text-primary-foreground' : 'bg-muted/50'
                        } rounded-2xl px-4 py-3 relative`}>
                          {/* Message Actions */}
                          <div className="absolute -right-16 top-2 opacity-0 group-hover:opacity-100 transition-opacity flex gap-1">
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => copyMessage(message.content, message.id)}
                              className="w-8 h-8 p-0"
                              title="Copiar mensagem"
                            >
                              {copiedMessageId === message.id ? (
                                <Check className="w-3 h-3 text-green-500" />  
                              ) : (
                                <Copy className="w-3 h-3" />
                              )}
                            </Button>
                            {message.role === 'assistant' && (
                              <>
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  onClick={() => regenerateResponse(message.id)}
                                  className="w-8 h-8 p-0"
                                  title="Regenerar resposta"
                                >
                                  <RefreshCw className="w-3 h-3" />
                                </Button>
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  onClick={() => exportMessage(message.content)}
                                  className="w-8 h-8 p-0"
                                  title="Exportar resposta"
                                >
                                  <Download className="w-3 h-3" />
                                </Button>
                              </>
                            )}
                          </div>

                          <div className="whitespace-pre-wrap text-sm leading-relaxed">
                            {message.content}
                          </div>
                          
                          {/* Sources */}
                          {message.sources && message.sources.length > 0 && (
                            <div className="mt-3 pt-3 border-t border-border/20">
                              <div className="text-xs font-medium text-muted-foreground mb-2 flex items-center gap-1">
                                <ExternalLink className="w-3 h-3" />
                                Fontes consultadas:
                              </div>
                              <div className="space-y-1">
                                {message.sources.slice(0, 3).map((source, idx) => (
                                  <div key={idx} className="text-xs text-muted-foreground">
                                    <span className="font-medium">{idx + 1}.</span>{' '}
                                    {source.document}
                                    {source.page && ` (p. ${source.page})`}
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                        
                        {message.role === 'user' && (
                          <div className="w-8 h-8 rounded-full bg-secondary flex items-center justify-center flex-shrink-0 mt-1">
                            <User className="w-4 h-4" />
                          </div>
                        )}
                      </div>
                    </motion.div>
                  ))}
                </AnimatePresence>

                {/* Loading */}
                {isLoading && (
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="flex gap-4"
                  >
                    <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
                      <Bot className="w-4 h-4 text-primary" />
                    </div>
                    <div className="bg-muted/50 rounded-2xl px-4 py-3">
                      <div className="flex items-center gap-2 text-sm text-muted-foreground">
                        <div className="flex gap-1">
                          <div className="w-2 h-2 bg-primary/60 rounded-full animate-pulse" />
                          <div className="w-2 h-2 bg-primary/60 rounded-full animate-pulse" style={{ animationDelay: '0.2s' }} />
                          <div className="w-2 h-2 bg-primary/60 rounded-full animate-pulse" style={{ animationDelay: '0.4s' }} />
                        </div>
                        <span>Pensando...</span>
                      </div>
                    </div>
                  </motion.div>
                )}
              </div>
            )}
          </div>
        </ScrollArea>

        {/* Input Area - Fixed Bottom ChatGPT Style */}
        <div className="sticky bottom-0 bg-background border-t border-border/20 p-4">
          <form onSubmit={handleSubmit} className="max-w-3xl mx-auto">
            <div className="relative">
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault()
                    handleSubmit(e as React.FormEvent)
                  }
                }}
                placeholder="Envie uma mensagem para Inteligência Tributária"
                className="w-full pr-12 min-h-12 max-h-32 py-3 px-4 rounded-2xl border border-border/30 focus:border-border shadow-sm bg-background focus:bg-background hover:bg-muted/10 transition-all resize-none focus:outline-none"
                disabled={isLoading}
                rows={1}
                style={{
                  height: 'auto',
                  minHeight: '48px'
                }}
                onInput={(e) => {
                  const target = e.target as HTMLTextAreaElement
                  target.style.height = 'auto'
                  target.style.height = Math.min(target.scrollHeight, 128) + 'px'
                }}
              />
              <Button
                type="submit"
                disabled={!input.trim() || isLoading}
                variant="ghost"
                className={`absolute right-2 top-1/2 -translate-y-1/2 w-8 h-8 p-0 hover:bg-transparent transition-colors ${
                  input.trim() && !isLoading ? 'text-foreground' : 'text-muted-foreground'
                }`}
              >
                <Send className="w-4 h-4" />
              </Button>
            </div>
            <div className="text-center mt-2 space-y-1">
              <p className="text-xs text-muted-foreground/60">
                Inteligência Tributária pode cometer erros. Considere verificar informações importantes.
              </p>
              <div className="flex items-center justify-center gap-4 text-xs text-muted-foreground/40">
                <span>↵ Enviar</span>
                <span>Shift + ↵ Nova linha</span>
                <span>Ctrl + K Nova conversa</span>
                <span>Ctrl + B Toggle sidebar</span>
              </div>
            </div>
          </form>
        </div>
      </div>

      {/* Database Selector Modal */}
      <DatabaseSelector
        selectedDatabases={selectedDatabases}
        onDatabasesChange={setSelectedDatabases}
        isOpen={databaseSelectorOpen}
        onClose={() => setDatabaseSelectorOpen(false)}
      />
    </div>
  )
}