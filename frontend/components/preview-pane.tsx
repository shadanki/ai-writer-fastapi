"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Copy, FileText } from "lucide-react"
import { useToast } from "@/hooks/use-toast"
import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"

interface PreviewPaneProps {
  markdownContent: string
}

export function PreviewPane({ markdownContent }: PreviewPaneProps) {
  const { toast } = useToast()

  const handleCopyMarkdown = async () => {
    if (!markdownContent) {
      toast({
        title: "エラー",
        description: "コピーするコンテンツがありません。",
        variant: "destructive",
      })
      return
    }

    try {
      // ```markdownと```を除去してからコピー
      const cleanedMarkdown = markdownContent.replace(/```markdown/g, "").replace(/```/g, "")
      
      await navigator.clipboard.writeText(cleanedMarkdown)
      toast({
        title: "成功",
        description: "Markdownをクリップボードにコピーしました。",
      })
    } catch (error) {
      toast({
        title: "エラー",
        description: "コピーに失敗しました。",
        variant: "destructive",
      })
    }
  }

  // デバッグ用：Markdown内容の確認
  const cleanedContent = markdownContent ? markdownContent.replace(/```markdown/g, "").replace(/```/g, "") : ""

  return (
    <Card className="h-full flex flex-col">
      <CardContent className="flex-1 overflow-auto">
        {markdownContent ? (
          <div className="space-y-4">
            {/* コピーボタン */}
            <div className="flex justify-end">
              <Button onClick={handleCopyMarkdown} disabled={!markdownContent} variant="outline" size="sm">
                <Copy className="mr-2 h-4 w-4" />
                .mdをコピー
              </Button>
            </div>
            
            {/* Markdown表示 */}
            <div className="prose prose-sm max-w-none">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {cleanedContent}
              </ReactMarkdown>
            </div>
          </div>
        ) : (
          <div className="flex items-center justify-center h-full text-muted-foreground">
            <div className="text-center">
              <FileText className="h-12 w-12 mx-auto mb-4 opacity-50" />
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
