"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

interface OutlinePanelProps {
  outline: any
}

export function OutlinePanel({ outline }: OutlinePanelProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>生成されたアウトライン</CardTitle>
      </CardHeader>
      <CardContent>
        <pre className="bg-muted p-4 rounded-md text-sm overflow-auto max-h-96">{JSON.stringify(outline, null, 2)}</pre>
      </CardContent>
    </Card>
  )
}
