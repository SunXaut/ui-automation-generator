// AUTO-GENERATED START
import { test, expect } from '@playwright/test';
import { AboutPage } from './pages/about.page';

/**
 * About 组件测试
 */
test.describe('About', () => {

  /**
   * Click{showDetails ? '隐藏' : '显示'}详情
   */
  test('should click showdetails隐藏显示detail', async ({ page }) => {
    const aboutPage = new AboutPage(page);
    await aboutPage.goto();
    await aboutPage.clickElement();
    // TODO: 添加断言
  });
});

// AUTO-GENERATED END