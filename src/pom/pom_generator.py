"""
POM (Page Object Model) 生成器
生成 TypeScript 和 Python 的页面对象模型
"""

from typing import List
from src.parser.vue_parser import VueComponent, VueElement
from src.generator.selector_generator import SelectorGenerator, SelectorInfo
from src.utils.naming_service import NamingService
from src.utils.identifier_utils import to_camel_case, to_snake_case, to_kebab_case


class TypeScriptPOMGenerator:
    """TypeScript POM 生成器"""

    def __init__(self, naming_service: NamingService = None):
        self.selector_generator = SelectorGenerator()
        self.naming_service = naming_service or NamingService()

    def _selector_to_ts(self, selector: SelectorInfo) -> str:
        """将 SelectorInfo 转换为 TypeScript Playwright API 调用"""
        if selector.type == 'testid':
            return f"getByTestId('{selector.value}')"
        elif selector.type == 'role':
            if selector.name:
                return f"getByRole('{selector.role}', {{ name: '{selector.name}' }})"
            return f"getByRole('{selector.role}')"
        elif selector.type == 'label':
            return f"getByLabel('{selector.name}')"
        elif selector.type == 'placeholder':
            return f"getByPlaceholder('{selector.value}')"
        else:  # css
            return f"locator('{selector.value}')"

    def generate(self, component: VueComponent) -> str:
        """生成 TypeScript POM 文件"""
        self.naming_service.reset()
        class_name = f"{component.name}Page"
        file_name = to_kebab_case(component.name)

        lines = [
            "import { type Page, type Locator } from '@playwright/test';",
            "",
            "/**",
            f" * {component.name} 页面对象模型",
            " * 封装页面元素定位器和操作方法",
            " */",
            f"export class {class_name} {{",
            "  readonly page: Page;",
        ]

        # 生成定位器属性
        locators = []
        for element in component.elements:
            locator_name = self.naming_service.get_locator_name(element, 'ts')
            selector = self.selector_generator.generate(element)
            comment = element.semantic_name or element.text_content or element.tag
            locators.append(f"  /** {comment} 元素定位器 */")
            locators.append(f"  readonly {locator_name}: Locator;")

        if locators:
            lines.append("")
            lines.extend(locators)

        # 生成构造函数
        lines.append("")
        lines.append(f"  constructor(page: Page) {{")
        lines.append("    this.page = page;")

        for element in component.elements:
            locator_name = self.naming_service.get_locator_name(element, 'ts')
            selector = self.selector_generator.generate(element)
            ts_selector = self._selector_to_ts(selector)
            lines.append(f"    this.{locator_name} = page.{ts_selector};")

        lines.append("  }")

        # 生成方法
        lines.append("")
        lines.append("  /**")
        lines.append("   * 导航到页面")
        lines.append("   */")
        lines.append("  async goto() {")
        lines.append(f"    await this.page.goto('/{file_name}');")
        lines.append("  }")

        for element in component.elements:
            methods = self._generate_methods(element)
            lines.extend(methods)

        lines.append("}")
        return "\n".join(lines)

    def _generate_methods(self, element: VueElement) -> List[str]:
        """生成操作方法"""
        lines = []
        locator_name = self.naming_service.get_locator_name(element, 'ts')

        for event_name in element.events:
            method_name = self.naming_service.get_method_name(element, event_name, 'ts')
            base_event = self.naming_service.get_base_event(event_name)

            lines.append("")
            lines.append("  /**")
            lines.append(f"   * {element.semantic_name or element.text_content or element.tag}")
            lines.append("   */")

            # 根据主要操作决定方法签名
            if element.primary_action in ['fill', 'check'] and element.tag == 'input':
                lines.append(f"  async {method_name}(value?: string) {{")
                lines.append(f"    await this.{locator_name}.fill(value ?? 'test_value');")
            elif base_event == 'click':
                lines.append(f"  async {method_name}() {{")
                lines.append(f"    await this.{locator_name}.click();")
            elif base_event == 'dblclick':
                lines.append(f"  async {method_name}() {{")
                lines.append(f"    await this.{locator_name}.dblclick();")
            elif base_event == 'blur':
                lines.append(f"  async {method_name}() {{")
                lines.append(f"    await this.{locator_name}.blur();")
            elif base_event == 'focus':
                lines.append(f"  async {method_name}() {{")
                lines.append(f"    await this.{locator_name}.focus();")
            else:
                lines.append(f"  async {method_name}() {{")
                lines.append(f"    await this.{locator_name}.{base_event}();")

            lines.append("  }")

        return lines


