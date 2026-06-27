# Python 输出修复方案

## 问题清单

### P0 - 严重影响可用性

| 问题 | 描述 | 影响 |
|------|------|------|
| **P0-1: POM 定位器/方法名重复** | 3个 input 元素都生成 `input_input`，2个登录按钮都生成 `login_button` | 生成的代码无法运行 |
| **P0-2: import 路径错误** | `from pages.login` 应为 `from pages.login_page` | 导入失败 |
| **P0-3: BAW 调用错误方法** | 用户名/密码输入调用了 `blur_input` 而非 `fill_input` | 逻辑错误 |

### P1 - 影响代码质量

| 问题 | 描述 | 影响 |
|------|------|------|
| **P1-1: 非法 Playwright API** | 生成 `.click.prevent()` / `.submit.prevent()` | 运行时错误 |
| **P1-2: BAW 类型注解错误** | 使用 `string` 而非 Python 的 `str` | 类型检查失败 |

### P2 - 代码规范问题

| 问题 | 描述 | 影响 |
|------|------|------|
| **P2-1: 方法名含中文** | `click_重置`、`test_click_忘记密码？` | 不符合 Python 命名规范 |
| **P2-2: 方法签名冗余** | 所有方法都有无用的 `value: str = 'test_value'` 参数 | 代码冗余 |
| **P2-3: 测试方法名重复** | `test_blur_input` 出现两次 | 测试冲突 |

---

## 修复方案

### P0-1: 定位器/方法名去重

**问题根源**：`_generate_locator_name()` 使用 `text + tag` 组合，当多个元素 tag 相同且 text 为空时，名称重复。

**修复方案**：
- 在生成器中维护已使用的名称计数器
- 重复名称自动添加数字后缀

```python
# pom_generator.py

class PythonPOMGenerator:
    def __init__(self):
        self.selector_generator = SelectorGenerator()
        self._name_counter = {}  # 新增：名称计数器

    def _generate_locator_name(self, element: VueElement) -> str:
        """生成定位器属性名（带去重）"""
        text = element.text_content or element.attributes.get('aria-label', element.tag)
        base_name = f"{to_snake_case(text)}_{element.tag}"

        # 去重处理
        if base_name in self._name_counter:
            self._name_counter[base_name] += 1
            return f"{base_name}_{self._name_counter[base_name]}"
        else:
            self._name_counter[base_name] = 0
            return base_name

    def generate(self, component: VueComponent) -> str:
        """生成 Python POM 文件"""
        self._name_counter = {}  # 重置计数器
        # ... 其余代码
```

### P0-2: 修复 import 路径

**问题根源**：`py_generator.py` 中 `page_file` 使用组件名转换，但实际文件名是 `{component_name}_page.py`。

**修复方案**：
```python
# py_generator.py

def generate_test(self, component: VueComponent) -> str:
    """生成完整的测试文件"""
    page_file = self._to_snake_case(component.name) + "_page"  # 添加 _page 后缀
    lines = [
        "import pytest",
        "from playwright.sync_api import Page, expect",
        f"from pages.{page_file} import {component.name}Page",
        # ...
    ]
```

### P0-3: BAW 调用正确方法

**问题根源**：`_get_method_name()` 使用元素的第一个事件，但 input 元素的第一个事件可能是 `blur` 而非 `input`。

**修复方案**：
- 根据元素类型和上下文智能选择方法
- input 元素优先使用 `fill` 方法

```python
# baw_generator.py

def _generate_step_calls(self, component: VueComponent, flow: BusinessFlow, page_var: str, lang: str) -> List[Dict[str, str]]:
    """根据流程步骤生成实际的 POM 方法调用"""
    calls = []
    flow_name = flow.name.lower()

    if flow_name == "login":
        username_elem = None
        password_elem = None
        submit_elem = None
        for elem in component.elements:
            if elem.tag == 'input':
                placeholder = elem.attributes.get('placeholder', '').lower()
                if '用户名' in placeholder or 'username' in placeholder:
                    username_elem = elem
                if '密码' in placeholder or 'password' in placeholder:
                    password_elem = elem
            if elem.tag == 'button' and elem.text_content == '登录':
                submit_elem = elem

        calls.append({"comment": "打开登录页面", "code": f"self.{page_var}.goto()"})
        if username_elem:
            # 使用 fill 而非 blur
            calls.append({"comment": "输入用户名", "code": f"self.{page_var}.fill_{self._get_element_name(username_elem)}(username)"})
        if password_elem:
            calls.append({"comment": "输入密码", "code": f"self.{page_var}.fill_{self._get_element_name(password_elem)}(password)"})
        if submit_elem:
            calls.append({"comment": "点击登录按钮", "code": f"self.{page_var}.click_{self._get_element_name(submit_elem)}()"})

    return calls

def _get_element_name(self, element: VueElement) -> str:
    """获取元素的描述性名称"""
    # 优先使用 aria-label
    if element.attributes.get('aria-label'):
        return to_snake_case(element.attributes['aria-label'])
    # 其次使用 placeholder
    if element.attributes.get('placeholder'):
        return to_snake_case(element.attributes['placeholder'])
    # 最后使用 text_content 或 tag
    return to_snake_case(element.text_content or element.tag)
```

