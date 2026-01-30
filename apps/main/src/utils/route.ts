const BASE_PATH = import.meta.env.BASE_URL.replace(/\/$/, '')

export function startsWithPath(pathname: string, subPath = '/') {
  return pathname.startsWith(`${BASE_PATH}${subPath}`)
}

export function isExactPath(pathname: string, subPath = '/') {
  return pathname === `${BASE_PATH}${subPath}`
}
