"""
选择器生成器
根据元素信息生成 Playwright 语义选择器（结构化数据）
"""

from typing import Optional
from dataclasses import dataclass
from src.parser.vue_parser import VueElement


@dataclass
class SelectorInfo:
    """选择器信息（语言无关）"""
    type: str  # 'role', 'label', 'placeholder', 'testid', 'css'
    role: str = ""  # 'button', 'link', 'checkbox', etc.
    name: str = ""  # name parameter for role/label
    value: str = ""  # for testid, placeholder, css


class SelectorGenerator:
    """Playwright 选择器生成器 - 返回结构化数据"""

    def generate(self, element: VueElement) -> SelectorInfo:
        """为元素生成最佳选择器（结构化）"""
        # 优先级：data-testid > role > label > placeholder > CSS
        if element.data_testid:
            return SelectorInfo(type='testid', value=element.data_testid)

        if element.tag == 'button':
            return self._generate_button_selector(element)
        elif element.tag == 'input':
            return self._generate_input_selector(element)
        elif element.tag == 'a':
            return self._generate_link_selector(element)
        else:
            return self._generate_css_selector(element)

    def _generate_button_selector(self, element: VueElement) -> SelectorInfo:
        """生成按钮选择器"""
        text = element.text_content
        if text:
            return SelectorInfo(type='role', role='button', name=text)

        # 使用 aria-label
        aria_label = element.attributes.get('aria-label')
        if aria_label:
            return SelectorInfo(type='role', role='button', name=aria_label)

        return self._generate_css_selector(element)

    def _generate_input_selector(self, element: VueElement) -> SelectorInfo:
        """生成输入框选择器"""
        input_type = element.attributes.get('type', 'text')

        # checkbox/radio
        if input_type in ['checkbox', 'radio']:
            label = element.attributes.get('aria-label', '')
            if label:
                return SelectorInfo(type='role', role=input_type, name=label)

        # 使用 label 关联
        label = element.attributes.get('aria-label')
        if label:
            return SelectorInfo(type='label', name=label)

        # 使用 placeholder
        placeholder = element.attributes.get('placeholder')
        if placeholder:
            return SelectorInfo(type='placeholder', value=placeholder)

        return self._generate_css_selector(element)

    def _generate_link_selector(self, element: VueElement) -> SelectorInfo:
        """生成链接选择器"""
        text = element.text_content
        if text:
            return SelectorInfo(type='role', role='link', name=text)

        return self._generate_css_selector(element)

    def _generate_css_selector(self, element: VueElement) -> SelectorInfo:
        """生成 CSS 选择器（兜底方案）"""
        selector = element.tag

        if element.attributes.get('id'):
            selector += f"#{element.attributes['id']}"
        elif element.attributes.get('class'):
            classes = element.attributes['class'].split()
            selector += f".{classes[0]}"

        return SelectorInfo(type='css', value=selector)
