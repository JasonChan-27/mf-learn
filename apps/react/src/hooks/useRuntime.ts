import { useContext } from 'react'
import { RuntimeContext } from '@/constant'
import type { Runtime } from '@/types'

export const useRuntime = (): Runtime => {
  const runtime = useContext<Runtime>(RuntimeContext)

  if (!runtime) {
    throw new Error('Runtime not provided')
  }

  return runtime
}
