"""
集成解析器 - 将增强解析器接入现有生成流程

用法：
  from .integrated_parser import EnhancedPlaywrightGenerator

  generator = EnhancedPlaywrightGenerator()
  generator.generate_from_file(vue_file, output_dir, language, generate_pom)

内部逻辑：
  1. 优先用 html.parser 解析 Vue template（支持 >、多行属性等边界场景）
  2. 增强解析器失败时自动回退到当前正则解析
  3. 额外提取 <script setup> 的 data properties，改善 v-model fill 方法命名
"""

import logging
import re
import sys
from pathlib import Path
from typing import Optional

from .enhanced_parser import (
    parse_vue_template_with_htmlparser,
    parse_script_setup,
    safe_parse_vue,
)

logger = logging.getLogger(__name__)


def patch_generator(generator_class):
    """Monkey-patch PlaywrightGenerator 的 parse 方法。

    对 generator_class 的实例方法进行热替换，不修改原始文件。
    """
    original_parse_file = generator_class.generate_component

    def patched_generate_component(self, component_file: str):
        """增强版生成组件对象。

        1. 检测组件类型（Vue/React）
        2. Vue: 优先用 html.parser 解析 template
        3. 回退到当前正则解析
        """
        component_type = self.detect_component_type(component_file)
        file_path = str(component_file)

        if component_type == 'vue':
            return _parse_vue_enhanced(self, file_path)

        # React 保持现有正则解析（未来接入 Babel）
        return original_parse_file(file_path)

    generator_class.generate_component = patched_generate_component
    return generator_class


def _parse_vue_enhanced(generator, file_path: str):
    """增强版 Vue 解析。

    返回与现有 VueComponent 兼容的对象。
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        logger.warning('[集成解析器] 文件读取失败: %s', e)
        return generator._legacy_parse_file(file_path)

    component_name = Path(file_path).stem

    # 提取 template
    template_match = re.search(r'<template>(.*?)</template>', content, re.DOTALL)
    if not template_match:
        # 没有 template，回退到传统解析
        return generator._legacy_parse_file(file_path)

    template = template_match.group(1).strip()

    # 用 html.parser 解析
    from .enhanced_parser import parse_vue_template_with_htmlparser
    selector_fn = generator.vue_parser._generate_selector_fallback

    try:
        events_raw, inputs = parse_vue_template_with_htmlparser(template, selector_fn)
    except Exception as e:
        logger.warning('[集成解析器] html.parser 解析失败，回退到正则: %s', e)
        return generator._legacy_parse_file(file_path)

    # 如果增强解析器没有提取到事件，回退到正则
    if not events_raw and not inputs:
        return generator._legacy_parse_file(file_path)

    # 构造 VueComponent 兼容的结构（使用现有数据类）
    from .enhanced_parser import DataclassVueEvent, DataclassVueComponent

    # 转换为 VueEvent 格式
    events = []
    for e in events_raw:
        event = generator.vue_parser.EVENT_CLASS(
            event_type=e['event_type'],
            handler=e['handler'],
            selector=e['selector'],
            element_tag=e['element_tag'],
            element_text=e['element_text'],
        )
        events.append(event)

    # 构造组件
    component = generator.vue_parser.COMPONENT_CLASS(
        name=component_name,
        file_path=file_path,
        events=events,
        inputs=inputs,
    )

    # 额外：提取 script setup 的 data properties
    try:
        script_info = parse_script_setup(content)
        component.data_properties = script_info.get('data_properties', [])
    except Exception:
        component.data_properties = []

    return component


class EnhancedPlaywrightGenerator:
    """增强版生成器，优先使用 html.parser 解析 Vue 模板。

    用法与 PlaywrightGenerator 完全相同，仅替换解析层。
    """

    def __init__(self):
        # 延迟导入，避免循环依赖
        spec_path = Path(__file__).parent.parent.parent / '.claude/skills/uicode-to-automation-test/scripts/front_end_to_ui_automation.py'

        import importlib.util
        spec = importlib.util.spec_from_file_location('skill_gen', str(spec_path))
        skill_gen = importlib.util.module_from_spec(spec)

        # 加载模块
        import sys
        sys.modules['skill_gen'] = skill_gen
        spec.loader.exec_module(skill_gen)

        # 创建原始生成器
        self._original = skill_gen.PlaywrightGenerator()

        # 修补 parse_file 方法
        self._patch()

    def _patch(self):
        """热替换 parse_file 和 generate_component 方法，使用增强解析器。"""
        original_parse = self._original.generate_component

        def enhanced_parse(component_file):
            """增强解析入口。"""
            component_type = self._original.detect_component_type(component_file)
            file_path = str(component_file)

            if component_type != 'vue':
                return original_parse(file_path)

            # Vue: 优先用 html.parser
            try:
                result = self._parse_vue(file_path)
                if result and (result.events or result.inputs):
                    return result
            except Exception:
                pass

            # 回退到原始解析器
            return original_parse(file_path)

        self._original.generate_component = enhanced_parse
        self._original.parse_file = lambda f: self._original.vue_parser.parse_file(f)

    def _parse_vue(self, file_path):
        """用 html.parser 解析 Vue 文件。"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception:
            return None

        component_name = Path(file_path).stem

        # 提取 template
        template_match = re.search(r'<template>(.*?)</template>', content, re.DOTALL)
        if not template_match:
            return None

        template = template_match.group(1).strip()
        selector_fn = self._original.vue_parser._generate_selector_fallback

        # html.parser 解析
        events_raw, inputs = parse_vue_template_with_htmlparser(template, selector_fn)

        if not events_raw and not inputs:
            return None

        # 构造 VueEvent 列表（使用原始数据类）
        VueEvent_cls = self._original.vue_parser.EVENT_CLASS
        VueComponent_cls = self._original.vue_parser.COMPONENT_CLASS

        events = []
        for e in events_raw:
            events.append(VueEvent_cls(
                event_type=e['event_type'],
                handler=e['handler'],
                selector=e['selector'],
                element_tag=e['element_tag'],
                element_text=e['element_text'],
            ))

        component = VueComponent_cls(
            name=component_name,
            file_path=file_path,
            events=events,
            inputs=inputs,
        )

        return component

    def __getattr__(self, name):
        """将所有调用委托给原始生成器。"""
        return getattr(self._original, name)


