"""
统一命名服务
集中管理所有命名逻辑，确保一致性
"""

from typing import Dict, Set
from src.parser.vue_parser import VueElement
from src.utils.identifier_utils import to_snake_case, to_camel_case, to_kebab_case


class NamingService:
    """统一命名服务 - 确保命名一致性和唯一性"""

    def __init__(self):
        self._used_names: Dict[str, Set[str]] = {
            'locator': set(),
            'method': set(),
            'test': set(),
            'file': set()
        }
        # 缓存：元素 -> 已生成的名称，避免同一元素多次调用得到不同名称
        self._locator_cache: Dict[int, str] = {}
        self._method_cache: Dict[tuple, str] = {}

    def reset(self):
        """重置命名记录（每个组件生成前调用）"""
        for key in self._used_names:
            self._used_names[key].clear()
        self._locator_cache.clear()
        self._method_cache.clear()

    def get_locator_name(self, element: VueElement, lang: str = 'py') -> str:
        """
        生成定位器名称

        Args:
            element: Vue 元素
            lang: 语言类型 ('py' 或 'ts')

        Returns:
            唯一的定位器名称
        """
        # 检查缓存
        cache_key = (id(element), lang)
        if cache_key in self._locator_cache:
            return self._locator_cache[cache_key]

        # 使用语义名称作为基础
        base_name = self._get_semantic_base(element)

        # 根据语言转换格式
        if lang == 'ts':
            name = to_camel_case(base_name)
        else:
            name = to_snake_case(base_name)

        # 确保唯一性
        unique_name = self._ensure_unique(name, 'locator')

        # 缓存结果
        self._locator_cache[cache_key] = unique_name

        return unique_name

    def get_method_name(self, element: VueElement, event: str, lang: str = 'py') -> str:
        """
        生成方法名称

        Args:
            element: Vue 元素
            event: 事件名称（可能包含修饰符）
            lang: 语言类型 ('py' 或 'ts')

        Returns:
            唯一的方法名称
        """
        # 检查缓存
        cache_key = (id(element), event, lang)
        if cache_key in self._method_cache:
            return self._method_cache[cache_key]

        # 提取基础事件（去除修饰符）
        base_event = event.split('.')[0]

        # 使用事件类型作为方法名的前缀，而不是元素的主要操作
        action = base_event

        # 获取语义基础名称
        base_name = self._get_semantic_base(element)

        # 组合方法名
        if lang == 'ts':
            name = f"{to_camel_case(action)}{to_camel_case(base_name)}"
        else:
            name = f"{to_snake_case(action)}_{to_snake_case(base_name)}"

        # 确保唯一性
        unique_name = self._ensure_unique(name, 'method')

        # 缓存结果
        self._method_cache[cache_key] = unique_name

        return unique_name

    def get_test_name(self, element: VueElement, event: str, lang: str = 'py') -> str:
        """
        生成测试方法名称

        Args:
            element: Vue 元素
            event: 事件名称（可能包含修饰符）
            lang: 语言类型 ('py' 或 'ts')

        Returns:
            唯一的测试方法名称
        """
        # 提取基础事件（去除修饰符）
        base_event = event.split('.')[0]

        # 使用主要操作或事件名称
        action = element.primary_action if element.primary_action else base_event

        # 获取语义基础名称
        base_name = self._get_semantic_base(element)

        # 组合测试名
        if lang == 'ts':
            name = f"should {to_camel_case(action)} {to_camel_case(base_name)}"
        else:
            name = f"test_{to_snake_case(action)}_{to_snake_case(base_name)}"

        # 确保唯一性
        return self._ensure_unique(name, 'test')

    def get_file_name(self, component_name: str, suffix: str = '', lang: str = 'py') -> str:
        """
        生成文件名称

        Args:
            component_name: 组件名称
            suffix: 文件后缀（如 '_page', '_baw'）
            lang: 语言类型 ('py' 或 'ts')

        Returns:
            唯一的文件名称
        """
        if lang == 'ts':
            name = f"{to_kebab_case(component_name)}{suffix}"
        else:
            name = f"{to_snake_case(component_name)}{suffix}"

        # 确保唯一性
        return self._ensure_unique(name, 'file')

    def _get_semantic_base(self, element: VueElement) -> str:
        """
        获取语义基础名称

        优先级：semantic_name > data-testid > aria-label > placeholder > text_content > tag
        """
        # 优先使用解析器提取的语义名称
        if element.semantic_name:
            return element.semantic_name

        # 降级方案
        if element.data_testid:
            return element.data_testid
        elif element.attributes.get('aria-label'):
            return element.attributes['aria-label']
        elif element.attributes.get('placeholder'):
            return element.attributes['placeholder']
        elif element.text_content:
            return element.text_content
        else:
            return element.tag

    def _ensure_unique(self, name: str, category: str) -> str:
        """
        确保名称在指定类别中唯一

        Args:
            name: 原始名称
            category: 类别 ('locator', 'method', 'test', 'file')

        Returns:
            唯一的名称（如有重复则添加数字后缀）
        """
        if name not in self._used_names[category]:
            self._used_names[category].add(name)
            return name

        # 名称已存在，添加数字后缀
        counter = 1
        while f"{name}_{counter}" in self._used_names[category]:
            counter += 1

        unique_name = f"{name}_{counter}"
        self._used_names[category].add(unique_name)
        return unique_name

    def get_base_event(self, event: str) -> str:
        """
        提取基础事件名称（去除修饰符）

        Args:
            event: 事件名称（如 'click.prevent'）

        Returns:
            基础事件名称（如 'click'）
        """
        return event.split('.')[0]
