import React, { useState } from 'react'

function Search() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<string[]>([])

  const handleSearch = () => {
    console.log('搜索:', query)
    if (query) {
      setResults([
        `结果1: ${query}相关内容`,
        `结果2: ${query}更多信息`,
        `结果3: ${query}相关条目`
      ])
    }
  }

  const handleClear = () => {
    setQuery('')
    setResults([])
  }

  return (
    <div className="search-page">
      <h1>搜索页面</h1>
      <div className="search-container">
        <input
          type="search"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="输入搜索关键词"
          className="search-input"
          data-testid="search-input"
        />
        <button onClick={handleSearch} data-testid="search-btn">
          搜索
        </button>
        <button onClick={handleClear} data-testid="clear-btn">
          清除
        </button>
      </div>
      {results.length > 0 && (
        <div className="results">
          <p>找到 {results.length} 个结果:</p>
          <ul>
            {results.map((result, index) => (
              <li key={index} data-testid={`result-${index}`}>
                {result}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}

export default Search