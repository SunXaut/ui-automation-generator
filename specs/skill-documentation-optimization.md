# 技能文档优化方案

> 针对 `.claude/skills/uicode-to-automation-test/` 技能的文档优化

## 背景

最近对 `src/` 模块化架构进行了重大优化（NamingService 统一命名、语义信息提取、POM 去重等），但技能文档未同步更新，导致文档与实际行为不一致。

## 优化项

### 1. SKILL.md 更新

#### 1.1 POM 方法命名示例修正

**现状**：文档中的示例与实际生成代码不一致

| 文档示例 | 实际生成 | 问题 |
|---------|---------|------|
| `fill_username` | `input_username_input` | 方法名不匹配 |
| `click_login_button` | `click_login_button` | 一致 |
| `blur_username_input` | `blur_username_input` | 一致 |

**优化方案**：
- 更新 POM 方法命名表，反映 NamingService 的实际行为
- 说明方法命名规则：`{事件类型}_{元素语义名}`
- 示例：`input_username_input`, `blur_username_input`, `click_login_button`

#### 1.2 BAW 方法调用示例修正

**现状**：文档说 BAW 生成注释占位符，实际生成真实方法调用

**优化方案**：
- 删除"注释占位符"的描述
- 更新为实际生成的方法调用示例
- 说明 BAW 通过 NamingService 确保调用与 POM 方法一致

#### 1.3 添加 NamingService 说明

**现状**：文档完全没有提及统一命名服务

**优化方案**：添加新章节：

```markdown
## 统一命名服务（NamingService）

所有生成器共享同一个 NamingService 实例，确保：

1. **命名一致性** — POM 定位器、方法名、测试名、文件名全局唯一
2. **自动去重** — 相同 tag/语义的元素自动追加后缀（如 `input_1`, `input_2`）
3. **事件驱动命名** — 方法名反映事件类型（blur/focus/click），而非主要操作

### 命名优先级

| 类型 | 优先级 | 说明 |
|------|--------|------|
| 定位器名 | data-testid > aria-label > placeholder > text_content > tag | 语义越明确越优先 |
| 方法名 | {事件类型}_{元素语义名} | 如 `blur_username_input` |
| 测试名 | test_{方法名} | 如 `test_blur_username_input` |
| 文件名 | {组件名}_{后缀} | 如 `login_page.py` |
```

#### 1.4 选择器策略说明调整

**现状**：文档说 `data-testid` 优先，但 Playwright Golden Rules 说 `getByRole()` 优先

**优化方案**：明确分层策略

```markdown
## 选择器策略

### 生成时（代码生成器）

优先级：`data-testid` > `aria-label` > `placeholder` > `getByRole` > CSS

- 若 Vue 组件有 `data-testid`，生成 `get_by_test_id()`
- 若有 `aria-label`，生成 `get_by_role()` + name
- 若有 `placeholder`，生成 `get_by_role()` + name
- 否则回退到 CSS 选择器

### 手动编写时（开发者）

遵循 Playwright Golden Rules：`getByRole()` over CSS/XPath

- 优先使用语义化定位器
- 避免依赖 CSS class 或 DOM 结构
```

### 2. references/advanced-features.md 更新

#### 2.1 反映最新模块化架构

**现状**：文档说"技能脚本是单体脚本"，但 `src/` 已经模块化

**优化方案**：

- 更新模块结构图，添加 `naming_service.py`
- 说明 `src/` 的完整能力：语义提取、统一命名、POM 去重
- 更新"何时使用 src/"表格

#### 2.2 添加 NamingService 模块说明

**新增内容**：

```markdown
### 5. 统一命名服务

`src/utils/naming_service.py` 提供跨生成器的统一命名：

- **缓存机制** — 记录已使用的名称，避免重复
- **去重策略** — 自动追加 `_1`, `_2` 后缀
- **多语言支持** — Python(snake_case) / TypeScript(camelCase) / Java(camelCase)
```

### 3. 添加测试验证章节

**现状**：技能文档没有说明如何验证生成质量

**优化方案**：在 SKILL.md 添加新章节：

```markdown
## 测试验证

### 单元测试

```bash
# 运行所有单元测试
python -m pytest tests/test_naming_service.py tests/test_identifier_utils.py -v

# 运行命名服务测试（25 个用例）
python -m pytest tests/test_naming_service.py -v

# 运行标识符工具测试（36 个用例）
python -m pytest tests/test_identifier_utils.py -v
```

### 端到端验证

```bash
# 1. 生成代码
python src/vue_test_generator.py front-end-code/vue/src/views/Login.vue -o tests_py --language python --generate-baw

# 2. 验证语法
python -m py_compile tests_py/python/pages/login_page.py
python -m py_compile tests_py/python/test_login.py
python -m py_compile tests_py/python/baw/login_baw.py

# 3. 检查一致性
# - POM 方法名与 BAW 调用一致
# - 测试导入路径正确
# - 无重复方法定义
```
```

### 4. references/pom-baw.md 更新

#### 4.1 POM 方法生成规则

**新增内容**：

```markdown
## POM 方法生成规则

### 自动生成规则

| 元素类型 | 自动生成方法 | 说明 |
|---------|-------------|------|
| `<input>` (非 checkbox/radio) | `input_{name}(value)` | 自动 fill 方法 |
| `<button>` | `click_{name}()` | 自动 click 方法 |
| 绑定事件 | `{event}_{name}()` | 按事件类型生成 |

### 方法去重

同一元素的同一事件只生成一个方法。例如：
- `@click="submit"` + `@click.prevent="validate"` → 只生成一个 `click_{name}()` 方法
- 通过 NamingService 缓存保证

### 方法签名

| 事件类型 | 参数 | 实现 |
|---------|------|------|
| input / change (input 元素) | `value: str` | `.fill(value)` |
| click / dblclick | 无 | `.click()` / `.dblclick()` |
| blur / focus | 无 | `.blur()` / `.focus()` |
| submit | 无 | `.submit()` |
```

## 实施优先级

| 优先级 | 优化项 | 工作量 | 影响 |
|--------|--------|--------|------|
| P0 | SKILL.md POM 方法命名修正 | 小 | 消除用户困惑 |
| P0 | SKILL.md 添加 NamingService 说明 | 中 | 核心架构文档缺失 |
| P1 | SKILL.md 选择器策略调整 | 小 | 与 Playwright 最佳实践对齐 |
| P1 | references/pom-baw.md 方法生成规则 | 中 | 补充关键规范 |
| P2 | references/advanced-features.md 更新 | 中 | 反映最新架构 |
| P2 | SKILL.md 添加测试验证章节 | 小 | 提升可验证性 |

## 涉及文件

| 文件 | 操作 |
|------|------|
| `.claude/skills/uicode-to-automation-test/SKILL.md` | 修改 |
| `.claude/skills/uicode-to-automation-test/references/pom-baw.md` | 修改 |
| `.claude/skills/uicode-to-automation-test/references/advanced-features.md` | 修改 |
| `.claude/skills/uicode-to-automation-test/references/naming.md` | 修改 |
