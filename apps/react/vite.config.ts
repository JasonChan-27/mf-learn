import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { federation } from '@module-federation/vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react({
      jsxRuntime: 'automatic', // 必须和 tsconfig jsx 对应
    }),
    federation({
      name: 'reactApp',
      filename: 'remoteEntry.js',
      exposes: {
        './DashBoard': './src/DashBoard/index.tsx',
      },
      shared: {
        react: { singleton: true, version: '^19.0.0' },
        'react-dom': { singleton: true },
      },
    }) as any,
  ],
  build: { target: 'esnext' },
  server: {
    port: 3002,
    cors: true,
    // origin: 'http://localhost:3000',
  },
})

// export default defineConfig(({ command }) => ({
//   plugins: [
//     react({
//       jsxRuntime: command === 'serve' ? 'automatic' : 'classic',
//     }),
//     federation({
//       name: 'reactApp',
//       filename: 'remoteEntry.js',
//       exposes: {
//         './DashBoard': './src/DashBoard/index.tsx',
//       },
//       shared: {
//         react: { singleton: true, version: '^19.0.0' },
//         'react-dom': { singleton: true },
//       } as any,
//     }),
//   ],
//   build: { target: 'esnext' },
//   server: {
//     port: 3002,
//     cors: true,
//     // origin: 'http://localhost:3000',
//   },
// }))
