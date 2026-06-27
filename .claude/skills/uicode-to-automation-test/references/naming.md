# 命名规范

## TypeScript

| 类型 | 规范 | 示例 |
|------|------|------|
| 文件名 | kebab-case | `login-form.page.ts` |
| 类名 | PascalCase | `LoginFormPage` |
| 方法名 | camelCase | `clickLoginButton()` |
| 变量/属性 | camelCase | `loginButton` |
| 常量 | UPPER_SNAKE_CASE | `MAX_RETRY_COUNT` |
| 测试文件后缀 | .spec.ts | `login-form.spec.ts` |

## Java

| 类型 | 规范 | 示例 |
|------|------|------|
| 文件名 | PascalCase | `LoginFormPage.java` |
| 类名 | PascalCase | `LoginFormPage` |
| 方法名 | camelCase | `clickLoginButton()` |
| 变量/属性 | camelCase | `loginButton` |
| 常量 | UPPER_SNAKE_CASE | `MAX_RETRY_COUNT` |
| 测试文件后缀 | Test.java | `LoginFormTest.java` |

## Python

| 类型 | 规范 | 示例 |
|------|------|------|
| 文件名 | snake_case | `login_form_page.py` |
| 类名 | PascalCase | `LoginFormPage` |
| 方法名 | snake_case | `click_login_button()` |
| 变量/属性 | snake_case | `login_button` |
| 常量 | UPPER_SNAKE_CASE | `MAX_RETRY_COUNT` |
| 测试文件前缀 | test_ | `test_login_form.py` |

## POM 方法命名（跨语言映射）

| 操作 | TypeScript | Java | Python |
|------|-----------|------|--------|
| click | `async clickLoginButton()` | `public void clickLoginButton()` | `def click_login_button(self)` |
| fill | `async fillUsername(value?: string)` | `public void fillUsername(String value)` | `def fill_username(self, value: str = 'test_value')` |
| check | `async checkRememberMe()` | `public void checkRememberMe()` | `def check_remember_me(self)` |
| hover | `async hoverSubmitButton()` | `public void hoverSubmitButton()` | `def hover_submit_button(self)` |
| blur | `async blurUsernameInput()` | `public void blurUsernameInput()` | `def blur_username_input(self)` |
| focus | `async focusPasswordInput()` | `public void focusPasswordInput()` | `def focus_password_input(self)` |

### 关键规则

- **只有 `fill` 操作需要参数**，其他操作（click/hover/blur/focus/check/dblclick）都不需要参数
- fill 操作应提供默认测试值，便于快速测试
