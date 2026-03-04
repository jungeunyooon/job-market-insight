import { useState, useEffect, useCallback } from 'react'
import { ApiError } from '@/api/client'

interface UseApiState<T> {
  data: T | null
  loading: boolean
  error: string | null
}

export function useApi<T>(
  fetcher: () => Promise<T>,
  deps: unknown[] = [],
) {
  const [state, setState] = useState<UseApiState<T>>({
    data: null,
    loading: true,
    error: null,
  })

  const refetch = useCallback(() => {
    setState((prev) => ({ ...prev, loading: true, error: null }))
    fetcher()
      .then((data) => setState({ data, loading: false, error: null }))
      .catch((err) => {
        const message =
          err instanceof ApiError
            ? `${err.status}: ${err.statusText}`
            : err instanceof Error
              ? err.message
              : 'Unknown error'
        setState({ data: null, loading: false, error: message })
      })
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps)

  useEffect(() => {
    refetch()
  }, [refetch])

  return { ...state, refetch }
}
