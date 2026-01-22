import type { MicroAppConfig } from 'mf-runtime-loader'
import type { SharedRuntime } from 'mf-shared'

export type Runtime = SharedRuntime | undefined | null

export type { MicroAppConfig, SharedRuntime }
