<template>
  <div>Home页面2</div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRuntime } from '@/hooks'
import type { Runtime } from '@/types'

const runtime: Runtime = useRuntime()

onMounted(() => {
  runtime?.bus?.on('mainAppBtnClick', (data) => {
    console.log('Home页面收到主应用按钮点击事件，时间：', data)
  })
  runtime?.globalState$?.subscribe((state) => {
    console.log('Home页面收到全局状态更新：', state)
  })
})
</script>
