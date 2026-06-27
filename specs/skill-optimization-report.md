# Skill 优化报告

> 生成时间: 2026-06-20
> 范围: `.claude/skills/uicode-to-automation-test/`

---

## 一、修复的 Bug

### 1.1 Python POM 选择器 JS / Python 语法混用

**问题**: 生成的 `login_form_page.py` 中，`page.getByRole('button', { name: '登录' })` 为 JS 语法，Python 应使用 `page.get_by_role('button', name='登录')`。

**修复**: `_generate_python_pom_file()` 改用 `_convert_selector_to_python()` 转换后再写入。

**对比**:
```python
# ❌ 修复前
self.login_button = page.getByRole('button', { name: '登录' })

# ✅ 修复后
self.login_button = page.get_by_role('button', name='登录')
```

### 1.2 Python 测试缺失 expect 导入

**问题**: 生成的 Python 测试文件缺少 `from playwright.sync_api import Page, expect` 中的 `expect`。

**修复**: `_generate_python_pom_test()` 导入语句增加 `expect`。

### 1.3 Python 输出混入 `// TODO` 注释

**问题**: `_generate_assertions()` 硬编码 `// TODO:` 注释，Python 应使用 `# TODO:`。

**修复**: 断言注释根据 `language` 参数输出 `// TODO` (TypeScript) 或 `# TODO` (Python)。

### 1.4 `getByLabel` 遗留的 JS 语法

**问题**: POM 中 fallback 填充方法使用 `self.page.getByLabel('rememberMe')`（JS 语法）。

**修复**: 改为 `self.page.get_by_label('rememberMe')`（Python 语法）。

---

## 二、新增 CLI 功能

### 2.1 `--scaffold` 外部站点脚手架

为外部网站（如 Bing、百度）生成 POM + BAW + Test 模板，无需 Vue/React 组件。

```bash
python ... --scaffold bing_search --base-url https://www.bing.com -o tests --language python
```

### 2.2 `--snapshot` 截图断言

生成测试中包含 `page.screenshot()` 调用，图片按用例存储到 `__snapshots__/{test_name}/`。

```bash
python ... --scaffold bing_search --base-url https://www.bing.com --snapshot
```

**存储结构**:
```
tests/python/test_cases/__snapshots__/
├── bing_search/bing_search_basic_flow.png
└── login_form/login_form_basic_flow.png
```

### 2.3 `--force` 强制覆盖

scaffold 默认跳过已有文件，`--force` 可强制覆盖。

```bash
# A 测试（无 --force）：跳过已有文件 ✅
# B 测试（有 --force）：强制覆盖 ✅
```

### 2.4 `--all` 批量生成

自动扫描 `front-end-code/` 目录，生成所有 Vue/React 组件 + Router + Store 测试。

```bash
python ... --all -o tests --language python
```

---

## 三、运行环境配置化

### 3.1 `test_config.toml`

集中配置浏览器、日志、环境参数。

| 段 | 配置项 | 默认值 | 说明 |
|------|----------|--------|------|
| `[browser]` | `channel` | `"chrome"` | 浏览器通道 |
| `[browser]` | `headless` | `false` | 无头模式 |
| `[logging]` | `directory` | `"logs"` | 日志输出目录 |
| `[logging]` | `format` | `%(asctime)s [%(levelname)s] %(message)s` | 日志格式 |
| `[logging]` | `level` | `"INFO"` | 日志级别 |
| `[environment]` | `base_url` | `""` | 被测应用基 URL |

### 3.2 `conftest.py`

自动生成的 pytest 全局配置：

```python
# 3 个 fixture，覆盖全部运行配置
@pytest.fixture(scope='session')
def browser_type_launch_args(): ...      # 本地 Chrome 默认

@pytest.fixture(scope='session')
def log_dir(): ...                       # 时间戳日志目录

@pytest.fixture(autouse=True)
def log_config(request, log_dir): ...    # 每个用例独立日志 + self.logger 注入
```

### 3.3 日志系统

```
tests/logs/
└── 20260620_204504/              # 每次 pytest 运行的时间戳目录
    ├── test_bing_search.log       # 每个用例独立日志（BAW + POM + 验证点）
    └── test_login_form.log
```

