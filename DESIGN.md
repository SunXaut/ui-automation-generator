# Vue to Playwright Test Generator - 设计文档

## 项目概述

**项目名称**: vue-playwright-generator
**项目类型**: CLI工具 / Node.js 包
**核心功能**: 通过AST解析Vue组件代码，自动生成Playwright场景化UI自动化测试
**技术栈**: Node.js + TypeScript + @vue/compiler-sfc + Playwright

## 目标

- 从Vue组件代码中提取用户交互场景
- 自动生成可执行的Playwright测试脚本
- 帮助团队快速建立UI自动化测试覆盖率

## 技术选型

| 维度 | 选择 |
|------|------|
| 测试框架 | Playwright |
| AST解析 | @vue/compiler-sfc |
| 项目规模 | 中型 (20-100组件) |
| 输出格式 | TypeScript (.spec.ts) |

## MVP范围

### 第一阶段：简单场景生成

从 .vue 文件中提取：
- @click 事件绑定 → 生成点击测试
- @input / @change 事件 → 生成输入测试
- 组件结构信息 → 生成组件定位符

### 后续扩展（暂不实现）

- [ ] 路由配置解析 → 页面流程测试
- [ ] Pinia/Vuex Store解析 → 状态管理测试
- [ ] 边界条件场景补充
- [ ] AI辅助场景扩展

## 设计架构

```
┌─────────────────────────────────────────┐
│           Vue 组件 (.vue)                 │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│        @vue/compiler-sfc                │
│   解析 template + script + styles        │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│         AST 遍历与提取                   │
│   - 提取事件绑定 (@click, @input...)     │
│   - 提取元素选择器                       │
│   - 提取条件分支                        │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│        场景化测试生成器                  │
│   - 生成 Playwright 测试用例             │
│   - 生成定位策略                         │
│   - 生成断言                            │
└─────────────────────────────────────────┘
```

## 输出示例

输入 Vue 组件：
```vue
<template>
  <button @click="handleSubmit">提交</button>
  <input v-model="username" @blur="validateUsername" />
</template>
```

输出 Playwright 测试：
```typescript
import { test, expect } from '@playwright/test';

test.describe('组件名', () => {
  test('点击提交按钮', async ({ page }) => {
    await page.click('button');
  });

  test('输入用户名并验证', async ({ page }) => {
    await page.fill('input', 'testuser');
    await page.blur('input');
  });
});
```

## 下一步行动

1. 创建项目结构
2. 实现 AST 解析模块
3. 实现测试生成模块
4. 创建 CLI 入口
5. 测试验证