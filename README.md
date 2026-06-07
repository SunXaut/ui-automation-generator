# Vue to Playwright Test Generator

从Vue组件代码自动生成Playwright场景化UI自动化测试用例，支持Page Object Model模式、BAW模式和多多语言输出。

## 功能特性

- **Vue组件解析**: 解析Vue组件模板，提取事件绑定和用户交互
- **语义选择器**: 遵循Playwright最佳实践，优先使用语义选择器（getByRole, getByLabel等）
- **POM模式**: 自动生成Page Object Model类，封装页面操作
- **BAW模式**: 自动生成Business Action Workflow，封装业务流程
- **多语言支持**: 支持TypeScript、Java、Python三种语言
- **断言生成**: 自动生成Web-first assertions
- **Router测试**: 解析Vue Router配置生成路由测试
- **Pinia测试**: 解析Pinia store生成状态管理测试

## 引用Playwright Skill

本skill直接引用 **playwright-skill** 的最佳实践。在生成测试时，应遵循playwright-skill中的指南和Golden Rules。

### 前置检查

在使用本skill之前，请确保上下文中已安装 **playwright-skill**。如果未安装，请执行以下命令：

```bash
# 安装完整的playwright-skill
npx skills add testdino-hq/playwright-skill

# 或安装单个skill包
npx skills add testdino-hq/playwright-skill/core      # 核心测试指南
npx skills add testdino-hq/playwright-skill/ci        # CI/CD指南
npx skills add testdino-hq/playwright-skill/pom       # POM模式指南
npx skills add testdino-hq/playwright-skill/migration # 迁移指南
```

**GitHub仓库**: <https://github.com/testdino-hq/playwright-skill>

### Golden Rules（来自playwright-skill）

1. **`getByRole()`** **over CSS/XPath** — 弹性应对标记变化，镜像用户视角
2. **Never** **`page.waitForTimeout()`** — 使用 `expect(locator).toBeVisible()` 或 `page.waitForURL()`
3. **Web-first assertions** — `expect(locator)` 自动重试
4. **Isolate every test** — 无共享状态，无执行顺序依赖
5. **`baseURL`** **in config** — 测试中零硬编码URL
6. **Retries:** **`2`** **in CI,** **`0`** **locally** — 在重要地方暴露不稳定性
7. **Traces:** **`'on-first-retry'`** — 丰富的调试产物
8. **Fixtures over globals** — 通过 `test.extend()` 共享状态
9. **One behavior per test** — 多个相关的 `expect()` 调用是可以的
10. **Mock external services only** — 永远不要mock自己的应用

## 使用方法

### 执行流程

当用户请求生成UI自动化测试时，按以下步骤执行：

1. **确定Vue组件路径**: 获取用户指定的Vue组件文件或目录路径
2. **选择编程语言**:
   - 如果用户已指定语言，直接使用
   - 如果用户未指定语言，**必须**使用 `AskUserQuestion` 工具询问用户选择
3. **生成测试脚本**: 根据选择的语言执行对应的生成命令

### 语言选择

本skill支持以下编程语言：

- **1. TypeScript** - 推荐用于Vue/React等前端项目
- **2. Java** - 适用于Java技术栈项目
- **3. Python** - 适用于Python技术栈项目

**重要**: 如果用户没有指定编程语言，必须使用 `AskUserQuestion` 工具询问用户选择支持的语言，格式如下：

```
问题: 请选择生成测试脚本的编程语言
选项:
- 1. TypeScript (推荐用于Vue/React等前端项目)
- 2. Java (适用于Java技术栈项目)
- 3. Python (适用于Python技术栈项目)
```

### 基本用法

```bash
# 生成TypeScript测试（包含POM和BAW）
python vue_test_generator.py <vue_file> -o <output_dir> --language typescript --generate-baw

# 生成Java测试（包含POM和BAW）
python vue_test_generator.py <vue_file> -o <output_dir> --language java --generate-baw

# 生成Python测试（包含POM和BAW）
python vue_test_generator.py <vue_file> -o <output_dir> --language python --generate-baw

# 仅生成POM（不生成BAW）
python vue_test_generator.py <vue_file> -o <output_dir> --language typescript

# 不生成POM和BAW
python vue_test_generator.py <vue_file> -o <output_dir> --no-pom
```

