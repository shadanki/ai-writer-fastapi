"use client"

import { useState } from "react"
import { Toaster } from "@/components/ui/toaster"
import { BlogWizardForm } from "@/components/blog-wizard-form"

export default function BlogWizardPage() {
  const [markdownContent, setMarkdownContent] = useState<string>("")

  const handleMarkdownUpdate = (content: string) => {
    setMarkdownContent(content)
  }

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto p-6">
        <h1 className="text-3xl font-bold text-center mb-8">LLMO Blog Writer</h1>

        <div className="grid grid-cols-1 gap-6">
          {/* 各ステップのカード */}
          <div className="space-y-6">
            <BlogWizardForm onMarkdownUpdate={handleMarkdownUpdate} />
          </div>
        </div>
      </div>
      <Toaster />
    </div>
  )
}
