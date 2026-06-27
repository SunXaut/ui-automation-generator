// AUTO-GENERATED START
import { test, expect } from '@playwright/test';
import { HomePage } from './pages/home.page';

/**
 * Home 组件测试
 */
test.describe('Home', () => {

  /**
   * Click显示提示
   */
  test('should click 显示tooltip', async ({ page }) => {
    const homePage = new HomePage(page);
    await homePage.goto();
    await homePage.clickElement();
    // TODO: 添加断言
  });

  /**
   * Click更新消息
   */
  test('should click update消息', async ({ page }) => {
    const homePage = new HomePage(page);
    await homePage.goto();
    await homePage.clickElement();
    // TODO: 添加断言
  });
});

// AUTO-GENERATED END