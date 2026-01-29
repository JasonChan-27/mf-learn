// This file contains the loader for remote modules
// It does not require the main application to configure the federation plugin in vite.config.ts

import { createErrorFallback } from './fallback'
import type { MicroAppModule, MicroAppConfig } from './types'
import { sendMetric } from 'mf-telemetry'

type Module = Record<string, unknown>

// Simple circuit breaker state per app
const circuitState: Record<string, { failures: number; openedAt?: number }> = {}
const DEFAULT_CIRCUIT_FAILURE_THRESHOLD = 5
const DEFAULT_CIRCUIT_OPEN_MS = 60_000

function isCircuitOpen(key: string, windowMs = DEFAULT_CIRCUIT_OPEN_MS) {
  const s = circuitState[key]
  if (!s) return false
  if (s.openedAt && Date.now() - s.openedAt < windowMs) return true
  if (s.openedAt) {
    // reset after window
    delete circuitState[key]
    return false
  }
  return false
}

function recordFailure(
  key: string,
  threshold = DEFAULT_CIRCUIT_FAILURE_THRESHOLD,
) {
  const s = circuitState[key] || { failures: 0 }
  s.failures = (s.failures || 0) + 1
  if (s.failures >= threshold) s.openedAt = Date.now()
  circuitState[key] = s
}

function recordSuccess(key: string) {
  delete circuitState[key]
}

// in-memory cache for loaded remote modules
const remoteCache: Record<string, Promise<Module> | undefined> = {}
// in-flight import promises to dedupe concurrent requests for same URL
const inFlightRequests: Record<string, Promise<Module> | undefined> = {}

async function tryImportWithRetry(
  url: string,
  maxAttempts = 3,
  timeoutMs = 5000,
): Promise<Module> {
  // return cached module when available
  if (remoteCache[url]) return remoteCache[url]
  // if another request is already importing this URL, reuse its promise
  if (inFlightRequests[url]) return await inFlightRequests[url]

  const importPromise = (async () => {
    for (let attempt = 1; attempt <= maxAttempts; attempt++) {
      try {
        // dynamic import with per-attempt timeout
        // eslint-disable-next-line no-await-in-loop
        const mod = await Promise.race([
          import(/* @vite-ignore */ url),
          new Promise((_, reject) =>
            setTimeout(() => reject(new Error('import timeout')), timeoutMs),
          ),
        ])
        // cache and return
        remoteCache[url] = mod
        return mod
      } catch (e) {
        const base = 200
        const jitter = 0.8 + Math.random() * 0.4
        const wait = Math.round(base * Math.pow(2, attempt - 1) * jitter)
        if (process.env.NODE_ENV !== 'production')
          console.warn(
            `[mf-runtime-loader] import ${url} attempt ${attempt} failed`,
            e,
            `wait ${wait}ms`,
          )
        // eslint-disable-next-line no-await-in-loop
        await new Promise((r) => setTimeout(r, wait))
      }
    }
    throw new Error('max attempts reached')
  })()

  inFlightRequests[url] = importPromise
  try {
    const res = await importPromise
    return res
  } finally {
    delete inFlightRequests[url]
  }
}

/**
 * 远程模块加载器
 * 无需主应用在 vite.config.ts 中配置 federation 插件
 */
