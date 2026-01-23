import { createErrorFallback } from 'mf-runtime-loader'
import type { MicroAppConfig } from 'mf-runtime-loader'
import { sharedRuntime } from '@/utils'

// const isProd = import.meta.env.PROD

export const microRegistry: MicroAppConfig[] = [
  {
    name: 'reactDashboard',
    scope: 'reactApp',
    module: './DashBoard',
    url: import.meta.env.VITE_REACT_REMOTE_URL,
    props: { runtime: sharedRuntime },
    activeWhen: ({ pathname }) => pathname.startsWith('/'),
    timeout: 8000,
    fallback: () => {
      return createErrorFallback('远程组件DashBoard加载超时')
    },
  },
  {
    name: 'vueHome',
    scope: 'vueApp',
    module: './Home',
    url: import.meta.env.VITE_VUE_REMOTE_URL,
    props: { runtime: sharedRuntime },
    activeWhen: ({ pathname }) => pathname === '/',
    fallback: () => {
      return createErrorFallback('远程组件Home加载超时')
    },
  },
]
