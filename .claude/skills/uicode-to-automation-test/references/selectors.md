# 选择器策略与 Playwright 最佳实践

> 整合自 [playwright-skill](D:\code\skills\external\playwright-skill) (v2.2.0) — 50+ 生产验证指南

## 选择器优先级

优先级：`data-testid` > `getByRole` > `getByLabel` > `getByPlaceholder` > CSS

| 元素类型 | 推荐定位器 | 示例 |
|---------|-----------|------|
| 按钮 | `getByRole('button', { name })` | `page.getByRole('button', { name: '登录' })` |
| 链接 | `getByRole('link', { name })` | `page.getByRole('link', { name: '首页' })` |
| 文本输入 | `getByRole('textbox', { name })` | `page.getByRole('textbox', { name: '邮箱' })` |
| 密码输入 | `getByLabel()` | `page.getByLabel('密码')` |
| 复选框 | `getByRole('checkbox', { name })` | `page.getByRole('checkbox', { name: '记住我' })` |
| 下拉框 | `getByRole('combobox', { name })` | `page.getByRole('combobox', { name: '国家' })` |
| 标题 | `getByRole('heading', { name, level })` | `page.getByRole('heading', { name: '仪表盘', level: 1 })` |
| 对话框 | `getByRole('dialog', { name })` | `page.getByRole('dialog', { name: '确认删除' })` |
| 静态文本 | `getByText()` | `page.getByText('没有找到结果')` |
| iframe 内容 | `frameLocator()` | `page.frameLocator('#payment').getByLabel('卡号')` |

### 反模式

| 不要这样做 | 问题 | 正确的做法 |
|-----------|------|-----------|
| `page.locator('.btn-primary')` | CSS class 变更即断裂 | `page.getByRole('button', { name: '保存' })` |
| `page.getByText('提交')` 对按钮 | 不验证元素是否可交互 | `page.getByRole('button', { name: '提交' })` |
| `page.locator('div > span:nth-child(3)')` | DOM 结构调整即断裂 | `page.getByText('期望内容')` |
| `page.locator('#submit-btn')` | ID 是实现细节 | `page.getByRole('button', { name: '提交' })` |

## Playwright Golden Rules

1. **`getByRole()` over CSS/XPath** — 弹性应对标记变化，镜像用户视角
2. **Never `page.waitForTimeout()`** — 使用 `expect(locator).toBeVisible()` 或 `page.waitForURL()`
3. **Web-first assertions** — `expect(locator)` 自动重试；`expect(await locator.textContent())` 不会
4. **Isolate every test** — 无共享状态，无执行顺序依赖
5. **`baseURL` in config** — 测试中零硬编码 URL
6. **Retries: 2 in CI, 0 locally** — 在重要地方暴露不稳定性
7. **Traces: 'on-first-retry'** — 丰富的调试产物，不影响 CI 速度
8. **Fixtures over globals** — 通过 `test.extend()` 共享状态，而非模块级变量
9. **One behavior per test** — 多个相关的 `expect()` 调用是可以的
10. **Mock external services only** — 永远不要 mock 自己的应用；mock 第三方 API、支付网关、邮件

## 断言模式

### Web-First 断言（自动重试）

```typescript
// 可见性
await expect(page.getByRole('heading', { name: 'Products' })).toBeVisible();

// 文本匹配
await expect(page.getByTestId('total')).toHaveText('Total: $99.00');
await expect(page.getByTestId('total')).toContainText('$99');

// 计数
await expect(page.getByRole('listitem')).toHaveCount(5);

// 属性
await expect(page.getByRole('textbox')).toHaveValue('user@test.com');
await expect(page.getByRole('button')).toBeEnabled();

// URL
await expect(page).toHaveURL(/.*dashboard/);
await expect(page).toHaveTitle(/Dashboard/);

// CSS 属性
await expect(page.getByTestId('error')).toHaveCSS('color', 'rgb(220, 38, 38)');

// 取反 — 自动重试直到条件成立
await expect(page.getByRole('dialog')).not.toBeVisible();
await expect(page.getByTestId('spinner')).toBeHidden();

// 软断言 — 收集所有失败，不停止测试
await expect.soft(page.getByRole('heading')).toHaveText('Title');

// 动态等待 — 等待网络响应
const responsePromise = page.waitForResponse('**/api/search*');
await page.getByRole('button', { name: '加载更多' }).click();
await responsePromise;
```

### 解析器断言

```typescript
// 等待加载指示器消失
await expect(page.getByRole('progressbar')).toBeHidden();

// 等待 URL 变化
await page.getByRole('link', { name: '结果' }).click();
await page.waitForURL('**/results/**');

// toPass — 多次断言必须同时通过
await expect(async () => {
  const response = await page.request.get('https://api.example.com/status');
  expect(response.ok()).toBeTruthy();
}).toPass();
```

## Fixture 模式

使用 `test.extend()` 而非 `beforeEach`：

```typescript
// fixtures.ts — 自定义 fixture 确保 setup/teardown
import { test as base } from '@playwright/test';
import { LoginPage } from './pages/login.page';

export const test = base.extend<{ loginPage: LoginPage }>({
  loginPage: async ({ page }, use) => {
    const loginPage = new LoginPage(page);
    await loginPage.goto();   // setup
    await use(loginPage);     // 测试使用
    // teardown 自动运行
  },
});
```

