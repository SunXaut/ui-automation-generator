import React, { useState } from 'react'

function Dashboard() {
  const [count, setCount] = useState(0)

  const increment = () => {
    setCount(count + 1)
    console.log('增加:', count + 1)
  }

  const decrement = () => {
    setCount(count - 1)
    console.log('减少:', count - 1)
  }

  const reset = () => {
    setCount(0)
    console.log('重置计数器')
  }

  return (
    <div className="dashboard">
      <h1>仪表盘</h1>
      <div className="counter">
        <p>计数器: {count}</p>
        <div className="counter-buttons">
          <button onClick={increment} data-testid="increment-btn">
            增加
          </button>
          <button onClick={decrement} data-testid="decrement-btn">
            减少
          </button>
          <button onClick={reset} data-testid="reset-btn">
            重置
          </button>
        </div>
      </div>
    </div>
  )
}

export default Dashboard