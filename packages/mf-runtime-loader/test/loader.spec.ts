import { describe, it, expect } from 'vitest'
import { loadRemote } from '../src/loader'
import type { MicroAppConfig } from '../src/types'

function dataModuleCode(successText = 'ok', delay = 0) {
  return `export async function init() { return }
export function get(name) { return () => ({ mount: (el, props) => { ${delay ? `const t = Date.now(); while(Date.now()-t<${delay}){};` : ''} el.innerHTML = '${successText}'; return () => { el.innerHTML = '' } } }) }`
}

function dataUrl(code: string) {
  return 'data:text/javascript;base64,' + Buffer.from(code).toString('base64')
}

describe('mf-runtime-loader loadRemote', () => {
  it('loads remote module successfully', async () => {
    const code = dataModuleCode('loaded')
    const url = dataUrl(code)
    const el = document.createElement('div')
    const unmount = await loadRemote(el, {
      app: 'test',
      name: 'm1',
      scope: 's',
      module: './x',
      url,
    } as MicroAppConfig)
    expect(el.innerHTML).toBe('loaded')
    // call unmount
    unmount()
    expect(el.innerHTML).toBe('')
  })

  // it('falls back to alternate url on timeout', async () => {
  //   const slow = dataUrl(dataModuleCode('slow', 200))
  //   const fast = dataUrl(dataModuleCode('fast'))
  //   const el = document.createElement('div')
  //   const unmount = await loadRemote(el, {
  //     app: 'test',
  //     name: 'm2',
  //     scope: 's',
  //     module: './x',
  //     url: slow,
  //     alternates: [fast],
  //     timeout: 50,
  //   } as MicroAppConfig)
  //   expect(el.innerHTML).toBe('fast')
  //   unmount()
  // })

  // it('opens circuit after repeated failures', async () => {
  //   const bad = 'data:text/javascript,throw new Error("bad")'
  //   const el = document.createElement('div')
  //   // three sequential failures should trigger circuit (config below)
  //   for (let i = 0; i < 4; i++) {
  //     try {
  //       await loadRemote(el, {
  //         app: 'test',
  //         name: 'm3',
  //         scope: 's',
  //         module: './x',
  //         url: bad,
  //         retryCount: 1,
  //         circuitThreshold: 3,
  //         circuitWindowMs: 10000,
  //         timeout: 20,
  //       } as MicroAppConfig)
  //     } catch (e) {
  //       console.log('loadRemote failed as expected:', e)
  //     }
  //   }
  //   // now circuit should be open and immediate reject
  //   await expect(
  //     loadRemote(document.createElement('div'), {
  //       app: 'test',
  //       name: 'm3',
  //       scope: 's',
  //       module: './x',
  //       url: bad,
  //       retryCount: 1,
  //       circuitThreshold: 3,
  //       circuitWindowMs: 10000,
  //       timeout: 20,
  //     } as MicroAppConfig),
  //   ).rejects.toThrow(/circuit open/)
  // })

  it('dedupes concurrent imports for same url', async () => {
    // reset counter
    ;(globalThis as unknown).__LOAD_COUNT__ = 0
    const code = `window.__LOAD_COUNT__ = (window.__LOAD_COUNT__ || 0) + 1; export async function init(){}; export function get(){ return () => ({ mount: (el) => { el.innerHTML = 'dedupe'; return () => { el.innerHTML = '' } } }) }`
    const url =
      'data:text/javascript;base64,' + Buffer.from(code).toString('base64')
    const el1 = document.createElement('div')
    const el2 = document.createElement('div')

    const cfg = {
      app: 'test',
      name: 'm4',
      scope: 's',
      module: './x',
      url,
    } as MicroAppConfig

    const p1 = loadRemote(el1, cfg)
    const p2 = loadRemote(el2, cfg)

    await Promise.all([p1, p2])

    expect((globalThis as unknown).__LOAD_COUNT__).toBe(1)
    expect(el1.innerHTML).toBe('dedupe')
    expect(el2.innerHTML).toBe('dedupe')
  })
})

function makeDataModule(code: string) {
  const b64 = Buffer.from(code).toString('base64')
  return `data:text/javascript;base64,${b64}`
}

describe('loader', () => {
  it('loads remote module from primary url', async () => {
    const code = `export async function init(){}; export async function get(name){ return () => ({ mount(el){ el.innerHTML = 'mounted:'+name; return ()=>{} } }) }`
    const url = makeDataModule(code)
    const el = document.createElement('div')

    const unmount = await loadRemote(el, {
      name: 'm',
      scope: 's',
      module: 'mod',
      url,
    })
    expect(el.innerHTML).toContain('mounted:mod')
    // call unmount
    unmount()
  })

  // it('falls back to alternate url when primary fails', async () => {
  //   const bad = 'https://invalid.invalid/does-not-exist.js'
  //   const code = `export async function init(){}; export async function get(name){ return () => ({ mount(el){ el.innerHTML = 'alt:'+name; return ()=>{} } }) }`
  //   const alt = makeDataModule(code)
  //   const el = document.createElement('div')

  //   const unmount = await loadRemote(el, {
  //     name: 'm',
  //     scope: 's',
  //     module: 'mod',
  //     url: bad,
  //     alternates: [alt],
  //     timeout: 1000,
  //   })

  //   expect(el.innerHTML).toContain('alt:mod')
  //   unmount()
  // })

  it('uses provided fallback when all urls fail', async () => {
    const bad = 'https://invalid.invalid/does-not-exist.js'
    const el = document.createElement('div')

    const fallback = () => {
      const d = document.createElement('div')
      d.textContent = 'fallback'
      return d
    }

    await expect(
      loadRemote(el, {
        name: 'm',
        scope: 's',
        module: 'mod',
        url: bad,
        alternates: ['https://also.invalid/rem.js'],
        timeout: 500,
        fallback,
      }),
    ).resolves.toBeInstanceOf(Function)

    expect(el.textContent).toBe('fallback')
  })
})
