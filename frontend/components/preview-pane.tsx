"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Copy, FileText } from "lucide-react"
import { useToast } from "@/hooks/use-toast"
import ReactMarkdown from "react-markdown"

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

  return (
    <Card className="h-full flex flex-col">
      <CardHeader className="flex-shrink-0">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            プレビュー
          </CardTitle>
          <Button onClick={handleCopyMarkdown} disabled={!markdownContent} variant="outline" size="sm">
            <Copy className="mr-2 h-4 w-4" />
            .mdをコピー
          </Button>
        </div>
      </CardHeader>
      <CardContent className="flex-1 overflow-auto">
        {markdownContent ? (
          <div className="prose prose-sm max-w-none dark:prose-invert">
            <ReactMarkdown>{markdownContent}</ReactMarkdown>
          </div>
        ) : (
          <div className="flex items-center justify-center h-full text-muted-foreground">
            <div className="text-center">
              <FileText className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>記事を生成するとここにプレビューが表示されます</p>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
