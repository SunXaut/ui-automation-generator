import React, { useState } from 'react'

function About() {
  const [showDetails, setShowDetails] = useState(false)

  const toggleDetails = () => {
    setShowDetails(!showDetails)
    console.log('切换详情:', !showDetails)
  }

  return (
    <div className="about-page">
      <h1>关于我们</h1>
      <p>这是一个关于页面</p>
      <button onClick={toggleDetails} data-testid="toggle-btn">
        {showDetails ? '隐藏' : '显示'}详情
      </button>
      {showDetails && (
        <div className="details" data-testid="details-section">
          <p>这里是更多详情信息...</p>
        </div>
      )}
    </div>
  )
}

export default About