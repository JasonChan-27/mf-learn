import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { federation } from '@module-federation/vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    federation({
      name: 'vueApp', // 子应用唯一标识
      filename: 'remoteEntry.js', // 模块联邦入口文件
      exposes: {
        // 暴露需要被主应用加载的组件/页面
        './Home': './src/Home/mount.ts',
      },
      shared: {
        // 共享依赖（与主应用复用，避免重复加载）
        vue: { singleton: true },
        // rxjs: { singleton: true },
        'mf-shared': { singleton: true, strictVersion: true },
      },
    }) as any,
  ],
  build: {
    target: 'esnext', // 适配现代浏览器
    minify: true,
    // rollupOptions: {
    //   external: ['mf-shared'],
    // },
  },
  server: {
    port: 3001, // 子应用端口
    cors: true, // 允许跨域（主应用加载需要）
    // origin: 'http://localhost:3000', // 允许主应用访问
  },
})
