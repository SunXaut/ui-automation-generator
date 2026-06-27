"""
高级解析器模块 - 替换正则解析器

提供：
- P0: html.parser 解析 Vue 模板（处理 >、多行属性、自闭合标签）
- P1: @babel/parser 解析 React JSX（处理箭头函数、三元表达式）
- P2: 提取 <script setup> 的 data properties
- P3: 异常安全，解析失败回退到正则

用法：
  from .enhanced_parser import parse_vue_template
"""

import json
import logging
import re
import subprocess
import sys
from html.parser import HTMLParser
from typing import Any, Callable, List, Optional, Tuple

logger = logging.getLogger(__name__)


# ============================================================
# P0: html.parser-based Vue Template Parser
# ============================================================

class VueTemplateHTMLParser(HTMLParser):
    """Streaming Vue template parser using Python's built-in html.parser.

    解决正则无法处理的场景：
    - 属性值中的 > 符号（<a title="a > b" @click="fn">）
    - 多行属性（<input\n  @blur="validate"\n  v-model="name">）
    - 自闭合组件（<UserProfile @action="handle" />）
    - 布尔属性（<input disabled @change="fn">）
    - 事件修饰符（@click.stop.prevent → event_type: click）
    """

    def __init__(self, selector_fn: Callable):
        super().__init__(convert_charrefs=True)
        self.selector_fn = selector_fn
        self.events: List[dict] = []
        self.inputs: List[str] = []
        self._current_tag_stack: List[Optional[str]] = []
        self._current_text: List[str] = []

    def handle_starttag(self, tag, attrs):
        self._process_tag(tag, attrs)
        self._current_tag_stack.append(tag)
        self._current_text = []

    def handle_endtag(self, tag):
        if self._current_tag_stack and self._current_tag_stack[-1] == tag:
            self._current_tag_stack.pop()
        self._current_text = []

    def handle_startendtag(self, tag, attrs):
        self._process_tag(tag, attrs, is_self_closing=True)

    def handle_data(self, data):
        text = data.strip()
        if text and self._current_tag_stack:
            self._current_text.append(text)

    def _process_tag(self, tag: str, attrs: List[Tuple[str, Optional[str]]], is_self_closing: bool = False):
        attr_dict = {}
        event_items = []
        v_model = None

        raw_attr_parts = []
        for name, value in attrs:
            if value is None:
                value = ''
                raw_attr_parts.append(name)
            else:
                raw_attr_parts.append(f'{name}="{value}"')

            attr_dict[name] = value

            # Vue events: @click, @click.prevent, @keyup.enter
            if name.startswith('@'):
                event_type = name[1:].split('.')[0]
                event_items.append((event_type, value))
            # v-on:click
            elif name.startswith('v-on:'):
                event_type = name[5:].split('.')[0]
                event_items.append((event_type, value))
            # v-model
            elif name == 'v-model':
                v_model = value

        attr_str = ' '.join(raw_attr_parts)
        element_text = ' '.join(self._current_text).strip() or None

        for event_type, handler in event_items:
            selector = self.selector_fn(tag, attr_str, element_text, None)
            self.events.append({
                'event_type': event_type,
                'handler': handler,
                'selector': selector,
                'element_tag': tag,
                'element_text': element_text,
            })

        if v_model is not None:
            self.inputs.append(v_model)

    def reset_state(self):
        self.events = []
        self.inputs = []
        self._current_tag_stack = []
        self._current_text = []


def parse_vue_template_with_htmlparser(
    template: str,
    selector_fn: Callable,
) -> Tuple[List[dict], List[str]]:
    """解析 Vue 模板，返回 (events, inputs)"""
    parser = VueTemplateHTMLParser(selector_fn)
    try:
        parser.feed(template)
        return parser.events, parser.inputs
    except Exception as e:
        logger.warning('[增强解析器] html.parser 解析失败: %s，回退到空结果', e)
        return [], []
    finally:
        parser.reset_state()


# ============================================================
# P1: @babel/parser for React JSX (via Node.js subprocess)
# ============================================================

