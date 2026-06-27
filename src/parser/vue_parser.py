"""
Vue 组件解析器
解析 .vue 文件，提取模板中的交互元素和事件绑定
支持 v-if, v-for, v-model, 动态绑定等 Vue 特性
使用 html.parser 支持复杂嵌套结构（插槽、teleport、v-for 等）
"""

from typing import List, Dict, Any, Optional
import re
import os
from html.parser import HTMLParser
from dataclasses import dataclass, field


@dataclass
class VueDirective:
    """Vue 指令信息"""
    name: str  # v-if, v-for, v-model 等
    value: str  # 指令值
    argument: Optional[str] = None  # v-on:click 中的 click
    modifiers: List[str] = field(default_factory=list)  # .prevent, .stop 等


@dataclass
class VueElement:
    """Vue 模板中的交互元素"""
    tag: str
    attributes: Dict[str, str] = field(default_factory=dict)
    events: Dict[str, str] = field(default_factory=dict)
    text_content: str = ""
    data_testid: Optional[str] = None
    directives: List[VueDirective] = field(default_factory=list)
    v_model: Optional[str] = None  # v-model 绑定的变量
    v_if: Optional[str] = None  # v-if / v-else-if 条件
    v_for: Optional[Dict[str, str]] = None  # v-for 信息
    computed_props: List[str] = field(default_factory=list)  # :prop 动态绑定的属性
    # 语义信息（新增）
    semantic_name: str = ""  # 语义名称，如 "username_input", "login_button"
    primary_action: str = ""  # 主要操作，如 "fill", "click"


@dataclass
class VueComponent:
    """Vue 组件信息"""
    name: str
    elements: List[VueElement] = field(default_factory=list)
    props: List[Dict[str, Any]] = field(default_factory=list)
    emits: List[str] = field(default_factory=list)
    data_properties: List[str] = field(default_factory=list)
    methods: List[str] = field(default_factory=list)
    computed: List[str] = field(default_factory=list)


# 可交互元素白名单（包含标准 HTML 元素和常见 Vue 组件）
INTERACTIVE_TAGS = {
    # 标准 HTML 交互元素
    'button', 'input', 'a', 'select', 'textarea', 'form',
    # 常见交互容器（有事件绑定时）
    'div', 'span', 'li', 'tr', 'td',
    # Vue Router 组件
    'router-link', 'router-view',
    # Element Plus 组件
    'el-button', 'el-input', 'el-select', 'el-form', 'el-dialog',
    # Ant Design Vue 组件
    'a-button', 'a-input', 'a-select', 'a-form', 'a-modal',
}


