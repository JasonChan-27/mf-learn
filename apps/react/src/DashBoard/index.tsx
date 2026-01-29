import { useEffect } from 'react'
import { useRuntime } from '@/hooks'
import type { Runtime } from '@/types'

function DashBoard() {
  const runtime: Runtime = useRuntime()

  useEffect(() => {
    runtime?.bus?.on('mainAppBtnClick', (data: unknown) => {
      console.log('DashBoard页面收到主应用按钮点击事件，时间：', data)
    })

    runtime?.globalState$?.subscribe((state: unknown) => {
      console.log('DashBoard页面收到全局状态更新：', state)
    })
  }, [])

  return <div>DashBoard页</div>
}

export default DashBoard