**对比**:
```python
# ❌ 修复前：每个测试文件重复配置日志（15 行）
def setup(self, page, request, log_dir):
    log_file = ...
    handler = FileHandler(log_file)
    ...

# ✅ 修复后：conftest 统一处理，测试文件 0 行配置
logger: logging.Logger  # 由 conftest 注入
```

---

## 四、选择器生成优化

### 4.1 `getByTestId` 支持

POM 生成器增加了 `getByTestId` 选择器处理。

**对比**:
```python
# ❌ 修复前：getByTestId 选择器被忽略，生成 click_element()
def click_element(self):
    pass

# ✅ 修复后：getByTestId 生成对应定位器和操作方法
self.forgot_link_element = page.get_by_test_id('forgot-link')

def click_forgot_link_element(self):
    self.forgot_link_element.click()
```

### 4.2 `to_snake_case` 处理连字符

data-testid 值中的连字符自动转换为下划线。

```python
# 'forgot-link' + '_element' → (修复前) 'forgot-link_element' (无效 Python)
#                          → (修复后) 'forgot_link_element' (有效 Python)
```

---

## 五、Router 测试生成改进

**对比**:

```python
# ❌ 修复前：sync_playwright() 独立管理浏览器
def test_visit_home_page(self):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto('/')
        assert page.url == '/'
        browser.close()

# ✅ 修复后：Page fixture + Web-first 断言 + 日志
def test_visit_home_page(self):
    self.logger.info('[Router测试] 访问: %s', '/')
    self.page.goto('/')
    expect(self.page).to_have_url('/')
```

---

## 六、智能断言增强

断言场景从 **9 种** 扩展到 **20+ 种**：

| 场景 | 修复前 | 修复后 |
|------|--------|--------|
| 登录 | ✅ | ✅ + signin 匹配 |
| 注册 | ❌ | ✅ |
| 保存 | ❌ | ✅ |
| 取消 / 关闭 | ❌ | ✅ |
| 下一步 / 上一步 | ❌ | ✅ |
| 重置 / 清空 | ❌ | ✅ |
| 手机 / 验证码 blur | ❌ | ✅ |
| check 断言 | ❌ | ✅ |
| 忘记密码链接 | ❌ | ✅ |
| handler toggle | ❌ | ✅ |
| handler handleLogin | ❌ | ✅ |

---

## 七、变量命名规范

### Python (snake_case)

```python
self.bing_search_page = BingSearchPage(page)   # POM 变量
self.bing_search_baw = BingSearchBAW(page)      # BAW 变量
```

### TypeScript (camelCase)

```typescript
const bingSearchPage = new BingSearchPage(page);   // POM 变量
const bingSearchBAW = new BingSearchBAW(page);      // BAW 变量
```

### Java (camelCase)

```java
BingSearchPage bingSearchPage = new BingSearchPage(page);
BingSearchBAW bingSearchBAW = new BingSearchBAW(page);
```

---

## 八、解析器升级

### html.parser 替代正则

| 场景 | 正则 | html.parser |
|------|------|-------------|
| `title="Score: 80 > 60"` | ❌ 被 `>` 截断 | ✅ |
| 多行属性 | ❌ `\n` 截断 | ✅ |
| `v-if="count > 0"` | ❌ 被 `>` 截断 | ✅ |
| 布尔属性 `disabled` | ⚠️ 有值依赖 | ✅ |
| `@click.stop.prevent` 修饰符链 | ⚠️ 部分支持 | ✅ |
| 自闭合 Vue 组件 `<Component />` | ⚠️ | ✅ |

---

## 九、测试验证结果

| 测试 | 收集数 | 说明 |
|------|--------|------|
| Bing 搜索（外部站点） | 1 项 | 真实 URL 导航 + 搜索结果验证 |
| Router 测试（5 条路由） | 5 项 | URL 导航 + Web-first 断言 |
| LoginForm（Vue 组件） | 13 项 | 按钮 / 输入 / 链接 / 双击 |
| **核心链路** | **19 项** | 全部语法通过 |

预存限制（非本次优化引入）:
- Complex Vue 模板（三元运算、方法参数）：3 项解析失败