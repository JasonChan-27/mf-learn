type RemoteMount = (el: HTMLElement) => () => void

declare module 'vueApp/*' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<any, any, any>
  export default component
}

type RemoteMount = (el: HTMLElement) => () => void
declare module 'reactApp/*' {
  const mount: RemoteMount
  export default mount
}
