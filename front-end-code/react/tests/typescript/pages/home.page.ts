// AUTO-GENERATED START
import { type Page, type Locator } from '@playwright/test';

/**
 * Home 页面对象模型
 * 封装页面元素定位器和操作方法
 */
export class HomePage {
  readonly page: Page;

  constructor(page: Page) {
    this.page = page;
  }

  /**
   * 导航到页面
   */
  async goto() {
    await this.page.goto('/home');
  }

  /**
   * 填写message
   */
  async fillMessage(value?: string) {
    await this.page.getByLabel('message').fill(value || 'test_value');
  }
}

// AUTO-GENERATED END