class VueTemplateParser(HTMLParser):
    """Vue 模板解析器 - 基于 html.parser 支持嵌套结构"""

    def __init__(self):
        super().__init__()
        self.elements: List[VueElement] = []
        self._tag_stack: List[Dict] = []  # 标签栈，用于跟踪嵌套结构
        self._current_text: List[str] = []  # 当前标签内的文本

        # 编译正则表达式
        self.event_pattern = re.compile(r'@(\w+)(?:\.(\w+))?(?:\.(\w+))?="([^"]*)"')
        self.v_on_pattern = re.compile(r'v-on:(\w+)(?:\.(\w+))?="([^"]*)"')
        self.attr_pattern = re.compile(r'([\w:-]+)="([^"]*)"')
        self.v_model_pattern = re.compile(r'v-model(?:\.(\w+))?="([^"]*)"')
        self.v_if_pattern = re.compile(r'v-(?:else-if|if)="([^"]*)"')
        self.v_for_pattern = re.compile(r'v-for="([^"]*)"')
        self.bind_pattern = re.compile(r'(?::|v-bind:)([\w-]+)="([^"]*)"')

    def handle_starttag(self, tag: str, attrs: List[tuple]):
        """处理开始标签"""
        # 将属性列表转换为字典
        attrs_dict = dict(attrs)
        attrs_str = ' '.join(f'{k}="{v}"' for k, v in attrs)

        # 压入标签栈（先压栈，确保文本收集到正确的标签）
        self._tag_stack.append({
            'tag': tag.lower(),
            'text_parts': [],
            'attrs_dict': attrs_dict,
            'attrs_str': attrs_str,
            'is_interactive': tag.lower() in INTERACTIVE_TAGS and self._has_interaction(attrs_dict)
        })

    def handle_startendtag(self, tag: str, attrs: List[tuple]):
        """处理自闭合标签（如 <input />）"""
        # 将属性列表转换为字典
        attrs_dict = dict(attrs)
        attrs_str = ' '.join(f'{k}="{v}"' for k, v in attrs)

        # 检查是否是可交互元素
        if tag.lower() in INTERACTIVE_TAGS and self._has_interaction(attrs_dict):
            element = self._parse_element(tag.lower(), attrs_dict, attrs_str, [])
            self.elements.append(element)

    def handle_endtag(self, tag: str):
        """处理结束标签"""
        # 弹出标签栈并处理交互元素
        if self._tag_stack:
            tag_info = self._tag_stack.pop()
            
            # 如果是交互元素，在结束标签时创建元素（此时文本已收集完毕）
            if tag_info.get('is_interactive'):
                element = self._parse_element(
                    tag.lower(),
                    tag_info['attrs_dict'],
                    tag_info['attrs_str'],
                    tag_info['text_parts']
                )
                self.elements.append(element)

    def handle_data(self, data: str):
        """处理文本数据"""
        # 收集文本内容（忽略纯空白）
        text = data.strip()
        if text and self._tag_stack:
            self._tag_stack[-1]['text_parts'].append(text)

    def _has_interaction(self, attrs: Dict[str, str]) -> bool:
        """检查元素是否有交互性"""
        for key in attrs.keys():
            if key.startswith('@') or key.startswith('v-on:'):
                return True
            if key in ('href', 'type', 'name'):
                return True
        return False

    def _parse_element(self, tag: str, attrs: Dict[str, str], attrs_str: str, text_parts: List[str] = None) -> VueElement:
        """解析单个元素"""
        # 提取普通属性（排除 Vue 特殊属性）
        attributes = {}
        for key, value in attrs.items():
            if not key.startswith('@') and not key.startswith(':') and not key.startswith('v-'):
                attributes[key] = value

        # 提取事件（支持 @ 和 v-on: 两种语法）
        events = {}
        # @click 语法
        for match in self.event_pattern.finditer(attrs_str):
            event_name = match.group(1)
            modifier1 = match.group(2)
            modifier2 = match.group(3)
            event_handler = match.group(4)

            # 处理修饰符
            modifiers = [m for m in [modifier1, modifier2] if m]
            if modifiers:
                event_name = f"{event_name}.{'.'.join(modifiers)}"

            events[event_name] = event_handler

        # v-on:click 语法
        for match in self.v_on_pattern.finditer(attrs_str):
            event_name = match.group(1)
            modifier = match.group(2)
            event_handler = match.group(3)

            if modifier:
                event_name = f"{event_name}.{modifier}"

            events[event_name] = event_handler

        # 获取 data-testid
        data_testid = attrs.get('data-testid')

        # 解析 v-model
        v_model = None
        v_model_match = self.v_model_pattern.search(attrs_str)
        if v_model_match:
            v_model = v_model_match.group(2)

        # 解析 v-if / v-else-if
        v_if = None
        v_if_match = self.v_if_pattern.search(attrs_str)
        if v_if_match:
            v_if = v_if_match.group(1)

        # 解析 v-for
        v_for = None
        v_for_match = self.v_for_pattern.search(attrs_str)
        if v_for_match:
            v_for_str = v_for_match.group(1)
            # 解析 v-for="item in items" 或 v-for="(item, index) in items"
            for_match = re.match(r'\((\w+),\s*(\w+)\)\s+in\s+(\w+)', v_for_str)
            if for_match:
                v_for = {
                    'item': for_match.group(1),
                    'index': for_match.group(2),
                    'collection': for_match.group(3)
                }
            else:
                simple_match = re.match(r'(\w+)\s+in\s+(\w+)', v_for_str)
                if simple_match:
                    v_for = {
                        'item': simple_match.group(1),
                        'collection': simple_match.group(2)
                    }

        # 解析动态属性绑定
        computed_props = []
        for match in self.bind_pattern.finditer(attrs_str):
            computed_props.append(match.group(1))

        # 获取文本内容（从参数中获取）
        text_content = ' '.join(text_parts).strip() if text_parts else ''

        # 构建指令列表
        directives = []
        if v_model:
            directives.append(VueDirective(name='v-model', value=v_model))
        if v_if:
            directives.append(VueDirective(name='v-if', value=v_if))
        if v_for:
            directives.append(VueDirective(name='v-for', value=str(v_for)))

        element = VueElement(
            tag=tag,
            attributes=attributes,
            events=events,
            text_content=text_content.strip(),
            data_testid=data_testid,
            directives=directives,
            v_model=v_model,
            v_if=v_if,
            v_for=v_for,
            computed_props=computed_props
        )

        # 提取语义信息
        self._extract_semantic_info(element)

        return element

    def _extract_semantic_info(self, element: VueElement):
        """提取元素的语义信息"""
        # 1. 语义名称：优先使用有意义的属性
        if element.data_testid:
            element.semantic_name = element.data_testid
        elif element.attributes.get('aria-label'):
            element.semantic_name = element.attributes['aria-label']
        elif element.attributes.get('placeholder'):
            element.semantic_name = element.attributes['placeholder']
        elif element.text_content:
            element.semantic_name = element.text_content
        else:
            element.semantic_name = element.tag

        # 2. 主要操作：根据元素类型推断
        if element.tag == 'input':
            input_type = element.attributes.get('type', 'text')
            if input_type in ['checkbox', 'radio']:
                element.primary_action = 'check'
            else:
                element.primary_action = 'fill'
        elif element.tag in ['button', 'a']:
            element.primary_action = 'click'
        elif element.tag == 'form':
            element.primary_action = 'submit'
        else:
            # 使用第一个事件的基础名称
            first_event = list(element.events.keys())[0] if element.events else 'click'
            element.primary_action = first_event.split('.')[0]


