// AUTO-GENERATED START
import { Page } from '@playwright/test';
import { LoginFormPage } from '../pages/login-form.page';

/**
 * 登录流程
 * 组合POM操作：goto → fillUsername → fillPassword → clickLoginButton
 */
export class LoginFormLoginBAW {
  private loginFormPage: LoginFormPage;

  constructor(page: Page) {
    this.loginFormPage = new LoginFormPage(page);
  }

  /**
   * 执行登录流程
   */
  async execute(username: string, password: string): Promise<void> {
    // 1. goto
    await this.loginFormPage.goto();
    // 2. fillUsername
    await this.loginFormPage.fillUsername(username);
    // 3. fillPassword
    await this.loginFormPage.fillPassword(password);
    // 4. clickLoginButton
    await this.loginFormPage.clickLoginButton();
  }
}

// AUTO-GENERATED END