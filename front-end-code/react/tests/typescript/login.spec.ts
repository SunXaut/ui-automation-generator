// AUTO-GENERATED START
import { test, expect } from '@playwright/test';
import { LoginPage } from './pages/login.page';

/**
 * Login 组件测试
 */
test.describe('Login', () => {

  /**
   * ClicksetIsSubmitted(false)}>
            返回登录
   */
  test('should click setissubmittedfalsebacklogin', async ({ page }) => {
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.clickSetissubmittedfalsebackloginButton();
    // TODO: 添加断言
  });

  /**
   * Login)}
   */
  test('should click element', async ({ page }) => {
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.clickElement();
    // TODO: 添加断言
  });
});

// AUTO-GENERATED END