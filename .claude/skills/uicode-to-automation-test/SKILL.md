---
name: "uicode-to-automation-test"
description: "Generates Playwright UI automation tests from Vue (.vue) and React (.tsx/.jsx) components. Supports POM (Page Object Model), BAW (Business Action Workflow) patterns, TypeScript/Java/Python output, and includes full Playwright best practices (locators, assertions, fixtures, auth, debugging, CI/CD). Use when user asks to: create UI automation tests from front-end component files, convert Vue/React code to Playwright tests, write or debug Playwright tests, set up Playwright project configuration, or optimize existing Playwright test suites."
---

# UI Code to Automation Test Generator — Playwright Edition

> 整合了 [playwright-skill](https://github.com/testdino-hq/playwright-skill) (v2.2.0) 的全部最佳实践。集测试生成与 Playwright 专家指导于一体。

从 Vue / React 组件代码自动生成 Playwright 场景化 UI 自动化测试用例。

## 核心能力

| 维度 | 支持 | 详情 |
|------|------|------|
| **前端框架** | Vue + React | `.vue` / `.tsx` / `.jsx` |
| **输出语言** | TypeScript / Java / Python | 自动适配命名规范 |
| **模式** | POM + BAW | 单页操作 + 业务流程 |
| **扩展解析** | Router / Pinia / Redux | 路由和状态管理测试 |
| **外部站点** | `--scaffold` | 为非 Vue/React 站点生成测试脚手架 |
| **批量生成** | `--all` | 一键扫描目录生成所有组件测试 |
| **快照测试** | `--snapshot` | 截图断言，自动比对基线 |
| **日志系统** | conftest 集成 | 每个用例独立日志文件 |
| **配置系统** | `test_config.toml` | 浏览器 / 日志 / 环境集中配置 |
| **选择器** | `data-testid` 优先 | 自动识别并生成对应定位器 |

## 执行流程

### ⚠️ 执行前检查清单（必须执行）

| # | 检查项 | 说明 |
|---|--------|------|
| 1 | **确定组件路径** | Vue(.vue) 或 React(.tsx/.jsx) 文件或目录 |
| 2 | **确认编程语言** | **若用户未指定，必须用 AskUserQuestion 询问** |
| 3 | **确定输出目录** | 默认 `tests/`，可自定义 |
| 4 | **选择生成模式** | 纯 spec / POM / POM+BAW |

> 💡 **Python 自动安装依赖**：选择 Python 语言时，生成脚本会自动检测并安装 `playwright`、`pytest`、`pytest-playwright` 等缺失依赖，以及 Chromium 浏览器。无需手动 `pip install`。

### ⚠️ 重要：语言选择规则

> **如果用户未指定编程语言，必须立即使用 AskUserQuestion 工具询问：**
>
> ```
> 问题: 请选择生成测试脚本的编程语言
> 选项:
> - 1. TypeScript (推荐用于Vue/React等前端项目)
> - 2. Java (适用于Java技术栈项目)
> - 3. Python (适用于Python技术栈项目)
> ```

## 引用 Playwright Skill

本技能直接引用 **playwright-skill** 的最佳实践。在生成测试时，应遵循 playwright-skill 中的指南和 Golden Rules（见下方）。

如果使用 `skill` 命令，建议先加载 playwright-skill：

```
/claude playwright-skill
```

## 执行命令

```bash
# TS测试（含POM+BAW）
python .claude/skills/uicode-to-automation-test/scripts/front_end_to_ui_automation.py <component_file> -o tests --language typescript --generate-baw

# Python测试
python .claude/skills/uicode-to-automation-test/scripts/front_end_to_ui_automation.py <component_file> -o tests --language python --generate-baw

# Java测试
python .claude/skills/uicode-to-automation-test/scripts/front_end_to_ui_automation.py <component_file> -o tests --language java --generate-baw

# 纯spec（无POM/BAW）
python <script> <component_file> -o tests --language typescript --no-pom

# 生成外部站点测试脚手架（无需 Vue/React 组件）
python .claude/skills/uicode-to-automation-test/scripts/front_end_to_ui_automation.py \
  --scaffold bing_search --base-url https://www.bing.com -o tests --language python

# 生成外部站点测试脚手架 + Snapshot 截图断言
python .claude/skills/uicode-to-automation-test/scripts/front_end_to_ui_automation.py \
  --scaffold bing_search --base-url https://www.bing.com -o tests --language python --snapshot

# 生成 TypeScript 脚手架
python .claude/skills/uicode-to-automation-test/scripts/front_end_to_ui_automation.py \
  --scaffold bing_search --base-url https://www.bing.com -o tests --language typescript

# 强制覆盖已有文件（配合 --scaffold）
python .claude/skills/uicode-to-automation-test/scripts/front_end_to_ui_automation.py \
  --scaffold bing_search --base-url https://www.bing.com --force

# 批量生成所有组件测试（自动扫描 front-end-code/）
python .claude/skills/uicode-to-automation-test/scripts/front_end_to_ui_automation.py \
  --all -o tests --language python

# 解析Router/Store/Reducer（支持 Python/TS/Java）
python .claude/skills/uicode-to-automation-test/scripts/front_end_to_ui_automation.py <router_file> --router -o tests --language python
python .claude/skills/uicode-to-automation-test/scripts/front_end_to_ui_automation.py <store_file> --store -o tests
python .claude/skills/uicode-to-automation-test/scripts/front_end_to_ui_automation.py <reducer_file> --redux -o tests
```

参数说明：

| 参数 | 说明 |
|------|------|
| `<component_file>` | Vue/React 组件文件或目录路径 |
| `-o <output_dir>` | 输出目录，默认 `./tests` |
| `--language` | 输出语言：`typescript` / `java` / `python` |
| `--generate-baw` | 生成 BAW 业务流程文件 |
| `--no-pom` | 不生成 POM 文件 |
| `--router` | 解析 Vue/React Router 配置 |
| `--store` | 解析 Pinia Store 配置 |
| `--all` | 批量扫描 front-end-code/ 目录，自动识别 Vue(.vue) / React(.tsx) / Router / Store 并生成测试 |
| `--scaffold <name>` | 为外部站点生成测试脚手架（需配合 `--base-url`） |
| `--base-url <url>` | 外部站点基 URL |
| `--snapshot` | 生成截图断言（Snapshot 基线） |
| `--force` | 强制覆盖已有文件 |
| `--install-deps` | 自动安装缺失的 Python 依赖（默认开启） |

## 组件类型智能识别

扩展名模糊时（如 `.js`），根据内容特征判断：

| 框架 | 特征 |
|------|------|
| Vue | `<template>` 标签、`defineComponent`、`ref/reactive from 'vue'` |
| React | `useState/useEffect`、`import React`、JSX 语法 |

## UI 组件库支持

技能脚本自动识别以下 UI 库组件（与标准 HTML 元素同等处理）：

| 库 | 组件示例 |
|----|---------|
| Element Plus | `el-button`, `el-input`, `el-select`, `el-form`, `el-dialog` |
| Ant Design Vue | `a-button`, `a-input`, `a-select`, `a-form`, `a-modal` |
| Vue Router | `router-link`, `router-view` |

## Vue 指令解析

解析器从模板中提取以下结构化信息：

- **v-if / v-else-if** — 条件表达式
- **v-for** — 集合名、迭代变量、索引
- **v-model** — 绑定的数据属性
- **动态绑定** — `:prop="expr"` / `v-bind:prop="expr"`
- **事件修饰符** — `.prevent`, `.stop`, `.capture` 等

## 组件元信息提取

从 `<script>` 中提取组件元数据，用于更智能的测试生成：

- **props** — 属性定义（名称、类型、是否必填）
- **emits** — 事件声明
- **data/methods/computed** — Composition API（ref/reactive）或 Options API

## 选择的器生成策略

优先级：`data-testid` > `getByRole` > `getByLabel` > `getByPlaceholder` > CSS

详细规则见 [references/selectors.md](references/selectors.md)。

## 智能断言生成

根据元素类型和上下文自动生成 Web-first 断言：

| 场景 | 生成断言 |
|------|----------|
| 登录按钮点击 | `toHaveURL(/dashboard/)` + `toContainText('欢迎')` |
| 注册按钮点击 | `toHaveURL(/register/)` + `toContainText('注册成功')` |
| 提交按钮点击 | `toBeVisible()` success-message |
| 搜索按钮点击 | `toHaveCount(>0)` 搜索结果 |
| 保存按钮点击 | `toBeVisible()` 保存成功 |
| 删除操作 | `toBeHidden()` 被删元素 |
| 取消/关闭 | TODO 验证弹窗关闭 |
| 下一步/上一步 | TODO 验证步骤变化 |
| 用户名 blur | `toBeVisible()` error-message |
| 密码 blur | `toBeVisible()` error-message |
| 手机/验证码 blur | 生成 placeholder 相关错误提示 TODO |
| 表单提交 | `toBeVisible()` success-message |
| `validate` 方法 | `toBeVisible()` error-message |
| `reset` 方法 | `toHaveValue('')` 输入框清空 |
| `toggle` 方法 | TODO 验证切换状态 |
| 链接点击（登录） | `toHaveURL()` 登录页面 |
| 链接点击（忘记密码） | `toHaveURL()` 忘记密码页面 |

## 配置系统

所有运行配置集中在 `tests/python/test_config.toml`：

```toml
[browser]
channel = "chrome"           # 浏览器：chrome/msedge/chromium/firefox
headless = false              # 默认有头模式

[logging]
directory = "logs"            # 日志输出目录
format = "%(asctime)s [%(levelname)s] %(message)s"
level = "INFO"                # 日志级别

[environment]
base_url = "http://localhost:3000"  # POM goto() 自动拼接的基 URL
```

### 配置优先级

环境变量 > 配置文件 > 默认值

```bash
# 配置文件默认值
pytest tests/

# 环境变量覆盖
BASE_URL=http://staging.example.com pytest tests/
```

## POM 结构规范

技能脚本生成标准 POM 类，包含：

1. **独立的 `readonly` Locator 属性** — 每个交互元素对应一个定位器
2. **构造函数初始化** — 所有定位器在 `constructor` 中初始化
3. **`goto()` 方法** — 封装页面导航
4. **操作方法** — click/fill/hover 等，区分有参/无参

详细规范见 [references/pom-baw.md](references/pom-baw.md)。

## BAW 变量命名规范

BAW 代表**业务流程**，变量名应完整表达语义：

| 角色 | 好的命名 ✅ | 差的命名 ❌ |
|------|------------|------------|
| POM 实例 | `self.bing_search_page` | `self.bing_page` |
| BAW 实例 | `self.search_workflow` | `self.bing_baw` |
| BAW 方法参数 | `keyword: str` | `kw: str` |

### Python 示例

```python
# ✅ 语义清晰
self.bing_search_page = BingSearchPage(page)
self.search_workflow = BingSearchBAW(page)
self.search_workflow.execute('AI自动化技术分析')

# ❌ 语义模糊
self.bing_page = BingSearchPage(page)
self.bing_baw = BingSearchBAW(page)
self.bing_baw.execute('AI自动化技术分析')
```

### 命名原则

1. **POM 变量**: `{页面名}_page` — 如 `bing_search_page`、`login_page`
2. **BAW 变量**: `{业务动作}_workflow` / `{业务动作}_flow` — 如 `search_workflow`、`login_workflow`
3. **方法参数**: 全拼写，如 `keyword` 而非 `kw`

## Pinia Store 测试

解析 store 定义，为 state / getters / actions 分别生成测试：

- **类型推断** — 自动推断 state 类型（string/number/boolean/array）
- **状态验证** — 测试默认值和状态变化
- **Getter 测试** — 验证计算值
- **Action 测试** — 验证状态变更

## 中文标识符规范化

中文文本自动转换为英文标识符（50+ 词汇映射）：

| 中文 | 英文 | 中文 | 英文 |
|------|------|------|------|
| 登录 | Login | 验证码 | Code |
| 注册 | Register | 忘记密码 | ForgotPassword |
| 提交 | Submit | 设置 | Settings |
| 搜索 | Search | 弹窗 | Modal |
| 删除 | Delete | 分页 | Pagination |

## 日志系统

### 运行配置（conftest.py）

`--scaffold` 自动生成 `tests/python/conftest.py`，包含：

| 配置 | 说明 |
|------|------|
| `browser_type_launch_args` | 默认使用本地 Chrome 执行 |
| `log_dir` | 每次运行创建 `logs/YYYYMMDD_HHMMSS/` 时间戳目录 |
| `log_config` | 每个测试用例配置文件日志，`self.logger` 自动注入 |

### 运行方式

```bash
# 有头模式（看到浏览器窗口）
pytest tests/python/test_bing_search.py -v --headed

# 无头模式（后台运行）
pytest tests/python/test_bing_search.py -v

# 指定浏览器
pytest tests/python/test_bing_search.py -v --headed --browser-channel=msedge
```

## Snapshot 截图断言

> 首次运行生成基线截图，后续运行自动比对差异，精准捕捉 UI 回归。

### 使用方式

```bash
# 生成时加 --snapshot，测试中自动包含截图断言
python ... --scaffold bing_search --snapshot

# 运行测试（首次：创建基线）
pytest tests/python/test_bing_search.py -v --headed

# 运行测试（后续：自动比对）
pytest tests/python/test_bing_search.py -v --headed
```

### 生成代码示例

```python
# 图片按用例存储：test_cases/__snapshots__/bing_search/bing_search_basic_flow.png
expect(self.page).to_have_screenshot(
    str(Path('__snapshots__') / 'bing_search' / 'bing_search_basic_flow.png')
)
```

### 目录结构

```
tests/python/test_cases/
├── test_bing_search.py
└── __snapshots__/
    └── bing_search/              # 按测试用例分类
        └── bing_search_basic_flow.png    # 基线截图
```

### 适用场景

| 适合 | 不适合 |
|------|--------|
| 布局结构稳定的页面 | 含动态广告/视频的页面 |
| 表单/列表/配置页 | 实时数据仪表盘 |
| CI 回检查 | 频繁改动的页面 |
| 组件库回归 | 第三方嵌入内容 |

### 日志目录结构

```
tests/logs/
└── 20260620_204504/              # 每次 pytest 运行自动创建时间戳目录
    ├── test_login_form.log       # 每个测试用例独立日志文件
    └── test_bing_search.log
```

### 日志实现机制

| 组件 | 获取 Logger | 日志内容 |
|------|------------|----------|
| **conftest.py** | `@pytest.fixture(scope='session')` | 创建 `logs/YYYYMMDD_HHMMSS/` 时间戳目录 |
| **Test** | `logging.root` 通过 `basicConfig` 配置 | 测试起止、断言验证点 `[验证]` |
| **BAW** | `self.logger = logging.getLogger(__name__)` | 执行步骤 `[BAW]   step 1/4: goto` |
| **POM** | `self.logger = logging.getLogger(__name__)` | 关键操作点 `[POM] search: keyword="AI"` |

### 日志内容示例

```
2026-06-20 19:52:58 [INFO] ========== 测试开始 ==========
2026-06-20 19:52:58 [INFO] [BAW] 开始执行: Bing搜索流程
2026-06-20 19:52:58 [INFO] [BAW]   step 1/4: goto Bing首页
2026-06-20 19:52:58 [INFO] [POM] goto: https://www.bing.com
2026-06-20 19:52:58 [INFO] [BAW]   step 3/4: 输入搜索关键词
2026-06-20 19:53:01 [INFO] [BAW] 完成: Bing搜索流程
2026-06-20 19:53:01 [INFO] [验证] 搜索结果数量: 7
2026-06-20 19:53:01 [INFO] ========== 测试结束 ==========
```

### 生成的 conftest.py

使用 `--scaffold` 生成脚手架时，自动创建 `tests/python/conftest.py`：

```python
@pytest.fixture(scope='session', autouse=True)
def log_dir():
    dir_path = Path('logs') / datetime.now().strftime('%Y%m%d_%H%M%S')
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path
```

测试类通过 `def setup(self, page, request, log_dir):` 自动注入。详见 [references/pom-baw.md](references/pom-baw.md)。

## 外部网站手动编写 POM

> 当测试对象是**外部网站**（如 Bing/百度/Google），而非项目内的 Vue/React 组件时，**技能脚本无法自动生成 POM**。需要手动编写 POM 类。

### 手动编写规范

| 语言 | 选择器语法（正确） | 选择器语法（错误 ❌） |
|------|-------------------|-----------------------|
| TypeScript | `page.getByRole('button', { name: '登录' })` | `page.getByRole('button', { name: '登录' }).toBeVisible()` |
| Python | `page.get_by_role('button', name='登录')` | `page.getByRole('button', { name: '登录' })` |
| Java | `page.getByRole(AriaRole.BUTTON, new Page.GetByRoleOptions().setName("登录"))` | `page.getByRole('button', { name: '登录' })` |

### Python 手动 POM 示例

```python
import re
from playwright.sync_api import Page

class BingSearchPage:
    def __init__(self, page: Page):
        self.page = page
        self.search_box = page.get_by_role('combobox', name=re.compile(r'search|搜索', re.IGNORECASE))
        self.search_results = page.locator('#b_results')

    def goto(self):
        self.page.goto('https://www.bing.com')

    def search(self, keyword: str):
        self.search_box.click()
        self.search_box.fill(keyword)
        self.search_box.press('Enter')
```

### 目录结构

```
tests/python/
├── test_bing_search.py           # 测试文件（使用 POM）
└── pages/
    └── bing_search_page.py       # 手动编写的 POM 类
```

### ⚠️ 常见错误

1. **Python 选择器混入 JS 语法**：`page.getByRole('button', { name: '登录' })` → 应使用 `page.get_by_role('button', name='登录')`
2. **缺失 `expect` 导入**：Python 测试文件需要 `from playwright.sync_api import Page, expect`
3. **未封装 POM**：直接在测试文件中写定位器，导致多个测试间重复代码

## 输出结构

```
tests/
├── typescript/
│   ├── login-form.spec.ts
│   ├── pages/login-form.page.ts    # POM
│   └── baw/login.baw.ts            # BAW
├── java/
│   ├── LoginFormTest.java
│   ├── pages/LoginFormPage.java
│   └── baw/LoginBAW.java
└── python/
    ├── test_login_form.py
    ├── pages/login_form_page.py
    └── baw/login_baw.py
```

## 参考文档

使用技能时按需读取：

- **[references/naming.md](references/naming.md)** — 各语言命名规范（方法名、变量名、文件名约定）
- **[references/pom-baw.md](references/pom-baw.md)** — POM/BAW 设计规范、生成触发条件
- **[references/selectors.md](references/selectors.md)** — Playwright 选择器策略和 Golden Rules
- **[references/advanced-features.md](references/advanced-features.md)** — 技能脚本局限性与 `src/` 模块化架构的对比

## 示例文件

本技能配套的前端组件示例位于：

| 框架 | 文件 |
|------|------|
| Vue | `front-end-code/LoginForm.vue` |
| Vue (复杂组件) | `front-end-code/vue/test/ComplexComponent.vue` |
| React | `front-end-code/react/src/components/LoginForm.tsx` |

生成的测试模板：

| 语言 | 测试文件 | POM文件 | BAW文件 |
|------|---------|---------|---------|
| TypeScript | `tests/typescript/{name}.spec.ts` | `tests/typescript/pages/{name}.page.ts` | `tests/typescript/baw/{name}.baw.ts` |
| Java | `tests/java/{Name}Test.java` | `tests/java/pages/{Name}Page.java` | `tests/java/baw/{Name}BAW.java` |
| Python | `tests/python/test_{name}.py` | `tests/python/pages/{name}_page.py` | `tests/python/baw/{name}_baw.py` |

## 常见问题

### Java 测试方法参数错误

生成的 Java 测试中，click/hover 等方法被错误传参：

```java
// ❌ 错误
loginFormPage.clickResetButton(null);
loginFormPage.hoverElement(null);

// ✅ 正确
loginFormPage.clickResetButton();
loginFormPage.hoverElement();
```

**规律**: 只有 `fill` 操作需要参数，其他操作（click/hover/blur/focus/check/dblclick）都不需要参数。

### POM 方法参数规则

| 语言 | fill 操作 | 其他操作 |
|------|-----------|----------|
| TypeScript | `await page.fillUsername('test_value');` | `await page.clickLoginButton();` |
| Java | `page.fillUsername("test_value");` | `page.clickLoginButton();` |
| Python | `page.fill_username('test_value')` | `page.click_login_button()` |

## 相关 Skill

- **playwright-skill** — Playwright 最佳实践指南（选择器、断言、调试等）
- **superpowers** — 软件开发工作流框架

## Playwright 配置文件推荐

```typescript
// playwright.config.ts
export default defineConfig({
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
    testIdAttribute: 'data-testid',
  },
  retries: process.env.CI ? 2 : 0,
});
```

## Playwright Golden Rules

1. `getByRole()` over CSS/XPath
2. Never `page.waitForTimeout()`
3. Web-first assertions (`expect(locator)` 自动重试)
4. Isolate every test
5. `baseURL` in config
6. Retries: 2 in CI, 0 locally
7. Traces: 'on-first-retry'
8. Fixtures over globals
9. One behavior per test
10. Mock external services only

## Playwright 深度指南索引

技能集成了 playwright-skill 的完整知识体系，可通过以下路径访问更深度的指南：

### 测试编写

| 场景 | 指南位置 | 内容概要 |
|------|---------|---------|
| 定位器选择策略 | [references/selectors.md](references/selectors.md) | getByRole/getByLabel/getByText 详解 + 反模式 |
| 断言与等待 | [references/selectors.md](references/selectors.md) | Web-first 断言、软断言、动态等待 |
| 测试结构与 Fixture | `../playwright-skill/core/fixtures-and-hooks.md` | `test.extend()` 优于 `beforeEach` |
| 认证与登录 | `../playwright-skill/core/authentication.md` | storageState 复用、API 登录 |
| 测试组织 | `../playwright-skill/core/test-organization.md` | 按功能分组、文件结构 |
| 配置与项目 | `../playwright-skill/core/configuration.md` | playwright.config.ts 全参数 |
| 网络 Mock | `../playwright-skill/core/network-mocking.md` | API 拦截、Mock |
| 可视化回归 | `../playwright-skill/core/visual-regression.md` | screenshot 对比 |
| 无障碍测试 | `../playwright-skill/core/accessibility.md` | axe-core 集成 |

### 调试与修复

| 问题 | 指南位置 | 内容概要 |
|------|---------|---------|
| 一般调试工作流 | `D:\code\skills\external\playwright-skill\core\debugging.md` | UI Mode / Inspector / Trace Viewer |
| 不稳定测试 | `D:\code\skills\external\playwright-skill\core\flaky-tests.md` | 4 大类根因分析与修复 |
| 常见错误 | `D:\code\skills\external\playwright-skill\core\common-pitfalls.md` | 新手常见陷阱 |
| 错误信息索引 | `D:\code\skills\external\playwright-skill\core\error-index.md` | 已知错误代码排查 |

### CI/CD 与基础设施

| 场景 | 指南位置 |
|------|---------|
| GitHub Actions | `../playwright-skill/ci/ci-github-actions.md` |
| GitLab CI | `../playwright-skill/ci/ci-gitlab.md` |
| Docker | `../playwright-skill/ci/docker-and-containers.md` |
| 并行与分片 | `../playwright-skill/ci/parallel-and-sharding.md` |

### 框架专项

| 框架 | 指南位置 |
|------|---------|
| Vue 3 / Nuxt | `../playwright-skill/core/vue.md` |
| React / CRA / Vite | `../playwright-skill/core/react.md` |
| Next.js | `../playwright-skill/core/nextjs.md` |

### 迁移指南

| 从 | 指南位置 |
|----|---------|
| Cypress | `../playwright-skill/migration/from-cypress.md` |
| Selenium | `../playwright-skill/migration/from-selenium.md` |

### 高级主题

| 主题 | 指南位置 |
|------|---------|
| iframes / Shadow DOM | `../playwright-skill/core/iframes-and-shadow-dom.md` |
| WebSocket / 实时 | `../playwright-skill/core/websockets-and-realtime.md` |
| 多用户协作 | `../playwright-skill/core/multi-user-and-collaboration.md` |
| 文件上传/下载 | `../playwright-skill/core/file-operations.md` |

> **提示**：playwright-skill 已通过 junction 链接到 `.claude/skills/playwright-skill/`，上述指南可按需读取。 |

> **提示**：上述 `D:\code\skills\external\playwright-skill\` 路径下的指南在使用时按需读取即可，不需要全部加载。
