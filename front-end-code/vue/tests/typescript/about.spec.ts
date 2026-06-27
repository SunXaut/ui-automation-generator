// AUTO-GENERATED START
import { test, expect } from '@playwright/test';
import { AboutPage } from './pages/about.page';

/**
 * About 组件测试
 */
test.describe('About', () => {

  /**
   * 点击元素
   */
  test('should click element', async ({ page }) => {
    const aboutPage = new AboutPage(page);
    await aboutPage.goto();
    await aboutPage.clickElement();
    // TODO: 添加断言
  });
});

// AUTO-GENERATED END