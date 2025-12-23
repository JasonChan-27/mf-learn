import type { MicroAppConfig } from './types'

const isProd = import.meta.env.PROD

export const microRegistry: MicroAppConfig[] = [
  {
    name: 'reactDashboard',
    scope: 'reactApp',
    module: './DashBoard',
    url: isProd
      ? 'http://localhost:4002/remoteEntry.js'
      : 'http://localhost:3002/remoteEntry.js',
    activeWhen: ({ pathname }) => pathname.startsWith('/'),
    timeout: 8000,
  },
  {
    name: 'vueHome',
    scope: 'vueApp',
    module: './Home',
    url: isProd
      ? 'http://localhost:4001/remoteEntry.js'
      : 'http://localhost:3001/remoteEntry.js',
    activeWhen: ({ pathname }) => pathname === '/',
  },
]
