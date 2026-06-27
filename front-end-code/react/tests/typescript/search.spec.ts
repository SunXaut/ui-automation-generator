// AUTO-GENERATED START
import { test, expect } from '@playwright/test';
import { SearchPage } from './pages/search.page';

/**
 * Search 组件测试
 */
test.describe('Search', () => {

  /**
   * ChangesetQuery(e.target.value)}
          placeholder="输入搜索关键词"
          className="search-input"
          data-testid="search-input"
        />
   */
  test('should click setqueryetargetvalueplaceholderinputsearch关键词classnamesearchinputdatatestidsearchinput', async ({ page }) => {
    const searchPage = new SearchPage(page);
    await searchPage.goto();
    await searchPage.clickElement();
    // TODO: 添加断言
  });

  /**
   * Click搜索
   */
  test('should click search', async ({ page }) => {
    const searchPage = new SearchPage(page);
    await searchPage.goto();
    await searchPage.clickElement();
    // TODO: 添加断言
  });

  /**
   * Click清除
   */
  test('should click clear', async ({ page }) => {
    const searchPage = new SearchPage(page);
    await searchPage.goto();
    await searchPage.clickElement();
    // TODO: 添加断言
  });
});

// AUTO-GENERATED END