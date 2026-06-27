// AUTO-GENERATED START
import { type Page, type Locator } from '@playwright/test';

/**
 * Login 页面对象模型
 * 封装页面元素定位器和操作方法
 */
export class LoginPage {
  readonly page: Page;

  constructor(page: Page) {
    this.page = page;
  }

  /**
   * 导航到页面
   */
  async goto() {
    await this.page.goto('/login');
  }

  /**
   * 填写formData.username
   */
  async fillformdata.username(value?: string) {
    await this.page.getByLabel('formData.username').fill(value || 'test_value');
  }

  /**
   * 填写formData.password
   */
  async fillformdata.password(value?: string) {
    await this.page.getByLabel('formData.password').fill(value || 'test_value');
  }

  /**
   * 填写formData.rememberMe
   */
  async fillformdata.rememberme(value?: string) {
    await this.page.getByLabel('formData.rememberMe').fill(value || 'test_value');
  }
}

// AUTO-GENERATED END