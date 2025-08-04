'use client'

import { Moon, Sun } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { useEffect, useState } from 'react'

export function ThemeToggle() {
  const [isDark, setIsDark] = useState(true) // Default dark mode

  useEffect(() => {
    // Check if user has a preference stored
    const stored = localStorage.getItem('theme')
    if (stored) {
      const prefersDark = stored === 'dark'
      setIsDark(prefersDark)
      updateTheme(prefersDark)
    } else {
      // Default to dark mode
      setIsDark(true)
      updateTheme(true)
    }
  }, [])

  const updateTheme = (dark: boolean) => {
    const html = document.documentElement
    const body = document.body
    
    if (dark) {
      html.classList.add('dark')
      body.classList.add('dark')
    } else {
      html.classList.remove('dark')
      body.classList.remove('dark')
    }
  }

  const toggleTheme = () => {
    const newIsDark = !isDark
    setIsDark(newIsDark)
    updateTheme(newIsDark)
    localStorage.setItem('theme', newIsDark ? 'dark' : 'light')
  }

  return (
    <Button
      variant="ghost"
      size="icon"
      onClick={toggleTheme}
      className="h-9 w-9 hover:bg-accent/50 transition-colors"
      title={isDark ? 'Ativar modo claro' : 'Ativar modo escuro'}
    >
      {isDark ? (
        <Sun className="h-4 w-4 text-accent" />
      ) : (
        <Moon className="h-4 w-4 text-accent" />
      )}
      <span className="sr-only">
        {isDark ? 'Ativar modo claro' : 'Ativar modo escuro'}
      </span>
    </Button>
  )
}