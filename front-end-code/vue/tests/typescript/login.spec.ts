// AUTO-GENERATED START
import { test, expect } from '@playwright/test';
import { LoginPage } from './pages/login.page';

/**
 * Login 组件测试
 */
test.describe('Login', () => {

  /**
   * 点击忘记密码？
   */
  test('should click forgotPassword', async ({ page }) => {
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.clickElement();
    // TODO: 添加断言
  });

  /**
   * 提交form
   */
  test('should click form', async ({ page }) => {
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.clickElement();
    // TODO: 添加断言
  });

  /**
   * 失焦input
   */
  test('should blur input', async ({ page }) => {
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.blurElement();
    // TODO: 添加断言
  });

  /**
   * 聚焦input
   */
  test('should focus input', async ({ page }) => {
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.focusElement();
    // TODO: 添加断言
  });

  /**
   * 失焦input
   */
  test('should blur input', async ({ page }) => {
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.blurElement();
    // TODO: 添加断言
  });

  /**
   * 选择input
   */
  test('should check input', async ({ page }) => {
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.checkElement();
    // TODO: 添加断言
  });

  /**
   * 点击元素
   */
  test('should click element', async ({ page }) => {
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.clickElement();
    // TODO: 添加断言
  });

  /**
   * 点击a
   */
  test('should click a', async ({ page }) => {
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.clickElement();
    // TODO: 添加断言
  });

  /**
   * 点击button
   */
  test('should click button', async ({ page }) => {
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.clickElement();
    // TODO: 添加断言
  });

  /**
   * 双击button
   */
  test('should dblclick button', async ({ page }) => {
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.dblclickElement();
    // TODO: 添加断言
  });
});

// AUTO-GENERATED END