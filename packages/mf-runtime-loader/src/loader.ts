import { createErrorFallback } from './fallback'
import type { MicroAppModule, MicroAppConfig } from './types'
import { sendMetric } from './metrics'

/**
 * 远程模块加载器
 * 无需主应用在 vite.config.ts 中配置 federation 插件
 */
export async function loadRemote(el: HTMLElement, config: MicroAppConfig) {
  try {
    // 支持备用 URL 列表：先尝试主 URL，若失败再按顺序尝试 alternates
    const urls = [config.url, ...(config.alternates ?? [])]
    const timeout = config.timeout ?? 5000

    let remote: any = null
    let lastError: unknown = null

    for (const url of urls) {
      try {
        // record an attempt
        sendMetric('mf_remote_load_attempt_total', 1, {
          app: (config as any).app || 'main',
          name: config.name,
          url,
        })
        const importPromise = import(/* @vite-ignore */ url)
        remote = await Promise.race([
          importPromise,
          new Promise((_, reject) =>
            setTimeout(() => reject(new Error('load timeout')), timeout),
          ),
        ])
        // 成功加载，跳出重试循环
        break
      } catch (e) {
        console.warn(`尝试加载 ${url} 失败:`, e)
        lastError = e
        // 继续尝试下一个备用 URL
      }
    }

    if (!remote) {
      // record overall failure
      sendMetric('mf_remote_load_failure_total', 1, {
        app: (config as any).app || 'main',
        name: config.name,
      })
      throw lastError ?? new Error('no remote loaded')
    }

    // 2. 初始化共享作用域 (重要！)
    // 由于主应用没用插件，这里我们手动创建一个空作用域
    // 如果后续需要共享依赖，可以在这个对象里按协议注入
    if (!(window as any).__federation_shared_instance__) {
      await remote.init({})
    }

    // 3. 获取模块工厂并执行
    // config.module 必须是子应用 exposes 里的 Key，例如 './DashBoard'
    // console.log('1111', remote, config.module)
    const factory = await remote.get(config.module)
    const mod = factory() as MicroAppModule

    // 4. 统一调用约定好的 mount 方法
    // 建议子应用暴露出的接口统一为：(el, props) => unmount
    if (typeof mod.mount !== 'function') {
      throw new Error(`模块 ${config.module} 未导出有效的 mount 方法`)
    }

    console.log(`正在挂载远程模块: ${config.module}`)
    const mountStart = performance.now()
    const unmount: any = mod.mount(el, config.props)
    const mountDuration = (performance.now() - mountStart) / 1000
    sendMetric('mf_mount_duration_seconds', mountDuration, {
      app: (config as any).app || 'main',
      name: config.name,
    })
    // success
    sendMetric('mf_remote_load_success_total', 1, {
      app: (config as any).app || 'main',
      name: config.name,
    })

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

    // 优先使用上层配置中提供的 fallback 回退（manager 会做相同处理），否则渲染默认错误提示
    try {
      if (
        (config as any).fallback &&
        typeof (config as any).fallback === 'function'
      ) {
        const fb = (config as any).fallback()
        // 如果 fallback 元素存在，插入并返回一个 noop 卸载函数
        if (fb instanceof HTMLElement) {
          el.innerHTML = ''
          el.appendChild(fb)
          sendMetric('mf_remote_fallback_total', 1, {
            app: (config as any).app || 'main',
            name: config.name,
            reason: 'custom-fallback',
          })
          return () => {}
        }
      }
    } catch (e) {
      console.warn('执行自定义 fallback 时出错', e)
    }

    sendMetric('mf_remote_fallback_total', 1, {
      app: (config as any).app || 'main',
      name: config.name,
      reason: message,
    })

    const errFallback = createErrorFallback(`远程组件加载失败: ${message}`)
    el.innerHTML = errFallback.outerHTML
    throw error
  }
}
