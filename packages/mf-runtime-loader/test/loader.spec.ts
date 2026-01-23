import { describe, it, expect } from 'vitest'
import { loadRemote } from '../src/loader'

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

  it('falls back to alternate url when primary fails', async () => {
    const bad = 'https://invalid.invalid/does-not-exist.js'
    const code = `export async function init(){}; export async function get(name){ return () => ({ mount(el){ el.innerHTML = 'alt:'+name; return ()=>{} } }) }`
    const alt = makeDataModule(code)
    const el = document.createElement('div')

    const unmount = await loadRemote(el, {
      name: 'm',
      scope: 's',
      module: 'mod',
      url: bad,
      alternates: [alt],
      timeout: 1000,
    })

    expect(el.innerHTML).toContain('alt:mod')
    unmount()
  })

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
