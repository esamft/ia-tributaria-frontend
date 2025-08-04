'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Checkbox } from '@/components/ui/checkbox'
import { 
  Database,
  FileText,
  BookOpen,
  Gavel,
  Building2,
  Globe,
  CheckCircle2,
  AlertCircle,
  Info
} from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'

interface DatabaseInfo {
  id: string
  name: string
  description: string
  type: 'pdf' | 'txt' | 'guide'
  size: string
  chunks: number
  topics: string[]
  lastUpdated: string
  selected: boolean
  icon: 'law' | 'building' | 'globe' | 'book' | 'file'
}

// Dados reais baseados nos arquivos processados na base de conhecimento
const availableDatabases: DatabaseInfo[] = [
  {
    id: 'ey-worldwide-personal-tax-guide-2025',
    name: 'EY Worldwide Personal Tax Guide 2025',
    description: 'Guia mundial completo de tributação pessoal e imigração por país',
    type: 'pdf',
    size: '12.0 MB',
    chunks: 3583,
    topics: ['Tributação Internacional', 'Direito Tributário', 'Residência Fiscal', 'Planejamento Global'],
    lastUpdated: '2025-08-04',
    selected: true,
    icon: 'globe'
  },
  {
    id: 'tributacao-internacional-pdf',
    name: 'Tributação Internacional (PDF Principal)',
    description: 'Documento base sobre direito tributário internacional',
    type: 'pdf',
    size: '914 KB',
    chunks: 726,
    topics: ['Tributação Internacional', 'Direito Tributário', 'Imposto de Renda'],
    lastUpdated: '2025-08-04',
    selected: true,
    icon: 'law'
  },
  {
    id: 'lei-14754-2023-parte1',
    name: 'Lei 14.754/2023 - CFC Pessoa Física (Parte 1)',
    description: 'Nova lei sobre controladas no exterior para pessoas físicas',
    type: 'txt',
    size: '121 B',
    chunks: 1,
    topics: ['Lei 14.754/2023', 'CFC', 'Controlled Foreign Company', 'Tributação Internacional'],
    lastUpdated: '2025-08-04',
    selected: true,
    icon: 'law'
  },
  {
    id: 'lei-14754-2023-novo-regime',
    name: 'Lei 14.754/2023 - Novo Regime Tributário',
    description: 'Novo regime tributário para investimentos no exterior',
    type: 'txt',
    size: '110 B',
    chunks: 1,
    topics: ['Lei 14.754/2023', 'CFC', 'Controlled Foreign Company', 'Investimentos Exterior'],
    lastUpdated: '2025-08-04',
    selected: true,
    icon: 'law'
  },
  {
    id: 'l14754-complementar',
    name: 'L14754 - Documento Complementar',
    description: 'Informações complementares sobre a Lei 14.754',
    type: 'txt',
    size: '71 B',
    chunks: 1,
    topics: ['Tributação Internacional', 'Direito Tributário'],
    lastUpdated: '2025-08-04',
    selected: true,
    icon: 'law'
  },
  {
    id: 'fatca-crs-ipld',
    name: 'FATCA e CRS - Conformidade Fiscal (IPLD)',
    description: 'Leis de conformidade fiscais FATCA e CRS',
    type: 'txt',
    size: '150 B',
    chunks: 1,
    topics: ['FATCA', 'CRS', 'Common Reporting Standard', 'Compliance', 'Conformidade Fiscal'],
    lastUpdated: '2025-08-04',
    selected: true,
    icon: 'building'
  },
  {
    id: 'fatca-crs-ipld1',
    name: 'FATCA e CRS - Conformidade Fiscal (IPLD1)',
    description: 'Documentos adicionais sobre FATCA e CRS',
    type: 'txt',
    size: '150 B',
    chunks: 1,
    topics: ['FATCA', 'CRS', 'Common Reporting Standard', 'Compliance', 'Troca de Informações'],
    lastUpdated: '2025-08-04',
    selected: true,
    icon: 'building'
  },
  {
    id: 'crs-common-reporting',
    name: 'CRS - Common Reporting Standard',
    description: 'O que é CRS Common Reporting Standard',
    type: 'txt',
    size: '66 B',
    chunks: 1,
    topics: ['CRS', 'Common Reporting Standard', 'Troca de Informações'],
    lastUpdated: '2025-08-04',
    selected: false,
    icon: 'globe'
  },
  {
    id: 'beps-brasil',
    name: 'BEPS e Direito Tributário Brasileiro',
    description: 'Base Erosion and Profit Shifting no contexto brasileiro',
    type: 'txt',
    size: '79 B',
    chunks: 1,
    topics: ['BEPS', 'Base Erosion', 'Profit Shifting'],
    lastUpdated: '2025-08-04',
    selected: false,
    icon: 'globe'
  },
  {
    id: 'estrategias-offshore',
    name: 'Estratégias Offshore - Planejamento Global',
    description: 'Planejamento patrimonial e fiscal no cenário global',
    type: 'txt',
    size: '111 B',
    chunks: 1,
    topics: ['Offshore', 'Planejamento Patrimonial', 'Estruturas Internacionais'],
    lastUpdated: '2025-08-04',
    selected: false,
    icon: 'building'
  }
]

