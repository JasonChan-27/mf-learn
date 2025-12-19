export type RemoteMount = (el: HTMLElement) => () => void

declare module 'vueApp/*' {
  import { DefineComponent } from 'vue'
  const component: DefineComponent<any, any, any>
  export default component
}

declare module 'reactApp/*' {
  const mount: RemoteMount
  export default mount
}
