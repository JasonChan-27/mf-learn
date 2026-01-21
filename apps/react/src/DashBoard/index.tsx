import { useEffect } from 'react'
import { type SharedRuntime } from 'mf-shared'

function DashBoard({ runtime }: { runtime: SharedRuntime }) {
  useEffect(() => {
    runtime?.bus?.on('mainAppBtnClick', (data) => {
      console.log('DashBoard页面收到主应用按钮点击事件，时间：', data)
    })

    runtime?.globalState$?.subscribe((state) => {
      console.log('DashBoard页面收到全局状态更新：', state)
    })
  }, [])

  return <div>DashBoard页</div>
}

export default DashBoard