### P1-1: 修复非法 Playwright API

**问题根源**：事件名包含修饰符（如 `click.prevent`），直接拼接导致生成 `.click.prevent()`。

**修复方案**：
- 在生成方法调用前，先提取基础事件名
- 使用 `get_action()` 获取正确的 API 调用

```python
# pom_generator.py

def _generate_methods(self, element: VueElement) -> List[str]:
    """生成操作方法"""
    lines = []
    locator_name = self._generate_locator_name(element)

    for event_name in element.events:
        method_name = self._generate_method_name(element, event_name)
        base_event = event_name.split('.')[0]  # 提取基础事件

        lines.append("")
        lines.append(f"    def {method_name}(self):")
        lines.append('        """')
        lines.append(f"        {element.text_content or element.tag}")
        lines.append('        """')

        if base_event in ['input', 'change'] and element.tag == 'input':
            lines.append(f"        self.{locator_name}.fill('test_value')")
        elif base_event == 'click':
            lines.append(f"        self.{locator_name}.click()")
        elif base_event == 'dblclick':
            lines.append(f"        self.{locator_name}.dblclick()")
        elif base_event == 'blur':
            lines.append(f"        self.{locator_name}.blur()")
        elif base_event == 'focus':
            lines.append(f"        self.{locator_name}.focus()")
        else:
            lines.append(f"        self.{locator_name}.{base_event}()")

    return lines
```

### P1-2: 修复 BAW 类型注解

**问题根源**：`BusinessFlow` 参数类型直接使用 Vue 中定义的类型（如 `string`），未转换为 Python 类型。

**修复方案**：
```python
# baw_generator.py

def _convert_type(self, vue_type: str, lang: str) -> str:
    """将 Vue 类型转换为目标语言类型"""
    type_map = {
        'string': {'py': 'str', 'ts': 'string'},
        'number': {'py': 'int', 'ts': 'number'},
        'boolean': {'py': 'bool', 'ts': 'boolean'},
        'object': {'py': 'dict', 'ts': 'object'},
        'array': {'py': 'list', 'ts': 'any[]'},
    }
    return type_map.get(vue_type, {}).get(lang, vue_type)

def generate(self, component: VueComponent, flow: BusinessFlow) -> str:
    """生成 Python BAW 文件"""
    # ...
    for param in flow.parameters:
        py_type = self._convert_type(param['type'], 'py')
        lines.append(f"            {param['name']}: {py_type},  # {param['description']}")
    # ...
```

### P2-1: 方法名中文化处理

**问题根源**：`to_snake_case()` 调用 `normalize_identifier()`，但中文字符未被完全转换。

**修复方案**：
- 确保 `to_snake_case()` 正确处理中文
- 添加更多中文词汇映射

```python
# identifier_utils.py

def to_snake_case(text: str) -> str:
    """转换为 snake_case"""
    # 先处理中文
    text = _handle_chinese(text)
    # 移除非字母数字字符
    text = re.sub(r'[^\w]', '', text)
    # 确保以字母开头
    if text and not text[0].isalpha():
        text = "elem_" + text
    # 插入下划线
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', text)
    result = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    return result
```

### P2-2: 移除冗余参数

**问题根源**：所有方法都生成 `value: str = 'test_value'` 参数，但只有 input/change 事件需要。

**修复方案**：
```python
# pom_generator.py

def _generate_methods(self, element: VueElement) -> List[str]:
    """生成操作方法"""
    lines = []
    locator_name = self._generate_locator_name(element)

    for event_name in element.events:
        method_name = self._generate_method_name(element, event_name)
        base_event = event_name.split('.')[0]

        lines.append("")

        # 只有 input/change 事件需要 value 参数
        if base_event in ['input', 'change'] and element.tag == 'input':
            lines.append(f"    def {method_name}(self, value: str = 'test_value'):")
        else:
            lines.append(f"    def {method_name}(self):")

        lines.append('        """')
        lines.append(f"        {element.text_content or element.tag}")
        lines.append('        """')

        if base_event in ['input', 'change'] and element.tag == 'input':
            lines.append(f"        self.{locator_name}.fill(value)")
        elif base_event == 'click':
            lines.append(f"        self.{locator_name}.click()")
        # ... 其余代码

    return lines
```

