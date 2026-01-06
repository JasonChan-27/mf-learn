export function createErrorFallback(msg: string) {
  const el = document.createElement('div')
  el.style.padding = '16px'
  el.style.color = '#f56c6c'
  el.innerText = msg
  return el
}