### 解析Router

```bash
python src/vue_test_generator.py src/router/index.ts --router -o tests
```

### 解析Pinia Store

```bash
python src/vue_test_generator.py src/stores/user.ts --store -o tests
```

### 批量处理目录

```bash
python src/vue_test_generator.py src/components/ -o tests --generate-baw
```

## 输出结构

```
tests/
├── typescript/
│   ├── login-form.spec.ts         # TypeScript测试文件
│   ├── pages/
│   │   └── login-form.page.ts     # TypeScript POM文件
│   └── baw/
│       └── login.baw.ts          # TypeScript BAW文件
├── java/
│   ├── LoginFormTest.java         # Java测试文件
│   └── pages/
│       └── LoginFormPage.java     # Java POM文件
│   └── baw/
│       └── LoginBAW.java         # Java BAW文件
└── python/
    ├── test_login_form.py         # Python测试文件
    └── pages/
        └── login_form_page.py     # Python POM文件
    └── baw/
        └── login_baw.py          # Python BAW文件
```

## 示例文件

本skill包含完整的示例文件：

### Vue组件示例

- [examples/LoginForm.vue](examples/LoginForm.vue) - 包含多种事件类型的登录表单组件

### 生成的测试示例

#### TypeScript

- [tests/typescript/login-form.spec.ts](tests/typescript/login-form.spec.ts) - TypeScript测试文件
- [tests/typescript/pages/login-form.page.ts](tests/typescript/pages/login-form.page.ts) - TypeScript POM文件

#### Java

- [tests/java/LoginFormTest.java](tests/java/LoginFormTest.java) - Java测试文件
- [tests/java/pages/LoginFormPage.java](tests/java/pages/LoginFormPage.java) - Java POM文件

#### Python

- [tests/python/test\_login\_form.py](tests/python/test_login_form.py) - Python测试文件
- [tests/python/pages/loginform\_page.py](tests/python/pages/loginform_page.py) - Python POM文件

### TypeScript POM

```typescript
import { type Page, type Locator } from '@playwright/test';

/**
 * LoginForm 页面对象模型
 * 封装页面元素定位器和操作方法
 */
export class LoginFormPage {
  readonly page: Page;
  /** 登录 元素定位器 */
  readonly loginButton: Locator;
  /** 用户名 元素定位器 */
  readonly usernameInput: Locator;

  constructor(page: Page) {
    this.page = page;
    this.loginButton = page.getByRole('button', { name: '登录' });
    this.usernameInput = page.getByLabel('用户名');
  }

  /**
   * 导航到页面
   */
  async goto() {
    await this.page.goto('/loginform');
  }

  /**
   * 点击登录
   */
  async clickLoginButton() {
    await this.loginButton.click();
  }
}
```

### TypeScript Test

```typescript
import { test, expect } from '@playwright/test';
import { LoginFormPage } from './pages/loginform.page';

/**
 * LoginForm 组件测试
 */
test.describe('LoginForm', () => {
  /**
   * 点击登录
   */
  test('should click login', async ({ page }) => {
    const loginFormPage = new LoginFormPage(page);
    await loginFormPage.goto();
    await loginFormPage.clickLoginButton();
    // TODO: 添加断言
  });
});
```

## 命名规范

生成的测试脚本必须遵循各语言的命名规范：

### TypeScript 命名规范

| 类型     | 规范                 | 示例                                         |
| ------ | ------------------ | ------------------------------------------ |
| 文件名    | kebab-case         | `login-form.page.ts`, `login-form.spec.ts` |
| 类名     | PascalCase         | `LoginFormPage`                            |
| 方法名    | camelCase          | `clickLoginButton()`, `goto()`             |
| 变量/属性  | camelCase          | `loginButton`, `usernameInput`             |
| 常量     | UPPER\_SNAKE\_CASE | `MAX_RETRY_COUNT`                          |
| 测试文件后缀 | .spec.ts           | `login-form.spec.ts`                       |