# ============================================================
# 快速自测
# ============================================================

if __name__ == '__main__':
    # 验证集成不报错
    print("[集成解析器] 模块加载成功")

    # 测试增强解析能否产生正确的测试输出
    generator = EnhancedPlaywrightGenerator()

    # 生成 Vue 组件测试
    import tempfile
    output_dir = tempfile.mkdtemp()

    # 用边界场景模板测试
    edge_template = """
    <template>
      <a title="Score: 80 > 60" @click="handleClick">Compare</a>
      <button @click.stop="onSave">Save</button>
      <input v-model="formData.email" placeholder="Email" />
    </template>
    <script setup>
    const formData = reactive({ email: '' })
    const handleClick = () => {}
    const onSave = () => {}
    </script>
    """

    tmp_file = Path(output_dir) / 'TestComponent.vue'
    tmp_file.write_text(edge_template, encoding='utf-8')

    result = generator.generate_from_file(
        str(tmp_file),
        output_dir,
        language='python',
        generate_pom=True,
    )
    print(f"[集成解析器] 生成结果: {result}")

    # 验证生成的文件语法
    import ast
    test_dir = Path(output_dir) / 'python' / 'test_cases'
    if test_dir.exists():
        for py_file in test_dir.glob('*.py'):
            try:
                ast.parse(py_file.read_text(encoding='utf-8'))
                print(f"[集成解析器] ✅ 语法验证通过: {py_file.name}")
            except SyntaxError as e:
                print(f"[集成解析器] ❌ 语法错误: {py_file.name}: {e}")

    import shutil
    shutil.rmtree(output_dir)
    print("[集成解析器] 自测完成")
