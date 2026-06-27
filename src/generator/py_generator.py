"""
Python 测试生成器
生成 Playwright Python 测试文件
集成智能断言生成
"""

from typing import List
from src.parser.vue_parser import VueComponent, VueElement
from src.generator.selector_generator import SelectorGenerator
from src.generator.assertion_generator import AssertionGenerator
from src.utils.naming_service import NamingService
from src.utils.identifier_utils import to_snake_case


class PythonGenerator:
    """Python 测试代码生成器"""

    def __init__(self, naming_service: NamingService = None):
        self.selector_generator = SelectorGenerator()
        self.assertion_generator = AssertionGenerator()
        self.naming_service = naming_service or NamingService()

    def generate_test(self, component: VueComponent) -> str:
        """生成完整的测试文件"""
        self.naming_service.reset()
        page_file = self.naming_service.get_file_name(component.name, '_page', 'py')
        lines = [
            "import pytest",
            "from playwright.sync_api import Page, expect",
            f"from pages.{page_file} import {component.name}Page",
            "",
            "",
            f"class Test{component.name}:",
            '    """',
            f"    {component.name} 组件测试",
            '    """',
            "",
        ]

        # 为每个交互元素生成测试
        for element in component.elements:
            test_cases = self._generate_test_cases(component, element)
            lines.extend(test_cases)

        return "\n".join(lines)

    def _generate_test_cases(self, component: VueComponent, element: VueElement) -> List[str]:
        """为元素生成测试用例"""
        lines = []

        for event_name in element.events:
            test_name = self.naming_service.get_test_name(element, event_name, 'py')
            method_name = self.naming_service.get_method_name(element, event_name, 'py')

            # 生成智能断言
            assertions = self.assertion_generator.generate_assertions(
                component, element, event_name
            )

            lines.extend([
                f"    def {test_name}(self, page: Page):",
                '        """',
                f"        {test_name}",
                '        """',
                f"        page_obj = {component.name}Page(page)",
                "        page_obj.goto()",
                f"        page_obj.{method_name}()",
            ])

            # 添加智能断言
            if assertions:
                lines.append("")
                for assertion in assertions:
                    lines.append(f"        # {assertion.description}")
                    lines.append(self.assertion_generator.generate_py_assertion_code(assertion))
                    lines.append("")
            else:
                lines.append("        # TODO: 添加断言")

            lines.append("")
            lines.append("")

        return lines
