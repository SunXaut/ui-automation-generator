import React, { useState } from 'react'
import LoginForm from './LoginForm'

function Login() {
  const [isSubmitted, setIsSubmitted] = useState(false)

  const handleLogin = (username: string, password: string) => {
    console.log('登录:', { username, password })
    setIsSubmitted(true)
  }

  return (
    <div className="login-page">
      <h1>登录页面</h1>
      {isSubmitted ? (
        <div className="success-message">
          <p>登录成功！</p>
          <button onClick={() => setIsSubmitted(false)}>
            返回登录
          </button>
        </div>
      ) : (
        <LoginForm onLogin={handleLogin} />
      )}
    </div>
  )
}

export default Login