// AUTO-GENERATED START
import { test, expect } from '@playwright/test';
import { DashboardPage } from './pages/dashboard.page';

/**
 * Dashboard 组件测试
 */
test.describe('Dashboard', () => {

  /**
   * Click增加
   */
  test('should click 增加', async ({ page }) => {
    const dashboardPage = new DashboardPage(page);
    await dashboardPage.goto();
    await dashboardPage.clickElement();
    // TODO: 添加断言
  });

  /**
   * Click减少
   */
  test('should click 减少', async ({ page }) => {
    const dashboardPage = new DashboardPage(page);
    await dashboardPage.goto();
    await dashboardPage.clickElement();
    // TODO: 添加断言
  });

  /**
   * Click重置
   */
  test('should click reset', async ({ page }) => {
    const dashboardPage = new DashboardPage(page);
    await dashboardPage.goto();
    await dashboardPage.clickElement();
    // TODO: 添加断言
  });
});

// AUTO-GENERATED END