class PythonPOMGenerator:
    """Python POM 生成器"""

    def __init__(self, naming_service: NamingService = None):
        self.selector_generator = SelectorGenerator()
        self.naming_service = naming_service or NamingService()

    def _selector_to_py(self, selector: SelectorInfo) -> str:
        """将 SelectorInfo 转换为 Python Playwright API 调用"""
        if selector.type == 'testid':
            return f"get_by_test_id('{selector.value}')"
        elif selector.type == 'role':
            if selector.name:
                return f"get_by_role('{selector.role}', name='{selector.name}')"
            return f"get_by_role('{selector.role}')"
        elif selector.type == 'label':
            return f"get_by_label('{selector.name}')"
        elif selector.type == 'placeholder':
            return f"get_by_placeholder('{selector.value}')"
        else:  # css
            return f"locator('{selector.value}')"

    def generate(self, component: VueComponent) -> str:
        """生成 Python POM 文件"""
        self.naming_service.reset()
        class_name = f"{component.name}Page"

        lines = [
            "from playwright.sync_api import Page, Locator",
            "",
            "",
            f"class {class_name}:",
            '    """',
            f"    {component.name} 页面对象模型",
            "    封装页面元素定位器和操作方法",
            '    """',
            "",
        ]

        # 生成定位器属性
        for element in component.elements:
            locator_name = self.naming_service.get_locator_name(element, 'py')
            comment = element.semantic_name or element.text_content or element.tag
            lines.append(f"    # {comment} 元素定位器")
            lines.append(f"    {locator_name}: Locator")
            lines.append("")

        # 生成构造函数
        lines.append("    def __init__(self, page: Page):")
        lines.append('        """')
        lines.append(f"        初始化 {component.name} 页面对象")
        lines.append('        """')
        lines.append("        self.page = page")

        for element in component.elements:
            locator_name = self.naming_service.get_locator_name(element, 'py')
            selector = self.selector_generator.generate(element)
            py_selector = self._selector_to_py(selector)
            lines.append(f"        self.{locator_name} = page.{py_selector}")

        # 生成方法
        lines.append("")
        lines.append("    def goto(self):")
        lines.append('        """')
        lines.append("        导航到页面")
        lines.append('        """')
        file_name = to_snake_case(component.name)
        lines.append(f"        self.page.goto('/{file_name}')")

        for element in component.elements:
            methods = self._generate_methods(element)
            lines.extend(methods)

        return "\n".join(lines)

    def _generate_methods(self, element: VueElement) -> List[str]:
        """生成操作方法"""
        lines = []
        locator_name = self.naming_service.get_locator_name(element, 'py')
        generated_methods = set()  # 跟踪已生成的方法名，避免重复

        # 为 input 元素生成 fill 方法
        if element.tag == 'input' and element.attributes.get('type') not in ['checkbox', 'radio']:
            fill_method = self.naming_service.get_method_name(element, 'input', 'py')
            if fill_method not in generated_methods:
                lines.append("")
                lines.append(f"    def {fill_method}(self, value: str = 'test_value'):")
                lines.append('        """')
                lines.append(f"        填写 {element.semantic_name or element.text_content or element.tag}")
                lines.append('        """')
                lines.append(f"        self.{locator_name}.fill(value)")
                generated_methods.add(fill_method)

        # 为 button 元素生成 click 方法
        if element.tag == 'button':
            click_method = self.naming_service.get_method_name(element, 'click', 'py')
            if click_method not in generated_methods:
                lines.append("")
                lines.append(f"    def {click_method}(self):")
                lines.append('        """')
                lines.append(f"        点击 {element.semantic_name or element.text_content or element.tag}")
                lines.append('        """')
                lines.append(f"        self.{locator_name}.click()")
                generated_methods.add(click_method)

        # 为绑定事件生成方法
        for event_name in element.events:
            method_name = self.naming_service.get_method_name(element, event_name, 'py')
            
            # 如果方法已生成，跳过
            if method_name in generated_methods:
                continue
            
            base_event = self.naming_service.get_base_event(event_name)
            lines.append("")

            # 根据事件类型决定方法签名和实现
            if base_event in ['input', 'change'] and element.tag == 'input':
                # input 和 change 事件需要 value 参数
                lines.append(f"    def {method_name}(self, value: str = 'test_value'):")
                lines.append('        """')
                lines.append(f"        {element.semantic_name or element.text_content or element.tag}")
                lines.append('        """')
                lines.append(f"        self.{locator_name}.fill(value)")
            else:
                # 其他事件不需要 value 参数
                lines.append(f"    def {method_name}(self):")
                lines.append('        """')
                lines.append(f"        {element.semantic_name or element.text_content or element.tag}")
                lines.append('        """')
                
                if base_event == 'click':
                    lines.append(f"        self.{locator_name}.click()")
                elif base_event == 'dblclick':
                    lines.append(f"        self.{locator_name}.dblclick()")
                elif base_event == 'blur':
                    lines.append(f"        self.{locator_name}.blur()")
                elif base_event == 'focus':
                    lines.append(f"        self.{locator_name}.focus()")
                elif base_event == 'submit':
                    lines.append(f"        self.{locator_name}.submit()")
                else:
                    lines.append(f"        self.{locator_name}.{base_event}()")
            
            generated_methods.add(method_name)

        return lines