### Java 命名规范

| 类型     | 规范                 | 示例                                         |
| ------ | ------------------ | ------------------------------------------ |
| 文件名    | PascalCase         | `LoginFormPage.java`, `LoginFormTest.java` |
| 类名     | PascalCase         | `LoginFormPage`                            |
| 方法名    | camelCase          | `clickLoginButton()`, `gotoPage()`         |
| 变量/属性  | camelCase          | `loginButton`, `usernameInput`             |
| 常量     | UPPER\_SNAKE\_CASE | `MAX_RETRY_COUNT`                          |
| 测试文件后缀 | Test.java          | `LoginFormTest.java`                       |

### Python 命名规范

| 类型     | 规范                 | 示例                                         |
| ------ | ------------------ | ------------------------------------------ |
| 文件名    | snake\_case        | `login_form_page.py`, `test_login_form.py` |
| 类名     | PascalCase         | `LoginFormPage`                            |
| 方法名    | snake\_case        | `click_login_button()`, `goto()`           |
| 变量/属性  | snake\_case        | `login_button`, `username_input`           |
| 常量     | UPPER\_SNAKE\_CASE | `MAX_RETRY_COUNT`                          |
| 测试文件前缀 | test\_             | `test_login_form.py`                       |

## POM方法设计规范

Page Object Model类中的方法应根据操作类型设计参数：

### 无参数方法

以下操作不需要参数，方法签名应简洁：

| 操作类型  | TypeScript                   | Java                               | Python                            |
| ----- | ---------------------------- | ---------------------------------- | --------------------------------- |
| click | `async clickLoginButton()`   | `public void clickLoginButton()`   | `def click_login_button(self):`   |
| check | `async checkRememberMe()`    | `public void checkRememberMe()`    | `def check_remember_me(self):`    |
| hover | `async hoverSubmitButton()`  | `public void hoverSubmitButton()`  | `def hover_submit_button(self):`  |
| blur  | `async blurUsernameInput()`  | `public void blurUsernameInput()`  | `def blur_username_input(self):`  |
| focus | `async focusPasswordInput()` | `public void focusPasswordInput()` | `def focus_password_input(self):` |

### 有参数方法

只有需要输入值的操作才需要参数：

| 操作类型 | TypeScript                           | Java                                     | Python                                                |
| ---- | ------------------------------------ | ---------------------------------------- | ----------------------------------------------------- |
| fill | `async fillUsername(value?: string)` | `public void fillUsername(String value)` | `def fill_username(self, value: str = 'test_value'):` |

### 设计原则

1. **最小参数原则**: 只有真正需要数据的操作（如fill）才接受参数
2. **默认值设计**: fill操作应提供默认值，便于快速测试
3. **语义清晰**: 方法名应清晰表达操作意图，无需通过参数来区分
4. **类型安全**: 参数类型应明确，避免使用无意义的通用参数

### 示例对比

❌ **不推荐**（所有方法都带无意义参数）:

```java
public void clickLoginButton(String value) {
    this.loginButton.click();
}
```

✅ **推荐**（根据操作类型决定参数）:

```java
// 点击操作不需要参数
public void clickLoginButton() {
    this.loginButton.click();
}

// 只有fill操作需要参数
public void fillUsername(String value) {
    this.usernameInput.fill(value);
}
```

## BAW（Business Action Workflow）设计规范

### 什么是BAW？

BAW（Business Action Workflow，业务操作流程）是一种将多个POM操作组合成单一可复用业务动作的设计模式。

### BAW vs POM