export async function loadRemote(el: HTMLElement, config: MicroAppConfig) {
  try {
    // 支持备用 URL 列表：先尝试主 URL，若失败再按顺序尝试 alternates
    const urls = [config.url, ...(config.alternates ?? [])]
    const timeout = config.timeout ?? 5000

    let remote: Module | null = null
    let lastError: unknown = null

    const key = config.name || config.url
    if (isCircuitOpen(key)) {
      sendMetric({
        name: 'mf_remote_circuit_open_total',
        value: 1,
        labels: { app: config.app || 'main', name: config.name },
      })
      throw new Error('circuit open')
    }

    for (const url of urls) {
      try {
        // record an attempt
        const traceparent =
          config.props?.traceparent || config.props?.trace?.traceparent
        sendMetric({
          name: 'mf_remote_load_attempt_total',
          value: 1,
          labels: {
            app: config.app || 'main',
            name: config.name,
            url,
            ...(traceparent ? { traceparent } : {}),
          },
        })
        // try import with retry+timeout+jitter
        try {
          remote = await tryImportWithRetry(url, 3, timeout)
          // 成功加载，记录成功并退出
          recordSuccess(key)
          sendMetric({
            name: 'mf_remote_load_fetched_total',
            value: 1,
            labels: {
              app: config.app || 'main',
              name: config.name,
              url,
            },
          })
          break
        } catch (ie) {
          // per-url attempts failed -> mark failure and continue to next alternate
          recordFailure(key)
          if (process.env.NODE_ENV !== 'production')
            console.warn('[mf-runtime-loader] url attempts failed', url, ie)
          lastError = ie
          // continue to next url
        }
      } catch (e) {
        console.warn(`尝试加载 ${url} 失败:`, e)
        lastError = e
        // 继续尝试下一个备用 URL
      }
    }

    if (!remote) {
      // record overall failure
      const traceparent =
        config.props?.traceparent || config.props?.trace?.traceparent
      sendMetric({
        name: 'mf_remote_load_failure_total',
        value: 1,
        labels: {
          app: config.app || 'main',
          name: config.name,
          ...(traceparent ? { traceparent } : {}),
        },
      })
      throw lastError ?? new Error('no remote loaded')
    }

    // 2. 初始化共享作用域 (重要！)
    // 由于主应用没用插件，这里我们手动创建一个空作用域
    // 如果后续需要共享依赖，可以在这个对象里按协议注入
    if (
      !window.__federation_shared_instance__ &&
      typeof remote.init === 'function'
    ) {
      await remote.init({})
    }

    // 3. 获取模块工厂并执行
    // config.module 必须是子应用 exposes 里的 Key，例如 './DashBoard'
    // console.log('1111', remote, config.module)
    const factory = await (typeof remote.get === 'function'
      ? remote.get(config.module)
      : () => {})
    const mod = factory() as MicroAppModule

    // 4. 统一调用约定好的 mount 方法
    // 建议子应用暴露出的接口统一为：(el, props) => unmount
    if (typeof mod.mount !== 'function') {
      throw new Error(`模块 ${config.module} 未导出有效的 mount 方法`)
    }

    console.log(`正在挂载远程模块: ${config.module}`)
    const traceparent =
      config.props?.traceparent || config.props?.trace?.traceparent
    const mountStart = performance.now()
    const unmount: unknown = mod.mount(el, config.props)
    const mountDuration = (performance.now() - mountStart) / 1000
    sendMetric({
      name: 'mf_mount_duration_seconds',
      value: mountDuration,
      labels: {
        app: config.app || 'main',
        name: config.name,
        ...(traceparent ? { traceparent } : {}),
      },
    })
    // success
    sendMetric({
      name: 'mf_remote_load_success_total',
      value: 1,
      labels: {
        app: config.app || 'main',
        name: config.name,
        ...(traceparent ? { traceparent } : {}),
      },
    })

    // 返回销毁函数
    return () => {
      if (typeof unmount === 'function') {
        unmount()
      } else if (
        unmount instanceof Promise &&
        typeof unmount.then === 'function'
      ) {
        // 处理异步卸载的情况
        unmount.then((fn: () => void | undefined) => fn?.())
      }
    }
  } catch (error: unknown) {
    console.error('加载远程模块失败:', error)
    const message = error instanceof Error ? error.message : String(error)

    // 优先使用上层配置中提供的 fallback 回退（manager 会做相同处理），否则渲染默认错误提示
    try {
      if (config.fallback && typeof config.fallback === 'function') {
        const fb = config.fallback()
        // 如果 fallback 元素存在，插入并返回一个 noop 卸载函数
        if (fb instanceof HTMLElement) {
          el.innerHTML = ''
          el.appendChild(fb)
          const traceparent =
            config.props?.traceparent || config.props?.trace?.traceparent
          sendMetric({
            name: 'mf_remote_fallback_total',
            value: 1,
            labels: {
              app: config.app || 'main',
              name: config.name,
              reason: 'custom-fallback',
              ...(traceparent ? { traceparent } : {}),
            },
          })
          return () => {}
        }
      }
    } catch (e) {
      console.warn('执行自定义 fallback 时出错', e)
    }

    sendMetric({
      name: 'mf_remote_fallback_total',
      value: 1,
      labels: {
        app: config.app || 'main',
        name: config.name,
        reason: message,
      },
    })

    const errFallback = createErrorFallback(`远程组件加载失败: ${message}`)
    el.innerHTML = errFallback.outerHTML
    throw error
  }
}
