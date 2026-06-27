// AUTO-GENERATED START
import { type Page, type Locator } from '@playwright/test';

/**
 * Search 页面对象模型
 * 封装页面元素定位器和操作方法
 */
export class SearchPage {
  readonly page: Page;
  /** 输入搜索关键词 元素定位器 */
  readonly inputsearch关键词Input: Locator;

  constructor(page: Page) {
    this.page = page;
    this.inputsearch关键词Input = page.getByPlaceholder('输入搜索关键词');
  }

  /**
   * 导航到页面
   */
  async goto() {
    await this.page.goto('/search');
  }

  /**
   * 输入输入搜索关键词
   */
  async fillInputsearch关键词input(value?: string) {
    await this.inputsearch关键词Input.fill(value || 'test_value');
  }

  /**
   * 聚焦输入搜索关键词
   */
  async focusInputsearch关键词input() {
    await this.inputsearch关键词Input.focus();
  }

  /**
   * 失焦输入搜索关键词
   */
  async blurInputsearch关键词input() {
    await this.inputsearch关键词Input.blur();
  }

  /**
   * 填写searchQuery
   */
  async fillSearchQuery(value?: string) {
    await this.page.getByLabel('searchQuery').fill(value || 'test_value');
  }
}

// AUTO-GENERATED END