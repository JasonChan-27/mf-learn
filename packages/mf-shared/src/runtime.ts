import { BehaviorSubject } from 'rxjs'
import { bus, EventBus } from './eventBus'
import { type GlobalState } from './store'

export interface SharedRuntime {
  bus: EventBus
  globalState$: BehaviorSubject<GlobalState>
  setGlobalState: (state: Partial<GlobalState>) => void
  getGlobalState: () => GlobalState
}

export function createSharedRuntime(): SharedRuntime {
  const globalState$ = new BehaviorSubject<GlobalState>({})

  return {
    bus: new EventBus(),
    globalState$,
    setGlobalState(state) {
      globalState$.next({ ...globalState$.value, ...state })
    },
    getGlobalState() {
      return globalState$.value
    },
  }
}
