// AUTO-GENERATED START
import { type Page, type Locator } from '@playwright/test';

/**
 * LoginForm 页面对象模型
 * 封装页面元素定位器和操作方法
 */
export class LoginFormPage {
  readonly page: Page;
  /** 用户名 元素定位器 */
  readonly usernameInput: Locator;
  /** 密码 元素定位器 */
  readonly passwordInput: Locator;
  /** 记住我 元素定位器 */
  readonly rememberMeInput: Locator;

  constructor(page: Page) {
    this.page = page;
    this.usernameInput = page.getByLabel('用户名');
    this.passwordInput = page.getByLabel('密码');
    this.rememberMeInput = page.getByLabel('记住我');
  }

  /**
   * 导航到页面
   */
  async goto() {
    await this.page.goto('/loginform');
  }

  /**
   * Change用户名
   */
  async clickUsernameInput() {
    await this.usernameInput.click();
  }

  /**
   * Change密码
   */
  async clickPasswordInput() {
    await this.passwordInput.click();
  }

  /**
   * Change记住我
   */
  async clickRememberMeInput() {
    await this.rememberMeInput.click();
  }

  /**
   * 填写username
   */
  async fillUsername(value?: string) {
    await this.usernameInput.fill(value || 'test_value');
  }

  /**
   * 填写password
   */
  async fillPassword(value?: string) {
    await this.passwordInput.fill(value || 'test_value');
  }

  /**
   * 填写rememberMe
   */
  async fillRememberMe(value?: string) {
    await this.rememberMeInput.fill(value || 'test_value');
  }
}

// AUTO-GENERATED END