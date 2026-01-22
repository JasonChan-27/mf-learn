import { inject } from 'vue'
import { RuntimeKey } from '@/constant'
import type { Runtime } from '@/types'

export const useRuntime = (): Runtime => {
  const runtime = inject<Runtime>(RuntimeKey)
  if (!runtime) {
    throw new Error('Runtime not provided')
  }
  return runtime
}
