import { defineConfig, devices } from '@playwright/test';

/**
 * Playwright 配置文件
 * @see https://playwright.dev/docs/test-configuration
 */
export default defineConfig({
  testDir: './tests',

  /* 测试文件匹配模式 */
  testMatch: ['**/*.spec.ts', '**/test_*.py'],

  /* 并行运行测试 */
  fullyParallel: true,

  /* 失败时禁止并行 */
  forbidOnly: !!process.env.CI,

  /* 重试配置：CI环境重试2次，本地不重试 */
  retries: process.env.CI ? 2 : 0,

  /* 工作者数量 */
  workers: process.env.CI ? 1 : undefined,

  /* 报告器配置 */
  reporter: [
    ['html', { outputFolder: 'playwright-report' }],
    ['list']
  ],

  /* 共享配置 */
  use: {
    /* 基础URL - 支持环境变量覆盖 */
    baseURL: process.env.BASE_URL || 'https://www.baidu.com',

    /* 追踪配置：首次失败时记录 */
    trace: 'on-first-retry',

    /* 截图配置：失败时自动截图 */
    screenshot: 'only-on-failure',

    /* 视频配置：失败时记录 */
    video: 'on-first-retry',

    /* 视口大小 */
    viewport: { width: 1280, height: 720 },

    /* 浏览器启动选项 - 仅调试时启用 slowMo */
    launchOptions: {
      slowMo: process.env.DEBUG ? 1000 : 0,
    },
  },

  /* 项目配置 */
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
    /* 测试移动设备 */
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
    },
    {
      name: 'Mobile Safari',
      use: { ...devices['iPhone 12'] },
    },
  ],

  /* 本地开发服务器配置（如需要） */
  // webServer: {
  //   command: 'npm run start',
  //   url: 'http://127.0.0.1:3000',
  //   reuseExistingServer: !process.env.CI,
  // },
});
