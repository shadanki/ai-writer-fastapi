"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { Loader2, Check } from "lucide-react"
import { useToast } from "@/hooks/use-toast"
import { TitleList } from "@/components/title-list"
import { OutlinePanel } from "@/components/outline-panel"
import { PreviewPane } from "@/components/preview-pane"
import * as api from "@/lib/api"

interface BlogWizardFormProps {
  onMarkdownUpdate: (content: string) => void
}

export function BlogWizardForm({ onMarkdownUpdate }: BlogWizardFormProps) {
  const [currentStep, setCurrentStep] = useState(1)
  const [isLoading, setIsLoading] = useState(false)
  const [sessionId, setSessionId] = useState<string | null>(null)
  const [titles, setTitles] = useState<Array<{ id: string; title: string; score?: number | null; intent?: string | null; why?: string | null }>>([])
  const [selectedTitle, setSelectedTitle] = useState<string | null>(null)
  const [selectedCandidateId, setSelectedCandidateId] = useState<string | null>(null)
  const [outline, setOutline] = useState<any>(null)
  const [markdown, setMarkdown] = useState<string>("")

  // Step 1 form data
  const [topic, setTopic] = useState("")
  const [summary, setSummary] = useState("")

  const { toast } = useToast()

  // Step 1: タイトル生成（セッション作成 + タイトル生成）
  const handleGenerateTitles = async () => {
    if (!topic.trim()) {
      toast({
        title: "エラー",
        description: "トピックを入力してください。",
        variant: "destructive",
      })
      return
    }

    setIsLoading(true)
    try {
      // セッション未作成なら自動で作成
      let currentSessionId = sessionId
      if (!currentSessionId) {
        const sessionResponse = await api.createSession({ topic, summary: summary.trim() || null })
        currentSessionId = sessionResponse.sessionId
        setSessionId(currentSessionId)
        toast({
          title: "成功",
          description: "セッションが作成されました。",
        })
      }

      // タイトル生成
      const { candidates } = await api.generateTitles(currentSessionId, 10)
      setTitles(candidates)
      setCurrentStep(2)
      toast({
        title: "成功",
        description: "タイトル候補を生成しました。",
      })
    } catch (error) {
      toast({
        title: "エラー",
        description: "タイトル生成に失敗しました。",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  // Step 2: タイトル選択
  const handleSelectTitle = async (candidateId: string, title: string) => {
    if (!sessionId) { 
      toast({
        title: "エラー",
        description: "セッションIDが存在しません",
        variant: "destructive",
      });
      return 
    }
    
    setIsLoading(true)
    try {
      // タイトル選択APIを実行
      await api.selectTitle(sessionId, candidateId)
      setSelectedCandidateId(candidateId)
      setSelectedTitle(title)
      toast({ title: "成功", description: "タイトルが選択されました。", })
      
      // Step3（アウトライン生成中）に遷移
      setCurrentStep(3)
      
      // 自動的にアウトライン生成を実行
      const { outline } = await api.generateOutline(sessionId)
      
      setOutline(outline)
      setCurrentStep(4) // アウトライン確認画面に遷移
      toast({ title: "成功", description: "アウトラインを生成しました。", })
      
    } catch (error) {
      toast({ title: "エラー", description: "タイトル選択またはアウトライン生成に失敗しました。", variant: "destructive", })
    } finally { setIsLoading(false) }
  }

  // Step 4: 本文生成
  const handleGenerateArticle = async () => {
    if (!sessionId) return

    if (!outline) {
      toast({
        title: "エラー",
        description: "先にアウトラインを生成してください",
        variant: "destructive",
      })
      return
    }

    setIsLoading(true)
    try {
      const response = await api.generateArticle(sessionId, outline || undefined)
      setMarkdown(response.markdown)
      onMarkdownUpdate(response.markdown)
      setCurrentStep(5) // プレビュー画面に遷移
      toast({
        title: "成功",
        description: "記事を生成しました。",
      })
    } catch (error) {
      toast({
        title: "エラー",
        description: "記事生成に失敗しました。",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  // ステップの表示制御
  const renderCurrentStep = () => {
    switch (currentStep) {
      case 1:
        return (
          <Card className="ring-2 ring-primary">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <span className="bg-primary text-primary-foreground rounded-full w-6 h-6 flex items-center justify-center text-sm">
                  1
                </span>
                基本情報の入力
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="topic">トピック</Label>
                <Input
                  id="topic"
                  value={topic}
                  onChange={(e) => setTopic(e.target.value)}
                  placeholder="ブログのトピックを入力してください"
                />
              </div>
              <div>
                <Label htmlFor="summary">概要</Label>
                <Textarea
                  id="summary"
                  value={summary}
                  onChange={(e) => setSummary(e.target.value)}
                  placeholder="ブログの概要を入力してください"
                  rows={4}
                />
              </div>
              <Button onClick={handleGenerateTitles} disabled={isLoading} className="w-full">
                {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                タイトルを生成
              </Button>
            </CardContent>
          </Card>
        )

      case 2:
        return (
          <Card className="ring-2 ring-primary">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <span className="bg-primary text-primary-foreground rounded-full w-6 h-6 flex items-center justify-center text-sm">
                  2
                </span>
                タイトル選択
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {titles.length === 0 ? (
                <div className="text-center py-8">
                  <Loader2 className="mx-auto h-8 w-8 animate-spin mb-4" />
                  <p>タイトルを生成中...</p>
                </div>
              ) : (
                <TitleList
                  titles={titles}
                  onSelectTitle={handleSelectTitle}
                  selectedTitle={selectedTitle}
                  isLoading={isLoading}
                  disabled={false}
                />
              )}
            </CardContent>
          </Card>
        )

      case 3:
        return (
          <Card className="ring-2 ring-primary">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <span className="bg-primary text-primary-foreground rounded-full w-6 h-6 flex items-center justify-center text-sm">
                  3
                </span>
                アウトライン生成中
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="text-center py-8">
                <Loader2 className="mx-auto h-8 w-8 animate-spin mb-4" />
                <p className="text-lg font-medium mb-2">アウトラインを生成中...</p>
                <p className="text-sm text-muted-foreground">しばらくお待ちください</p>
              </div>
            </CardContent>
          </Card>
        )

      case 4:
        return (
          <Card className="ring-2 ring-primary">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <span className="bg-primary text-primary-foreground rounded-full w-6 h-6 flex items-center justify-center text-sm">
                  4
                </span>
                アウトライン確認
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {outline && <OutlinePanel outline={outline} />}
              <div className="flex justify-end">
                <Button onClick={handleGenerateArticle} disabled={isLoading}>
                  {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                  本文生成へ
                </Button>
              </div>
            </CardContent>
          </Card>
        )

      case 5:
        return (
          <Card className="ring-2 ring-primary">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <span className="bg-primary text-primary-foreground rounded-full w-6 h-6 flex items-center justify-center text-sm">
                  5
                </span>
                プレビュー
              </CardTitle>
            </CardHeader>
            <CardContent>
              <PreviewPane markdownContent={markdown} />
            </CardContent>
          </Card>
        )

      default:
        return null
    }
  }

  return (
    <div className="space-y-6">
      {/* Stepper Header */}
      <div className="flex items-center justify-center mb-8">
        <div className="flex items-center space-x-4">
          {[1, 2, 3, 4, 5].map((step) => (
            <div key={step} className="flex items-center">
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                  currentStep > step
                    ? "bg-green-500 text-white"
                    : currentStep === step
                    ? "bg-primary text-primary-foreground"
                    : "bg-gray-200 text-gray-500"
                }`}
              >
                {currentStep > step ? <Check className="w-4 h-4" /> : step}
              </div>
              {step < 5 && (
                <div
                  className={`w-12 h-0.5 mx-2 ${
                    currentStep > step ? "bg-green-500" : "bg-gray-200"
                  }`}
                />
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Current Step Content */}
      {renderCurrentStep()}
    </div>
  )
}
