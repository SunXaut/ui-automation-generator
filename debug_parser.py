#!/usr/bin/env python3
"""
调试 Vue 解析器 - 检查为什么某些组件没有提取到元素
"""

import re

# 测试 Dashboard.vue 的模板
dashboard_template = """
  <div class="dashboard">
    <h1>仪表盘</h1>
    <div class="stats">
      <div class="stat-card">
        <h3>总用户数</h3>
        <p class="stat-value">{{ totalUsers }}</p>
        <button @click="refreshStats" class="refresh-btn">
          刷新
        </button>
      </div>
    </div>
  </div>
"""

# 测试 Search.vue 的模板
search_template = """
  <div class="search">
    <input v-model="searchQuery" type="text" placeholder="请输入搜索关键词" 
      @input="handleSearch" @focus="onFocus" @blur="onBlur" />
    <button @click="performSearch" class="search-btn">搜索</button>
  </div>
"""

# 测试 App.vue 的模板
app_template = """
  <div id="app">
    <header class="app-header">
      <nav>
        <router-link to="/">首页</router-link>
        <router-link to="/about">关于</router-link>
      </nav>
    </header>
  </div>
"""

print("=" * 60)
print("调试模板元素提取")
print("=" * 60)

# 测试标签匹配正则
tag_pattern = re.compile(r'<(\w+)([^>]*)>(.*?)</\1>|<(\w+)([^>]*)/>', re.DOTALL)

for name, template in [("Dashboard", dashboard_template), ("Search", search_template), ("App", app_template)]:
    print(f"\n{'='*60}")
    print(f"模板: {name}")
    print(f"{'='*60}")
    
    matches = list(tag_pattern.finditer(template))
    print(f"找到 {len(matches)} 个标签匹配")
    
    for match in matches:
        if match.group(1):  # 闭合标签
            tag = match.group(1)
            attrs_str = match.group(2)
            text = match.group(3).strip()
        else:  # 自闭合标签
            tag = match.group(4)
            attrs_str = match.group(5)
            text = ""
        
        # 检查是否是可交互元素
        interactive_tags = ['button', 'input', 'a', 'select', 'textarea', 'form']
        is_interactive = tag in interactive_tags
        
        print(f"  标签: <{tag}>, 可交互: {is_interactive}")
        if '@' in attrs_str:
            print(f"    属性: {attrs_str[:80]}...")
            # 检查事件
            event_pattern = re.compile(r'@(\w+)(?:\.(\w+))?(?:\.(\w+))?="([^"]*)"')
            events = list(event_pattern.finditer(attrs_str))
            if events:
                print(f"    事件: {[e.group(1) for e in events]}")
