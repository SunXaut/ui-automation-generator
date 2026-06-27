// AUTO-GENERATED START
import { test, expect } from '@playwright/test';
import { HomePage } from './pages/home.page';

/**
 * Home 组件测试
 */
test.describe('Home', () => {

  /**
   * 点击元素
   */
  test('should click element', async ({ page }) => {
    const homePage = new HomePage(page);
    await homePage.goto();
    await homePage.clickElement();
    // TODO: 添加断言
  });
});

// AUTO-GENERATED END