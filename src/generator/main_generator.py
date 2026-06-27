"""
主生成器
协调解析和生成流程
支持 Vue 组件、Router 配置、Pinia Store
"""

import os
from pathlib import Path
from typing import Optional

from src.parser.vue_parser import VueParser
from src.parser.router_parser import RouterParser, RouterTestGenerator
from src.parser.pinia_parser import PiniaParser, PiniaTestGenerator
from src.generator.ts_generator import TypeScriptGenerator
from src.generator.py_generator import PythonGenerator
from src.pom.pom_generator import TypeScriptPOMGenerator, PythonPOMGenerator
from src.baw.baw_generator import BAWDetector, TypeScriptBAWGenerator, PythonBAWGenerator
from src.utils.naming_service import NamingService
from src.utils.identifier_utils import to_kebab_case, to_snake_case


class TestGenerator:
    """测试生成器主类"""

    def __init__(self, output_dir: str = "tests", language: str = "typescript", generate_baw: bool = True):
        self.output_dir = Path(output_dir)
        self.language = language
        self.generate_baw = generate_baw

        # 初始化解析器
        self.vue_parser = VueParser()
        self.router_parser = RouterParser()
        self.pinia_parser = PiniaParser()

        # 创建共享的命名服务
        self.naming_service = NamingService()

        # 初始化生成器（共享命名服务）
        if language == "typescript":
            self.test_generator = TypeScriptGenerator()
            self.pom_generator = TypeScriptPOMGenerator(self.naming_service)
            self.baw_generator = TypeScriptBAWGenerator(self.naming_service)
            self.router_test_generator = RouterTestGenerator("typescript")
            self.pinia_test_generator = PiniaTestGenerator("typescript")
        elif language == "python":
            self.test_generator = PythonGenerator(self.naming_service)
            self.pom_generator = PythonPOMGenerator(self.naming_service)
            self.baw_generator = PythonBAWGenerator(self.naming_service)
            self.router_test_generator = RouterTestGenerator("python")
            self.pinia_test_generator = PiniaTestGenerator("python")
        else:
            raise ValueError(f"不支持的语言: {language}")

        # BAW 检测器
        self.baw_detector = BAWDetector()

    def generate(self, vue_file: str):
        """生成测试文件"""
        # 解析 Vue 组件
        component = self.vue_parser.parse_file(vue_file)

        # 重置命名服务（每个组件重新开始）
        self.naming_service.reset()

        # 确定输出目录
        if self.language == "typescript":
            test_dir = self.output_dir / "typescript"
            pom_dir = test_dir / "pages"
            baw_dir = test_dir / "baw"
        else:
            test_dir = self.output_dir / "python"
            pom_dir = test_dir / "pages"
            baw_dir = test_dir / "baw"

        # 创建目录
        test_dir.mkdir(parents=True, exist_ok=True)
        pom_dir.mkdir(parents=True, exist_ok=True)
        if self.generate_baw:
            baw_dir.mkdir(parents=True, exist_ok=True)

        # 生成测试文件
        test_content = self.test_generator.generate_test(component)
        test_file = self._get_test_file_name(component.name)
        (test_dir / test_file).write_text(test_content, encoding='utf-8')
        print(f"生成测试文件: {test_dir / test_file}")

        # 生成 POM 文件
        pom_content = self.pom_generator.generate(component)
        pom_file = self._get_pom_file_name(component.name)
        (pom_dir / pom_file).write_text(pom_content, encoding='utf-8')
        print(f"生成 POM 文件: {pom_dir / pom_file}")

        # 生成 BAW 文件
        if self.generate_baw:
            flows = self.baw_detector.detect(component)
            for flow in flows:
                baw_content = self.baw_generator.generate(component, flow)
                baw_file = self._get_baw_file_name(flow.name)
                (baw_dir / baw_file).write_text(baw_content, encoding='utf-8')
                print(f"生成 BAW 文件: {baw_dir / baw_file}")

    def generate_router_test(self, router_file: str):
        """生成 Router 测试文件"""
        # 解析 Router 配置
        config = self.router_parser.parse_file(router_file)

        # 确定输出目录
        if self.language == "typescript":
            test_dir = self.output_dir / "typescript"
        else:
            test_dir = self.output_dir / "python"

        test_dir.mkdir(parents=True, exist_ok=True)

        # 生成测试文件
        test_content = self.router_test_generator.generate(config)

        if self.language == "typescript":
            test_file = "router-navigation.spec.ts"
        else:
            test_file = "test_router_navigation.py"

        (test_dir / test_file).write_text(test_content, encoding='utf-8')
        print(f"生成 Router 测试文件: {test_dir / test_file}")

    def generate_store_test(self, store_file: str):
        """生成 Pinia Store 测试文件"""
        # 解析 Store 配置
        store = self.pinia_parser.parse_file(store_file)

        # 确定输出目录
        if self.language == "typescript":
            test_dir = self.output_dir / "typescript"
        else:
            test_dir = self.output_dir / "python"

        test_dir.mkdir(parents=True, exist_ok=True)

        # 生成测试文件
        test_content = self.pinia_test_generator.generate(store)

        store_name = to_kebab_case(store.name) if self.language == "typescript" else to_snake_case(store.name)

        if self.language == "typescript":
            test_file = f"{store_name}-store.spec.ts"
        else:
            test_file = f"test_{store_name}_store.py"

        (test_dir / test_file).write_text(test_content, encoding='utf-8')
        print(f"生成 Store 测试文件: {test_dir / test_file}")

    def _get_test_file_name(self, component_name: str) -> str:
        """获取测试文件名"""
        if self.language == "typescript":
            return f"{to_kebab_case(component_name)}.spec.ts"
        else:
            return f"test_{to_snake_case(component_name)}.py"

    def _get_pom_file_name(self, component_name: str) -> str:
        """获取 POM 文件名"""
        if self.language == "typescript":
            return f"{to_kebab_case(component_name)}.page.ts"
        else:
            return f"{to_snake_case(component_name)}_page.py"

    def _get_baw_file_name(self, flow_name: str) -> str:
        """获取 BAW 文件名"""
        if self.language == "typescript":
            return f"{to_kebab_case(flow_name)}.baw.ts"
        else:
            return f"{to_snake_case(flow_name)}_baw.py"
