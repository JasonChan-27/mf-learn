<script setup lang="ts">
// 加载 React 组件：需用 @vue/reactivity 或 vue-react-wrapper 适配
import { ref, onMounted, onUnmounted, defineAsyncComponent } from 'vue'

// 懒加载 Vue 子应用组件
const VueHomePage = defineAsyncComponent(() => import('vueApp/Home'))
const reactModulePromise = import('reactApp/DashBoard')
const reactContainer = ref<HTMLElement | null>(null)
let unmount: (() => void) | null = null

onMounted(async () => {
  const { mount } = await reactModulePromise
  unmount = mount(reactContainer.value)
})

onUnmounted(() => {
  unmount?.()
})
</script>

<template>
  <div>
    <h1>主应用</h1>
    <!-- 加载 Vue3 子应用组件 -->
    <VueHomePage />
    <!-- 加载 React19 子应用组件（需适配 Vue 中使用 React） -->
    <div ref="reactContainer"></div>
  </div>
</template>

<style scoped>
.logo {
  height: 6em;
  padding: 1.5em;
  will-change: filter;
  transition: filter 300ms;
}
.logo:hover {
  filter: drop-shadow(0 0 2em #646cffaa);
}
.logo.vue:hover {
  filter: drop-shadow(0 0 2em #42b883aa);
}
</style>
