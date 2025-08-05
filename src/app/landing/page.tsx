'use client'

import React from 'react'
import Link from 'next/link'
import Image from 'next/image'
import { ArrowRight, FileText, Search, CheckCircle, Upload, BookOpen, Scale, Globe } from 'lucide-react'
import { motion } from 'framer-motion'

export default function LandingPage() {
  // Forçar dark mode na landing page
  React.useEffect(() => {
    document.documentElement.classList.add('dark')
  }, [])
  const fadeIn = {
    initial: { opacity: 0, y: 20 },
    animate: { opacity: 1, y: 0 },
    transition: { duration: 0.6 }
  }

  const staggerChildren = {
    animate: {
      transition: {
        staggerChildren: 0.1
      }
    }
  }

  return (
    <div className="min-h-screen bg-black">
      {/* Hero Section */}
      <motion.section 
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.8 }}
        className="relative overflow-hidden"
      >
        <div className="max-w-6xl mx-auto px-4 py-20 text-center">
          <motion.div {...fadeIn} className="mb-8">
            <Image
              src="/logo.png"
              alt="Inteligência Tributária"
              width={300}
              height={150}
              className="mx-auto opacity-90"
              priority
            />
          </motion.div>
          
          <motion.h1 
            {...fadeIn}
            transition={{ delay: 0.2 }}
            className="text-5xl md:text-6xl font-serif text-gray-100 mb-6"
          >
            Inteligência Tributária Internacional com IA
          </motion.h1>
          
          <motion.p 
            {...fadeIn}
            transition={{ delay: 0.3 }}
            className="text-xl text-gray-300 max-w-3xl mx-auto mb-10 leading-relaxed"
          >
            Consulte especialistas virtuais sobre residência fiscal, tratados e planejamento tributário global
          </motion.p>
          
          <motion.div
            {...fadeIn}
            transition={{ delay: 0.4 }}
          >
            <Link
              href="/"
              className="inline-flex items-center gap-2 bg-[#689F38] hover:bg-[#5D8A2E] text-white px-8 py-4 rounded-sm text-lg font-medium transition-all duration-300 shadow-lg hover:shadow-xl"
            >
              Começar Consulta Gratuita
              <ArrowRight className="w-5 h-5" />
            </Link>
          </motion.div>
        </div>
      </motion.section>

      {/* Como Funciona */}
      <section className="py-20 bg-gray-950">
        <div className="max-w-6xl mx-auto px-4">
          <motion.h2 
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            className="text-4xl font-serif text-gray-100 text-center mb-16"
          >
            Como Funciona
          </motion.h2>
          
          <motion.div 
            variants={staggerChildren}
            initial="initial"
            whileInView="animate"
            viewport={{ once: true }}
            className="grid md:grid-cols-3 gap-8"
          >
            {[
              {
                icon: <FileText className="w-8 h-8" />,
                title: "Faça sua pergunta",
                description: "Digite sua dúvida tributária internacional"
              },
              {
                icon: <Search className="w-8 h-8" />,
                title: "IA analisa",
                description: "Múltiplos agentes consultam nossa base especializada"
              },
              {
                icon: <CheckCircle className="w-8 h-8" />,
                title: "Resposta fundamentada",
                description: "Receba análise jurídica completa com fontes"
              }
            ].map((step, index) => (
              <motion.div
                key={index}
                variants={fadeIn}
                className="text-center p-8 rounded-sm border border-gray-800 hover:border-gray-700 bg-gray-900/50 transition-all duration-300 hover:shadow-md hover:shadow-[#689F38]/20"
              >
                <div className="text-[#689F38] mb-4 flex justify-center">
                  {step.icon}
                </div>
                <h3 className="text-xl font-serif text-gray-100 mb-3">
                  {step.title}
                </h3>
                <p className="text-gray-400">
                  {step.description}
                </p>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* Diferenciais */}
      <section className="py-20 bg-black">
        <div className="max-w-6xl mx-auto px-4">
          <motion.h2 
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            className="text-4xl font-serif text-gray-100 text-center mb-16"
          >
            Nossos Diferenciais
          </motion.h2>
          
          <motion.div 
            variants={staggerChildren}
            initial="initial"
            whileInView="animate"
            viewport={{ once: true }}
            className="grid md:grid-cols-2 lg:grid-cols-4 gap-8"
          >
            <motion.div
              variants={fadeIn}
              className="bg-gray-900 p-6 rounded-sm shadow-sm hover:shadow-lg hover:shadow-[#689F38]/10 transition-all duration-300 border border-gray-800 hover:border-gray-700"
            >
              <BookOpen className="w-10 h-10 text-[#689F38] mb-4" />
              <h3 className="text-lg font-serif text-gray-100 mb-3">
                Base de Conhecimento Especializada
              </h3>
              <ul className="text-sm text-gray-400 space-y-2">
                <li>• EY Worldwide Tax Guide 2025</li>
                <li>• Tratados internacionais</li>
                <li>• Legislação atualizada</li>
              </ul>
            </motion.div>

            <motion.div
              variants={fadeIn}
              className="bg-gray-900 p-6 rounded-sm shadow-sm hover:shadow-lg hover:shadow-[#689F38]/10 transition-all duration-300 border border-gray-800 hover:border-gray-700"
            >
              <Globe className="w-10 h-10 text-[#689F38] mb-4" />
              <h3 className="text-lg font-serif text-gray-100 mb-3">
                Sistema Multi-Agente
              </h3>
              <ul className="text-sm text-gray-400 space-y-2">
                <li>• Pesquisador RAG - Respostas baseadas apenas na Base Especializada</li>
                <li>• Validador Jurídico</li>
                <li>• Análise contextualizada</li>
              </ul>
            </motion.div>

            <motion.div
              variants={fadeIn}
              className="bg-gray-900 p-6 rounded-sm shadow-sm hover:shadow-lg hover:shadow-[#689F38]/10 transition-all duration-300 border border-gray-800 hover:border-gray-700"
            >
              <Scale className="w-10 h-10 text-[#689F38] mb-4" />
              <h3 className="text-lg font-serif text-gray-100 mb-3">
                Respostas Profissionais
              </h3>
              <ul className="text-sm text-gray-400 space-y-2">
                <li>• Tom formal de advogado</li>
                <li>• Citação de fontes</li>
                <li>• Orientações práticas</li>
              </ul>
            </motion.div>

            <motion.div
              variants={fadeIn}
              className="bg-gray-900 p-6 rounded-sm shadow-sm hover:shadow-lg hover:shadow-[#689F38]/10 transition-all duration-300 border border-gray-800 hover:border-gray-700"
            >
              <Upload className="w-10 h-10 text-[#689F38] mb-4" />
              <h3 className="text-lg font-serif text-gray-100 mb-3">
                Personalize sua Base
              </h3>
              <ul className="text-sm text-gray-400 space-y-2">
                <li>• Adicione seus próprios documentos</li>
                <li>• Upload de PDFs, livros e textos especializados</li>
                <li>• Crie sua biblioteca tributária personalizada</li>
              </ul>
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* Exemplos de Consultas */}
      <section className="py-20 bg-gray-950">
        <div className="max-w-6xl mx-auto px-4">
          <motion.h2 
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            className="text-4xl font-serif text-gray-100 text-center mb-16"
          >
            Exemplos de Consultas
          </motion.h2>
          
          <motion.div 
            variants={staggerChildren}
            initial="initial"
            whileInView="animate"
            viewport={{ once: true }}
            className="grid md:grid-cols-3 gap-8"
          >
            {[
              {
                question: "Como funciona a residência fiscal em Portugal?",
                preview: "Portugal determina residência fiscal através de critérios bem definidos..."
              },
              {
                question: "Quais os critérios do tratado Brasil-EUA?",
                preview: "O tratado previne dupla tributação e estabelece regras claras..."
              },
              {
                question: "Como evitar dupla tributação?",
                preview: "Existem mecanismos específicos nos tratados internacionais..."
              }
            ].map((example, index) => (
              <motion.div
                key={index}
                variants={fadeIn}
                className="group bg-gray-900 p-6 rounded-sm border border-gray-800 hover:border-gray-700 transition-all duration-300 hover:shadow-lg hover:shadow-[#689F38]/10 cursor-pointer"
              >
                <h3 className="text-lg font-medium text-gray-100 mb-3">
                  "{example.question}"
                </h3>
                <p className="text-sm text-gray-400 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                  {example.preview}
                </p>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* CTA Final */}
      <section className="py-20 bg-black">
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="max-w-4xl mx-auto px-4 text-center"
        >
          <h2 className="text-4xl font-serif text-gray-100 mb-6">
            Comece sua consulta tributária agora
          </h2>
          <p className="text-xl text-gray-300 mb-10">
            Grátis. Sem cadastro. Respostas imediatas.
          </p>
          <Link
            href="/"
            className="inline-flex items-center gap-2 bg-[#689F38] hover:bg-[#5D8A2E] text-white px-10 py-5 rounded-sm text-xl font-medium transition-all duration-300 shadow-xl shadow-[#689F38]/20 hover:shadow-2xl hover:shadow-[#689F38]/30 transform hover:scale-105"
          >
            Iniciar Consulta
            <ArrowRight className="w-6 h-6" />
          </Link>
        </motion.div>
      </section>

      {/* Footer */}
      <footer className="bg-black text-gray-400 py-8">
        <div className="max-w-6xl mx-auto px-4 text-center">
          <p className="text-sm mb-4 opacity-80">
            Powered by Agno Framework + OpenAI
          </p>
          <div className="flex justify-center gap-6 text-sm">
            <Link href="#" className="hover:text-[#689F38] transition-colors">Termos</Link>
            <Link href="#" className="hover:text-[#689F38] transition-colors">Privacidade</Link>
            <Link href="#" className="hover:text-[#689F38] transition-colors">Contato</Link>
          </div>
        </div>
      </footer>
    </div>
  )
}