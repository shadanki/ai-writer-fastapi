import { cn } from "@/lib/utils"

export type Step = 1 | 2 | 3 | 4

const STEPS: { key: Step; label: string }[] = [
  { key: 1, label: "基本情報" },
  { key: 2, label: "タイトル" },
  { key: 3, label: "アウトライン" },
  { key: 4, label: "本文" },
]

export function Stepper({ current }: { current: Step }) {
  return (
    <ol className="flex items-center justify-between gap-3 w-full">
      {STEPS.map((s, i) => {
        const done = current > s.key
        const active = current === s.key
        return (
            <li key={s.key} className="flex-1">
                <div className="flex items-center gap-2">
                    <div aria-current={active ? "step" : undefined}
                    className={cn("size-7 rounded-full grid place-items-center text-xs font-semibold border",
                        done && "bg-green-600 text-white border-green-600",
                        active && !done && "bg-primary text-primary-foreground border-primary",
                        !active && !done && "bg-muted text-muted-foreground border-muted-foreground/20"
                    )}
                    >
                        {i + 1}
                    </div>
                    <span className={cn("text-sm", active ? "font-medium" : "text-muted-foreground")}>{s.label}</span>
                </div>
            </li>
        )
      })}
    </ol>
  )
}