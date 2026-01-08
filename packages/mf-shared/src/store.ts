import { BehaviorSubject } from 'rxjs'

export interface GlobalState {
  user?: { id: number; name: string }
  theme?: string
  [key: string]: any
}

// 初始化全局状态
export const globalState$ = new BehaviorSubject<GlobalState>({})

// 便利方法
export const setGlobalState = (state: Partial<GlobalState>) => {
  globalState$.next({ ...globalState$.value, ...state })
}

export const getGlobalState = () => globalState$.value