class VueParser:
    """Vue 组件解析器"""

    def __init__(self):
        pass

    def parse_file(self, file_path: str) -> VueComponent:
        """解析 Vue 文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return self.parse_content(content, file_path)

    def parse_content(self, content: str, file_name: str = "") -> VueComponent:
        """解析 Vue 文件内容"""
        # 提取组件名（兼容 Windows 和 Unix 路径分隔符）
        name = os.path.basename(file_name).replace('.vue', '') if file_name else "Unknown"

        # 提取 template 部分 - 使用更精确的匹配，找到最外层的 <template>
        # 先找到第一个 <template> 的位置
        template_start = content.find('<template>')
        if template_start == -1:
            template_content = ""
        else:
            # 从 <template> 之后开始，找到对应的 </template>
            # 需要计算嵌套深度来找到正确的结束位置
            search_start = template_start + len('<template>')
            depth = 1
            pos = search_start
            template_content = ""
            while depth > 0 and pos < len(content):
                # 查找下一个 <template 或 </template>
                next_open = content.find('<template', pos)
                next_close = content.find('</template>', pos)
                
                if next_close == -1:
                    # 没有找到闭合标签，取剩余内容
                    template_content = content[search_start:]
                    break
                
                if next_open != -1 and next_open < next_close:
                    # 先遇到开标签，深度+1
                    depth += 1
                    pos = next_open + len('<template')
                else:
                    # 遇到闭标签，深度-1
                    depth -= 1
                    if depth == 0:
                        template_content = content[search_start:next_close]
                    else:
                        pos = next_close + len('</template>')

        # 提取 script 部分
        script_match = re.search(r'<script[^>]*>(.*?)</script>', content, re.DOTALL)
        script_content = script_match.group(1) if script_match else ""

        # 预处理 template 内容：将 Vue 的 <template> 标签替换为 <vue-template>
        # 这样 html.parser 就不会误认为模板结束
        template_content = re.sub(r'<template([^>]*)>', r'<vue-template\1>', template_content)
        template_content = template_content.replace('</template>', '</vue-template>')

        # 使用 html.parser 提取交互元素
        parser = VueTemplateParser()
        parser.feed(template_content)
        elements = parser.elements

        # 提取组件元信息
        props = self._extract_props(script_content)
        emits = self._extract_emits(script_content)
        data_properties = self._extract_data_properties(script_content)
        methods = self._extract_methods(script_content)
        computed = self._extract_computed(script_content)

        return VueComponent(
            name=name,
            elements=elements,
            props=props,
            emits=emits,
            data_properties=data_properties,
            methods=methods,
            computed=computed
        )

    def _extract_props(self, script: str) -> List[Dict[str, Any]]:
        """提取组件 props 定义"""
        props = []

        # defineProps TypeScript 语法
        props_match = re.search(r'defineProps<\{([^}]+)\}>', script, re.DOTALL)
        if props_match:
            props_content = props_match.group(1)
            for line in props_content.split('\n'):
                line = line.strip()
                if not line or line.startswith('//'):
                    continue
                prop_match = re.match(r'(\w+)(\??):\s*(\w+)', line)
                if prop_match:
                    props.append({
                        'name': prop_match.group(1),
                        'required': prop_match.group(2) != '?',
                        'type': prop_match.group(3)
                    })

        # Options API props
        props_obj_match = re.search(r'props:\s*\{([^}]+)\}', script, re.DOTALL)
        if props_obj_match:
            props_content = props_obj_match.group(1)
            for line in props_content.split('\n'):
                line = line.strip()
                if ':' in line and not line.startswith('//'):
                    prop_name = line.split(':')[0].strip()
                    props.append({'name': prop_name, 'type': 'any'})

        return props

    def _extract_emits(self, script: str) -> List[str]:
        """提取组件 emits 定义"""
        emits = []

        # defineEmits TypeScript 语法
        emits_match = re.search(r'defineEmits<\{([^}]+)\}>', script, re.DOTALL)
        if emits_match:
            emits_content = emits_match.group(1)
            emit_matches = re.findall(r"'(\w+)'|\"(\w+)\"", emits_content)
            for m in emit_matches:
                emits.append(m[0] or m[1])

        # Options API emits
        emits_arr_match = re.search(r'emits:\s*\[([^\]]+)\]', script)
        if emits_arr_match:
            emits_content = emits_arr_match.group(1)
            for m in re.findall(r"'(\w+)'|\"(\w+)\"", emits_content):
                emits.append(m[0] or m[1])

        return emits

    def _extract_data_properties(self, script: str) -> List[str]:
        """提取 data 属性（Composition API ref/reactive）"""
        properties = []

        # ref 定义
        for match in re.finditer(r'const\s+(\w+)\s*=\s*ref', script):
            properties.append(match.group(1))

        # reactive 属性
        for match in re.finditer(r'const\s+(\w+)\s*=\s*reactive', script):
            properties.append(match.group(1))

        return properties

    def _extract_methods(self, script: str) -> List[str]:
        """提取方法定义"""
        methods = []

        # const fn = () => 或 function fn()
        for match in re.finditer(r'(?:const\s+(\w+)\s*=\s*(?:async\s+)?\(|function\s+(\w+))', script):
            methods.append(match.group(1) or match.group(2))

        return methods

    def _extract_computed(self, script: str) -> List[str]:
        """提取 computed 属性"""
        computed = []

        # computed(() => 或 computed({
        for match in re.finditer(r'const\s+(\w+)\s*=\s*computed', script):
            computed.append(match.group(1))

        return computed
