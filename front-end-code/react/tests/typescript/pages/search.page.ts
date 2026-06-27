// AUTO-GENERATED START
import { type Page, type Locator } from '@playwright/test';

/**
 * Search 页面对象模型
 * 封装页面元素定位器和操作方法
 */
export class SearchPage {
  readonly page: Page;

  constructor(page: Page) {
    this.page = page;
  }

  /**
   * 导航到页面
   */
  async goto() {
    await this.page.goto('/search');
  }

  /**
   * 填写query
   */
  async fillQuery(value?: string) {
    await this.page.getByLabel('query').fill(value || 'test_value');
  }

  /**
   * 填写results
   */
  async fillResults(value?: string) {
    await this.page.getByLabel('results').fill(value || 'test_value');
  }
}

// AUTO-GENERATED END