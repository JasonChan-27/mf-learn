import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { federation } from '@module-federation/vite'
import type { UserConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig(({ mode }: UserConfig) => {
  // const isProduction = mode === 'production'
  const isDEV = mode === 'development'

  return {
    plugins: [
      ...(isDEV ? [react()] : []),
      federation({
        name: 'reactApp',
        filename: 'remoteEntry.js',
        exposes: {
          './DashBoard': './src/DashBoard/mount.tsx',
        },
        shared: {
          react: { singleton: true },
          'react-dom': { singleton: true },
          // rxjs: {
          //   singleton: true,
          // },
          // 'mf-shared': {
          //   singleton: true
          // }
        },
      }) as any,
    ],
    build: {
      target: 'esnext',
      minify: true,
    },
    server: {
      port: 3002,
      cors: true,
      // origin: 'http://localhost:3002',
    },
  }
})