_BABEL_BOOTSTRAP = '''
try {
  const babel = require('@babel/parser');
  const input = JSON.parse(process.argv[1]);

  const ast = babel.parse(input.code, {
    sourceType: 'module',
    plugins: ['jsx', 'typescript', 'decorators-legacy', 'optionalChaining', 'nullishCoalescingOperator']
  });

  const events = [];
  const inputs = [];

  function walkNode(node, tagStack = []) {
    if (!node || typeof node !== 'object') return;

    // JSXElement
    if (node.type === 'JSXElement') {
      const tag = node.openingElement.name.name ||
                  (node.openingElement.name.object ?
                    node.openingElement.name.object.name + '.' + node.openingElement.name.property.name :
                    'component');

      const attrs = {};
      const rawAttrs = [];

      for (const attr of node.openingElement.attributes) {
        if (attr.type !== 'JSXAttribute') continue;
        const name = attr.name.name || attr.name?.object?.name + '.' + attr.name?.property?.name;
        let value = '';

        if (attr.value === null) {
          value = '';
        } else if (attr.value.type === 'StringLiteral') {
          value = attr.value.value;
        } else if (attr.value.type === 'JSXExpressionContainer') {
          // Extract expression - could be arrow function, variable, ternary, etc.
          const expr = attr.value.expression;
          if (expr.type === 'ArrowFunctionExpression' || expr.type === 'FunctionExpression') {
            value = '{arrow function}';
          } else if (expr.type === 'Identifier') {
            value = expr.name;
          } else if (expr.type === 'ConditionalExpression') {
            value = '{ternary}';
          } else if (expr.type === 'MemberExpression') {
            value = expr.object.name + '.' + expr.property.name;
          } else {
            value = '{expression}';
          }
        }

        attrs[name] = value;
        rawAttrs.push(name + '="' + value + '"');

        // React events: onClick, onChange, onSubmit
        if (name.startsWith('on') && name.length > 2 && name[2] === name[2].toUpperCase()) {
          const eventType = name[2].toLowerCase() + name.slice(3);
          events.push({
            event_type: eventType,
            handler: value,
            selector: '',
            element_tag: tag,
            element_text: ''
          });
        }
      }

      // Extract text from children
      let text = '';
      if (node.children) {
        for (const child of node.children) {
          if (child.type === 'JSXText') {
            const t = child.value.trim();
            if (t) text = t;
          }
        }
      }
      if (events.length > 0 && events[events.length-1].element_tag === tag) {
        events[events.length-1].element_text = text;
      }

      // Recursively walk children
      if (node.children) {
        for (const child of node.children) {
          walkNode(child, [...tagStack, tag]);
        }
      }
    }

    // Recurse into common node types
    for (const key of ['body', 'declarations', 'init', 'arguments', 'callee',
                       'consequent', 'alternate', 'test', 'block', 'handler',
                       'expression', 'left', 'right', 'properties', 'value',
                       'elements', 'children']) {
      if (Array.isArray(node[key])) {
        for (const child of node[key]) walkNode(child, tagStack);
      } else if (node[key] && typeof node[key] === 'object') {
        walkNode(node[key], tagStack);
      }
    }
  }

  walkNode(ast);
  console.log(JSON.stringify({ events, inputs }));

} catch (e) {
  console.error(JSON.stringify({ error: e.message, stack: e.stack }));
  process.exit(1);
}
'''


def parse_jsx_with_babel(code: str) -> Tuple[List[dict], List[str]]:
    """使用 @babel/parser（Node.js）解析 React JSX 组件。

    返回 (events, inputs)。
    如果 @babel/parser 不可用，返回空列表。
    """
    try:
        result = subprocess.run(
            ['node', '-e', _BABEL_BOOTSTRAP, json.dumps({'code': code})],
            capture_output=True,
            text=True,
            timeout=15,
        )
        if result.returncode != 0:
            err = result.stderr.strip()
            logger.warning('[Babel] 解析失败: %s', err[:200])
            return [], []

        data = json.loads(result.stdout)
        return data.get('events', []), data.get('inputs', [])

    except FileNotFoundError:
        logger.warning('[Babel] Node.js 未安装，回退到正则解析')
        return [], []
    except subprocess.TimeoutExpired:
        logger.warning('[Babel] 解析超时（15s），回退到正则解析')
        return [], []
    except json.JSONDecodeError as e:
        logger.warning('[Babel] 输出解析失败: %s', e)
        return [], []
    except Exception as e:
        logger.warning('[Babel] 未知错误: %s', e)
        return [], []


# ============================================================
# P2: Vue <script setup> data property extraction
# ============================================================

def extract_script_properties(script_content: str) -> List[str]:
    """从 Vue <script setup> 中提取 data properties（reactive ref 等）。

    简单正则提取，不依赖 AST，覆盖常见模式。
    """
    props = []
    patterns = [
        r'(?:const|let|var)\s+(\w+)\s*=\s*ref\s*\(\s*',
        r'(?:const|let|var)\s+(\w+)\s*=\s*reactive\s*\(\s*\{',
        r'(?:const|let|var)\s+\{([^}]+)\}\s*=\s*reactive\s*\(\s*',
        r'(?:const|let|var)\s+(\w+)\s*=\s*computed\s*\(\s*',
    ]
    for pattern in patterns:
        for m in re.finditer(pattern, script_content):
            value = m.group(1).strip()
            if '{' in value:
                # Destructured: { a, b } = reactive(...)
                for part in value.split(','):
                    p = part.strip().lstrip('{').rstrip('}')
                    if p:
                        props.append(p.split(':')[0].strip())
            else:
                props.append(value)

    return list(set(props))


