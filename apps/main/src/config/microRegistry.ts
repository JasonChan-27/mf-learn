import { createErrorFallback } from 'mf-runtime-loader'
import type { MicroAppConfig } from 'mf-runtime-loader'
import { sharedRuntime, startsWithPath, isExactPath } from '@/utils'

// const isProd = import.meta.env.PROD

export const microRegistry: MicroAppConfig[] = [
  {
    app: 'react',
    name: 'reactDashboard',
    scope: 'reactApp',
    module: './DashBoard',
    url: import.meta.env.VITE_REACT_REMOTE_URL,
    alternates: [import.meta.env.VITE_REACT_REMOTE_ALT_URL],
    props: { runtime: sharedRuntime },
    activeWhen: ({ pathname }) => startsWithPath(pathname, '/'),
    timeout: 8000,
    fallback: () => {
      return createErrorFallback('远程组件DashBoard加载超时')
    },
  },
  {
    app: 'vue',
    name: 'vueHome',
    scope: 'vueApp',
    module: './Home',
    url: import.meta.env.VITE_VUE_REMOTE_URL,
    alternates: [import.meta.env.VITE_VUE_REMOTE_ALT_URL],
    props: { runtime: sharedRuntime },
    activeWhen: ({ pathname }) => isExactPath(pathname, '/'),
    fallback: () => {
      return createErrorFallback('远程组件Home加载超时')
    },
  },
]
