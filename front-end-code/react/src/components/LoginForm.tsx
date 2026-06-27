import React, { useState } from 'react'

interface LoginFormProps {
  onLogin?: (username: string, password: string) => void
}

export const LoginForm: React.FC<LoginFormProps> = ({ onLogin }) => {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [rememberMe, setRememberMe] = useState(false)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onLogin?.(username, password)
  }

  const handleReset = () => {
    setUsername('')
    setPassword('')
    setRememberMe(false)
  }

  return (
    <div className="login-form">
      <h2>用户登录</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="username">用户名</label>
          <input
            id="username"
            type="text"
            placeholder="请输入用户名"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            data-testid="username-input"
          />
        </div>

        <div className="form-group">
          <label htmlFor="password">密码</label>
          <input
            id="password"
            type="password"
            placeholder="请输入密码"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            data-testid="password-input"
          />
        </div>

        <div className="form-group">
          <input
            id="remember"
            type="checkbox"
            checked={rememberMe}
            onChange={(e) => setRememberMe(e.target.checked)}
            data-testid="remember-checkbox"
          />
          <label htmlFor="remember">记住我</label>
        </div>

        <button type="submit" data-testid="login-button">
          登录
        </button>

        <button type="button" onClick={handleReset} data-testid="reset-button">
          重置
        </button>
      </form>

      <a href="/forgot-password" data-testid="forgot-link">
        忘记密码？
      </a>
    </div>
  )
}

export default LoginForm