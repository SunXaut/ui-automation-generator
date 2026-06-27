// AUTO-GENERATED START
import { Page } from '@playwright/test';
import { LoginPage } from '../pages/login.page';

/**
 * 登录流程
 * 组合POM操作：goto → fillUsername → fillPassword → clickLoginButton
 */
export class LoginLoginBAW {
  private loginPage: LoginPage;

  constructor(page: Page) {
    this.loginPage = new LoginPage(page);
  }

  /**
   * 执行登录流程
   */
  async execute(username: string, password: string): Promise<void> {
    // 1. goto
    await this.loginPage.goto();
    // 2. fillUsername
    await this.loginPage.fillUsername(username);
    // 3. fillPassword
    await this.loginPage.fillPassword(password);
    // 4. clickLoginButton
    await this.loginPage.clickLoginButton();
  }
}

// AUTO-GENERATED END