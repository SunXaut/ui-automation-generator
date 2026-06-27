import React from 'react'
import { Routes, Route, Link } from 'react-router-dom'
import Login from './components/Login'
import Dashboard from './components/Dashboard'
import Search from './components/Search'
import Home from './components/Home'
import About from './components/About'

function App() {
  return (
    <div className="app">
      <header className="app-header">
        <nav>
          <Link to="/">首页</Link>
          <Link to="/about">关于</Link>
          <Link to="/login">登录</Link>
          <Link to="/dashboard">仪表盘</Link>
          <Link to="/search">搜索</Link>
        </nav>
      </header>
      <main>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/about" element={<About />} />
          <Route path="/login" element={<Login />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/search" element={<Search />} />
        </Routes>
      </main>
    </div>
  )
}

export default App