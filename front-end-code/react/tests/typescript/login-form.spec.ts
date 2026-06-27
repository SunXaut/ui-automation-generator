// AUTO-GENERATED START
import { test, expect } from '@playwright/test';
import { LoginFormPage } from './pages/login-form.page';

/**
 * LoginForm 组件测试
 */
test.describe('LoginForm', () => {

  /**
   * Submitform
   */
  test('should click form', async ({ page }) => {
    const loginFormPage = new LoginFormPage(page);
    await loginFormPage.goto();
    await loginFormPage.clickElement();
    // TODO: 添加断言
  });

  /**
   * ChangesetUsername(e.target.value)}
            data-testid="username-input"
          />
   */
  test('should click setusernameetargetvaluedatatestidusernameinput', async ({ page }) => {
    const loginFormPage = new LoginFormPage(page);
    await loginFormPage.goto();
    await loginFormPage.clickUsernameInput();
    // TODO: 添加断言
  });

  /**
   * ChangesetPassword(e.target.value)}
            data-testid="password-input"
          />
   */
  test('should click setpasswordetargetvaluedatatestidpasswordinput', async ({ page }) => {
    const loginFormPage = new LoginFormPage(page);
    await loginFormPage.goto();
    await loginFormPage.clickPasswordInput();
    // TODO: 添加断言
  });

  /**
   * ChangesetRememberMe(e.target.checked)}
            data-testid="remember-checkbox"
          />
   */
  test('should click setremembermeetargetcheckeddatatestidremembercheckbox', async ({ page }) => {
    const loginFormPage = new LoginFormPage(page);
    await loginFormPage.goto();
    await loginFormPage.clickRememberMeInput();
    // TODO: 添加断言
  });

  /**
   * Click重置
   */
  test('should click reset', async ({ page }) => {
    const loginFormPage = new LoginFormPage(page);
    await loginFormPage.goto();
    await loginFormPage.clickElement();
    // TODO: 添加断言
  });
});

// AUTO-GENERATED END