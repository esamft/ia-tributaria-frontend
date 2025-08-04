'use client'

import { useState, useCallback } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Progress } from '@/components/ui/progress'
import { Badge } from '@/components/ui/badge'
import { 
  Upload, 
  FileText, 
  CheckCircle, 
  XCircle, 
  Loader2,
  AlertCircle,
  Trash2,
  BookOpen
} from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'

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

interface DocumentUploadProps {
  onDocumentsChange?: (documents: Document[]) => void
}

export function DocumentUpload({ onDocumentsChange }: DocumentUploadProps) {
  const [documents, setDocuments] = useState<Document[]>([])
  const [dragActive, setDragActive] = useState(false)

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const getFileType = (filename: string): Document['type'] => {
    const ext = filename.toLowerCase().split('.').pop()
    switch (ext) {
      case 'pdf': return 'pdf'
      case 'md': return 'md'
      case 'txt': return 'txt'
      case 'docx': return 'docx'
      default: return 'txt'
    }
  }

  const uploadToBackend = async (file: File, doc: Document) => {
    try {
      // Atualizar progresso para upload
      setDocuments(prev => prev.map(d => 
        d.id === doc.id ? { ...d, status: 'uploading', progress: 50 } : d
      ))

      const formData = new FormData()
      formData.append('file', file)

      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'
      const response = await fetch(`${apiUrl}/upload`, {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        throw new Error(`Erro HTTP: ${response.status}`)
      }

      const result = await response.json()

      // Atualizar com resultado do backend
      setDocuments(prev => prev.map(d => 
        d.id === doc.id ? { 
          ...d, 
          status: 'completed',
          progress: 100,
          chunks: result.chunks_generated
        } : d
      ))

    } catch (error) {
      console.error('Erro no upload:', error)
      setDocuments(prev => prev.map(d => 
        d.id === doc.id ? { 
          ...d, 
          status: 'error',
          error: error instanceof Error ? error.message : 'Erro no upload',
          progress: 100
        } : d
      ))
    }
  }

  const handleFiles = useCallback((files: FileList) => {
    const filesArray = Array.from(files)
    
    const newDocuments: Document[] = filesArray.map(file => ({
      id: Math.random().toString(36).substr(2, 9),
      name: file.name,
      type: getFileType(file.name),
      size: file.size,
      status: 'uploading' as const,
      progress: 0,
      addedAt: new Date()
    }))

    setDocuments(prev => {
      const updated = [...prev, ...newDocuments]
      onDocumentsChange?.(updated)
      return updated
    })

    // Upload real para cada arquivo
    newDocuments.forEach((doc, index) => {
      uploadToBackend(filesArray[index], doc)
    })
  }, [onDocumentsChange])

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFiles(e.dataTransfer.files)
    }
  }, [handleFiles])

  const handleFileInput = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFiles(e.target.files)
    }
  }, [handleFiles])

  const removeDocument = (id: string) => {
    setDocuments(prev => {
      const updated = prev.filter(d => d.id !== id)
      onDocumentsChange?.(updated)
      return updated
    })
  }

  const getStatusIcon = (status: Document['status']) => {
    switch (status) {
      case 'uploading':
      case 'processing':
        return <Loader2 className="w-4 h-4 animate-spin text-primary" />
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-green-500" />
      case 'error':
        return <XCircle className="w-4 h-4 text-red-500" />
    }
  }

  const getStatusText = (doc: Document) => {
    switch (doc.status) {
      case 'uploading':
        return `Enviando... ${doc.progress}%`
      case 'processing':
        return 'Processando documento...'
      case 'completed':
        return `Processado • ${doc.chunks} chunks gerados`
      case 'error':
        return doc.error || 'Erro no processamento'
    }
  }

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <BookOpen className="w-5 h-5 text-primary" />
          Adicionar Fontes Confiáveis
        </CardTitle>
        <p className="text-sm text-muted-foreground">
          Faça upload de documentos PDF, Markdown ou texto para enriquecer a base de conhecimento tributário
        </p>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Upload Area */}
        <div
          className={`
            relative border-2 border-dashed rounded-lg p-8 text-center transition-all duration-200
            ${dragActive 
              ? 'border-primary bg-primary/5 scale-[1.02]' 
              : 'border-border hover:border-primary/50 hover:bg-accent/20'
            }
          `}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          <div className="space-y-4">
            <div className="w-16 h-16 mx-auto rounded-full bg-primary/10 flex items-center justify-center">
              <Upload className="w-8 h-8 text-primary" />
            </div>
            
            <div>
              <h3 className="text-lg font-medium text-foreground mb-2">
                Arraste documentos aqui
              </h3>
              <p className="text-sm text-muted-foreground mb-4">
                Ou clique para selecionar arquivos
              </p>
              
              <Label htmlFor="file-upload" className="cursor-pointer">
                <Button variant="outline" className="pointer-events-none">
                  Selecionar Arquivos
                </Button>
              </Label>
              
              <Input
                id="file-upload"
                type="file"
                multiple
                accept=".pdf,.md,.txt,.docx"
                onChange={handleFileInput}
                className="hidden"
              />
            </div>
            
            <div className="flex flex-wrap gap-2 justify-center">
              <Badge variant="secondary">PDF</Badge>
              <Badge variant="secondary">Markdown</Badge>
              <Badge variant="secondary">TXT</Badge>
              <Badge variant="secondary">DOCX</Badge>
            </div>
          </div>
        </div>

        {/* Documents List */}
        {documents.length > 0 && (
          <div className="space-y-3">
            <h4 className="text-sm font-medium text-foreground">
              Documentos ({documents.length})
            </h4>
            
            <AnimatePresence>
              {documents.map((doc) => (
                <motion.div
                  key={doc.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  className="border border-border rounded-lg p-4 bg-card"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-start gap-3 flex-1 min-w-0">
                      <div className="w-8 h-8 rounded bg-primary/10 flex items-center justify-center flex-shrink-0">
                        <FileText className="w-4 h-4 text-primary" />
                      </div>
                      
                      <div className="flex-1 min-w-0">
                        <h5 className="text-sm font-medium text-foreground truncate">
                          {doc.name}
                        </h5>
                        <div className="flex items-center gap-2 mt-1">
                          {getStatusIcon(doc.status)}
                          <span className="text-xs text-muted-foreground">
                            {getStatusText(doc)}
                          </span>
                        </div>
                        <p className="text-xs text-muted-foreground mt-1">
                          {formatFileSize(doc.size)} • Adicionado {doc.addedAt.toLocaleTimeString()}
                        </p>
                        
                        {(doc.status === 'uploading' || doc.status === 'processing') && (
                          <Progress value={doc.progress} className="mt-2 h-1" />
                        )}
                      </div>
                    </div>
                    
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => removeDocument(doc.id)}
                      className="text-muted-foreground hover:text-destructive"
                    >
                      <Trash2 className="w-4 h-4" />
                    </Button>
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        )}

        {/* Stats */}
        {documents.length > 0 && (
          <div className="pt-4 border-t border-border">
            <div className="grid grid-cols-3 gap-4 text-center">
              <div>
                <div className="text-lg font-bold text-primary">
                  {documents.filter(d => d.status === 'completed').length}
                </div>
                <div className="text-xs text-muted-foreground">Processados</div>
              </div>
              <div>
                <div className="text-lg font-bold text-accent">
                  {documents.reduce((sum, d) => sum + (d.chunks || 0), 0)}
                </div>
                <div className="text-xs text-muted-foreground">Chunks</div>
              </div>
              <div>
                <div className="text-lg font-bold text-muted-foreground">
                  {documents.filter(d => d.status === 'error').length}
                </div>
                <div className="text-xs text-muted-foreground">Erros</div>
              </div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}