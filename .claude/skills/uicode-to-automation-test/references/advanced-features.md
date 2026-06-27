# 高级特性参考 — 利用 src/ 模块化架构增强测试生成

技能脚本 `front_end_to_ui_automation.py` 是一个单体脚本，覆盖了核心功能。
项目 `src/` 目录是模块化架构的实现，包含一些技能脚本未完全覆盖的**高级特性**。

## 何时使用 src/ 模块而非技能脚本

| 场景 | 推荐 | 原因 |
|------|------|------|
| 仅 Vue 组件（.vue） | `src/` | 支持 Element Plus / Ant Design Vue，嵌套结构解析更准确 |
| Vue + React 混合 | 技能脚本 | 脚本同时支持两种框架 |
| 需要 Java 输出 | 技能脚本 | `src/` 不支持 Java |
| 需要智能断言 | `src/` | 上下文感知的断言生成 |
| 需要 Pinia Store 测试 | 两者均可 | `src/` 支持类型推断，更完善 |
| 需要 Redux 测试 | 技能脚本 | `src/` 不支持 Redux |

## src/ 模块结构

```
src/
├── vue_test_generator.py       # CLI 入口（仅 Vue）
├── parser/
│   ├── vue_parser.py           # HTMLParser 基础，支持嵌套结构
│   ├── router_parser.py        # Vue Router 解析
│   └── pinia_parser.py         # Pinia Store 解析
├── generator/
│   ├── main_generator.py       # 主生成器（协调解析和生成）
│   ├── ts_generator.py         # TypeScript 测试代码生成
│   ├── py_generator.py         # Python 测试代码生成
│   ├── selector_generator.py   # 结构化选择器（语言无关）
│   └── assertion_generator.py  # 智能断言生成
├── pom/
│   └── pom_generator.py        # POM 类生成（TS + Python）
├── baw/
│   └── baw_generator.py        # BAW 检测 + 生成
└── utils/
    └── identifier_utils.py     # 标识符规范化
```

## 核心差异详解

### 1. Vue 解析器 — html.parser vs regex

技能脚本使用正则表达式解析模板，`src/parser/vue_parser.py` 使用 `html.parser.HTMLParser`：

| 特性 | 技能脚本（regex） | src（HTMLParser） |
|------|------------------|-------------------|
| 嵌套结构 | 不支持 | ✅ 追踪标签栈 |
| `<template>` 内部模板标签 | ❌ 可能误判 | ✅ 替换为 `<vue-template>` |
| 文本收集 | 简单匹配 | ✅ 每层标签独立收集 |
| Element Plus 组件 | ❌ | ✅ `el-button`, `el-input` 等 |
| Ant Design Vue 组件 | ❌ | ✅ `a-button`, `a-input` 等 |

### 2. 断言生成 — 上下文感知

技能脚本生成基础断言，`src/generator/assertion_generator.py` 支持更丰富的场景：

```python
# 登录按钮 → 断言 URL 跳转 + 欢迎文本
# 提交按钮 → 断言 success-message 可见
# 删除操作 → 断言元素隐藏
# reset 方法 → 断言输入框清空
# validate 方法 → 断言错误消息可见
```

使用方法：
```python
from src.generator.assertion_generator import AssertionGenerator
generator = AssertionGenerator()
assertions = generator.generate_assertions(component, element, event_name)
# 返回 Assertion 列表，可转换为 TS/Python 断言代码
```

### 3. POM 结构

技能脚本生成内联定位器，`src/pom/pom_generator.py` 生成标准 POM：

```typescript
// 技能脚本方式
async clickLoginButton(page) {
  await page.getByRole('button', { name: '登录' }).click();
}

// src 方式 — 有独立 Locator + goto()
export class LoginPage {
  readonly loginButton: Locator;        // 独立的定位器属性
  constructor(page: Page) {
    this.loginButton = page.getByRole('button', { name: '登录' });
  }
  async goto() { /* ... */ }            // 封装导航
  async clickLoginButton() {            // 方法调用
    await this.loginButton.click();
  }
}
```

### 4. BAW 方法调用

技能脚本生成注释步骤，`src/baw/baw_generator.py` 生成**实际方法调用**：

```typescript
// 技能脚本方式
export class LoginBAW {
  async execute(username: string, password: string) {
    await this.loginPage.goto();
    // 输入用户名 <- 占位符
    // 输入密码   <- 占位符
    // 点击登录   <- 占位符
  }
}

// src 方式 — 根据解析到的元素生成真实调用
export class LoginBAW {
  async execute(username: string, password: string) {
    await this.loginPage.goto();
    await this.loginPage.fillUsername(username);   // 实际方法
    await this.loginPage.fillPassword(password);   // 实际方法
    await this.loginPage.clickLoginButton();       // 实际方法
  }
}
```

### 5. 标识符规范化

技能脚本有基础中文映射，`src/utils/identifier_utils.py` 更完整：

```python
# 额外处理
normalize_identifier('<button>登录</button>')  # → "Login"（移除HTML标签）
normalize_identifier('{{ user.name }}')         # → ""（移除插值）
normalize_identifier('@click.prevent="submit"')  # → ""（移除修饰符）
```

## 组合使用建议

对于复杂项目，可采用混合策略：

1. **快速原型**：使用技能脚本生成基础测试
2. **智能增强**：用 `src/` 的断言生成器提升测试质量
3. **React + Vue 混合项目**：使用技能脚本，手动增强断言
4. **纯 Vue 项目**：直接使用 `src/` 的模块化架构
