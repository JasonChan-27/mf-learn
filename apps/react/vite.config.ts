import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { federation } from '@module-federation/vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    federation({
      name: 'reactApp',
      filename: 'remoteEntry.js',
      exposes: {
        './DashBoard': './src/DashBoard/mount.tsx',
      },
      shared: {
        react: { singleton: true },
        'react-dom': { singleton: true },
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
})