def parse_script_setup(content: str) -> dict:
    """提取 Vue <script setup> 中的定义信息。

    返回: {
        'imports': [...],
        'props': [...],
        'data_properties': [...],
        'methods': [...],
        'emits': [...]
    }
    """
    result = {
        'imports': [],
        'props': [],
        'data_properties': [],
        'methods': [],
        'emits': [],
    }

    # 提取 <script setup> 块
    script_match = re.search(
        r'<script\s+setup[^>]*>(.*?)</script>',
        content,
        re.DOTALL,
    )
    if not script_match:
        return result

    code = script_match.group(1)

    # data properties
    result['data_properties'] = extract_script_properties(code)

    # 提取 defineProps
    props_match = re.search(r'defineProps\s*<([^>]+)>', code)
    if props_match:
        for m in re.finditer(r'(\w+)\s*[?:]', props_match.group(1)):
            result['props'].append(m.group(1))

    # 提取 defineEmits
    emits_match = re.search(r'defineEmits\s*<[^>]+>', code)
    if emits_match:
        for m in re.finditer(r"['\"](\w+)['\"]", emits_match.group(0)):
            result['emits'].append(m.group(1))

    # 提取函数定义（methods）
    for m in re.finditer(r'(?:const|function)\s+(\w+)\s*[=\(]', code):
        name = m.group(1)
        if name not in ['ref', 'reactive', 'computed', 'watch', 'defineProps', 'defineEmits']:
            result['methods'].append(name)

    return result


# ============================================================
# P3: Safe parsing wrapper
# ============================================================

def safe_parse_vue(file_path: str, selector_fn: Callable) -> Tuple[List[dict], List[str], List[str]]:
    """安全解析 Vue 文件，任何失败都回退而不是崩溃。

    Args:
        file_path: .vue 文件路径
        selector_fn: selector 生成函数

    Returns:
        (events, inputs, data_properties)
    """
    events = []
    inputs = []
    data_props = []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        logger.error('[增强解析器] 文件读取失败 %s: %s', file_path, e)
        return events, inputs, data_props

    # 1. 解析 <script setup>
    try:
        script_info = parse_script_setup(content)
        data_props = script_info.get('data_properties', [])
    except Exception as e:
        logger.warning('[增强解析器] script setup 解析失败: %s', e)

    # 2. 提取 <template>
    template_match = re.search(r'<template>(.*?)</template>', content, re.DOTALL)
    if not template_match:
        logger.warning('[增强解析器] 未找到 <template>')
        return events, inputs, data_props

    template = template_match.group(1).strip()

    # 3. 用 html.parser 解析 template
    events, inputs = parse_vue_template_with_htmlparser(template, selector_fn)

    return events, inputs, data_props


def safe_parse_react(file_path: str, selector_fn: Callable) -> Tuple[List[dict], List[str]]:
    """安全解析 React 文件，@babel/parser 优先，正则回退。

    Returns:
        (events, state_vars)
    """
    events = []
    state_vars = []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        logger.error('[增强解析器] 文件读取失败 %s: %s', file_path, e)
        return events, state_vars

    # 先用 Babel 解析
    babel_events, _ = parse_jsx_with_babel(content)
    if babel_events:
        return babel_events, state_vars

    # Babel 不可用或失败，返回空（让调用方用正则回退）
    return events, state_vars


# ============================================================
# 自测
# ============================================================

if __name__ == '__main__':
    print("=== P0: html.parser Edge Case Test ===\n")

    def dummy_selector(tag, attrs, text, template):
        return f"locator('{tag}')"

    cases = [
        '<button @click="handleClick">Submit</button>',
        '<a title="Score: 80 > 60" @click="handleClick">Compare</a>',
        '<button\n  v-if="count > 0"\n  @click="handleClick">Click</button>',
        '<input v-model="formData.username" type="text" />',
        '<input disabled @change="handleChange" />',
        '<a @click.stop.prevent="onSave" href="#">Save</a>',
    ]

    for code in cases:
        events, inputs = parse_vue_template_with_htmlparser(code, dummy_selector)
        status = 'OK' if events or inputs else 'EMPTY'
        print(f'  [{status}] {code[:60]}...')
        for e in events:
            print(f'    event={e["event_type"]} handler={e["handler"]}')
        for i in inputs:
            print(f'    v-model={i}')

    print("\n=== P2: Script Setup Test ===\n")
    test_setup = '''
    <script setup lang="ts">
    import { ref, reactive, computed } from 'vue'
    const username = ref('')
    const password = ref('')
    const formData = reactive({
        username: '',
        password: ''
    })
    const fullName = computed(() => '')
    const handleSubmit = () => {}
    const handleReset = () => {}
    </script>
    '''
    info = parse_script_setup(f'<template></template>\n{test_setup}')
    print(f'  data_properties: {info["data_properties"]}')
    print(f'  methods: {info["methods"]}')
    print(f'  props: {info["props"]}')
    print(f'  emits: {info["emits"]}')

    print("\n=== All Tests Complete ===")
