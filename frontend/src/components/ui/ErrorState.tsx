import { AlertTriangle, RefreshCw } from 'lucide-react'

export function ErrorState({ message, onRetry }: { message: string; onRetry?: () => void }) {
  return (
    <div className="flex flex-col items-center justify-center py-20">
      <AlertTriangle className="h-8 w-8 text-accent-red" />
      <p className="mt-3 text-sm text-text-muted">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="mt-4 flex items-center gap-2 rounded-lg bg-accent-blue px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-accent-blue/90"
        >
          <RefreshCw className="h-4 w-4" />
          다시 시도
        </button>
      )}
    </div>
  )
}
