"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { Loader2 } from "lucide-react"
import { useToast } from "@/hooks/use-toast"
import { TitleList } from "@/components/title-list"
import { OutlinePanel } from "@/components/outline-panel"
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

  // Step 1 form data
  const [topic, setTopic] = useState("")
  const [summary, setSummary] = useState("")

  const { toast } = useToast()

  const handleCreateSession = async () => {
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
      const response = await api.createSession({ topic, summary: summary.trim() || null })
      setSessionId(response.sessionId)
      setCurrentStep(2)
      toast({
        title: "成功",
        description: "セッションが作成されました。",
      })
    } catch (error) {
      toast({
        title: "エラー",
        description: "セッションの作成に失敗しました。",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  const handleGenerateTitles = async () => {
    if (!sessionId) return

    setIsLoading(true)
    try {
      const { candidates } = await api.generateTitles(sessionId, 10)
      setTitles(candidates)
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

  const handleSelectTitle = async (candidateId: string, title: string) => {
    if (!sessionId) return

    setIsLoading(true)
    try {
      await api.selectTitle(sessionId, candidateId)
      setSelectedCandidateId(candidateId)
      setSelectedTitle(title)
      setCurrentStep(3)
      toast({
        title: "成功",
        description: "タイトルが選択されました。",
      })
    } catch (error) {
      toast({
        title: "エラー",
        description: "タイトル選択に失敗しました。",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  const handleGenerateOutline = async () => {
    if (!sessionId) return

    setIsLoading(true)
    try {
      const { outline } = await api.generateOutline(sessionId)
      setOutline(outline)
      toast({
        title: "成功",
        description: "アウトラインを生成しました。",
      })
    } catch (error) {
      toast({
        title: "エラー",
        description: "アウトライン生成に失敗しました。",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

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
      onMarkdownUpdate(response.markdown)
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

  return (
    <div className="space-y-6">
      {/* Step 1: トピック入力 */}
      <Card className={currentStep === 1 ? "ring-2 ring-primary" : ""}>
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
              disabled={currentStep > 1}
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
              disabled={currentStep > 1}
            />
          </div>
          {currentStep === 1 && (
            <Button onClick={handleCreateSession} disabled={isLoading} className="w-full">
              {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              セッション作成
            </Button>
          )}
        </CardContent>
      </Card>

      {/* Step 2: タイトル生成 */}
      <Card className={currentStep === 2 ? "ring-2 ring-primary" : ""}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <span className="bg-primary text-primary-foreground rounded-full w-6 h-6 flex items-center justify-center text-sm">
              2
            </span>
            タイトル生成
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {currentStep < 2 ? (
            <p className="text-muted-foreground">セッション作成後に候補が表示されます。</p>
          ) : (
            <>
              {titles.length === 0 ? (
                <Button onClick={handleGenerateTitles} disabled={isLoading} className="w-full">
                  {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                  タイトルを生成
                </Button>
              ) : (
                <TitleList
                  titles={titles}
                  onSelectTitle={handleSelectTitle}
                  selectedTitle={selectedTitle}
                  isLoading={isLoading}
                  disabled={currentStep > 2}
                />
              )}
            </>
          )}
        </CardContent>
      </Card>

      {/* Step 3: アウトライン・本文生成 */}
      <Card className={currentStep === 3 ? "ring-2 ring-primary" : ""}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <span className="bg-primary text-primary-foreground rounded-full w-6 h-6 flex items-center justify-center text-sm">
              3
            </span>
            コンテンツ生成
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {currentStep < 3 ? (
            <p className="text-muted-foreground">タイトルを採用すると、ここでアウトラインを生成できます。</p>
          ) : (
            <>
              <div className="flex gap-2">
                <Button onClick={handleGenerateOutline} disabled={!sessionId || isLoading} className="flex-1">
                  {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                  アウトライン生成
                </Button>
                <Button onClick={handleGenerateArticle} disabled={!outline || isLoading} className="flex-1">
                  {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                  本文生成
                </Button>
              </div>
              {outline && <OutlinePanel outline={outline} />}
            </>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
