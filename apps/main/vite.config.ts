import { defineConfig } from 'vite'
import type { ConfigEnv } from 'vite'
// import type { UserConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
// import react from '@vitejs/plugin-react'
import { federation } from '@module-federation/vite'
import path from 'path'

// https://vite.dev/config/
export default defineConfig(({ mode }: ConfigEnv) => {
  const isProduction = mode === 'production'
  console.log(
    'Vite isProduction:',
    isProduction,
    mode,
    process.env.VITE_APP_BASE,
  )
  // const isDEV = mode === 'development'

  // const vueAppEntry = isProduction
  //   ? 'http://localhost:4001/remoteEntry.js'
  //   : 'http://localhost:3001/remoteEntry.js'

  // const reactAppEntry = isProduction
  //   ? 'http://localhost:4002/remoteEntry.js'
  //   : 'http://localhost:3002/remoteEntry.js'

  return {
    // base: isProduction ? '/mf-learn/' : '/',
    base: process.env.VITE_APP_BASE || '/',
    resolve: {
      alias: {
        '@': path.resolve(__dirname, 'src'),
      },
    },
    plugins: [
      vue(),
      // ...(isDEV ? [react()] : []),
      federation({
        name: 'mainApp',
        // remotes: {
        //   // 远程加载子应用（开发环境用本地地址，生产用部署地址）
        //   vueApp: {
        //     type: 'module',
        //     name: 'vueApp',
        //     entry: vueAppEntry,
        //   },
        //   reactApp: {
        //     type: 'module',
        //     name: 'reactApp',
        //     entry: reactAppEntry,
        //   },
        // },
        shared: {
          // 共享依赖（与子应用复用）
          vue: { singleton: true },
          // react: { singleton: true },
          // 'react-dom': { singleton: true },
          // rxjs: { singleton: true },
          'mf-shared': { singleton: true, strictVersion: true },
        },
      }) as any,
    ],
    build: {
      target: 'esnext',
      sourcemap: true,
    },
    // optimizeDeps: {
    //   // 必须把共享的依赖加入预构建，防止加载子应用时 Vite 重启导致白屏
    //   include: ['vue'],
    // },
    server: { port: 3000 },
  }
})
