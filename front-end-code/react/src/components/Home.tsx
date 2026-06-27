import React, { useState } from 'react'

function Home() {
  const [message, setMessage] = useState('欢迎来到首页')

  const showAlert = () => {
    alert('这是首页提示！')
  }

  const updateMessage = () => {
    setMessage('消息已更新')
  }

  return (
    <div className="home-page">
      <h1>{message}</h1>
      <p>这是一个React 18 + TypeScript + Vite项目</p>
      <div className="home-actions">
        <button onClick={showAlert} data-testid="alert-btn">
          显示提示
        </button>
        <button onClick={updateMessage} data-testid="update-btn">
          更新消息
        </button>
      </div>
    </div>
  )
}

export default Home