interface DatabaseSelectorProps {
  selectedDatabases: string[]
  onDatabasesChange: (databases: string[]) => void
  isOpen: boolean
  onClose: () => void
}

export function DatabaseSelector({ 
  selectedDatabases, 
  onDatabasesChange, 
  isOpen, 
  onClose 
}: DatabaseSelectorProps) {
  const [databases, setDatabases] = useState<DatabaseInfo[]>(availableDatabases)
  const [stats, setStats] = useState({
    total: 0,
    selected: 0,
    totalChunks: 0,
    selectedChunks: 0
  })

  useEffect(() => {
    // Sincroniza seleção com props
    const updatedDatabases = databases.map(db => ({
      ...db,
      selected: selectedDatabases.includes(db.id)
    }))
    setDatabases(updatedDatabases)
  }, [selectedDatabases])

  useEffect(() => {
    // Atualiza estatísticas
    const selected = databases.filter(db => db.selected)
    setStats({
      total: databases.length,
      selected: selected.length,
      totalChunks: databases.reduce((sum, db) => sum + db.chunks, 0),
      selectedChunks: selected.reduce((sum, db) => sum + db.chunks, 0)
    })
  }, [databases])

  const handleDatabaseToggle = (databaseId: string) => {
    const updatedDatabases = databases.map(db => 
      db.id === databaseId ? { ...db, selected: !db.selected } : db
    )
    setDatabases(updatedDatabases)
    
    const newSelected = updatedDatabases
      .filter(db => db.selected)
      .map(db => db.id)
    
    onDatabasesChange(newSelected)
  }

  const handleSelectAll = () => {
    const allSelected = databases.every(db => db.selected)
    const updatedDatabases = databases.map(db => ({ ...db, selected: !allSelected }))
    setDatabases(updatedDatabases)
    
    const newSelected = allSelected ? [] : updatedDatabases.map(db => db.id)
    onDatabasesChange(newSelected)
  }

  const getIcon = (iconType: string) => {
    switch (iconType) {
      case 'law': return <Gavel className="w-4 h-4" />
      case 'building': return <Building2 className="w-4 h-4" />
      case 'globe': return <Globe className="w-4 h-4" />
      case 'book': return <BookOpen className="w-4 h-4" />
      default: return <FileText className="w-4 h-4" />
    }
  }

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'pdf': return 'text-red-600'
      case 'guide': return 'text-blue-600'
      case 'txt': return 'text-green-600'
      default: return 'text-gray-600'
    }
  }

  if (!isOpen) return null

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4"
        onClick={onClose}
      >
        <motion.div
          initial={{ scale: 0.95, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.95, opacity: 0 }}
          className="bg-background rounded-xl shadow-2xl w-full max-w-4xl max-h-[90vh] flex flex-col overflow-hidden"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Header */}
          <div className="p-6 border-b border-border">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Database className="w-6 h-6 text-primary" />
                <div>
                  <h2 className="text-xl font-semibold">Bases de Conhecimento</h2>
                  <p className="text-sm text-muted-foreground">
                    Selecione quais bases deseja usar para suas consultas
                  </p>
                </div>
              </div>
              <Button variant="ghost" onClick={onClose}>
                ✕
              </Button>
            </div>

            {/* Statistics */}
            <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center p-3 bg-muted/30 rounded-lg">
                <div className="text-lg font-bold text-primary">{stats.selected}</div>
                <div className="text-xs text-muted-foreground">Selecionadas</div>
              </div>
              <div className="text-center p-3 bg-muted/30 rounded-lg">
                <div className="text-lg font-bold">{stats.total}</div>
                <div className="text-xs text-muted-foreground">Disponíveis</div>
              </div>
              <div className="text-center p-3 bg-muted/30 rounded-lg">
                <div className="text-lg font-bold text-green-600">{stats.selectedChunks.toLocaleString()}</div>
                <div className="text-xs text-muted-foreground">Chunks Ativos</div>
              </div>
              <div className="text-center p-3 bg-muted/30 rounded-lg">
                <div className="text-lg font-bold text-muted-foreground">{stats.totalChunks.toLocaleString()}</div>
                <div className="text-xs text-muted-foreground">Total Chunks</div>
              </div>
            </div>
          </div>

          {/* Controls */}
          <div className="p-4 border-b border-border">
            <div className="flex items-center justify-between">
              <Button
                variant="outline"
                size="sm"
                onClick={handleSelectAll}
              >
                {databases.every(db => db.selected) ? 'Desmarcar Todas' : 'Selecionar Todas'}
              </Button>
              
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Info className="w-4 h-4" />
                <span>Bases selecionadas serão usadas para responder suas perguntas</span>
              </div>
            </div>
          </div>

          {/* Database List */}
          <div className="flex-1 overflow-y-auto p-4">
            <div className="space-y-3">
              {databases.map((database) => (
                <motion.div
                  key={database.id}
                  layout
                  className={`p-4 rounded-lg border transition-all cursor-pointer hover:bg-accent/50 ${
                    database.selected 
                      ? 'border-primary bg-primary/5' 
                      : 'border-border hover:border-border/70'
                  }`}
                  onClick={() => handleDatabaseToggle(database.id)}
                >
                  <div className="flex items-start gap-4">
                    {/* Checkbox */}
                    <Checkbox
                      checked={database.selected}
                      onChange={() => handleDatabaseToggle(database.id)}
                      className="mt-1"
                    />

                    {/* Icon */}
                    <div className={`p-2 rounded-lg flex-shrink-0 ${
                      database.selected ? 'bg-primary/10 text-primary' : 'bg-muted text-muted-foreground'
                    }`}>
                      <div className="w-4 h-4">
                        {getIcon(database.icon)}
                      </div>
                    </div>

                    {/* Content */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <h3 className="font-medium truncate">{database.name}</h3>
                        <span className={`text-xs px-2 py-1 rounded-full bg-muted ${getTypeColor(database.type)}`}>
                          {database.type.toUpperCase()}
                        </span>
                        {database.selected && (
                          <CheckCircle2 className="w-4 h-4 text-green-600 flex-shrink-0" />
                        )}
                      </div>
                      
                      <p className="text-sm text-muted-foreground mb-2">
                        {database.description}
                      </p>

                      {/* Topics */}
                      <div className="flex flex-wrap gap-1 mb-2">
                        {database.topics.slice(0, 3).map((topic) => (
                          <span
                            key={topic}
                            className="text-xs px-2 py-1 bg-accent/50 rounded-full"
                          >
                            {topic}
                          </span>
                        ))}
                        {database.topics.length > 3 && (
                          <span className="text-xs text-muted-foreground">
                            +{database.topics.length - 3} mais
                          </span>
                        )}
                      </div>

                      {/* Stats */}
                      <div className="flex items-center gap-4 text-xs text-muted-foreground">
                        <span>{database.size}</span>
                        <span>{database.chunks.toLocaleString()} chunks</span>
                        <span>Atualizado: {new Date(database.lastUpdated).toLocaleDateString('pt-BR')}</span>
                      </div>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>

          {/* Footer */}
          <div className="p-4 border-t border-border">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <AlertCircle className="w-4 h-4" />
                <span>
                  {stats.selected === 0 
                    ? 'Selecione pelo menos uma base para fazer consultas'
                    : `${stats.selectedChunks.toLocaleString()} chunks prontos para consulta`
                  }
                </span>
              </div>
              
              <div className="flex gap-2">
                <Button variant="outline" onClick={onClose}>
                  Cancelar
                </Button>
                <Button 
                  onClick={onClose}
                  disabled={stats.selected === 0}
                >
                  Aplicar Seleção
                </Button>
              </div>
            </div>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  )
}