| 机制 | 范围 | 清理保证 | 并行安全 | 用途 |
|------|------|---------|---------|------|
| `test.extend()` fixture | 每测试 | ✅ | ✅ | 大多数 setup/teardown |
| Worker-scoped fixture | 每 worker | ✅ | ✅ | 昂贵资源（DB、auth） |
| Auto fixture | 每测试/worker | ✅ | ✅ | 必须运行的操作 |
| `beforeEach` | 每测试 | ❌ | ✅ | 简单无需清理的操作 |

## 认证模式

### storageState 复用（推荐）

```typescript
// playwright.config.ts
export default defineConfig({
  use: {
    storageState: '.auth/user.json', // 所有测试从已认证状态开始
  },
});

// 生成 auth state 的脚本
// scripts/auth.setup.ts
import { test as setup } from '@playwright/test';
import { LoginPage } from '../pages/login.page';

setup('authenticate', async ({ page }) => {
  const loginPage = new LoginPage(page);
  await loginPage.goto();
  await loginPage.fillUsername('user@test.com');
  await loginPage.fillPassword('s3cure!Pass');
  await loginPage.clickLoginButton();
  await page.waitForURL('/dashboard');
  await page.context().storageState({ path: '.auth/user.json' });
});
```

### API 登录

```typescript
// 跳过 UI 直接通过 API 登录
const context = await browser.newContext();
const response = await context.request.post('/api/auth/login', {
  data: { email: 'user@test.com', password: 's3cure!Pass' },
});
await context.storageState({ path: '.auth/user.json' });
```

## 测试组织

```
tests/
├── auth/
│   ├── login.spec.ts
│   ├── signup.spec.ts
│   └── password-reset.spec.ts
├── dashboard/
│   ├── widgets.spec.ts
│   └── filters.spec.ts
├── checkout/
│   ├── cart.spec.ts
│   ├── payment.spec.ts
│   └── confirmation.spec.ts
├── fixtures/
│   └── auth.fixture.ts
└── pages/                   # POM 文件
    └── login.page.ts
```

## 调试工作流

遵循此顺序，大多数问题在步骤 2 前解决：

```
1. 读取完整错误信息
2. 使用 --ui 模式查看视觉时间线
   └─ npx playwright test --ui
3. 启用 tracing（若未开启）
   └─ use: { trace: 'on' }
4. 在 trace 中检查网络面板
   └─ 缺失响应、4xx/5xx、CORS 错误
5. 在失败点插入 page.pause()
   └─ 实时检查 DOM，在控制台测试选择器
6. 检查浏览器控制台 JS 错误
```

| 工具 | 命令 | 最佳用途 |
|------|------|---------|
| UI Mode | `npx playwright test --ui` | 交互式探索，视觉时间线 |
| Inspector | `PWDEBUG=1 npx playwright test` | 逐步调试，选择器测试 |
| Trace Viewer | `npx playwright show-trace trace.zip` | CI 失败后分析 |
| Headed | `npx playwright test --headed` | 观察浏览器执行 |
| Slow mo | `npx playwright test --headed --slow-mo=500` | 慢速观察交互 |
| Verbose | `DEBUG=pw:api npx playwright test` | 查看每个 API 调用 |

## 稳定性模式

| 类别 | 症状 | 根因 | 诊断方法 |
|------|------|------|---------|
| **时序/异步** | 间歇性失败 | 竞态条件、缺失 await、任意等待 | `--repeat-each=20` 本地复现 |
| **测试隔离** | 仅与其他测试一起运行时失败 | 共享可变状态、数据冲突 | `--workers=1 --grep "此测试"` 通过 |
| **环境** | 仅 CI 失败 | 不同 OS、视口、字体、网络延迟 | 对比 CI 截图/trace |
| **基础设施** | 随机失败 | 浏览器崩溃、OOM、DNS | 错误信息引用浏览器内部 |

```
# 暴露 flaky 测试
npx playwright test tests/checkout.spec.ts --repeat-each=10 --workers=1

# 重试
npx playwright test --retries=3 --trace=on
```

## 配置文件推荐

```typescript
// playwright.config.ts
import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  fullyParallel: true,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 2 : undefined,
  reporter: [['html'], ['list']],
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    testIdAttribute: 'data-testid',
  },
  projects: [
    { name: 'setup', testMatch: /.*\.setup\.ts/ },
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
      dependencies: ['setup'],
    },
  ],
});
```

## 参考

- `D:\code\skills\external\playwright-skill\core\locators.md` — 定位器完整指南
- `D:\code\skills\external\playwright-skill\core\assertions-and-waiting.md` — 断言与等待
- `D:\code\skills\external\playwright-skill\core\fixtures-and-hooks.md` — Fixture 与钩子
- `D:\code\skills\external\playwright-skill\core\authentication.md` — 认证测试
- `D:\code\skills\external\playwright-skill\core\flaky-tests.md` — 不稳定测试排查
- `D:\code\skills\external\playwright-skill\core\debugging.md` — 调试工作流
- `D:\code\skills\external\playwright-skill\core\test-organization.md` — 测试组织
- `D:\code\skills\external\playwright-skill\core\configuration.md` — 配置指南
- `D:\code\skills\external\playwright-skill\ci\ci-github-actions.md` — CI/CD 配置