| 特性 | POM（Page Object Model） | BAW（Business Action Workflow） |
| -- | ---------------------- | ----------------------------- |
| 粒度 | 页面级别的元素和单步操作           | 业务流程级别的多步操作                   |
| 职责 | 封装页面元素定位器              | 组合POM操作形成业务流                  |
| 方法 | click、fill、hover等原子操作  | login、submitForm、search等业务操作  |
| 断言 | 可包含简单状态断言              | **禁止包含任何断言**                  |
| 依赖 | 无依赖                    | 依赖POM对象                       |

### BAW设计原则

1. **纯POM组合**: BAW内部只能调用POM对象的方法，不能直接操作页面元素
2. **无断言**: BAW只负责执行流程，不验证结果
3. **单一职责**: 每个BAW对应一个完整的业务动作
4. **参数最小化**: 只传递业务必需的参数

### BAW设计示例

#### TypeScript BAW

```typescript
import { Page } from '@playwright/test';
import { LoginFormPage } from '../pages/login-form.page';

/**
 * 登录业务操作流程
 * 组合POM操作：打开页面 → 输入用户名 → 输入密码 → 点击登录
 */
export class LoginBAW {
  private loginPage: LoginFormPage;

  constructor(page: Page) {
    this.loginPage = new LoginFormPage(page);
  }

  /**
   * 执行登录流程
   * @param username 用户名
   * @param password 密码
   */
  async execute(username: string, password: string): Promise<void> {
    // 1. 打开登录页面
    await this.loginPage.goto();

    // 2. 输入用户名
    await this.loginPage.fillUsername(username);

    // 3. 输入密码
    await this.loginPage.fillPassword(password);

    // 4. 点击登录按钮
    await this.loginPage.clickLoginButton();
  }
}
```

#### Python BAW

```python
from playwright.sync_api import Page
from pages.login_form_page import LoginFormPage

class LoginBAW:
    """登录业务操作流程"""

    def __init__(self, page: Page):
        self.login_page = LoginFormPage(page)

    def execute(self, username: str, password: str):
        """
        执行登录流程

        Args:
            username: 用户名
            password: 密码
        """
        # 1. 打开登录页面
        self.login_page.goto()

        # 2. 输入用户名
        self.login_page.fill_username(username)

        # 3. 输入密码
        self.login_page.fill_password(password)

        # 4. 点击登录按钮
        self.login_page.click_login_button()
```

#### Java BAW

```java
import com.microsoft.playwright.Page;
import pages.LoginFormPage;

public class LoginBAW {
    private final LoginFormPage loginPage;

    public LoginBAW(Page page) {
        this.loginPage = new LoginFormPage(page);
    }

    public void execute(String username, String password) {
        // 1. 打开登录页面
        loginPage.goto();

        // 2. 输入用户名
        loginPage.fillUsername(username);

        // 3. 输入密码
        loginPage.fillPassword(password);

        // 4. 点击登录按钮
        loginPage.clickLoginButton();
    }
}
```

### 测试用例中使用BAW

#### TypeScript 测试

```typescript
import { test, expect } from '@playwright/test';
import { LoginBAW } from './baw/login.baw';

test.describe('登录功能', () => {
  test('使用有效凭据登录成功', async ({ page }) => {
    const loginBAW = new LoginBAW(page);

    // 执行登录流程
    await loginBAW.execute('testuser', 'password123');

    // 验证登录结果（在测试层，不在BAW层）
    await expect(page).toHaveURL('/dashboard');
    await expect(page.getByText('欢迎回来')).toBeVisible();
  });
});
```

#### Python 测试

```python
import pytest
from playwright.sync_api import Page, expect
from baw.login_baw import LoginBAW

class TestLogin:
    def test_login_with_valid_credentials(self, page: Page):
        login_baw = LoginBAW(page)

        # 执行登录流程
        login_baw.execute('testuser', 'password123')

        # 验证登录结果（在测试层，不在BAW层）
        expect(page).to_have_url('/dashboard')
        page.get_by_text('欢迎回来').is_visible()
```

### 常用BAW示例

