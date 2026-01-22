<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue'
import { startMicroRouter } from 'mf-runtime-loader'
import HelloWorld from './components/HelloWorld.vue'
import { microRegistry } from '@/config'
import { sharedRuntime } from '@/utils'

const sendMainAppBtnClickEvent = () => {
  sharedRuntime.bus.emit('mainAppBtnClick', {
    time: new Date().toLocaleString(),
  })
}

const setGlobalState = () => {
  sharedRuntime.globalState$.next({
    user: { id: 1, name: 'Jason', timestamp: new Date().toLocaleString() },
  })
}

onMounted(async () => {
  startMicroRouter(
    (name) => document.querySelectorAll(`[data-micro="${name}"]`),
    microRegistry,
  )

  sharedRuntime.bus.on('mainAppBtnClick', (data: any) => {
    console.log('主应用页面收到主应用按钮点击事件，时间：', data)
  })

  sharedRuntime.globalState$.subscribe((state: any) => {
    console.log('主应用页面收到全局状态更新：', state)
  })
})

onUnmounted(() => {
  // unmount?.()
})
</script>

<template>
  <div>
    <h1>主应用</h1>
    <div>
      <button @click="sendMainAppBtnClickEvent">
        点击发送主应用按钮点击事件
      </button>
      <button @click="setGlobalState">设置全局状态</button>
    </div>
    <!-- 加载 Vue3 子应用组件 -->
    <div data-micro="vueHome"></div>
    <!-- 加载 React19 子应用组件 -->
    <div data-micro="reactDashboard"></div>
    <HelloWorld msg="I am HelloWorld" />
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
