"""
Pinia Store 解析器
解析 Pinia store 配置，生成状态管理测试
"""

from typing import List, Dict, Any, Optional
import re
from dataclasses import dataclass, field


@dataclass
class StateProperty:
    """State 属性"""
    name: str
    default_value: str
    type: str = "any"


@dataclass
class Getter:
    """Getter 定义"""
    name: str
    return_type: str = "any"
    dependencies: List[str] = field(default_factory=list)


@dataclass
class Action:
    """Action 定义"""
    name: str
    is_async: bool = False
    parameters: List[Dict[str, str]] = field(default_factory=list)


@dataclass
class PiniaStore:
    """Pinia Store 信息"""
    name: str
    id: str
    state: List[StateProperty] = field(default_factory=list)
    getters: List[Getter] = field(default_factory=list)
    actions: List[Action] = field(default_factory=list)


class PiniaParser:
    """Pinia Store 解析器"""

    def __init__(self):
        self.define_store_pattern = re.compile(r'defineStore\(\s*[\'"]([^\'"]+)[\'"]')
        self.state_pattern = re.compile(r'state\s*[:=]\s*\(\)\s*=>\s*\{([^}]+)\}', re.DOTALL)
        self.getters_pattern = re.compile(r'getters\s*[:=]\s*\{([^}]+)\}', re.DOTALL)
        self.actions_pattern = re.compile(r'actions\s*[:=]\s*\{([^}]+)\}', re.DOTALL)

    def parse_file(self, file_path: str) -> PiniaStore:
        """解析 Pinia Store 文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return self.parse_content(content, file_path)

    def parse_content(self, content: str, file_name: str = "") -> PiniaStore:
        """解析 Pinia Store 内容"""
        # 提取 store ID
        id_match = self.define_store_pattern.search(content)
        store_id = id_match.group(1) if id_match else "unknown"

        # 提取 store 名称（从文件名）
        name = file_name.split('/')[-1].replace('.ts', '').replace('.js', '')
        # 转换为 PascalCase
        name = ''.join(word.title() for word in re.split(r'[-_]', name))

        # 提取 state
        state = self._extract_state(content)

        # 提取 getters
        getters = self._extract_getters(content)

        # 提取 actions
        actions = self._extract_actions(content)

        return PiniaStore(
            name=name,
            id=store_id,
            state=state,
            getters=getters,
            actions=actions
        )

    def _extract_state(self, content: str) -> List[StateProperty]:
        """提取 state 定义"""
        state_props = []

        state_match = self.state_pattern.search(content)
        if not state_match:
            return state_props

        state_content = state_match.group(1)

        # 解析 state 属性
        for line in state_content.split('\n'):
            line = line.strip()
            if not line or line.startswith('//'):
                continue

            # 匹配 property: value 或 property: ref(value)
            prop_match = re.match(r'(\w+):\s*(.+)', line)
            if prop_match:
                name = prop_match.group(1)
                default_value = prop_match.group(2).rstrip(',')

                # 推断类型
                prop_type = self._infer_type(default_value)

                state_props.append(StateProperty(
                    name=name,
                    default_value=default_value,
                    type=prop_type
                ))

        return state_props

    def _extract_getters(self, content: str) -> List[Getter]:
        """提取 getters 定义"""
        getters = []

        getters_match = self.getters_pattern.search(content)
        if not getters_match:
            return getters

        getters_content = getters_match.group(1)

        # 解析 getter 定义
        getter_pattern = re.compile(r'(\w+)\s*[:=]\s*(?:\(\s*state\s*\)\s*=>|function\s*\(\s*state\s*\))', re.DOTALL)

        for match in getter_pattern.finditer(getters_content):
            name = match.group(1)

            # 简单分析依赖
            # 查找 state.xxx 引用
            deps = re.findall(r'state\.(\w+)', getters_content)

            getters.append(Getter(
                name=name,
                dependencies=list(set(deps))
            ))

        return getters

    def _extract_actions(self, content: str) -> List[Action]:
        """提取 actions 定义"""
        actions = []

        actions_match = self.actions_pattern.search(content)
        if not actions_match:
            return actions

        actions_content = actions_match.group(1)

        # 解析 action 定义
        # 匹配 async fn(...) { 或 fn(...) {
        action_pattern = re.compile(r'(?:async\s+)?(\w+)\s*\(([^)]*)\)\s*(?::\s*\w+\s*)?=>?\s*\{', re.DOTALL)

        for match in action_pattern.finditer(actions_content):
            name = match.group(1)
            params_str = match.group(2)

            # 检查是否异步
            is_async = 'async ' in actions_content[max(0, match.start()-10):match.start()]

            # 解析参数
            parameters = []
            if params_str.strip():
                for param in params_str.split(','):
                    param = param.strip()
                    if param:
                        # 解析参数类型
                        param_match = re.match(r'(\w+)(?::\s*(\w+))?', param)
                        if param_match:
                            parameters.append({
                                'name': param_match.group(1),
                                'type': param_match.group(2) or 'any'
                            })

            actions.append(Action(
                name=name,
                is_async=is_async,
                parameters=parameters
            ))

        return actions

    def _infer_type(self, value: str) -> str:
        """推断类型"""
        value = value.strip().rstrip(',')

        if value.startswith('ref(') or value.startswith('reactive('):
            # 提取内部值
            inner = value[4:-1] if value.startswith('ref') else value[9:-1]
            return self._infer_type(inner)

        if value.startswith("'") or value.startswith('"'):
            return 'string'
        if value.isdigit():
            return 'number'
        if value in ['true', 'false']:
            return 'boolean'
        if value.startswith('['):
            return 'array'
        if value.startswith('{'):
            return 'object'
        if value == 'null':
            return 'null'
        if value == 'undefined':
            return 'undefined'

        return 'any'


class PiniaTestGenerator:
    """Pinia Store 测试生成器"""

    def __init__(self, language: str = "typescript"):
        self.language = language

    def generate(self, store: PiniaStore) -> str:
        """生成 Store 测试文件"""
        if self.language == "typescript":
            return self._generate_ts(store)
        else:
            return self._generate_py(store)

    def _generate_ts(self, store: PiniaStore) -> str:
        """生成 TypeScript Store 测试"""
        lines = [
            "import { test, expect } from '@playwright/test';",
            "",
            "/**",
            f" * {store.name} Store 测试",
            " * 测试状态管理和业务逻辑",
            " */",
            f"test.describe('{store.name} Store', () => {{",
            "",
            "  // TODO: 配置 store 测试环境",
            "  // 可以使用 Playwright 的 page.evaluate 在浏览器中测试 store",
            "",
        ]

        # 生成 state 测试
        if store.state:
            lines.extend([
                "  test.describe('State', () => {",
            ])

            for prop in store.state:
                lines.extend([
                    f"    test('should have default {prop.name}', async ({{ page }}) => {{",
                    f"      // 测试 {prop.name} 的默认值",
                    f"      // 期望类型: {prop.type}",
                    f"      // 默认值: {prop.default_value}",
                    "      // TODO: 验证 state 默认值",
                    "    });",
                    "",
                ])

            lines.append("  });")
            lines.append("")

        # 生成 getters 测试
        if store.getters:
            lines.extend([
                "  test.describe('Getters', () => {",
            ])

            for getter in store.getters:
                deps = ', '.join(getter.dependencies) if getter.dependencies else '无'
                lines.extend([
                    f"    test('should compute {getter.name}', async ({{ page }}) => {{",
                    f"      // 测试 {getter.name} getter",
                    f"      // 依赖: {deps}",
                    "      // TODO: 验证 getter 计算值",
                    "    });",
                    "",
                ])

            lines.append("  });")
            lines.append("")

        # 生成 actions 测试
        if store.actions:
            lines.extend([
                "  test.describe('Actions', () => {",
            ])

            for action in store.actions:
                params = ', '.join(p['name'] for p in action.parameters)
                async_prefix = "async " if action.is_async else ""
                await_prefix = "await " if action.is_async else ""

                lines.extend([
                    f"    test('should execute {action.name}', async ({{ page }}) => {{",
                    f"      // 测试 {action.name} action",
                    f"      // 参数: {params}",
                    f"      // TODO: 调用 action 并验证结果",
                    "    });",
                    "",
                ])

            lines.append("  });")

        lines.append("});")
        return "\n".join(lines)

    def _generate_py(self, store: PiniaStore) -> str:
        """生成 Python Store 测试"""
        lines = [
            "import pytest",
            "from playwright.sync_api import Page, expect",
            "",
            "",
            f"class Test{store.name}Store:",
            '    """',
            f"    {store.name} Store 测试",
            "    测试状态管理和业务逻辑",
            '    """',
            "",
            "    # TODO: 配置 store 测试环境",
            "    # 可以使用 Playwright 的 page.evaluate 在浏览器中测试 store",
            "",
        ]

        # 生成 state 测试
        if store.state:
            lines.append("    class TestState:")
            lines.append('        """State 测试"""')
            lines.append("")

            for prop in store.state:
                lines.extend([
                    f"        def test_default_{prop.name}(self, page: Page):",
                    f'            """',
                    f"            测试 {prop.name} 的默认值",
                    f"            期望类型: {prop.type}",
                    f"            默认值: {prop.default_value}",
                    '            """',
                    "            # TODO: 验证 state 默认值",
                    "",
                ])

        # 生成 getters 测试
        if store.getters:
            lines.append("    class TestGetters:")
            lines.append('        """Getters 测试"""')
            lines.append("")

            for getter in store.getters:
                deps = ', '.join(getter.dependencies) if getter.dependencies else '无'
                lines.extend([
                    f"        def test_{getter.name}(self, page: Page):",
                    f'            """',
                    f"            测试 {getter.name} getter",
                    f"            依赖: {deps}",
                    '            """',
                    "            # TODO: 验证 getter 计算值",
                    "",
                ])

        # 生成 actions 测试
        if store.actions:
            lines.append("    class TestActions:")
            lines.append('        """Actions 测试"""')
            lines.append("")

            for action in store.actions:
                params = ', '.join(p['name'] for p in action.parameters)
                lines.extend([
                    f"        def test_{action.name}(self, page: Page):",
                    f'            """',
                    f"            测试 {action.name} action",
                    f"            参数: {params}",
                    '            """',
                    "            # TODO: 调用 action 并验证结果",
                    "",
                ])

        return "\n".join(lines)
