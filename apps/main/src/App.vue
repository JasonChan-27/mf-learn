<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue'
import { startMicroRouter } from 'mf-runtime-loader'
import { microRegistry } from './config'

// 懒加载 Vue 子应用组件
// const VueHomePage = defineAsyncComponent(() => import('vueApp/Home'))
// const reactContainer = ref<HTMLElement | null>(null)
// let unmount: (() => void) | null = null

onMounted(async () => {
  startMicroRouter(
    (name) => document.querySelector(`[data-micro="${name}"]`),
    microRegistry,
  )
})

onUnmounted(() => {
  // unmount?.()
})
</script>

<template>
  <div>
    <h1>主应用</h1>
    <!-- 加载 Vue3 子应用组件 -->
    <!-- <VueHomePage /> -->
    <!-- 加载 React19 子应用组件（需适配 Vue 中使用 React） -->
    <!-- <div ref="reactContainer"></div> -->
    <div data-micro="vueHome"></div>
    <div data-micro="reactDashboard"></div>
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
