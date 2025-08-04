'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import { DocumentUpload } from './document-upload'
import { 
  BookOpen, 
  Plus, 
  Database,
  FileText,
  TrendingUp
} from 'lucide-react'
import { motion } from 'framer-motion'

interface Document {
  id: string
  name: string
  type: 'pdf' | 'md' | 'txt' | 'docx'
  size: number
  status: 'uploading' | 'processing' | 'completed' | 'error'
  progress: number
  error?: string
  chunks?: number
  addedAt: Date
}

export function KnowledgeManager() {
  const [isOpen, setIsOpen] = useState(false)
  const [documents, setDocuments] = useState<Document[]>([])

  const handleDocumentsChange = (newDocuments: Document[]) => {
    setDocuments(newDocuments)
  }

  const completedDocs = documents.filter(d => d.status === 'completed')
  const totalChunks = documents.reduce((sum, d) => sum + (d.chunks || 0), 0)

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button 
          variant="ghost" 
          size="sm" 
          className="w-full justify-start gap-2 hover:bg-accent/50"
        >
          <Database className="w-4 h-4" />
          Gerenciar Base de Conhecimento
          {completedDocs.length > 0 && (
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              className="ml-auto w-5 h-5 rounded-full bg-primary text-primary-foreground text-xs flex items-center justify-center"
            >
              {completedDocs.length}
            </motion.div>
          )}
        </Button>
      </DialogTrigger>
      
      <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <BookOpen className="w-5 h-5 text-primary" />
            Base de Conhecimento Tributário
          </DialogTitle>
          <DialogDescription>
            Adicione documentos confiáveis para enriquecer as respostas da IA. 
            Suporte para PDFs, Markdown e arquivos de texto.
          </DialogDescription>
        </DialogHeader>

        {/* Knowledge Base Stats */}
        {documents.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-primary/5 border border-primary/20 rounded-lg p-4"
            >
              <div className="flex items-center gap-2 mb-2">
                <FileText className="w-4 h-4 text-primary" />
                <span className="text-sm font-medium text-foreground">Documentos</span>
              </div>
              <div className="text-2xl font-bold text-primary">{completedDocs.length}</div>
              <div className="text-xs text-muted-foreground">
                {documents.length - completedDocs.length > 0 && 
                  `${documents.length - completedDocs.length} processando`
                }
              </div>
            </motion.div>

            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="bg-accent/5 border border-accent/20 rounded-lg p-4"
            >
              <div className="flex items-center gap-2 mb-2">
                <Database className="w-4 h-4 text-accent" />
                <span className="text-sm font-medium text-foreground">Chunks</span>
              </div>
              <div className="text-2xl font-bold text-accent">{totalChunks}</div>
              <div className="text-xs text-muted-foreground">Fragmentos indexados</div>
            </motion.div>

            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="bg-green-500/5 border border-green-500/20 rounded-lg p-4"
            >
              <div className="flex items-center gap-2 mb-2">
                <TrendingUp className="w-4 h-4 text-green-500" />
                <span className="text-sm font-medium text-foreground">Qualidade</span>
              </div>
              <div className="text-2xl font-bold text-green-500">
                {documents.length > 0 ? Math.round((completedDocs.length / documents.length) * 100) : 0}%
              </div>
              <div className="text-xs text-muted-foreground">Taxa de sucesso</div>
            </motion.div>
          </div>
        )}

        {/* Upload Component */}
        <DocumentUpload onDocumentsChange={handleDocumentsChange} />

        {/* Info Section */}
        <div className="mt-6 p-4 bg-muted/30 rounded-lg border border-border">
          <h4 className="text-sm font-medium text-foreground mb-2 flex items-center gap-2">
            <Plus className="w-4 h-4" />
            Como adicionar fontes de qualidade:
          </h4>
          <ul className="text-xs text-muted-foreground space-y-1 ml-6">
            <li>• <strong>PDFs oficiais:</strong> Guias da Receita Federal, EY Guide, documentos da OCDE</li>
            <li>• <strong>Legislação:</strong> Códigos tributários, regulamentos, portarias</li>
            <li>• <strong>Tratados:</strong> Acordos de bitributação entre países</li>
            <li>• <strong>Jurisprudência:</strong> Decisões do CARF, STJ, tribunais</li>
            <li>• <strong>Artigos técnicos:</strong> Análises de especialistas, pareceres</li>
          </ul>
        </div>

        <div className="flex justify-end gap-2 pt-4 border-t border-border">
          <Button 
            variant="outline" 
            onClick={() => setIsOpen(false)}
          >
            Fechar
          </Button>
          <Button 
            onClick={() => setIsOpen(false)}
            disabled={completedDocs.length === 0}
          >
            Aplicar Mudanças ({completedDocs.length})
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  )
}