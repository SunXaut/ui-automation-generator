"""
增强解析器集成 - 直接可用，无需修改现有代码

用法：
  python -m parser.run_enhanced <vue_file> -o <output_dir>
"""

import argparse
import importlib.util
import logging
import re
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(message)s')

# 确保 src 在路径中
SRC_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(SRC_DIR))

# 加载 skill 生成器
SKILL_SCRIPT = SRC_DIR.parent / '.claude/skills/uicode-to-automation-test/scripts/front_end_to_ui_automation.py'
spec = importlib.util.spec_from_file_location('skill_gen', str(SKILL_SCRIPT))
skill_gen = importlib.util.module_from_spec(spec)
sys.modules['skill_gen'] = skill_gen
spec.loader.exec_module(skill_gen)

# 加载增强解析器
from parser.enhanced_parser import parse_vue_template_with_htmlparser, parse_script_setup


def main():
    parser = argparse.ArgumentParser(description='增强解析器集成')
    parser.add_argument('input', help='Vue 文件路径')
    parser.add_argument('-o', '--output', default='./tests', help='输出目录')
    parser.add_argument('--language', default='python', choices=['python', 'typescript', 'java'])
    parser.add_argument('--verbose', action='store_true')

    args = parser.parse_args()

    if not Path(args.input).exists():
        print(f'错误: 文件不存在 {args.input}')
        return 1

    file_path = str(Path(args.input))
    content = Path(args.input).read_text(encoding='utf-8')

    # 1. 用 html.parser 解析 template
    template_match = re.search(r'<template>(.*?)</template>', content, re.DOTALL)
    if not template_match:
        print('错误: 未找到 <template>')
        return 1
    template = template_match.group(1).strip()

    # 创建原始生成器（用于 selector 生成）
    generator = skill_gen.PlaywrightGenerator()
    selector_fn = generator.vue_parser._generate_selector_fallback

    # 用 html.parser 解析
    events_raw, inputs = parse_vue_template_with_htmlparser(template, selector_fn)
    print(f'[增强解析器] 提取到 {len(events_raw)} 个事件, {len(inputs)} 个 v-model')

    if args.verbose:
        for e in events_raw:
            print(f'  event: {e["event_type"]} on <{e["element_tag"]}> handler={e["handler"]}')
        for i in inputs:
            print(f'  v-model: {i}')

    # 2. 提取 script setup
    script_info = parse_script_setup(content)
    if args.verbose:
        print(f'  script data_properties: {script_info["data_properties"]}')
        print(f'  script methods: {script_info["methods"][:10]}')

    # 3. 构造 VueComponent
    component = skill_gen.VueComponent(
        name=Path(args.input).stem,
        file_path=file_path,
        events=[],
        inputs=inputs,
    )

    for e_raw in events_raw:
        component.events.append(skill_gen.VueEvent(
            event_type=e_raw['event_type'],
            handler=e_raw['handler'],
            selector=e_raw['selector'],
            element_tag=e_raw['element_tag'],
            element_text=e_raw['element_text'],
        ))

    # 4. 用原始生成器生成测试文件
    try:
        result = generator.generate_from_file(file_path, args.output, args.language, generate_pom=True)
        print(f'[原始生成器] 结果: {result}')
    except Exception as err:
        print(f'[原始生成器] ❌ 生成失败: {err}')
        return 1

    # 5. 语法验证生成的测试文件
    test_dir = Path(args.output) / 'test_cases'
    if not test_dir.exists():
        test_dir = Path(args.output) / 'python' / 'test_cases'

    found = list(test_dir.glob(f'test_{Path(args.input).stem.lower()}*.py'))
    if found:
        for f in found:
            try:
                import ast
                ast.parse(f.read_text(encoding='utf-8'))
                print(f'[语法验证] ✅ {f.name}')
            except SyntaxError as err:
                print(f'[语法验证] ❌ {f.name}: {err}')
    else:
        print(f'[语法验证] ⚠️ 未找到测试文件在 {test_dir}')

    # 6. 边界场景测试
    print(f'\n--- 对抗测试: 边界场景 ---')
    edge_cases = [
        ('Case 1: 属性值含 >', '<a title="Score: 80 > 60" @click="handleClick">Compare</a>'),
        ('Case 2: 多行属性', '<button\n  v-if="count > 0"\n  @click="handleClick">Click</button>'),
        ('Case 3: 自闭合组件 + JS 内 >', '<UserProfile :items="items.filter(i => i.value > 0)" @action="handleAction" />'),
        ('Case 4: Composition API v-model', '<input v-model="formData.username" type="text" />'),
        ('Case 5: 事件修饰符', '<a @click.stop.prevent="onSave" href="#">Save</a>'),
        ('Case 6: 布尔属性', '<input disabled @change="handleChange" />'),
    ]

    for name, code in edge_cases:
        ev, inv = parse_vue_template_with_htmlparser(code, selector_fn)
        status = '✅' if (ev or inv) else '❌'
        print(f'  {status} {name}: {len(ev)} events, {len(inv)} inputs')

    return 0


if __name__ == '__main__':
    sys.exit(main())