### P2-3: 测试方法名去重

**问题根源**：多个元素有相同的事件和文本，导致测试方法名重复。

**修复方案**：
- 在测试生成器中维护已使用的方法名集合
- 重复名称自动添加数字后缀

```python
# py_generator.py

class PythonGenerator:
    def __init__(self):
        self.selector_generator = SelectorGenerator()
        self.assertion_generator = AssertionGenerator()
        self._test_name_counter = {}  # 新增：测试名计数器

    def generate_test(self, component: VueComponent) -> str:
        """生成完整的测试文件"""
        self._test_name_counter = {}  # 重置计数器
        # ... 其余代码

    def _generate_test_name(self, element: VueElement, event: str) -> str:
        """生成测试名称（带去重）"""
        text = element.text_content or element.attributes.get('aria-label', element.tag)
        action = get_action(event, 'name')
        base_name = f"{action}_{to_snake_case(text)}"

        # 去重处理
        if base_name in self._test_name_counter:
            self._test_name_counter[base_name] += 1
            return f"{base_name}_{self._test_name_counter[base_name]}"
        else:
            self._test_name_counter[base_name] = 0
            return base_name
```

---

## 修改文件清单

| 文件 | 修改内容 |
|------|----------|
| `src/pom/pom_generator.py` | P0-1 定位器去重、P1-1 修复非法 API、P2-2 移除冗余参数 |
| `src/generator/py_generator.py` | P0-2 修复 import 路径、P2-3 测试方法名去重 |
| `src/baw/baw_generator.py` | P0-3 BAW 调用正确方法、P1-2 修复类型注解 |
| `src/utils/identifier_utils.py` | P2-1 完善中文处理 |

---

## 验证步骤

1. 运行测试命令：
   ```bash
   python src/vue_test_generator.py front-end-code/vue/src/views/Login.vue -o tests_py --language python --generate-baw
   ```

2. 检查生成的文件：
   - `tests_py/python/test_login.py` - 测试方法名无重复，import 路径正确
   - `tests_py/python/pages/login_page.py` - 定位器名无重复，方法名无中文
   - `tests_py/python/baw/login_baw.py` - 调用 `fill_xxx` 而非 `blur_xxx`，类型注解正确

3. 验证生成的代码可运行：
   ```bash
   cd tests_py/python
   python -m pytest test_login.py --collect-only
   ```

---

## 预期输出示例

### login_page.py（修复后）
```python
from playwright.sync_api import Page, Locator


class LoginPage:
    """
    Login 页面对象模型
    封装页面元素定位器和操作方法
    """

    # 用户名 元素定位器
    username_input: Locator

    # 密码 元素定位器
    password_input: Locator

    # 登录 元素定位器
    login_button: Locator

    def __init__(self, page: Page):
        """
        初始化 Login 页面对象
        """
        self.page = page
        self.username_input = page.get_by_test_id('username-input')
        self.password_input = page.get_by_test_id('password-input')
        self.login_button = page.get_by_test_id('login-button')

    def goto(self):
        """
        导航到页面
        """
        self.page.goto('/login')

    def fill_username(self, value: str = 'test_value'):
        """
        用户名
        """
        self.username_input.fill(value)

    def fill_password(self, value: str = 'test_value'):
        """
        密码
        """
        self.password_input.fill(value)

    def click_login(self):
        """
        登录
        """
        self.login_button.click()
```

### login_baw.py（修复后）
```python
from playwright.sync_api import Page
from pages.login_page import LoginPage


class LoginBAW:
    """
    登录业务流程
    组合POM操作：打开登录页面 → 输入用户名 → 输入密码 → 点击登录按钮
    """

    def __init__(self, page: Page):
        self.login_page = LoginPage(page)

    def execute(self,
            username: str,  # 用户名
            password: str,  # 密码
            ):
        """
        执行流程
        """
        # 1. 打开登录页面
        self.login_page.goto()
        # 2. 输入用户名
        self.login_page.fill_username(username)
        # 3. 输入密码
        self.login_page.fill_password(password)
        # 4. 点击登录按钮
        self.login_page.click_login()
```