| BAW名称         | 描述   | 组成步骤                        |
| ------------- | ---- | --------------------------- |
| LoginBAW      | 登录流程 | 打开登录页 → 输入用户名 → 输入密码 → 点击登录 |
| LogoutBAW     | 登出流程 | 点击用户菜单 → 点击登出               |
| SearchBAW     | 搜索流程 | 打开搜索页 → 输入关键词 → 点击搜索        |
| SubmitFormBAW | 提交流程 | 填写表单 → 点击提交                 |
| FilterBAW     | 筛选流程 | 打开列表页 → 选择筛选条件 → 应用筛选       |

### 生成BAW的触发条件

在生成测试时，如果检测到以下业务场景，应自动生成对应的BAW：

1. **登录/注册流程**: 当存在用户名+密码+登录/注册按钮的组合
2. **搜索流程**: 当存在搜索框+搜索按钮的组合
3. **表单提交流程**: 当存在多个输入字段+提交按钮的组合
4. **复合操作流程**: 当同一页面存在3个以上可交互元素时

## 配置文件

### playwright.config.ts

项目根目录下的 `playwright.config.ts` 是 Playwright 测试的核心配置文件，定义了测试运行的所有全局设置。

#### 配置文件位置

```
d:\code\python_project\面试\booster\playwright.config.ts
```

#### 主要配置项说明

| 配置项 | 说明 | 当前值 |
|--------|------|--------|
| `testDir` | 测试文件目录 | `./tests` |
| `testMatch` | 测试文件匹配模式 | `['**/*.spec.ts', '**/test_*.py']` |
| `fullyParallel` | 并行运行测试 | `true` |
| `retries` | 失败重试次数 | CI: 2, 本地: 0 |
| `workers` | 并行工作进程数 | CI: 1, 本地: 自动 |
| `baseURL` | 基础URL | `https://www.baidu.com` |
| `trace` | 追踪配置 | `'on-first-retry'` |
| `screenshot` | 截图配置 | `'only-on-failure'` |
| `video` | 视频配置 | `'on-first-retry'` |

#### 浏览器项目配置

配置文件支持多浏览器测试：

- **chromium**: Desktop Chrome
- **firefox**: Desktop Firefox
- **webkit**: Desktop Safari
- **Mobile Chrome**: Pixel 5
- **Mobile Safari**: iPhone 12

#### 如何使用配置文件

**运行所有测试**：

```bash
npx playwright test
```

**运行特定浏览器的测试**：

```bash
npx playwright test --project=chromium
```

**运行特定测试文件**：

```bash
npx playwright test tests/baidu-search.spec.ts
```

**运行特定目录的测试**：

```bash
npx playwright test tests/typescript/
```

**生成 HTML 报告**：

```bash
npx playwright test
npx playwright show-report
```

**修改 baseURL**：

编辑 `playwright.config.ts` 中的 `baseURL` 配置：

```typescript
use: {
  baseURL: 'http://localhost:3000', // 修改为你的应用地址
}
```

#### 配置建议

1. **本地开发**：保持 `retries: 0`，快速暴露问题
2. **CI 环境**：设置 `retries: 2`，避免偶发失败
3. **调试模式**：设置 `launchOptions.slowMo = 1000`，便于观察
4. **生产环境**：关闭 `slowMo`，提高执行速度

生成的测试遵循以下配置建议：

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

## 最佳实践建议

在生成测试时，应遵循playwright-skill中的最佳实践：

1. **选择器策略**: 优先使用语义选择器（getByRole, getByLabel, getByPlaceholder等）
2. **断言模式**: 使用Web-first assertions，自动重试
3. **POM模式**: 封装页面操作，提高测试可维护性
4. **BAW模式**: 封装业务流程，提高测试可读性
5. **Vue测试**: 针对Vue组件特性生成测试
6. **调试技巧**: 使用trace和截图进行调试

## 相关Skill

- **playwright-skill**: Playwright最佳实践指南
- **superpowers**: 软件开发工作流框架

## 文件位置

### Skill文件

- SKILL.md: 本文件
- vue\_test\_generator.py: 测试生成器脚本
- examples/: 示例Vue组件
- tests/: 生成的测试示例

