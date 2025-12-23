import { createErrorFallback } from './fallback'
import type { MicroAppModule } from './types'

/**
 * 远程模块加载器
 * 无需主应用在 vite.config.ts 中配置 federation 插件
 */
export async function loadRemote(
  el: HTMLElement,
  config: { url: string; module: string },
  props?: any,
) {
  try {
    // 1. 动态导入远程入口文件 (ESM 格式)
    // @vite-ignore 告诉 Vite 不要尝试在编译时解析这个路径
    const remote = await import(/* @vite-ignore */ config.url)

    // 2. 初始化共享作用域 (重要！)
    // 由于主应用没用插件，这里我们手动创建一个空作用域
    // 如果后续需要共享依赖，可以在这个对象里按协议注入
    if (!(window as any).__federation_shared_instance__) {
      await remote.init({})
    }

    // 3. 获取模块工厂并执行
    // config.module 必须是子应用 exposes 里的 Key，例如 './DashBoard'
    const factory = await remote.get(config.module)
    const mod = factory() as MicroAppModule

    // 4. 统一调用约定好的 mount 方法
    // 建议子应用暴露出的接口统一为：(el, props) => unmount
    if (typeof mod.mount !== 'function') {
      throw new Error(`模块 ${config.module} 未导出有效的 mount 方法`)
    }

    console.log(`正在挂载远程模块: ${config.module}`)
    const unmount: any = mod.mount(el, props)

    // 返回销毁函数
    return () => {
      if (typeof unmount === 'function') {
        unmount()
      } else if (unmount && typeof unmount.then === 'function') {
        // 处理异步卸载的情况
        unmount.then((fn: any) => fn?.())
      }
    }
  } catch (error: unknown) {
    console.error('加载远程模块失败:', error)
    const message = error instanceof Error ? error.message : String(error)
    const errFallback = createErrorFallback(`远程组件加载失败: ${message}`)
    el.innerHTML = errFallback.outerHTML
    throw error
  }
}

// import type { MicroAppModule } from './types'

// const loadedScopes = new Set<string>()

// function loadScript(scope: string, url: string) {
//   if (loadedScopes.has(scope)) return Promise.resolve()

//   return new Promise<void>((resolve, reject) => {
//     const script = document.createElement('script')
//     script.type = 'module'
//     script.src = url
//     script.async = true
//     script.onload = () => {
//       loadedScopes.add(scope)
//       resolve()
//     }
//     script.onerror = () => reject(new Error(`load remoteEntry failed: ${url}`))
//     document.head.appendChild(script)
//   })
// }

// export async function loadRemote(
//   el: HTMLElement,
//   config: {
//     scope: string
//     module: string
//     url: string
//     timeout?: number
//   },
//   props?: any,
// ) {
//   let unmount: (() => void) | null = null

//   const task = (async () => {
//     await loadScript(config.scope, config.url)

//     // ✅ Vite MF 运行时模块直接挂到 window[scope]
//     const container = (window as any)[config.scope]
//     if (!container)
//       throw new Error(`Remote container ${config.scope} not found`)

//     const factory = await container.get(config.module)
//     const mod = factory() as MicroAppModule
//     unmount = mod.mount(el, props)
//   })()

//   await Promise.race([
//     task,
//     new Promise((_, reject) =>
//       setTimeout(
//         () => reject(new Error('load timeout')),
//         config.timeout ?? 8000,
//       ),
//     ),
//   ])

//   return () => unmount?.()
// }
