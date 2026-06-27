// AUTO-GENERATED START
import { test, expect } from '@playwright/test';
import { SearchPage } from './pages/search.page';

/**
 * Search 组件测试
 */
test.describe('Search', () => {

  /**
   * 输入input
   */
  test('should fill input', async ({ page }) => {
    const searchPage = new SearchPage(page);
    await searchPage.goto();
    await searchPage.fillInputsearch关键词input('test_value');
    // TODO: 添加断言
  });

  /**
   * 聚焦input
   */
  test('should focus input', async ({ page }) => {
    const searchPage = new SearchPage(page);
    await searchPage.goto();
    await searchPage.focusInputsearch关键词input();
    // TODO: 添加断言
  });

  /**
   * 失焦input
   */
  test('should blur input', async ({ page }) => {
    const searchPage = new SearchPage(page);
    await searchPage.goto();
    await searchPage.blurInputsearch关键词input();
    // TODO: 添加断言
  });

  /**
   * 点击元素
   */
  test('should click element', async ({ page }) => {
    const searchPage = new SearchPage(page);
    await searchPage.goto();
    await searchPage.clickElement();
    // TODO: 添加断言
  });

  /**
   * 点击元素
   */
  test('should click element', async ({ page }) => {
    const searchPage = new SearchPage(page);
    await searchPage.goto();
    await searchPage.clickElement();
    // TODO: 添加断言
  });
});

// AUTO-GENERATED END