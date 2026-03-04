import { Loader2 } from 'lucide-react'

export function LoadingState({ message = '데이터를 불러오는 중...' }: { message?: string }) {
  return (
    <div className="flex flex-col items-center justify-center py-20">
      <Loader2 className="h-8 w-8 animate-spin text-accent-blue" />
      <p className="mt-3 text-sm text-text-muted">{message}</p>
    </div>
  )
}
