"use client"

import { useState } from "react"
import { Toaster } from "@/components/ui/toaster"
import { BlogWizardForm } from "@/components/blog-wizard-form"
import { PreviewPane } from "@/components/preview-pane"

export default function BlogWizardPage() {
  const [markdownContent, setMarkdownContent] = useState("")

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto p-6">
        <h1 className="text-3xl font-bold text-center mb-8">ブログ生成ウィザード</h1>

        <div className="grid grid-cols-1 gap-6">
          {/* 各ステップのカード */}
          <div className="space-y-6">
            <BlogWizardForm onMarkdownUpdate={setMarkdownContent} />
          </div>

          {markdownContent ? (
             <div className="mt-6"><PreviewPane markdownContent={markdownContent} /></div>
          ) : null}
        </div>
      </div>
      <Toaster />
    </div>
  )
}
