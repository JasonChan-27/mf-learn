type Callback = (payload?: any) => void

class EventBus {
  private events = new Map<string, Set<Callback>>()

  on(event: string, callback: Callback) {
    if (!this.events.has(event)) this.events.set(event, new Set())
    this.events.get(event)!.add(callback)
  }

  off(event: string, callback: Callback) {
    this.events.get(event)?.delete(callback)
  }

  emit(event: string, payload?: any) {
    this.events.get(event)?.forEach((cb) => cb(payload))
  }
}

export const bus = new EventBus()
