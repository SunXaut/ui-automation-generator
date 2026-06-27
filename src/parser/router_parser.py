"""
Vue Router 配置解析器
解析 vue-router 配置文件，生成路由导航测试
"""

from typing import List, Dict, Any, Optional
import re
from dataclasses import dataclass, field


@dataclass
class Route:
    """路由配置"""
    path: str
    name: str
    component: str
    meta: Dict[str, Any] = field(default_factory=dict)
    children: List['Route'] = field(default_factory=list)
    redirect: Optional[str] = None


@dataclass
class RouterConfig:
    """路由器配置"""
    routes: List[Route] = field(default_factory=list)
    history_mode: str = "hash"  # hash, history, memory
    base_path: str = "/"


class RouterParser:
    """Vue Router 配置解析器"""

    def __init__(self):
        self.route_pattern = re.compile(
            r'\{\s*path:\s*[\'"]([^\'"]+)[\'"]\s*,\s*'
            r'name:\s*[\'"]([^\'"]+)[\'"]\s*,\s*'
            r'component:\s*(\w+)',
            re.DOTALL
        )
        self.meta_pattern = re.compile(r'meta:\s*\{([^}]+)\}', re.DOTALL)
        self.redirect_pattern = re.compile(r'redirect:\s*[\'"]([^\'"]+)[\'"]')
        self.history_pattern = re.compile(r'create(\w+)History')

    def parse_file(self, file_path: str) -> RouterConfig:
        """解析 Router 配置文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return self.parse_content(content)

    def parse_content(self, content: str) -> RouterConfig:
        """解析 Router 配置内容"""
        # 提取 history 模式
        history_match = self.history_pattern.search(content)
        history_mode = history_match.group(1).lower() if history_match else "hash"

        # 提取路由配置
        routes = self._extract_routes(content)

        return RouterConfig(
            routes=routes,
            history_mode=history_mode
        )

    def _extract_routes(self, content: str) -> List[Route]:
        """提取路由配置"""
        routes = []

        # 查找 routes 数组
        routes_arr_match = re.search(r'(?:const\s+)?routes\s*=\s*\[', content)
        if not routes_arr_match:
            return routes

        # 提取每个路由对象
        # 简化解析：查找 { path, name, component } 模式
        route_blocks = self._extract_route_blocks(content)

        for block in route_blocks:
            route = self._parse_route_block(block)
            if route:
                routes.append(route)

        return routes

    def _extract_route_blocks(self, content: str) -> List[str]:
        """提取路由代码块"""
        blocks = []

        # 查找所有路由对象
        start = 0
        while True:
            # 查找 { path:
            match = re.search(r'\{\s*path:', content[start:])
            if not match:
                break

            # 找到对应的闭合 }
            brace_count = 0
            block_start = start + match.start()
            for i in range(block_start, len(content)):
                if content[i] == '{':
                    brace_count += 1
                elif content[i] == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        blocks.append(content[block_start:i+1])
                        start = i + 1
                        break
            else:
                break

        return blocks

    def _parse_route_block(self, block: str) -> Optional[Route]:
        """解析单个路由块"""
        # 提取 path
        path_match = re.search(r'path:\s*[\'"]([^\'"]+)[\'"]', block)
        if not path_match:
            return None

        path = path_match.group(1)

        # 提取 name
        name_match = re.search(r'name:\s*[\'"]([^\'"]+)[\'"]', block)
        name = name_match.group(1) if name_match else ""

        # 提取 component
        component_match = re.search(r'component:\s*(\w+)', block)
        component = component_match.group(1) if component_match else ""

        # 提取 meta
        meta = {}
        meta_match = self.meta_pattern.search(block)
        if meta_match:
            meta_content = meta_match.group(1)
            for kv_match in re.finditer(r'(\w+):\s*(\w+)', meta_content):
                key = kv_match.group(1)
                value = kv_match.group(2)
                # 处理布尔值
                if value == 'true':
                    value = True
                elif value == 'false':
                    value = False
                meta[key] = value

        # 提取 redirect
        redirect = None
        redirect_match = self.redirect_pattern.search(block)
        if redirect_match:
            redirect = redirect_match.group(1)

        # 提取子路由
        children = []
        if 'children:' in block:
            children_content = block[block.index('children:'):]
            children = self._extract_routes(children_content)

        return Route(
            path=path,
            name=name,
            component=component,
            meta=meta,
            children=children,
            redirect=redirect
        )


class RouterTestGenerator:
    """路由测试生成器"""

    def __init__(self, language: str = "typescript"):
        self.language = language

    def generate(self, config: RouterConfig) -> str:
        """生成路由测试文件"""
        if self.language == "typescript":
            return self._generate_ts(config)
        else:
            return self._generate_py(config)

    def _generate_ts(self, config: RouterConfig) -> str:
        """生成 TypeScript 路由测试"""
        lines = [
            "import { test, expect } from '@playwright/test';",
            "",
            "/**",
            " * 路由导航测试",
            " * 测试所有路由的可访问性和导航",
            " */",
            "test.describe('路由导航', () => {",
        ]

        for route in config.routes:
            if route.redirect:
                continue

            lines.extend([
                "  /**",
                f"   * 测试 {route.name or route.path} 路由",
                "   */",
                f"  test('should navigate to {route.name or route.path}', async ({{ page }}) => {{",
                f"    await page.goto('{route.path}');",
            ])

            # 验证 URL
            lines.append(f"    await expect(page).toHaveURL(/^{route.path.replace('/', '\\/')}/);")

            # 验证 meta 要求
            if route.meta.get('requiresAuth'):
                lines.append("    // TODO: 需要先登录")
                lines.append("    // 可以使用 fixture 或 beforeEach 处理认证")

            lines.append("  });")
            lines.append("")

        lines.append("});")
        return "\n".join(lines)

    def _generate_py(self, config: RouterConfig) -> str:
        """生成 Python 路由测试"""
        lines = [
            "import pytest",
            "from playwright.sync_api import Page, expect",
            "",
            "",
            "class Test路由导航:",
            '    """',
            "    路由导航测试",
            "    测试所有路由的可访问性和导航",
            '    """',
            "",
        ]

        for route in config.routes:
            if route.redirect:
                continue

            test_name = (route.name or route.path).replace('/', '_').strip('_')

            lines.extend([
                f"    def test_{test_name}(self, page: Page):",
                '        """',
                f"        测试 {route.name or route.path} 路由",
                '        """',
                f"        page.goto('{route.path}')",
            ])

            # 验证 URL
            lines.append(f"        expect(page).to_have_url(r'^{route.path}')")

            # 验证 meta 要求
            if route.meta.get('requiresAuth'):
                lines.append("        # TODO: 需要先登录")

            lines.append("")

        return "\n".join(lines)
