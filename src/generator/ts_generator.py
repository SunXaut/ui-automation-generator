"""
TypeScript 测试生成器
生成 Playwright TypeScript 测试文件
集成智能断言生成
"""

from typing import List
from src.parser.vue_parser import VueComponent, VueElement
from src.generator.selector_generator import SelectorGenerator
from src.generator.assertion_generator import AssertionGenerator
from src.utils.identifier_utils import normalize_identifier, to_kebab_case, get_action


class TypeScriptGenerator:
    """TypeScript 测试代码生成器"""

    def __init__(self):
        self.selector_generator = SelectorGenerator()
        self.assertion_generator = AssertionGenerator()

    def generate_test(self, component: VueComponent) -> str:
        """生成完整的测试文件"""
        lines = [
            "import { test, expect } from '@playwright/test';",
            f"import {component.name}Page from './pages/{self._to_kebab_case(component.name)}.page';",
            "",
            "/**",
            f" * {component.name} 组件测试",
            " */",
            f"test.describe('{component.name}', () => {{",
        ]

        # 为每个交互元素生成测试
        for element in component.elements:
            test_cases = self._generate_test_cases(component, element)
            lines.extend(test_cases)

        lines.append("});")
        return "\n".join(lines)

    def _generate_test_cases(self, component: VueComponent, element: VueElement) -> List[str]:
        """为元素生成测试用例"""
        lines = []

        for event_name in element.events:
            test_name = self._generate_test_name(element, event_name)
            method_name = self._generate_method_name(element, event_name)
            # 获取原始中文文本用于注释
            original_text = element.text_content or element.tag

            # 生成智能断言
            assertions = self.assertion_generator.generate_assertions(
                component, element, event_name
            )

            lines.extend([
                "  /**",
                f"   * {original_text}",
                "   */",
                f"  test('should {test_name.lower()}', async ({{ page }}) => {{",
                f"    const pageObj = new {component.name}Page(page);",
                "    await pageObj.goto();",
                f"    await pageObj.{method_name}();",
            ])

            # 添加智能断言
            if assertions:
                lines.append("")
                for assertion in assertions:
                    lines.append(f"    // {assertion.description}")
                    lines.append(self.assertion_generator.generate_ts_assertion_code(assertion))
                    lines.append("")
            else:
                lines.append("    // TODO: 添加断言")

            lines.append("  });")
            lines.append("")

        return lines

    def _generate_test_name(self, element: VueElement, event: str) -> str:
        """生成测试名称"""
        text = element.text_content or element.attributes.get('aria-label', element.tag)
        action = get_action(event, 'name')
        normalized_text = normalize_identifier(text)
        return f"{action} {normalized_text}"

    def _generate_method_name(self, element: VueElement, event: str) -> str:
        """生成方法名"""
        text = element.text_content or element.tag
        action = get_action(event, 'ts')
        normalized_text = normalize_identifier(text)
        return f"{action}{normalized_text}"

    def _to_kebab_case(self, name: str) -> str:
        """转换为 kebab-case"""
        return to_kebab_case(name)
