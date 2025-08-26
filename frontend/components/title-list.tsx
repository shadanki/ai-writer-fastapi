"use client"

import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Check, Loader2 } from "lucide-react"

interface TitleListProps {
  titles: Array<{ id: string; title: string; score?: number | null; intent?: string | null; why?: string | null }>
  onSelectTitle: (candidateId: string, title: string) => void
  selectedTitle: string | null
  isLoading: boolean
  disabled: boolean
}

export function TitleList({ titles, onSelectTitle, selectedTitle, isLoading, disabled }: TitleListProps) {
  if (titles.length === 0) {
    return <div className="text-center py-8 text-muted-foreground">タイトル候補がありません</div>
  }

  return (
    <div className="space-y-3">
      <h3 className="font-medium">タイトル候補</h3>
      {titles.map((item) => (
        <Card key={item.id} className={selectedTitle === item.title ? "ring-2 ring-green-500" : ""}>
          <CardContent className="p-4">
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1">
                <h4 className="font-medium leading-relaxed">{item.title}</h4>
                <Badge variant="secondary" className="mt-2">
                  スコア: {typeof item.score === 'number' ? item.score.toFixed(2) : '—'}
                </Badge>
              </div>
              <Button
                onClick={() => onSelectTitle(item.id, item.title)}
                disabled={isLoading || disabled}
                variant={selectedTitle === item.title ? "default" : "outline"}
                size="sm"
              >
                {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                {selectedTitle === item.title ? (
                  <>
                    <Check className="mr-2 h-4 w-4" />
                    採用済み
                  </>
                ) : (
                  "採用"
                )}
              </Button>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}
