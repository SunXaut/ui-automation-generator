// AUTO-GENERATED START
import { type Page, type Locator } from '@playwright/test';

/**
 * Login 页面对象模型
 * 封装页面元素定位器和操作方法
 */
export class LoginPage {
  readonly page: Page;
  /** setIsSubmitted(false)}>
            返回登录 元素定位器 */
  readonly setissubmittedfalsebackloginButton: Locator;
  /** )} 元素定位器 */
  readonly elementText: Locator;

  constructor(page: Page) {
    this.page = page;
    this.setissubmittedfalsebackloginButton = page.getByRole('button', { name: 'setIsSubmitted(false)}>
            返回登录' });
    this.elementText = page.getByText(')}');
  }

  /**
   * 导航到页面
   */
  async goto() {
    await this.page.goto('/login');
  }

  /**
   * ClicksetIsSubmitted(false)}>
            返回登录
   */
  async clickSetissubmittedfalsebackloginButton() {
    await this.setissubmittedfalsebackloginButton.click();
  }

  /**
   * 填写isSubmitted
   */
  async fillIsSubmitted(value?: string) {
    await this.page.getByLabel('isSubmitted').fill(value || 'test_value');
  }
}

// AUTO-GENERATED END