// AUTO-GENERATED START
import { Page } from '@playwright/test';
import { SearchPage } from '../pages/search.page';

/**
 * 搜索流程
 * 组合POM操作：goto → fillSearchInput → clickSearchButton
 */
export class SearchSearchBAW {
  private searchPage: SearchPage;

  constructor(page: Page) {
    this.searchPage = new SearchPage(page);
  }

  /**
   * 执行搜索流程
   */
  async execute(keyword: string): Promise<void> {
    // 1. goto
    await this.searchPage.goto();
    // 2. fillSearchInput
    await this.searchPage.fillSearchInput(keyword);
    // 3. clickSearchButton
    await this.searchPage.clickSearchButton();
  }
}

// AUTO-GENERATED END