// AUTO-GENERATED START
import { type Page, type Locator } from '@playwright/test';

/**
 * About 页面对象模型
 * 封装页面元素定位器和操作方法
 */
export class AboutPage {
  readonly page: Page;

  constructor(page: Page) {
    this.page = page;
  }

  /**
   * 导航到页面
   */
  async goto() {
    await this.page.goto('/about');
  }
}

// AUTO-GENERATED END