import { initMetrics, sendMetric } from './index'

export async function init(opts?: { endpoint?: string }) {
  // initialize telemetry
  initMetrics(opts)

  // optional web-vitals integration if available
  try {
    // dynamic import so package is optional
    // eslint-disable-next-line
    // @ts-ignore
    const webVitals = await import('web-vitals')
    if (webVitals) {
      const { getCLS, getFID, getLCP } = webVitals
      getCLS((m: any) => sendMetric({ name: 'webvitals.cls', value: m.value }))
      getFID((m: any) => sendMetric({ name: 'webvitals.fid', value: m.value }))
      getLCP((m: any) => sendMetric({ name: 'webvitals.lcp', value: m.value }))
    }
  } catch (e) {
    // web-vitals not installed — that's fine
    if (process.env.NODE_ENV !== 'production')
      console.debug('[mf-telemetry] web-vitals not available')
  }
}

export default init
