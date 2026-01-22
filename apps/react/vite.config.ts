import { defineConfig } from 'vite'
// import react from '@vitejs/plugin-react'
import { federation } from '@module-federation/vite'
// import type { UserConfig } from 'vite'
import path from 'path'

// https://vite.dev/config/
export default defineConfig(({}) => {
  // const isProduction = mode === 'production'
  // const isDEV = mode === 'development'

  return {
    resolve: {
      alias: {
        '@': path.resolve(__dirname, 'src'),
      },
    },
    plugins: [
      // ...(isDEV ? [react()] : []),
      federation({
        name: 'reactApp',
        filename: 'remoteEntry.js',
        exposes: {
          './DashBoard': './src/DashBoard/mount.tsx',
        },
        shared: {
          react: { singleton: true },
          'react-dom': { singleton: true },
          // rxjs: { singleton: true },
          'mf-shared': { singleton: true, strictVersion: true },
        },
      }) as any,
    ],
    build: {
      target: 'esnext',
      minify: true,
      // rollupOptions: {
      //   external: ['mf-shared'],
      // },
    },
    server: {
      port: 3002,
      cors: true,
      // origin: 'http://localhost:3002',
    },
  }
})
