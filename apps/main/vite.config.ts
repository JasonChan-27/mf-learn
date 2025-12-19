import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import react from '@vitejs/plugin-react'
import { federation } from '@module-federation/vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    react({
      // fastRefresh: process.env.NODE_ENV !== 'production',
    }),
    federation({
      name: 'mainApp',
      remotes: {
        // 远程加载子应用（开发环境用本地地址，生产用部署地址）
        vueApp: {
          type: 'module',
          name: 'vueApp',
          entry: 'http://localhost:3001/remoteEntry.js',
        },
        reactApp: {
          type: 'module',
          name: 'reactApp',
          entry: 'http://localhost:3002/remoteEntry.js',
        },
      },
      shared: {
        // 共享依赖（与子应用复用）
        vue: { singleton: true },
        react: { singleton: true },
        'react-dom': { singleton: true },
      },
    }) as any,
  ],
  build: {
    target: 'esnext',
  },
  optimizeDeps: {
    // 必须把共享的依赖加入预构建，防止加载子应用时 Vite 重启导致白屏
    include: ['vue', 'react', 'react-dom', 'vue-router'],
  },
  server: { port: 3000 },
})
