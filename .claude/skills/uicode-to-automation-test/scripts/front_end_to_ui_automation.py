"""
Vue to Playwright Test Generator

解析Vue组件代码，自动生成Playwright场景化UI自动化测试用例。
"""

import re
import os
from dataclasses import dataclass, field
from html.parser import HTMLParser
from typing import Optional, Dict, List
from pathlib import Path

CHINESE_TO_ENGLISH = {
    '登录': 'login',
    '重置': 'reset',
    '提交': 'submit',
    '取消': 'cancel',
    '确认': 'confirm',
    '保存': 'save',
    '删除': 'delete',
    '编辑': 'edit',
    '添加': 'add',
    '搜索': 'search',
    '查询': 'query',
    '注册': 'register',
    '退出': 'logout',
    '返回': 'back',
    '下一步': 'next',
    '上一步': 'previous',
    '完成': 'finish',
    '关闭': 'close',
    '打开': 'open',
    '发送': 'send',
    '接收': 'receive',
    '下载': 'download',
    '上传': 'upload',
    '导入': 'import',
    '导出': 'export',
    '复制': 'copy',
    '粘贴': 'paste',
    '剪切': 'cut',
    '撤销': 'undo',
    '重做': 'redo',
    '刷新': 'refresh',
    '加载': 'load',
    '清除': 'clear',
    '过滤': 'filter',
    '排序': 'sort',
    '分组': 'group',
    '展开': 'expand',
    '折叠': 'collapse',
    '选择': 'select',
    '取消选择': 'deselect',
    '全选': 'selectAll',
    '反选': 'invertSelection',
    '用户名': 'username',
    '密码': 'password',
    '邮箱': 'email',
    '手机': 'phone',
    '姓名': 'name',
    '地址': 'address',
    '标题': 'title',
    '内容': 'content',
    '描述': 'description',
    '备注': 'remark',
    '状态': 'status',
    '类型': 'type',
    '分类': 'category',
    '标签': 'tag',
    '日期': 'date',
    '时间': 'time',
    '开始': 'start',
    '结束': 'end',
    '创建': 'create',
    '更新': 'update',
    '修改': 'modify',
    '查看': 'view',
    '详情': 'detail',
    '列表': 'list',
    '表格': 'table',
    '表单': 'form',
    '按钮': 'button',
    '输入': 'input',
    '选择框': 'select',
    '复选框': 'checkbox',
    '单选框': 'radio',
    '下拉': 'dropdown',
    '菜单': 'menu',
    '导航': 'navigation',
    '侧边栏': 'sidebar',
    '头部': 'header',
    '底部': 'footer',
    '主体': 'main',
    '容器': 'container',
    '卡片': 'card',
    '弹窗': 'modal',
    '对话框': 'dialog',
    '提示': 'tooltip',
    '警告': 'alert',
    '错误': 'error',
    '成功': 'success',
    '信息': 'info',
    '帮助': 'help',
    '忘记密码': 'forgotPassword',
    '记住我': 'rememberMe',
    '微信登录': 'wechatLogin',
    'QQ登录': 'qqLogin',
    '用户登录': 'userLogin',
    '忘记密码？': 'forgotPassword',
    '请输入': 'input',
    '请输入用户名': 'inputUsername',
    '请输入密码': 'inputPassword',
}


def translate_to_english(text: str) -> str:
    if text in CHINESE_TO_ENGLISH:
        return CHINESE_TO_ENGLISH[text]
    
    for cn, en in CHINESE_TO_ENGLISH.items():
        if cn in text:
            text = text.replace(cn, en)
    
    text = re.sub(r'[^\w]', '', text)
    
    if text and text[0].isupper():
        return text[0].lower() + text[1:] if len(text) > 1 else text.lower()
    
    return text.lower() if text else 'element'


def to_kebab_case(text: str) -> str:
    """转换为kebab-case命名格式（如：login-form）"""
    text = re.sub(r'([A-Z])', r'-\1', text)
    text = text.lower().strip('-')
    text = re.sub(r'-+', '-', text)
    return text


def to_snake_case(text: str) -> str:
    """转换为snake_case命名格式（如：login_form）"""
    text = re.sub(r'([A-Z])', r'_\1', text)
    text = text.lower().strip('_')
    text = re.sub(r'_+', '_', text)
    return text


def to_pascal_case(text: str) -> str:
    """转换为PascalCase命名格式（如：LoginForm）"""
    if not text:
        return text
    
    if re.match(r'^[A-Z][a-zA-Z0-9]*$', text):
        return text
    
    words = re.split(r'[-_\s]+', text)
    result = []
    for word in words:
        if word:
            if re.match(r'^[A-Z][a-zA-Z0-9]*$', word):
                result.append(word)
            elif re.match(r'^[a-z][a-zA-Z0-9]*$', word):
                result.append(word[0].upper() + word[1:])
            else:
                result.append(word.capitalize())
    return ''.join(result)


def to_camel_case(text: str) -> str:
    """转换为camelCase命名格式（如：loginForm）"""
    if not text:
        return text
    
    if re.match(r'^[a-z][a-zA-Z0-9]*$', text):
        return text
    
    pascal = to_pascal_case(text)
    return pascal[0].lower() + pascal[1:] if pascal else text


@dataclass
class VueEvent:
    event_type: str
    handler: str
    selector: str
    element_tag: str
    element_text: Optional[str] = None


@dataclass
class VueComponent:
    name: str
    file_path: str
    events: list = field(default_factory=list)
    inputs: list = field(default_factory=list)


@dataclass
class RouteConfig:
    path: str
    name: str
    component: str
    requires_auth: bool = False


@dataclass
class PiniaStore:
    name: str
    file_path: str
    state: dict = field(default_factory=dict)
    getters: list = field(default_factory=list)
    actions: list = field(default_factory=list)


@dataclass
class ReactEvent:
    event_type: str
    handler: str
    selector: str
    element_tag: str
    element_text: Optional[str] = None


@dataclass
class ReactComponent:
    name: str
    file_path: str
    events: list = field(default_factory=list)
    inputs: list = field(default_factory=list)


@dataclass
class ReduxReducer:
    name: str
    file_path: str
    initial_state: dict = field(default_factory=dict)
    actions: list = field(default_factory=list)


@dataclass
class BAWStep:
    """BAW中的单个步骤"""
    pom_class: str
    method: str
    parameters: dict = field(default_factory=dict)


@dataclass
class BAWConfig:
    """BAW配置"""
    name: str
    component_name: str
    description: str
    steps: list = field(default_factory=list)
    parameters: list = field(default_factory=list)  # [{name: str, type: str, default: str}]

class VueTemplateHTMLParser(HTMLParser):
    """基于 html.parser 的 Vue 模板解析器。

    替换原有的正则解析，修复以下场景：
    - 属性值中的 > 字符（如 title="a > b"）
    - 多行属性（如 v-if="count > 0"）
    - 布尔属性（如 <input disabled>）
    - 事件修饰符（如 @click.stop.prevent → click）
    """

    def __init__(self, selector_fn, events_config):
        super().__init__(convert_charrefs=True)
        self.selector_fn = selector_fn
        self.events_config = events_config
        self.events = []
        self.inputs = []
        self._tag_stack = []
        self._text_buffer = []

    def handle_starttag(self, tag, attrs):
        self._process_tag(tag, attrs)
        self._tag_stack.append(tag)
        self._text_buffer = []

    def handle_endtag(self, tag):
        if self._tag_stack and self._tag_stack[-1] == tag:
            self._tag_stack.pop()
        self._text_buffer = []

    def handle_startendtag(self, tag, attrs):
        self._process_tag(tag, attrs, is_self_closing=True)

    def handle_data(self, data):
        text = data.strip()
        if text and self._tag_stack:
            self._text_buffer.append(text)

    def _process_tag(self, tag, attrs, is_self_closing=False):
        attr_parts = []
        for name, value in attrs:
            if value is None:
                value = ''
                attr_parts.append(name)
            else:
                attr_parts.append(f'{name}="{value}"')

        attr_str = ' '.join(attr_parts)
        element_text = ' '.join(self._text_buffer).strip() or None
        event_items = []
        v_model = None

        for name, value in attrs:
            if value is None:
                value = ''
            if name.startswith('@'):
                event_type = name[1:].split('.')[0]
                event_items.append((event_type, value))
            elif name.startswith('v-on:'):
                event_type = name[5:].split('.')[0]
                event_items.append((event_type, value))
            elif name == 'v-model':
                v_model = value

        for event_type, handler in event_items:
            selector = self.selector_fn(tag, attr_str, element_text, None)
            self.events.append(VueEvent(
                event_type=event_type,
                handler=handler,
                selector=selector,
                element_tag=tag,
                element_text=element_text,
            ))

        if v_model is not None:
            self.inputs.append(v_model)

    def feed_and_get(self, template: str):
        """解析模板并返回 (events, inputs)"""
        self.events = []
        self.inputs = []
        self._tag_stack = []
        self._text_buffer = []
        self.feed(template)
        return self.events, self.inputs


class VueParser:
    EVENT_PATTERN = re.compile(r'@(\w+)(?:\.\w+)*\s*=\s*["\']([^"\']+)["\']')
    V_MODEL_PATTERN = re.compile(r'v-model\s*=\s*["\']([^"\']+)["\']')
    ELEMENT_PATTERN = re.compile(r'<(\w+)([^>]*)>([^<]*)?</\1>|<(\w+)([^>]*)/?>', re.DOTALL)
    TAG_PATTERN = re.compile(r'<(\w+)([^>]*)>')
    TEXT_CONTENT_PATTERN = re.compile(r'>([^<]+)<')

    def __init__(self):
        self.events_config = {
            'click': {'action': 'click', 'description': '点击'},
            'input': {'action': 'fill', 'description': '输入'},
            'change': {'action': 'check', 'description': '选择'},
            'blur': {'action': 'blur', 'description': '失焦'},
            'focus': {'action': 'focus', 'description': '聚焦'},
            'submit': {'action': 'click', 'description': '提交'},
            'dblclick': {'action': 'dblclick', 'description': '双击'},
            'mouseenter': {'action': 'hover', 'description': '鼠标悬停'},
            'mouseleave': {'action': 'hover', 'description': '鼠标离开'},
        }

    def parse_router(self, router_file: str) -> list:
        """解析Vue Router配置文件"""
        with open(router_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        routes = []
        
        # 提取routes数组
        routes_match = re.search(r'const routes = \[(.*?)\]', content, re.DOTALL)
        if routes_match:
            routes_content = routes_match.group(1)
            
            # 提取每个路由配置
            route_pattern = re.compile(r'\{[^\}]*path:\s*["\']([^"\']+)["\'][^\}]*name:\s*["\']([^"\']+)["\'][^\}]*component:\s*([^,\}]+)[^\}]*\}', re.DOTALL)
            
            for match in route_pattern.finditer(routes_content):
                path = match.group(1)
                name = match.group(2)
                component = match.group(3).strip()
                
                # 提取requiresAuth
                requires_auth = False
                auth_match = re.search(r'requiresAuth:\s*(true|false)', match.group(0))
                if auth_match:
                    requires_auth = auth_match.group(1) == 'true'
                
                routes.append(RouteConfig(
                    path=path,
                    name=name,
                    component=component,
                    requires_auth=requires_auth
                ))
        
        return routes

    def parse_pinia_store(self, store_file: str) -> list:
        """解析Pinia store文件"""
        with open(store_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        stores = []
        
        # 提取所有defineStore调用
        # 使用更可靠的方法来处理嵌套的大括号
        store_pattern = re.compile(r'defineStore\(["\']([^"\']+)["\'],')
        
        # 手动解析每个store
        for match in store_pattern.finditer(content):
            store_name = match.group(1)
            start_pos = match.end()
            
            # 找到store定义的开始
            brace_count = 0
            in_store = False
            store_content = ""
            
            for i in range(start_pos, len(content)):
                char = content[i]
                if char == '{':
                    brace_count += 1
                    in_store = True
                elif char == '}':
                    brace_count -= 1
                    if in_store and brace_count == 0:
                        store_content = content[start_pos:i+1]
                        break
            
            if not store_content:
                continue
            
            # 提取state
            state = {}
            state_match = re.search(r'state:\s*\(\)\s*=>\s*\(([\s\S]+?)\)', store_content)
            if state_match:
                state_content = state_match.group(1)
                # 提取state字段
                state_pattern = re.compile(r'(\w+):\s*([^,]+),', re.DOTALL)
                for state_match in state_pattern.finditer(state_content):
                    key = state_match.group(1)
                    value = state_match.group(2).strip()
                    state[key] = value
            
            # 提取getters
            getters = []
            getters_match = re.search(r'getters:\s*\{([\s\S]+?)\}', store_content)
            if getters_match:
                getters_content = getters_match.group(1)
                getter_pattern = re.compile(r'(\w+):', re.DOTALL)
                for getter_match in getter_pattern.finditer(getters_content):
                    getters.append(getter_match.group(1))
            
            # 提取actions
            actions = []
            actions_match = re.search(r'actions:\s*\{([\s\S]+?)\}', store_content)
            if actions_match:
                actions_content = actions_match.group(1)
                action_pattern = re.compile(r'(\w+)\s*\([^\)]*\)\s*\{', re.DOTALL)
                for action_match in action_pattern.finditer(actions_content):
                    actions.append(action_match.group(1))
            
            stores.append(PiniaStore(
                name=store_name,
                file_path=store_file,
                state=state,
                getters=getters,
                actions=actions
            ))
        
        return stores

    def parse_file(self, file_path: str) -> VueComponent:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        component_name = Path(file_path).stem
        component = VueComponent(name=component_name, file_path=file_path)
        
        template = self._extract_template(content)
        if template:
            component.events = self._extract_events(template)
            component.inputs = self._extract_inputs(template)
        
        return component

    def _extract_template(self, content: str) -> Optional[str]:
        match = re.search(r'<template>(.*?)</template>', content, re.DOTALL)
        return match.group(1).strip() if match else None

    def _extract_events(self, template: str) -> list:
        """使用 html.parser 解析 Vue 模板，提取事件绑定。

        修复正则解析器的已知问题：
        - 属性值含 > （title=\"Score: 80 > 60\"）
        - 多行属性（v-if 跨行）
        - 自闭合组件中的 >
        - 事件修饰符（@click.stop.prevent）
        - 布尔属性（<input disabled>）
        """
        parser = VueTemplateHTMLParser(self._generate_selector, self.events_config)
        events, _ = parser.feed_and_get(template)
        return events

    def _extract_inputs(self, template: str) -> list:
        """提取 v-model 绑定。"""
        parser = VueTemplateHTMLParser(self._generate_selector, self.events_config)
        _, inputs = parser.feed_and_get(template)
        return inputs

    def _generate_selector(self, tag: str, attributes: str, text: Optional[str], template: Optional[str] = None) -> str:
        return self._generate_selector_fallback(tag, attributes, text, template)
    
    def _generate_selector_fallback(self, tag: str, attributes: str, text: Optional[str], template: Optional[str] = None) -> str:
        # 根据Playwright最佳实践，优先使用语义选择器
        
        # 1. 检查data-testid属性（Playwright推荐）
        testid_match = re.search(r'data-testid\s*=\s*["\']([^"\']+)["\']', attributes)
        if testid_match:
            return f"getByTestId('{testid_match.group(1)}')"
        
        # 2. 检查aria-label属性
        aria_label_match = re.search(r'aria-label\s*=\s*["\']([^"\']+)["\']', attributes)
        if aria_label_match:
            aria_label = aria_label_match.group(1)
            role = self._get_element_role(tag, attributes)
            if role:
                return f"getByRole('{role}', {{ name: '{aria_label}' }})"
        
        # 3. 检查元素的role
        role = self._get_element_role(tag, attributes)
        
        # 4. 根据元素类型生成选择器
        if tag == 'button' or role == 'button':
            if text:
                return f"getByRole('button', {{ name: '{text}', exact: true }})"
            # ✅ 优先检查 id/name 属性作为回退定位器
            id_match = re.search(r'id\s*=\s*["\']([^"\']+)["\']', attributes)
            if id_match:
                return f"locator('#{id_match.group(1)}')"
            class_match = re.search(r'class\s*=\s*["\']([^"\']+)["\']', attributes)
            if class_match:
                return f"locator('{tag}.{class_match.group(1).split()[0]}')"
            return f"locator('{tag}')"

        elif tag == 'a':
            if text:
                return f"getByRole('link', {{ name: '{text}' }})"
            # ✅ <a> 无文本时，用 href 或 class 定位
            href_match = re.search(r'href\s*=\s*["\']([^"\']+)["\']', attributes)
            if href_match:
                return f"locator('a[href=\"{href_match.group(1)}\"]')"
            testid_match_link = re.search(r'data-testid\s*=\s*["\']([^"\']+)["\']', attributes)
            if testid_match_link:
                return f"getByTestId('{testid_match_link.group(1)}')"
            return f"locator('a')"
        
        elif tag == 'input':
            input_type_match = re.search(r'type\s*=\s*["\']([^"\']+)["\']', attributes)
            input_type = input_type_match.group(1) if input_type_match else 'text'
            
            # 检查id，尝试通过label关联
            id_match = re.search(r'id\s*=\s*["\']([^"\']+)["\']', attributes)
            if id_match and template:
                element_id = id_match.group(1)
                # 查找关联的label
                label_pattern = re.compile(r'<label[^>]*>(.*?)</label>', re.DOTALL)
                for label_match in label_pattern.finditer(template):
                    label_content = label_match.group(1)
                    # 检查是否有关联的input
                    if re.search(r'for\s*=\s*["\']' + element_id + r'["\']', label_match.group(0)):
                        label_text = re.sub(r'<[^>]+>', '', label_content).strip()
                        return f"getByLabel('{label_text}')"
            
            # 检查placeholder
            placeholder_match = re.search(r'placeholder\s*=\s*["\']([^"\']+)["\']', attributes)
            if placeholder_match:
                return f"getByPlaceholder('{placeholder_match.group(1)}')"
            
            # 根据input类型返回相应的role
            if input_type == 'checkbox':
                # 尝试查找相邻的label
                if id_match and template:
                    element_id = id_match.group(1)
                    # 查找包含该checkbox的form-group中的label
                    context_pattern = re.compile(r'<div[^>]*class="form-group"[^>]*>.*?<label[^>]*>(.*?)</label>.*?id="' + element_id + r'".*?</div>', re.DOTALL)
                    context_match = context_pattern.search(template)
                    if context_match:
                        label_text = re.sub(r'<[^>]+>', '', context_match.group(1)).strip()
                        return f"getByLabel('{label_text}')"
                return "getByRole('checkbox')"
            elif input_type == 'radio':
                return "getByRole('radio')"
            elif input_type in ['text', 'email', 'password', 'search']:
                return "getByRole('textbox')"
        
        elif tag == 'select':
            return "getByRole('combobox')"
        
        elif tag == 'textarea':
            return "getByRole('textbox')"
        
        elif tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            level = tag[1]
            if text:
                return f"getByRole('heading', {{ name: '{text}', level: {level} }})"
            return f"getByRole('heading', {{ level: {level} }})"
        
        # 5. 如果有文本内容，使用getByText
        if text:
            return f"getByText('{text}')"
        
        # 6. 最后回退到CSS选择器
        id_match = re.search(r'id\s*=\s*["\']([^"\']+)["\']', attributes)
        if id_match:
            return f"locator('#{id_match.group(1)}')"
        
        class_match = re.search(r'class\s*=\s*["\']([^"\']+)["\']', attributes)
        if class_match:
            classes = class_match.group(1).split()[0]
            return f"locator('{tag}.{classes}')"
        
        return f"locator('{tag}')"
    
    def _get_element_role(self, tag: str, attributes: str) -> Optional[str]:
        """获取元素的ARIA role"""
        # 检查显式的role属性
        role_match = re.search(r'role\s*=\s*["\']([^"\']+)["\']', attributes)
        if role_match:
            return role_match.group(1)
        
        # 根据HTML标签返回隐式role
        role_map = {
            'button': 'button',
            'a': 'link',
            'input': 'textbox',
            'select': 'combobox',
            'textarea': 'textbox',
            'h1': 'heading',
            'h2': 'heading',
            'h3': 'heading',
            'h4': 'heading',
            'h5': 'heading',
            'h6': 'heading',
            'nav': 'navigation',
            'main': 'main',
            'article': 'article',
            'section': 'section',
            'form': 'form',
            'table': 'table',
            'ul': 'list',
            'ol': 'list',
            'li': 'listitem',
            'dialog': 'dialog',
        }
        
        # 对于input，需要根据type确定role
        if tag == 'input':
            type_match = re.search(r'type\s*=\s*["\']([^"\']+)["\']', attributes)
            if type_match:
                input_type = type_match.group(1)
                input_role_map = {
                    'checkbox': 'checkbox',
                    'radio': 'radio',
                    'button': 'button',
                    'submit': 'button',
                    'reset': 'button',
                    'image': 'button',
                }
                return input_role_map.get(input_type, 'textbox')
        
        return role_map.get(tag)


class ReactParser:
    EVENT_PATTERN = re.compile(r'\bon(\w+)\s*=\s*\{?\s*([^}\s]+)\s*\}?')
    VALUE_PATTERN = re.compile(r'value\s*=\s*\{([^}]+)\}')
    ON_CHANGE_PATTERN = re.compile(r'\bonChange\s*=\s*\{?\s*(\w+)\s*\}?')
    ELEMENT_PATTERN = re.compile(r'<(\w+)([^>]*)(?:>|/>)([^<]*)?(?:</\1>)?', re.DOTALL)
    LABEL_FOR_PATTERN = re.compile(r'<label[^>]*htmlFor\s*=\s*["\']([^"\']+)["\'][^>]*>([^<]*)</label>', re.DOTALL)
    USE_STATE_PATTERN = re.compile(r'useState[^<]*<([^>]+)>')

    def __init__(self):
        self.events_config = {
            'click': {'action': 'click', 'description': '点击'},
            'change': {'action': 'fill', 'description': '输入'},
            'submit': {'action': 'click', 'description': '提交'},
            'blur': {'action': 'blur', 'description': '失焦'},
            'focus': {'action': 'focus', 'description': '聚焦'},
            'doubleClick': {'action': 'dblclick', 'description': '双击'},
            'mouseEnter': {'action': 'hover', 'description': '鼠标悬停'},
            'mouseLeave': {'action': 'hover', 'description': '鼠标离开'},
            'keyDown': {'action': 'press', 'description': '按键'},
            'input': {'action': 'fill', 'description': '输入'},
        }

    def parse_file(self, file_path: str) -> ReactComponent:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        component_name = Path(file_path).stem
        component = ReactComponent(name=component_name, file_path=file_path)

        component.events = self._extract_events(content)
        component.inputs = self._extract_state_vars(content)

        return component

    def _extract_events(self, content: str) -> list:
        events = []

        element_pattern = re.compile(r'<(\w+)([^>]*)(?:>|/>)([^<]*)?(?:</\1>)?', re.DOTALL)

        for match in element_pattern.finditer(content):
            element_tag = match.group(1)
            attributes = match.group(2)
            inner_content = match.group(3) or ''
            # ✅ 去除 JSX 表达式 { ... }，只提取纯文本
            clean_text = re.sub(r'\{[^}]*\}', '', inner_content)
            element_text = re.sub(r'<[^>]+>', '', clean_text).strip()

            for event_match in self.EVENT_PATTERN.finditer(attributes):
                event_type = event_match.group(1)
                handler = event_match.group(2).strip()

                # ✅ 跳过内嵌的箭头函数 handler（如 onClick={() => setIsSubmitted(false)}）
                #    这种是匿名回调，不是可测试的业务 handler
                if '=>' in handler or handler.startswith('(') or '{' in handler:
                    continue

                # ✅ 跳过 JSX 表达式嵌入的文本（如 {showDetails ? 'x' : 'y'}）
                if '{' in element_text or '}' in element_text:
                    element_text = ''

                selector = self._generate_selector(element_tag, attributes, element_text, content)

                events.append(ReactEvent(
                    event_type=event_type,
                    handler=handler,
                    selector=selector,
                    element_tag=element_tag,
                    element_text=element_text
                ))

        return events

    def _extract_state_vars(self, content: str) -> list:
        state_vars = []
        use_state_matches = re.finditer(r'(?:const|let)\s*\[(\w+)\s*,\s*\w+\]\s*=\s*useState', content)
        for match in use_state_matches:
            state_vars.append(match.group(1))
        return state_vars

    def _generate_selector(self, tag: str, attributes: str, text: Optional[str], content: str) -> str:
        return self._generate_selector_fallback(tag, attributes, text, content)

    def _generate_selector_fallback(self, tag: str, attributes: str, text: Optional[str], content: str) -> str:
        testid_match = re.search(r'data-testid\s*=\s*["\']([^"\']+)["\']', attributes)
        if testid_match:
            return f"getByTestId('{testid_match.group(1)}')"

        aria_label_match = re.search(r'aria-label\s*=\s*["\']([^"\']+)["\']', attributes)
        if aria_label_match:
            aria_label = aria_label_match.group(1)
            role = self._get_element_role(tag, attributes)
            if role:
                return f"getByRole('{role}', {{ name: '{aria_label}' }})"

        role = self._get_element_role(tag, attributes)

        if tag == 'button' or role == 'button':
            if text:
                return f"getByRole('button', {{ name: '{text}', exact: true }})"
            return f"locator('{tag}')"

        elif tag == 'a':
            if text:
                return f"getByRole('link', {{ name: '{text}' }})"
            return f"locator('a')"

        elif tag == 'input':
            id_match = re.search(r'id\s*=\s*["\']([^"\']+)["\']', attributes)
            if id_match and content:
                element_id = id_match.group(1)
                for label_match in self.LABEL_FOR_PATTERN.finditer(content):
                    if label_match.group(1) == element_id:
                        label_text = label_match.group(2).strip()
                        return f"getByLabel('{label_text}')"

            placeholder_match = re.search(r'placeholder\s*=\s*["\']([^"\']+)["\']', attributes)
            if placeholder_match:
                return f"getByPlaceholder('{placeholder_match.group(1)}')"

            input_type_match = re.search(r'type\s*=\s*["\']([^"\']+)["\']', attributes)
            input_type = input_type_match.group(1) if input_type_match else 'text'

            if input_type == 'checkbox':
                return "getByRole('checkbox')"
            elif input_type == 'radio':
                return "getByRole('radio')"
            elif input_type in ['text', 'email', 'password', 'search']:
                return "getByRole('textbox')"

        elif tag == 'select':
            return "getByRole('combobox')"

        elif tag == 'textarea':
            return "getByRole('textbox')"

        elif tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            level = tag[1]
            if text:
                return f"getByRole('heading', {{ name: '{text}', level: {level} }})"
            return f"getByRole('heading', {{ level: {level} }})"

        if text:
            return f"getByText('{text}')"

        id_match = re.search(r'id\s*=\s*["\']([^"\']+)["\']', attributes)
        if id_match:
            return f"locator('#{id_match.group(1)}')"

        class_match = re.search(r'className\s*=\s*["\']([^"\']+)["\']', attributes)
        if class_match:
            classes = class_match.group(1).split()[0]
            return f"locator('{tag}.{classes}')"

        return f"locator('{tag}')"

    def _get_element_role(self, tag: str, attributes: str) -> Optional[str]:
        role_match = re.search(r'role\s*=\s*["\']([^"\']+)["\']', attributes)
        if role_match:
            return role_match.group(1)

        role_map = {
            'button': 'button',
            'a': 'link',
            'input': 'textbox',
            'select': 'combobox',
            'textarea': 'textbox',
            'h1': 'heading',
            'h2': 'heading',
            'h3': 'heading',
            'h4': 'heading',
            'h5': 'heading',
            'h6': 'heading',
            'nav': 'navigation',
            'main': 'main',
            'article': 'article',
            'section': 'section',
            'form': 'form',
            'table': 'table',
            'ul': 'list',
            'ol': 'list',
            'li': 'listitem',
            'dialog': 'dialog',
        }

        if tag == 'input':
            type_match = re.search(r'type\s*=\s*["\']([^"\']+)["\']', attributes)
            if type_match:
                input_type = type_match.group(1)
                input_role_map = {
                    'checkbox': 'checkbox',
                    'radio': 'radio',
                    'button': 'button',
                    'submit': 'button',
                    'reset': 'button',
                    'image': 'button',
                }
                return input_role_map.get(input_type, 'textbox')

        return role_map.get(tag)

    def parse_redux_reducer(self, reducer_file: str) -> list:
        with open(reducer_file, 'r', encoding='utf-8') as f:
            content = f.read()

        reducers = []

        func_pattern = re.compile(r'(?:function|const)\s+(\w+Reducer|\w+)\s*=\s*\([^)]*\)\s*=>\s*\{([^}]+(?:\{[^}]*\}[^}]*)*)\}', re.DOTALL)

        for match in func_pattern.finditer(content):
            reducer_name = match.group(1)
            reducer_body = match.group(2)

            initial_state = {}
            state_match = re.search(r'(?:initialState|state)\s*=\s*\{([^}]+)\}', reducer_body, re.DOTALL)
            if state_match:
                state_content = state_match.group(1)
                for prop_match in re.finditer(r'(\w+)\s*:\s*([^,]+)', state_content):
                    key = prop_match.group(1)
                    value = prop_match.group(2).strip()
                    initial_state[key] = value

            actions = []
            action_matches = re.finditer(r'(?:case|action)\s+["\'](\w+)["\']', reducer_body)
            for action_match in action_matches:
                actions.append(action_match.group(1))

            reducers.append(ReduxReducer(
                name=reducer_name,
                file_path=reducer_file,
                initial_state=initial_state,
                actions=actions
            ))

        return reducers


class PlaywrightGenerator:
    def __init__(self):
        self.vue_parser = VueParser()
        self.react_parser = ReactParser()

    def _write_file_with_merge(self, output_file: str, content: str, language: str = 'typescript') -> str:
        """
        智能写入文件，如果文件存在则合并内容
        
        Args:
            output_file: 输出文件路径
            content: 新生成的内容
            language: 语言类型 ('typescript', 'java', 'python')
        
        Returns:
            输出文件路径
        """
        # 确保目录存在
        output_dir = os.path.dirname(output_file)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        # 根据语言确定注释标记
        if language == 'python':
            start_marker = '# AUTO-GENERATED START'
            end_marker = '# AUTO-GENERATED END'
        else:  # typescript, java
            start_marker = '// AUTO-GENERATED START'
            end_marker = '// AUTO-GENERATED END'
        
        # 如果文件不存在，创建新文件并添加标记
        if not os.path.exists(output_file):
            marked_content = f"{start_marker}\n{content}\n{end_marker}"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(marked_content)
            return output_file
        
        # 文件存在，读取现有内容
        with open(output_file, 'r', encoding='utf-8') as f:
            existing_content = f.read()
        
        # 检查是否有自动生成的标记
        start_idx = existing_content.find(start_marker)
        end_idx = existing_content.find(end_marker)
        
        # 如果没有标记，在内容前后添加标记
        if start_idx == -1 or end_idx == -1:
            marked_content = f"{start_marker}\n{content}\n{end_marker}"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(marked_content)
            return output_file
        
        # 有标记，替换标记之间的内容
        # 保留标记之前的内容
        before = existing_content[:start_idx + len(start_marker)]
        # 保留标记之后的内容
        after = existing_content[end_idx:]
        
        # 合并内容
        merged_content = f"{before}\n{content}\n{after}"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(merged_content)
        
        return output_file

    def _generate_test_case(self, event: VueEvent, index: int) -> list:
        config = self.current_parser.events_config.get(event.event_type, {
            'action': 'click',
            'description': event.event_type
        })
        
        action = config['action']
        description = config['description']
        
        if event.element_text:
            test_name = f'{description}{event.element_text}'
        elif 'getByRole' in event.selector or 'getByText' in event.selector:
            # 从选择器中提取名称
            name_match = re.search(r"name: '([^']+)'", event.selector)
            if name_match:
                test_name = f'{description}{name_match.group(1)}'
            else:
                test_name = f'{description}元素'
        else:
            test_name = f'{description}{event.element_tag}'
        
        lines = [
            "",
            f"  test('{test_name}', async ({' page '}) => {{"
        ]
        
        # 生成操作 - 使用新的选择器格式
        if action == 'click':
            lines.append(f"    await page.{event.selector}.click();")
        elif action == 'fill':
            lines.append(f"    await page.{event.selector}.fill('test_value');")
        elif action == 'hover':
            lines.append(f"    await page.{event.selector}.hover();")
        elif action == 'blur':
            lines.append(f"    await page.{event.selector}.blur();")
        elif action == 'focus':
            lines.append(f"    await page.{event.selector}.focus();")
        elif action == 'dblclick':
            lines.append(f"    await page.{event.selector}.dblclick();")
        elif action == 'check':
            lines.append(f"    await page.{event.selector}.check();")
        else:
            lines.append(f"    await page.{event.selector}.{action}();")
        
        if action == 'fill':
            lines.append(f"    await expect(page.{event.selector}).toHaveValue('test_value');")
        elif action == 'check':
            lines.append(f"    await expect(page.{event.selector}).toBeChecked();")
        elif action == 'click' and 'submit' in event.handler:
            lines.append("    // TODO: 添加提交后断言")
        
        lines.append("  });")
        
        return lines
    
    def generate_from_file(self, component_file: str, output_dir: Optional[str] = None, language: str = 'typescript', generate_pom: bool = True) -> str:
        component_type = self.detect_component_type(component_file)

        if component_type == 'react':
            component = self.react_parser.parse_file(component_file)
            self.current_parser = self.react_parser
        else:
            component = self.vue_parser.parse_file(component_file)
            self.current_parser = self.vue_parser

        if generate_pom:
            if language == 'typescript':
                pom_file = self._generate_typescript_pom_file(component, output_dir or './tests')
                test_code = self._generate_typescript_pom_test(component)
                
                if output_dir:
                    typescript_dir = os.path.join(output_dir, 'typescript')
                    os.makedirs(typescript_dir, exist_ok=True)
                    output_file = os.path.join(typescript_dir, f'{to_kebab_case(component.name)}.spec.ts')
                    self._write_file_with_merge(output_file, test_code, 'typescript')
                    return f'{output_file} (POM: {pom_file})'
                return test_code
            elif language == 'java':
                pom_file = self._generate_java_pom_file(component, output_dir or './tests')
                test_code = self._generate_java_pom_test(component)
                
                if output_dir:
                    java_dir = os.path.join(output_dir, 'java')
                    os.makedirs(java_dir, exist_ok=True)
                    output_file = os.path.join(java_dir, f'{to_pascal_case(component.name)}Test.java')
                    self._write_file_with_merge(output_file, test_code, 'java')
                    return f'{output_file} (POM: {pom_file})'
                return test_code
            else:  # python
                pom_file = self._generate_python_pom_file(component, output_dir or './tests')
                test_code = self._generate_python_pom_test(component)
                
                if output_dir:
                    python_dir = os.path.join(output_dir, 'python', 'test_cases')
                    os.makedirs(python_dir, exist_ok=True)
                    output_file = os.path.join(python_dir, f'test_{to_snake_case(component.name)}.py')
                    self._write_file_with_merge(output_file, test_code, 'python')
                    return f'{output_file} (POM: {pom_file})'
                return test_code
        else:
            test_code = self.generate_test(component, language)

            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
                if language == 'typescript':
                    typescript_dir = os.path.join(output_dir, 'typescript')
                    os.makedirs(typescript_dir, exist_ok=True)
                    output_file = os.path.join(typescript_dir, f'{to_kebab_case(component.name)}.spec.ts')
                elif language == 'java':
                    java_dir = os.path.join(output_dir, 'java')
                    os.makedirs(java_dir, exist_ok=True)
                    output_file = os.path.join(java_dir, f'{to_pascal_case(component.name)}Test.java')
                else:  # python
                    python_dir = os.path.join(output_dir, 'python', 'test_cases')
                    os.makedirs(python_dir, exist_ok=True)
                    output_file = os.path.join(python_dir, f'test_{to_snake_case(component.name)}.py')
                self._write_file_with_merge(output_file, test_code, language)
                return output_file
            
            return test_code

    def generate_test(self, component: VueComponent, language: str = 'typescript') -> str:
        if language == 'typescript':
            return self._generate_typescript_test(component)
        elif language == 'java':
            return self._generate_java_test(component)
        else:  # python
            return self._generate_python_test(component)

    def _generate_typescript_test(self, component: VueComponent) -> str:
        lines = [
            "import { test, expect } from '@playwright/test';",
            "",
            f"test.describe('{component.name}', () => {{"
        ]
        
        for idx, event in enumerate(component.events, 1):
            test_case = self._generate_test_case(event, idx)
            lines.extend(test_case)
        
        if not component.events:
            lines.append("  // TODO: 暂未检测到可交互元素")
        
        lines.append("});")
        
        return '\n'.join(lines)

    def _generate_typescript_pom_file(self, component: VueComponent, output_dir: str) -> str:
        class_name = f"{to_pascal_case(component.name)}Page"
        lines = [
            "import { type Page, type Locator } from '@playwright/test';",
            "",
            f"/**",
            f" * {component.name} 页面对象模型",
            f" * 封装页面元素定位器和操作方法",
            f" */",
            f"export class {class_name} {{"
        ]
        
        locators_info = []
        for event in component.events:
            if 'getByRole' in event.selector:
                role_match = re.search(r"getByRole\('([^']+)'", event.selector)
                name_match = re.search(r"name: '([^']+)'", event.selector)
                if role_match and name_match:
                    role = role_match.group(1)
                    name = name_match.group(1)
                    translated_name = translate_to_english(name)
                    locator_name = to_camel_case(f"{translated_name}_{role}")
                    if not any(loc['name'] == locator_name for loc in locators_info):
                        locators_info.append({
                            'name': locator_name,
                            'selector': event.selector,
                            'role': role,
                            'text': name
                        })
            elif 'getByLabel' in event.selector:
                label_match = re.search(r"getByLabel\('([^']+)'\)", event.selector)
                if label_match:
                    label = label_match.group(1)
                    translated_label = translate_to_english(label)
                    locator_name = to_camel_case(f"{translated_label}_input")
                    if not any(loc['name'] == locator_name for loc in locators_info):
                        locators_info.append({
                            'name': locator_name,
                            'selector': event.selector,
                            'role': 'input',
                            'text': label
                        })
            elif 'getByPlaceholder' in event.selector:
                placeholder_match = re.search(r"getByPlaceholder\('([^']+)'\)", event.selector)
                if placeholder_match:
                    placeholder = placeholder_match.group(1)
                    translated_placeholder = translate_to_english(placeholder)
                    locator_name = to_camel_case(f"{translated_placeholder[:20]}_input")
                    if not any(loc['name'] == locator_name for loc in locators_info):
                        locators_info.append({
                            'name': locator_name,
                            'selector': event.selector,
                            'role': 'input',
                            'text': placeholder
                        })
            elif 'getByText' in event.selector:
                text_match = re.search(r"getByText\('([^']+)'\)", event.selector)
                if text_match:
                    text = text_match.group(1)
                    translated_text = translate_to_english(text)
                    locator_name = to_camel_case(f"{translated_text}_text")
                    if not any(loc['name'] == locator_name for loc in locators_info):
                        locators_info.append({
                            'name': locator_name,
                            'selector': event.selector,
                            'role': 'text',
                            'text': text
                        })
            elif 'getByTestId' in event.selector:
                testid_match = re.search(r"getByTestId\('([^']+)'\)", event.selector)
                if testid_match:
                    testid = testid_match.group(1)
                    locator_name = to_snake_case(testid.replace("-", "_") + "_element")
                    if not any(loc['name'] == locator_name for loc in locators_info):
                        locators_info.append({
                            'name': locator_name,
                            'selector': event.selector,
                            'role': 'testid',
                            'text': testid
                        })
        
        lines.append("  readonly page: Page;")
        for loc in locators_info:
            lines.append(f"  /** {loc['text']} 元素定位器 */")
            lines.append(f"  readonly {loc['name']}: Locator;")
        
        lines.extend([
            "",
            f"  constructor(page: Page) {{",
            "    this.page = page;"
        ])
        
        for loc in locators_info:
            lines.append(f"    this.{loc['name']} = page.{loc['selector']};")
        
        lines.extend([
            "  }",
            "",
            "  /**",
            "   * 导航到页面",
            "   */",
            "  async goto() {",
            f"    await this.page.goto('/{component.name.lower()}');",
            "  }"
        ])
        
        methods_added = set()
        for event in component.events:
            config = self.current_parser.events_config.get(event.event_type, {
                'action': 'click',
                'description': event.event_type
            })
            action = config['action']
            description = config['description']
            
            locator_name = None
            element_text = None
            if 'getByRole' in event.selector:
                role_match = re.search(r"getByRole\('([^']+)'", event.selector)
                name_match = re.search(r"name: '([^']+)'", event.selector)
                if role_match and name_match:
                    name = name_match.group(1)
                    role = role_match.group(1)
                    translated_name = translate_to_english(name)
                    locator_name = to_camel_case(f"{translated_name}_{role}")
                    element_text = name
            elif 'getByLabel' in event.selector:
                label_match = re.search(r"getByLabel\('([^']+)'\)", event.selector)
                if label_match:
                    label = label_match.group(1)
                    translated_label = translate_to_english(label)
                    locator_name = to_camel_case(f"{translated_label}_input")
                    element_text = label
            elif 'getByPlaceholder' in event.selector:
                placeholder_match = re.search(r"getByPlaceholder\('([^']+)'\)", event.selector)
                if placeholder_match:
                    placeholder = placeholder_match.group(1)
                    translated_placeholder = translate_to_english(placeholder)
                    locator_name = to_camel_case(f"{translated_placeholder[:20]}_input")
                    element_text = placeholder
            elif 'getByTestId' in event.selector:
                testid_match = re.search(r"getByTestId\('([^']+)'\)", event.selector)
                if testid_match:
                    testid = testid_match.group(1)
                    locator_name = to_snake_case(testid.replace("-", "_") + "_element")
                    element_text = testid
            
            if locator_name and locator_name not in methods_added:
                method_name = to_camel_case(f"{action}_{locator_name}")
                if method_name not in methods_added:
                    methods_added.add(method_name)
                    comment = f"{description}{element_text}" if element_text else description
                    
                    # 根据action类型决定是否需要参数
                    if action == 'fill':
                        method_signature = f"  async {method_name}(value?: string) {{"
                        method_body = f"    await this.{locator_name}.fill(value || 'test_value');"
                    else:
                        method_signature = f"  async {method_name}() {{"
                        if action == 'click':
                            method_body = f"    await this.{locator_name}.click();"
                        elif action == 'check':
                            method_body = f"    await this.{locator_name}.check();"
                        elif action == 'hover':
                            method_body = f"    await this.{locator_name}.hover();"
                        elif action == 'blur':
                            method_body = f"    await this.{locator_name}.blur();"
                        elif action == 'focus':
                            method_body = f"    await this.{locator_name}.focus();"
                        else:
                            method_body = f"    await this.{locator_name}.{action}();"
                    
                    lines.extend([
                        "",
                        f"  /**",
                        f"   * {comment}",
                        f"   */",
                        method_signature,
                        method_body,
                        "  }"
                    ])
        
        # 为输入字段生成 fill 方法
        for input_name in component.inputs:
            # 生成 fill 方法
            fill_method_name = to_camel_case('fill' + to_pascal_case(input_name.replace('.', '_')))
            if fill_method_name not in methods_added:
                methods_added.add(fill_method_name)
                # 查找对应的定位器
                input_locator = None
                for loc in locators_info:
                    # 更准确的匹配：定位器名称中包含输入名称，或者文本中包含输入名称
                    if (input_name in loc['name'] and loc['name'].endswith('Input')) or \
                       (input_name in loc['text'].lower() and loc['role'] == 'input'):
                        input_locator = loc['name']
                        break
                
                if input_locator:
                    lines.extend([
                        "",
                        f"  /**",
                        f"   * 填写{input_name}",
                        f"   */",
                        f"  async {fill_method_name}(value?: string) {{",
                        f"    await this.{input_locator}.fill(value || 'test_value');",
                        "  }"
                    ])
                else:
                    # 如果没有找到定位器，使用通用的 getByLabel 或 getByPlaceholder
                    lines.extend([
                        "",
                        f"  /**",
                        f"   * 填写{input_name}",
                        f"   */",
                        f"  async {fill_method_name}(value?: string) {{",
                        f"    await this.page.getByLabel('{input_name}').fill(value || 'test_value');",
                        "  }"
                    ])
        
        lines.extend([
            "}",
            ""
        ])
        
        typescript_dir = os.path.join(output_dir, 'typescript')
        os.makedirs(os.path.join(typescript_dir, 'pages'), exist_ok=True)
        output_file = os.path.join(typescript_dir, 'pages', f"{to_kebab_case(component.name)}.page.ts")
        self._write_file_with_merge(output_file, '\n'.join(lines), 'typescript')
        return output_file

    def _get_selector_descriptor(self, selector: str) -> str:
        """从选择器中提取人类可读的描述名称"""
        # getByPlaceholder('xxx') → placeholder内容
        placeholder_match = re.search(r"getByPlaceholder\('([^']+)'\)", selector)
        if placeholder_match:
            return placeholder_match.group(1)[:15]
        # getByLabel('xxx') → label内容
        label_match = re.search(r"getByLabel\('([^']+)'\)", selector)
        if label_match:
            return label_match.group(1)[:15]
        # getByTestId('xxx') → testid内容
        testid_match = re.search(r"getByTestId\('([^']+)'\)", selector)
        if testid_match:
            return testid_match.group(1)[:15]
        # getByRole('xxx') → role名
        role_match = re.search(r"getByRole\('([^']+)'", selector)
        if role_match:
            name_match = re.search(r"name: '([^']+)'", selector)
            if name_match:
                return f"{role_match.group(1)}_{name_match.group(1)}"
            return role_match.group(1)
        # locator('xxx') → tag.class
        locator_match = re.search(r"locator\('([^']+)'\)", selector)
        if locator_match:
            return locator_match.group(1).replace('.', '_')[:15]
        return ''

    
    def _generate_assertions(self, event, action: str, language: str = 'typescript') -> list:
        """增强版：根据元素类型和上下文自动生成智能断言（20+ 场景）"""
        assertions = []
        text = (event.element_text or '').strip()
        handler = event.handler or ''
        selector = event.selector or ''
        text_lower = text.lower()
        handler_lower = handler.lower()

        def ts(py, ts_code=None):
            return ts_code if language == 'typescript' and ts_code else py
        def todo(msg):
            return f"// TODO: {msg}" if language == 'typescript' else f"# TODO: {msg}"

        # ============ 按钮断言 ============
        if event.element_tag == 'button':
            if text == '登录' or 'login' in text_lower or 'signin' in text_lower:
                assertions.append(('验证跳转到仪表盘页面', ts("expect(page).to_have_url(r'.*dashboard')", "await expect(page).toHaveURL(/.*dashboard/);")))
                assertions.append(('验证显示欢迎信息', ts("expect(page.get_by_text('欢迎')).to_be_visible()", "await expect(page.getByText('欢迎')).toBeVisible()")))
            elif '注册' in text or 'register' in text_lower or 'signup' in text_lower:
                assertions.append(('验证跳转到注册页面', ts("expect(page).to_have_url(r'.*register')", "await expect(page).toHaveURL(/.*register/);")))
                assertions.append(('验证显示注册成功消息', ts("expect(page.get_by_text('注册成功')).to_be_visible()", "await expect(page.getByText('注册成功')).toBeVisible()")))
            elif '提交' in text or 'submit' in text_lower or handler == 'submit':
                assertions.append(('验证显示成功消息', ts("expect(page.get_by_text('成功')).to_be_visible()", "await expect(page.getByText('成功')).toBeVisible()")))
            elif '搜索' in text or 'search' in text_lower:
                assertions.append(('验证搜索结果可见', ts("expect(page.locator('.result,.search-result,#results').first).to_be_visible()", "await expect(page.locator('.result,.search-result,#results').first).toBeVisible();")))
            elif '保存' in text or 'save' in text_lower:
                assertions.append(('验证保存成功提示', ts("expect(page.get_by_text('保存成功')).to_be_visible()", "await expect(page.getByText('保存成功')).toBeVisible()")))
            elif '删除' in text or 'delete' in text_lower or 'del' in handler_lower:
                assertions.append(('验证元素已删除', todo(f'验证元素{text or "目标"}已被删除')))
            elif '取消' in text or 'cancel' in text_lower:
                assertions.append(('验证弹窗已关闭', todo('验证弹窗/对话框已关闭')))
            elif '关闭' in text or 'close' in text_lower:
                assertions.append(('验证弹窗已关闭', todo('验证关闭后页面状态')))
            elif '下一步' in text or 'next' in text_lower:
                assertions.append(('验证进入下一步', todo('验证步骤已前进')))
            elif '上一步' in text or 'prev' in text_lower or 'back' in text_lower:
                assertions.append(('验证返回上一步', todo('验证步骤已后退')))
            elif '导出' in text or 'download' in text_lower or 'export' in text_lower:
                assertions.append(('验证文件已下载', todo('验证文件下载完成')))
            elif '重置' in text or 'reset' in text_lower or '清空' in text or 'clear' in text_lower:
                assertions.append(('验证输入框已清空', todo('验证输入框值已清空')))

        # ============ 输入框断言 ============
        elif event.element_tag == 'input':
            placeholder = ''
            ph_match = re.search(r"getByPlaceholder\('([^']+)'\)", selector)
            if ph_match:
                placeholder = ph_match.group(1)
            ph_lower = placeholder.lower()
            if action == 'blur':
                if '用户' in placeholder or 'username' in ph_lower or '邮箱' in placeholder or 'email' in ph_lower:
                    assertions.append(('验证显示用户名/邮箱错误信息', ts("expect(page.get_by_text('错误')).to_be_visible()", "await expect(page.getByText('错误')).toBeVisible()")))
                elif '密码' in placeholder or 'password' in ph_lower:
                    assertions.append(('验证显示密码错误信息', ts("expect(page.get_by_text('错误')).to_be_visible()", "await expect(page.getByText('错误')).toBeVisible()")))
                elif '手机' in placeholder or 'phone' in ph_lower:
                    assertions.append(('验证显示手机号错误信息', todo('验证手机格式错误提示')))
                elif '验证码' in placeholder or 'code' in ph_lower:
                    assertions.append(('验证验证码错误信息', todo('验证验证码错误提示')))
                else:
                    assertions.append(('验证显示错误信息', todo('验证错误提示')))
            elif action == 'focus':
                assertions.append(('验证错误信息已清除', ts("expect(page.get_by_text('错误')).to_be_hidden()", "await expect(page.getByText('错误')).toBeHidden()")))
            elif action == 'check':
                assertions.append(('验证已选中', ts(f"expect(page.{selector}).to_be_checked()", f"await expect(page.{selector}).toBeChecked();")))
            elif action == 'fill':
                assertions.append(('验证输入框值已更新', ts("expect(locator).to_have_value(re.compile(r'.+'))" if language == 'python' else "await expect(locator).toHaveValue(/.+/);")))

        # ============ 表单断言 ============
        elif event.element_tag == 'form' and ('submit' in handler_lower or action == 'submit'):
            assertions.append(('验证表单提交成功', ts("expect(page.get_by_text('成功')).to_be_visible()", "await expect(page.getByText('成功')).toBeVisible()")))

        # ============ 链接断言 ============
        elif event.element_tag == 'a':
            if '登录' in text or 'login' in text_lower:
                assertions.append(('验证跳转到登录页面', ts("expect(page).to_have_url(r'.*login')", "await expect(page).toHaveURL(/.*login/);")))
            elif '注册' in text or 'register' in text_lower:
                assertions.append(('验证跳转到注册页面', ts("expect(page).to_have_url(r'.*register')", "await expect(page).toHaveURL(/.*register/);")))
            elif '忘记密码' in text or 'forgot' in text_lower:
                assertions.append(('验证跳转到忘记密码页面', ts("expect(page).to_have_url(r'.*forgot|.*reset')", "await expect(page).toHaveURL(/.*forgot|.*reset/);")))
            elif '帮助' in text or 'help' in text_lower:
                assertions.append(('验证跳转到帮助页面', todo('验证帮助页面已打开')))

        # ============ 事件处理函数名分析 ============
        if handler_lower.startswith('validate') or handler_lower.startswith('check'):
            assertions.append(('验证显示验证错误', ts("expect(page.get_by_text('错误')).to_be_visible()", "await expect(page.getByText('错误')).toBeVisible()")))
        if handler_lower.startswith('toggle'):
            assertions.append(('验证切换状态已生效', todo('验证切换后的状态')))
        if handler_lower.startswith('handle') and ('login' in handler_lower or 'submit' in handler_lower):
            assertions.append(('验证页面跳转或状态变化', todo('验证跳转后的URL')))

        return assertions


    def _generate_typescript_pom_test(self, component: VueComponent) -> str:
        class_name = f"{to_pascal_case(component.name)}Page"
        page_var = to_camel_case(f"{component.name}_page")
        lines = [
            "import { test, expect } from '@playwright/test';",
            f"import {{ {class_name} }} from './pages/{to_kebab_case(component.name)}.page';",
            "",
            f"/**",
            f" * {component.name} 组件测试",
            f" */",
            f"test.describe('{component.name}', () => {{"
        ]
        
        seen_actions = set()  # 去重：(element_key, action) 对

        for idx, event in enumerate(component.events, 1):
            config = self.current_parser.events_config.get(event.event_type, {
                'action': 'click',
                'description': event.event_type
            })
            action = config['action']
            description = config['description']

            if event.element_text:
                test_name_cn = f'{description}{event.element_text}'
                test_name_en = f'should {action} {translate_to_english(event.element_text)}'
                element_key = event.element_text
            elif 'getByRole' in event.selector or 'getByText' in event.selector:
                name_match = re.search(r"name: '([^']+)'", event.selector)
                if name_match:
                    element_name = name_match.group(1)
                    test_name_cn = f'{description}{element_name}'
                    test_name_en = f'should {action} {translate_to_english(element_name)}'
                    element_key = element_name
                else:
                    descriptor = self._get_selector_descriptor(event.selector)
                    if descriptor:
                        test_name_cn = f'{description}{descriptor}'
                        test_name_en = f'should {action} {translate_to_english(descriptor)}'
                        element_key = descriptor
                    else:
                        test_name_cn = f'{description}元素'
                        test_name_en = f'should {action} element'
                        element_key = event.selector  # 用选择器作为唯一 key
            else:
                descriptor = self._get_selector_descriptor(event.selector)
                if descriptor:
                    test_name_cn = f'{description}{descriptor}'
                    test_name_en = f'should {action} {translate_to_english(descriptor)}'
                    element_key = descriptor
                else:
                    test_name_cn = f'{description}{event.element_tag}'
                    test_name_en = f'should {action} {event.element_tag}'
                    element_key = event.selector  # 用选择器作为唯一 key

            # 去重：同一元素的相同 action 只生成一次
            dedup_key = (element_key, action)
            if dedup_key in seen_actions:
                continue
            seen_actions.add(dedup_key)
            
            locator_name = None
            if 'getByRole' in event.selector:
                role_match = re.search(r"getByRole\('([^']+)'", event.selector)
                name_match = re.search(r"name: '([^']+)'", event.selector)
                if role_match and name_match:
                    name = name_match.group(1)
                    role = role_match.group(1)
                    translated_name = translate_to_english(name)
                    locator_name = to_camel_case(f"{translated_name}_{role}")
            elif 'getByLabel' in event.selector:
                label_match = re.search(r"getByLabel\('([^']+)'\)", event.selector)
                if label_match:
                    label = label_match.group(1)
                    translated_label = translate_to_english(label)
                    locator_name = to_camel_case(f"{translated_label}_input")
            elif 'getByPlaceholder' in event.selector:
                placeholder_match = re.search(r"getByPlaceholder\('([^']+)'\)", event.selector)
                if placeholder_match:
                    placeholder = placeholder_match.group(1)
                    translated_placeholder = translate_to_english(placeholder)
                    locator_name = to_camel_case(f"{translated_placeholder[:20]}_input")
            
            method_name = to_camel_case(f"{action}_{locator_name}") if locator_name else to_camel_case(f"{action}_element")
            
            lines.extend([
                "",
                f"  /**",
                f"   * {test_name_cn}",
                f"   */",
                f"  test('{test_name_en}', async ({{ page }}) => {{",
                f"    const {page_var} = new {class_name}(page);",
                f"    await {page_var}.goto();"
            ])
            
            if action == 'fill':
                lines.append(f"    await {page_var}.{method_name}('test_value');")
            else:
                lines.append(f"    await {page_var}.{method_name}();")
            
            # 智能断言
            ts_assertions = self._generate_assertions(event, action, 'typescript')
            if ts_assertions:
                lines.append('')
                for desc, code in ts_assertions:
                    lines.append(f'    // {desc}')
                    lines.append(f'    {code}')
                lines.append('')
            else:
                lines.append('    // TODO: 添加断言')
            lines.append('  });')
        
        if not component.events:
            lines.append("  // TODO: 暂未检测到可交互元素")
        
        lines.extend([
            "});",
            ""
        ])
        
        return '\n'.join(lines)

    def _generate_java_pom_file(self, component: VueComponent, output_dir: str) -> str:
        class_name = f"{to_pascal_case(component.name)}Page"
        lines = [
            "import com.microsoft.playwright.*;",
            "",
            f"/**",
            f" * {component.name} 页面对象模型",
            f" * 封装页面元素定位器和操作方法",
            f" */",
            f"public class {class_name} {{",
            "    private final Page page;"
        ]
        
        locators_info = []
        for event in component.events:
            if 'getByRole' in event.selector:
                role_match = re.search(r"getByRole\('([^']+)'", event.selector)
                name_match = re.search(r"name: '([^']+)'", event.selector)
                if role_match and name_match:
                    role = role_match.group(1)
                    name = name_match.group(1)
                    translated_name = translate_to_english(name)
                    locator_name = to_camel_case(f"{translated_name}_{role}")
                    if not any(loc['name'] == locator_name for loc in locators_info):
                        locators_info.append({
                            'name': locator_name,
                            'selector': event.selector,
                            'role': role,
                            'text': name
                        })
            elif 'getByLabel' in event.selector:
                label_match = re.search(r"getByLabel\('([^']+)'\)", event.selector)
                if label_match:
                    label = label_match.group(1)
                    translated_label = translate_to_english(label)
                    locator_name = to_camel_case(f"{translated_label}_input")
                    if not any(loc['name'] == locator_name for loc in locators_info):
                        locators_info.append({
                            'name': locator_name,
                            'selector': event.selector,
                            'role': 'input',
                            'text': label
                        })
            elif 'getByPlaceholder' in event.selector:
                placeholder_match = re.search(r"getByPlaceholder\('([^']+)'\)", event.selector)
                if placeholder_match:
                    placeholder = placeholder_match.group(1)
                    translated_placeholder = translate_to_english(placeholder)
                    locator_name = to_camel_case(f"{translated_placeholder[:20]}_input")
                    if not any(loc['name'] == locator_name for loc in locators_info):
                        locators_info.append({
                            'name': locator_name,
                            'selector': event.selector,
                            'role': 'input',
                            'text': placeholder
                        })
            elif 'getByTestId' in event.selector:
                testid_match = re.search(r"getByTestId\('([^']+)'\)", event.selector)
                if testid_match:
                    testid = testid_match.group(1)
                    locator_name = to_snake_case(testid.replace("-", "_") + "_element")
                    if not any(loc['name'] == locator_name for loc in locators_info):
                        locators_info.append({
                            'name': locator_name,
                            'selector': event.selector,
                            'role': 'testid',
                            'text': testid
                        })
        
        for loc in locators_info:
            lines.append(f"    /** {loc['text']} 元素定位器 */")
            lines.append(f"    private final Locator {loc['name']};")
        
        lines.extend([
            "",
            f"    public {class_name}(Page page) {{",
            "        this.page = page;"
        ])
        
        for loc in locators_info:
            if 'getByRole' in loc['selector']:
                role_match = re.search(r"getByRole\('([^']+)'", loc['selector'])
                name_match = re.search(r"name: '([^']+)'", loc['selector'])
                if role_match and name_match:
                    role = role_match.group(1).upper()
                    name = name_match.group(1)
                    lines.append(f"        this.{loc['name']} = page.getByRole(AriaRole.{role}, new Page.GetByRoleOptions().setName(\"{name}\"));")
            elif 'getByLabel' in loc['selector']:
                label_match = re.search(r"getByLabel\('([^']+)'\)", loc['selector'])
                if label_match:
                    label = label_match.group(1)
                    lines.append(f"        this.{loc['name']} = page.getByLabel(\"{label}\");")
            elif 'getByPlaceholder' in loc['selector']:
                placeholder_match = re.search(r"getByPlaceholder\('([^']+)'\)", loc['selector'])
                if placeholder_match:
                    placeholder = placeholder_match.group(1)
                    lines.append(f"        this.{loc['name']} = page.getByPlaceholder(\"{placeholder}\");")
        
        lines.extend([
            "    }",
            "",
            "    /**",
            "     * 导航到页面",
            "     */",
            "    public void goto() {",
            f"        page.navigate(\"/{component.name.lower()}\");",
            "    }"
        ])
        
        methods_added = set()
        for event in component.events:
            config = self.current_parser.events_config.get(event.event_type, {
                'action': 'click',
                'description': event.event_type
            })
            action = config['action']
            description = config['description']
            
            locator_name = None
            element_text = None
            if 'getByRole' in event.selector:
                role_match = re.search(r"getByRole\('([^']+)'", event.selector)
                name_match = re.search(r"name: '([^']+)'", event.selector)
                if role_match and name_match:
                    name = name_match.group(1)
                    role = role_match.group(1)
                    translated_name = translate_to_english(name)
                    locator_name = to_camel_case(f"{translated_name}_{role}")
                    element_text = name
            elif 'getByLabel' in event.selector:
                label_match = re.search(r"getByLabel\('([^']+)'\)", event.selector)
                if label_match:
                    label = label_match.group(1)
                    translated_label = translate_to_english(label)
                    locator_name = to_camel_case(f"{translated_label}_input")
                    element_text = label
            elif 'getByPlaceholder' in event.selector:
                placeholder_match = re.search(r"getByPlaceholder\('([^']+)'\)", event.selector)
                if placeholder_match:
                    placeholder = placeholder_match.group(1)
                    translated_placeholder = translate_to_english(placeholder)
                    locator_name = to_camel_case(f"{translated_placeholder[:20]}_input")
                    element_text = placeholder
            
            if locator_name and locator_name not in methods_added:
                method_name = to_camel_case(f"{action}_{locator_name}")
                if method_name not in methods_added:
                    methods_added.add(method_name)
                    comment = f"{description}{element_text}" if element_text else description
                    
                    # 根据action类型决定是否需要参数
                    if action == 'fill':
                        method_signature = f"    public void {method_name}(String value) {{"
                        method_body = f"        this.{locator_name}.fill(value != null ? value : \"test_value\");"
                    else:
                        method_signature = f"    public void {method_name}() {{"
                        if action == 'click':
                            method_body = f"        this.{locator_name}.click();"
                        elif action == 'check':
                            method_body = f"        this.{locator_name}.check();"
                        elif action == 'hover':
                            method_body = f"        this.{locator_name}.hover();"
                        elif action == 'blur':
                            method_body = f"        this.{locator_name}.blur();"
                        elif action == 'focus':
                            method_body = f"        this.{locator_name}.focus();"
                        else:
                            method_body = f"        this.{locator_name}.{action}();"
                    
                    lines.extend([
                        "",
                        f"    /**",
                        f"     * {comment}",
                        f"     */",
                        method_signature,
                        method_body,
                        "    }"
                    ])
        
        # 为输入字段生成 fill 方法
        for input_name in component.inputs:
            # 生成 fill 方法
            fill_method_name = to_camel_case('fill' + to_pascal_case(input_name.replace('.', '_')))
            if fill_method_name not in methods_added:
                methods_added.add(fill_method_name)
                # 查找对应的定位器
                input_locator = None
                for loc in locators_info:
                    # 更准确的匹配：定位器名称中包含输入名称，或者文本中包含输入名称
                    if (input_name in loc['name'] and loc['name'].endswith('Input')) or \
                       (input_name in loc['text'].lower() and loc['role'] == 'input'):
                        input_locator = loc['name']
                        break
                
                if input_locator:
                    lines.extend([
                        "",
                        f"    /**",
                        f"     * 填写{input_name}",
                        f"     */",
                        f"    public void {fill_method_name}(String value) {{",
                        f"        this.{input_locator}.fill(value != null ? value : \"test_value\");",
                        "    }"
                    ])
                else:
                    # 如果没有找到定位器，使用通用的 getByLabel 或 getByPlaceholder
                    lines.extend([
                        "",
                        f"    /**",
                        f"     * 填写{input_name}",
                        f"     */",
                        f"    public void {fill_method_name}(String value) {{",
                        f"        page.getByLabel(\"{input_name}\").fill(value != null ? value : \"test_value\");",
                        "    }"
                    ])
        
        lines.extend([
            "}",
            ""
        ])
        
        os.makedirs(os.path.join(output_dir, 'java', 'pages'), exist_ok=True)
        output_file = os.path.join(output_dir, 'java', 'pages', f"{to_pascal_case(component.name)}Page.java")
        self._write_file_with_merge(output_file, '\n'.join(lines), 'java')
        return output_file

    def _generate_java_pom_test(self, component: VueComponent) -> str:
        class_name = f"{component.name}Page"
        page_var = f"{component.name[0].lower()}{component.name[1:]}Page"
        lines = [
            "import com.microsoft.playwright.*;",
            "import org.junit.jupiter.api.Test;",
            "import org.junit.jupiter.api.BeforeEach;",
            "import org.junit.jupiter.api.AfterEach;",
            "import static org.junit.jupiter.api.Assertions.*;",
            f"import java.pages.{class_name};",
            "",
            f"/**",
            f" * {component.name} 组件测试",
            f" */",
            f"public class {component.name}Test {{",
            "    private Playwright playwright;",
            "    private Browser browser;",
            "    private Page page;",
            f"    private {class_name} {page_var};",
            "",
            "    @BeforeEach",
            "    public void setUp() {",
            "        playwright = Playwright.create();",
            "        browser = playwright.chromium().launch();",
            "        page = browser.newPage();",
            f"        {page_var} = new {class_name}(page);",
            "    }",
            "",
            "    @AfterEach",
            "    public void tearDown() {",
            "        browser.close();",
            "        playwright.close();",
            "    }"
        ]
        
        for idx, event in enumerate(component.events, 1):
            config = self.current_parser.events_config.get(event.event_type, {
                'action': 'click',
                'description': event.event_type
            })
            action = config['action']
            description = config['description']
            
            if event.element_text:
                test_name_cn = f'{description}{event.element_text}'
                test_name_en = f'test{action.capitalize()}{translate_to_english(event.element_text).capitalize()}'
            elif 'getByRole' in event.selector or 'getByText' in event.selector:
                name_match = re.search(r"name: '([^']+)'", event.selector)
                if name_match:
                    element_name = name_match.group(1)
                    test_name_cn = f'{description}{element_name}'
                    test_name_en = f'test{action.capitalize()}{translate_to_english(element_name).capitalize()}'
                else:
                    test_name_cn = f'{description}元素{idx}'
                    test_name_en = f'test{action.capitalize()}Element{idx}'
            else:
                test_name_cn = f'{description}{event.element_tag}{idx}'
                test_name_en = f'test{action.capitalize()}{event.element_tag.capitalize()}{idx}'
            
            locator_name = None
            if 'getByRole' in event.selector:
                role_match = re.search(r"getByRole\('([^']+)'", event.selector)
                name_match = re.search(r"name: '([^']+)'", event.selector)
                if role_match and name_match:
                    name = name_match.group(1)
                    role = role_match.group(1)
                    translated_name = translate_to_english(name)
                    locator_name = to_camel_case(f"{translated_name}_{role}")
            elif 'getByLabel' in event.selector:
                label_match = re.search(r"getByLabel\('([^']+)'\)", event.selector)
                if label_match:
                    label = label_match.group(1)
                    translated_label = translate_to_english(label)
                    locator_name = to_camel_case(f"{translated_label}_input")
            elif 'getByPlaceholder' in event.selector:
                placeholder_match = re.search(r"getByPlaceholder\('([^']+)'\)", event.selector)
                if placeholder_match:
                    placeholder = placeholder_match.group(1)
                    translated_placeholder = translate_to_english(placeholder)
                    locator_name = to_camel_case(f"{translated_placeholder[:20]}_input")
            
            method_name = to_camel_case(f"{action}_{locator_name}") if locator_name else to_camel_case(f"{action}_element")
            
            lines.extend([
                "",
                "    /**",
                f"     * {test_name_cn}",
                "     */",
                "    @Test",
                f"    public void {test_name_en}() {{",
                f"        {page_var}.goto();"
            ])
            
            if action == 'fill':
                lines.append(f"        {page_var}.{method_name}(\"test_value\");")
            else:
                lines.append(f"        {page_var}.{method_name}();")
            
            lines.extend([
                "        // TODO: 添加断言",
                "    }"
            ])
        
        lines.extend([
            "}",
            ""
        ])
        
        return '\n'.join(lines)

    def _generate_python_pom_file(self, component: VueComponent, output_dir: str) -> str:
        class_name = f"{component.name}Page"
        lines = [
            "import logging",
            "import os",
            "from playwright.sync_api import Page, Locator",
            "",
            "logger = logging.getLogger(__name__)",
            "",
            "# 从环境变量读取 base URL（由 test_config.toml 的 environment.base_url 注入）",
            "_BASE = os.environ.get('BASE_URL', '')",
            "",
            "",
            f'"""',
            f"{component.name} 页面对象模型",
            f"封装页面元素定位器和操作方法",
            f'"""',
            f"class {class_name}:",
            "    def __init__(self, page: Page):",
            "        self.page = page",
            "        self.logger = logging.getLogger(__name__)",
        ]
        
        locators_info = []
        for event in component.events:
            if 'getByRole' in event.selector:
                role_match = re.search(r"getByRole\('([^']+)'", event.selector)
                name_match = re.search(r"name: '([^']+)'", event.selector)
                if role_match and name_match:
                    role = role_match.group(1)
                    name = name_match.group(1)
                    translated_name = translate_to_english(name)
                    locator_name = to_snake_case(f"{translated_name}_{role}")
                    if not any(loc['name'] == locator_name for loc in locators_info):
                        locators_info.append({
                            'name': locator_name,
                            'selector': event.selector,
                            'role': role,
                            'text': name
                        })
            elif 'getByLabel' in event.selector:
                label_match = re.search(r"getByLabel\('([^']+)'\)", event.selector)
                if label_match:
                    label = label_match.group(1)
                    translated_label = translate_to_english(label)
                    locator_name = to_snake_case(f"{translated_label}_input")
                    if not any(loc['name'] == locator_name for loc in locators_info):
                        locators_info.append({
                            'name': locator_name,
                            'selector': event.selector,
                            'role': 'input',
                            'text': label
                        })
            elif 'getByPlaceholder' in event.selector:
                placeholder_match = re.search(r"getByPlaceholder\('([^']+)'\)", event.selector)
                if placeholder_match:
                    placeholder = placeholder_match.group(1)
                    translated_placeholder = translate_to_english(placeholder)
                    locator_name = to_snake_case(f"{translated_placeholder[:20]}_input")
                    if not any(loc['name'] == locator_name for loc in locators_info):
                        locators_info.append({
                            'name': locator_name,
                            'selector': event.selector,
                            'role': 'input',
                            'text': placeholder
                        })
            elif 'getByTestId' in event.selector:
                testid_match = re.search(r"getByTestId\('([^']+)'\)", event.selector)
                if testid_match:
                    testid = testid_match.group(1)
                    locator_name = to_snake_case(testid.replace("-", "_") + "_element")
                    if not any(loc['name'] == locator_name for loc in locators_info):
                        locators_info.append({
                            'name': locator_name,
                            'selector': event.selector,
                            'role': 'testid',
                            'text': testid
                        })
        
        for loc in locators_info:
            lines.append(f"        # {loc['text']} 元素定位器")
            py_selector = self._convert_selector_to_python(loc['selector'])
            py_selector_stripped = py_selector[len('page.'):] if py_selector.startswith('page.') else py_selector
            lines.append(f"        self.{loc['name']} = page.{py_selector_stripped}")
        
        lines.extend([
            "",
            "    def goto(self):",
            '        """导航到页面"""',
            "        self.logger.info('[POM] goto: %s', self.page.url)",
            f"        self.page.goto(_BASE + '/{component.name.lower()}')"
        ])
        
        methods_added = set()
        for event in component.events:
            config = self.current_parser.events_config.get(event.event_type, {
                'action': 'click',
                'description': event.event_type
            })
            action = config['action']
            description = config['description']
            
            locator_name = None
            element_text = None
            if 'getByRole' in event.selector:
                role_match = re.search(r"getByRole\('([^']+)'", event.selector)
                name_match = re.search(r"name: '([^']+)'", event.selector)
                if role_match and name_match:
                    name = name_match.group(1)
                    role = role_match.group(1)
                    translated_name = translate_to_english(name)
                    locator_name = to_snake_case(f"{translated_name}_{role}")
                    element_text = name
            elif 'getByLabel' in event.selector:
                label_match = re.search(r"getByLabel\('([^']+)'\)", event.selector)
                if label_match:
                    label = label_match.group(1)
                    translated_label = translate_to_english(label)
                    locator_name = to_snake_case(f"{translated_label}_input")
                    element_text = label
            elif 'getByPlaceholder' in event.selector:
                placeholder_match = re.search(r"getByPlaceholder\('([^']+)'\)", event.selector)
                if placeholder_match:
                    placeholder = placeholder_match.group(1)
                    translated_placeholder = translate_to_english(placeholder)
                    locator_name = to_snake_case(f"{translated_placeholder[:20]}_input")
                    element_text = placeholder
            elif 'getByTestId' in event.selector:
                testid_match = re.search(r"getByTestId\('([^']+)'\)", event.selector)
                if testid_match:
                    testid = testid_match.group(1)
                    locator_name = to_snake_case(testid.replace("-", "_") + "_element")
                    element_text = testid
            
            if locator_name and locator_name not in methods_added:
                method_name = to_snake_case(f"{action}_{locator_name}")
                if method_name not in methods_added:
                    methods_added.add(method_name)
                    comment = f"{description}{element_text}" if element_text else description

                    # 根据action类型决定是否需要参数
                    if action == 'fill':
                        method_signature = f"    def {method_name}(self, value: str = 'test_value'):"
                        method_body = f"        self.{locator_name}.fill(value)"
                    else:
                        method_signature = f"    def {method_name}(self):"
                        if action == 'click':
                            method_body = f"        self.{locator_name}.click()"
                        elif action == 'check':
                            method_body = f"        self.{locator_name}.check()"
                        elif action == 'hover':
                            method_body = f"        self.{locator_name}.hover()"
                        elif action == 'blur':
                            method_body = f"        self.{locator_name}.blur()"
                        elif action == 'focus':
                            method_body = f"        self.{locator_name}.focus()"
                        else:
                            method_body = f"        self.{locator_name}.{action}()"

                    log_msg = f'{action}_{locator_name}' if locator_name else action
                    log_line = f'        self.logger.info("[POM] {log_msg}")'

                    lines.extend([
                        "",
                        method_signature,
                        f'        """{comment}"""',
                        log_line,
                        method_body
                    ])
        
        # 为输入字段生成 fill 方法
        for input_name in component.inputs:
            # 生成 fill 方法
            fill_method_name = to_snake_case('fill_' + input_name.replace('.', '_'))
            if fill_method_name not in methods_added:
                methods_added.add(fill_method_name)
                # 查找对应的定位器
                input_locator = None
                for loc in locators_info:
                    # 更准确的匹配：定位器名称中包含输入名称，或者文本中包含输入名称
                    # 避免误匹配，比如 password 匹配到 forgot_password_link
                    if (input_name in loc['name'] and loc['name'].endswith('_input')) or \
                       (input_name in loc['text'].lower() and loc['role'] == 'input'):
                        input_locator = loc['name']
                        break
                
                if input_locator:
                    lines.extend([
                        "",
                        f"    def {fill_method_name}(self, value: str = 'test_value'):",
                        f'        """填写{input_name}"""',
                        f"        self.{input_locator}.fill(value)"
                    ])
                else:
                    # 如果没有找到定位器，使用通用的 getByLabel 或 getByPlaceholder
                    lines.extend([
                        "",
                        f"    def {fill_method_name}(self, value: str = 'test_value'):",
                        f'        """填写{input_name}"""',
                        f"        self.page.get_by_label('{input_name}').fill(value)"
                    ])
        
        lines.extend([
            "",
            ""
        ])
        
        os.makedirs(os.path.join(output_dir, 'python', 'pages'), exist_ok=True)
        output_file = os.path.join(output_dir, 'python', 'pages', f"{to_snake_case(component.name)}_page.py")
        self._write_file_with_merge(output_file, '\n'.join(lines), 'python')
        return output_file

    def _generate_python_pom_test(self, component: VueComponent) -> str:
        class_name = f"{component.name}Page"
        page_var = f"{component.name[0].lower()}{component.name[1:]}_page"
        lines = [
            "import logging",
            "",
            "import pytest",
            "from playwright.sync_api import Page, expect",
            f"from pages.{to_snake_case(component.name)}_page import {class_name}",
            "",
            "",
            f'"""',
            f"{component.name} 组件测试",
            f'"""',
            f"class Test{component.name}:",
            "    logger: logging.Logger  # 由 conftest.py 的 log_config fixture 注入",
            "    @pytest.fixture(autouse=True)",
            "    def setup(self, page: Page):",
            f"        self.page = page",
            f"        self.{page_var} = {class_name}(page)",
            ""
        ]
        
        seen_actions = set()  # 去重

        for idx, event in enumerate(component.events, 1):
            config = self.current_parser.events_config.get(event.event_type, {
                'action': 'click',
                'description': event.event_type
            })
            action = config['action']
            description = config['description']

            if event.element_text:
                test_name_cn = f'{description}{event.element_text}'
                test_name_en = f'test_{action}_{translate_to_english(event.element_text)}'
                element_key = event.element_text
            elif 'getByRole' in event.selector or 'getByText' in event.selector:
                name_match = re.search(r"name: '([^']+)'", event.selector)
                if name_match:
                    element_name = name_match.group(1)
                    test_name_cn = f'{description}{element_name}'
                    test_name_en = f'test_{action}_{translate_to_english(element_name)}'
                    element_key = element_name
                else:
                    descriptor = self._get_selector_descriptor(event.selector)
                    if descriptor:
                        test_name_cn = f'{description}{descriptor}'
                        test_name_en = f'test_{action}_{translate_to_english(descriptor)}'
                        element_key = descriptor
                    else:
                        test_name_cn = f'{description}元素{idx}'
                        test_name_en = f'test_{action}_element_{idx}'
                        element_key = event.selector  # 用选择器作为唯一 key
            else:
                descriptor = self._get_selector_descriptor(event.selector)
                if descriptor:
                    test_name_cn = f'{description}{descriptor}'
                    test_name_en = f'test_{action}_{translate_to_english(descriptor)}'
                    element_key = descriptor
                else:
                    test_name_cn = f'{description}{event.element_tag}{idx}'
                    test_name_en = f'test_{action}_{event.element_tag}_{idx}'
                    element_key = event.selector  # 用选择器作为唯一 key

            # 去重：同一元素的相同 action 只生成一次
            dedup_key = (element_key, action)
            if dedup_key in seen_actions:
                continue
            seen_actions.add(dedup_key)
            
            locator_name = None
            if 'getByRole' in event.selector:
                role_match = re.search(r"getByRole\('([^']+)'", event.selector)
                name_match = re.search(r"name: '([^']+)'", event.selector)
                if role_match and name_match:
                    name = name_match.group(1)
                    role = role_match.group(1)
                    translated_name = translate_to_english(name)
                    locator_name = f"{translated_name}_{role}"
            elif 'getByLabel' in event.selector:
                label_match = re.search(r"getByLabel\('([^']+)'\)", event.selector)
                if label_match:
                    label = label_match.group(1)
                    translated_label = translate_to_english(label)
                    locator_name = f"{translated_label}_input"
            elif 'getByPlaceholder' in event.selector:
                placeholder_match = re.search(r"getByPlaceholder\('([^']+)'\)", event.selector)
                if placeholder_match:
                    placeholder = placeholder_match.group(1)
                    translated_placeholder = translate_to_english(placeholder)
                    locator_name = f"{translated_placeholder[:20]}_input"
            elif 'getByTestId' in event.selector:
                testid_match = re.search(r"getByTestId\('([^']+)'\)", event.selector)
                if testid_match:
                    testid = testid_match.group(1)
                    locator_name = testid.replace('-', '_').replace('.', '_')
            
            method_name = f"{action}_{locator_name}" if locator_name else f"{action}_element"

            # ✅ 去重过滤：如果 locator_name 为 None（无法解析），跳过生成测试方法
            if not locator_name:
                continue
            
            lines.extend([
                f"    def {test_name_en}(self):",
                f'        """{test_name_cn}"""',
                f"        self.{page_var}.goto()"
            ])
            
            if action == 'fill':
                lines.append(f"        self.{page_var}.{method_name}('test_value')")
            else:
                lines.append(f"        self.{page_var}.{method_name}()")

            # 日志：标记测试步骤
            lines.append(f"        self.logger.info('[TEST] {test_name_cn}')")

            # 智能断言
            py_assertions = self._generate_assertions(event, action, 'python')
            if py_assertions:
                lines.append('')
                for desc, code in py_assertions:
                    lines.append(f'        # {desc}')
                    lines.append(f'        {code}')
                lines.append('')
            else:
                lines.append('        # TODO: 添加断言')
            lines.append('')
        
        return '\n'.join(lines)

    def _generate_java_test(self, component: VueComponent) -> str:
        lines = [
            "import com.microsoft.playwright.*;",
            "import org.junit.jupiter.api.Test;",
            "import org.junit.jupiter.api.BeforeEach;",
            "import org.junit.jupiter.api.AfterEach;",
            "import static org.junit.jupiter.api.Assertions.*;",
            "",
            f"public class {component.name}Test {{",
            "    private Playwright playwright;",
            "    private Browser browser;",
            "    private Page page;",
            "",
            "    @BeforeEach",
            "    public void setUp() {",
            "        playwright = Playwright.create();",
            "        browser = playwright.chromium().launch();",
            "        page = browser.newPage();",
            "    }",
            "",
            "    @AfterEach",
            "    public void tearDown() {",
            "        browser.close();",
            "        playwright.close();",
            "    }"
        ]
        
        event_type_map = {
            'click': 'Click',
            'input': 'Input',
            'change': 'Change',
            'blur': 'Blur',
            'focus': 'Focus',
            'submit': 'Submit',
            'dblclick': 'DoubleClick',
            'mouseenter': 'MouseEnter',
            'mouseleave': 'MouseLeave'
        }
        
        seen_actions = set()  # 去重

        for idx, event in enumerate(component.events, 1):
            config = self.current_parser.events_config.get(event.event_type, {
                'action': 'click',
                'description': event.event_type
            })
            action = config['action']
            event_type = event.event_type

            # 去重：同一元素的相同 action 只生成一次
            element_key = event.element_text or event.element_tag
            dedup_key = (element_key, action)
            if dedup_key in seen_actions:
                continue
            seen_actions.add(dedup_key)

            # 生成符合Java命名规范的测试方法名
            event_suffix = event_type_map.get(event_type, event_type.capitalize())
            
            # 从选择器中提取名称
            if 'getByRole' in event.selector or 'getByText' in event.selector:
                name_match = re.search(r"name: '([^']+)'", event.selector)
                if name_match:
                    element_name = name_match.group(1).replace(' ', '').replace('？', '')
                else:
                    element_name = event.element_tag.capitalize()
            elif 'getByPlaceholder' in event.selector:
                placeholder_match = re.search(r"getByPlaceholder\('([^']+)'\)", event.selector)
                if placeholder_match:
                    element_name = placeholder_match.group(1).replace(' ', '')[:10]
                else:
                    element_name = event.element_tag.capitalize()
            elif 'getByLabel' in event.selector:
                label_match = re.search(r"getByLabel\('([^']+)'\)", event.selector)
                if label_match:
                    element_name = label_match.group(1).replace(' ', '')
                else:
                    element_name = event.element_tag.capitalize()
            elif event.selector.startswith('locator'):
                # 从locator中提取信息
                locator_match = re.search(r"locator\('([^']+)'\)", event.selector)
                if locator_match:
                    element_name = locator_match.group(1).replace('#', '').replace('.', '').replace('-', '')[:15]
                else:
                    element_name = event.element_tag.capitalize()
            else:
                element_name = event.element_tag.capitalize()
            
            test_name = f"test{event_suffix}{element_name}{idx}"
            
            lines.extend([
                "",
                f"    @Test",
                f"    public void {test_name}() {{",
            ])
            
            # 将TypeScript选择器转换为Java格式
            java_selector = self._convert_selector_to_java(event.selector)
            
            # 生成对应的操作代码
            if action == 'click':
                lines.append(f"        {java_selector}.click();")
            elif action == 'fill':
                lines.append(f"        {java_selector}.fill(\"test_value\");")
                lines.append(f"        assertEquals(\"test_value\", {java_selector}.inputValue());")
            elif action == 'check':
                lines.append(f"        {java_selector}.check();")
                lines.append(f"        assertTrue({java_selector}.isChecked());")
            elif action == 'blur':
                lines.append(f"        {java_selector}.blur();")
            elif action == 'focus':
                lines.append(f"        {java_selector}.focus();")
            elif action == 'hover':
                lines.append(f"        {java_selector}.hover();")
            elif action == 'dblclick':
                lines.append(f"        {java_selector}.dblclick();")
            else:
                lines.append(f"        {java_selector}.{action}();")
            
            lines.append("    }")
        
        if not component.events:
            lines.append("    // TODO: 暂未检测到可交互元素")
        
        lines.append("}")
        
        return '\n'.join(lines)
    
    def _convert_selector_to_java(self, selector: str) -> str:
        """将TypeScript选择器转换为Java格式"""
        if selector.startswith('getByRole'):
            # getByRole('button', { name: '登录' }) -> page.getByRole(AriaRole.BUTTON, new Page.GetByRoleOptions().setName("登录"))
            role_match = re.search(r"getByRole\('([^']+)'", selector)
            name_match = re.search(r"name: '([^']+)'", selector)
            
            if role_match:
                role = role_match.group(1).upper()
                role_map = {
                    'BUTTON': 'BUTTON',
                    'LINK': 'LINK',
                    'TEXTBOX': 'TEXTBOX',
                    'CHECKBOX': 'CHECKBOX',
                    'RADIO': 'RADIO',
                    'COMBOBOX': 'COMBOBOX',
                    'HEADING': 'HEADING',
                }
                java_role = role_map.get(role, role)
                
                if name_match:
                    name = name_match.group(1)
                    return f"page.getByRole(AriaRole.{java_role}, new Page.GetByRoleOptions().setName(\"{name}\"))"
                else:
                    return f"page.getByRole(AriaRole.{java_role})"
        
        elif selector.startswith('getByText'):
            # getByText('帮助') -> page.getByText("帮助")
            text_match = re.search(r"getByText\('([^']+)'\)", selector)
            if text_match:
                text = text_match.group(1)
                return f"page.getByText(\"{text}\")"
        
        elif selector.startswith('getByLabel'):
            # getByLabel('用户名') -> page.getByLabel("用户名")
            label_match = re.search(r"getByLabel\('([^']+)'\)", selector)
            if label_match:
                label = label_match.group(1)
                return f"page.getByLabel(\"{label}\")"
        
        elif selector.startswith('getByPlaceholder'):
            # getByPlaceholder('请输入用户名') -> page.getByPlaceholder("请输入用户名")
            placeholder_match = re.search(r"getByPlaceholder\('([^']+)'\)", selector)
            if placeholder_match:
                placeholder = placeholder_match.group(1)
                return f"page.getByPlaceholder(\"{placeholder}\")"
        
        elif selector.startswith('getByTestId'):
            # getByTestId('submit-btn') -> page.getByTestId("submit-btn")
            testid_match = re.search(r"getByTestId\('([^']+)'\)", selector)
            if testid_match:
                testid = testid_match.group(1)
                return f"page.getByTestId(\"{testid}\")"
        
        elif selector.startswith('locator'):
            # locator('#submit-btn') -> page.locator("#submit-btn")
            locator_match = re.search(r"locator\('([^']+)'\)", selector)
            if locator_match:
                loc = locator_match.group(1)
                return f"page.locator(\"{loc}\")"
        
        # 默认返回page.locator
        return f"page.locator(\"{selector}\")"

    def _generate_python_test(self, component: VueComponent) -> str:
        lines = [
            "from playwright.sync_api import sync_playwright, expect",
            "import pytest",
            "",
            f"class Test{component.name}:"
        ]
        
        for idx, event in enumerate(component.events, 1):
            config = self.current_parser.events_config.get(event.event_type, {
                'action': 'click',
                'description': event.event_type
            })
            action = config['action']
            description = config['description']
            
            # 生成测试名称
            if 'getByRole' in event.selector or 'getByText' in event.selector:
                name_match = re.search(r"name: '([^']+)'", event.selector)
                if name_match:
                    test_name = f"{description}_{name_match.group(1)}".lower().replace(' ', '_').replace('？', '')
                else:
                    test_name = f"{description}_{event.element_tag}".lower()
            elif 'getByPlaceholder' in event.selector:
                placeholder_match = re.search(r"getByPlaceholder\('([^']+)'\)", event.selector)
                if placeholder_match:
                    test_name = f"{description}_{placeholder_match.group(1)[:10]}".lower().replace(' ', '_')
                else:
                    test_name = f"{description}_{event.element_tag}".lower()
            elif 'getByLabel' in event.selector:
                label_match = re.search(r"getByLabel\('([^']+)'\)", event.selector)
                if label_match:
                    test_name = f"{description}_{label_match.group(1)}".lower().replace(' ', '_')
                else:
                    test_name = f"{description}_{event.element_tag}".lower()
            else:
                test_name = f"{description}_{event.element_tag}".lower()
            
            lines.extend([
                "",
                f"    def test_{test_name}(self):",
                "        with sync_playwright() as p:",
                "            browser = p.chromium.launch()",
                "            page = browser.new_page()"
            ])
            
            # 将TypeScript选择器转换为Python格式
            python_selector = self._convert_selector_to_python(event.selector)
            
            # 生成对应的操作代码
            if action == 'click':
                lines.append(f"            {python_selector}.click()")
            elif action == 'fill':
                lines.append(f"            {python_selector}.fill('test_value')")
                lines.append(f"            expect({python_selector}).to_have_value('test_value')")
            elif action == 'check':
                lines.append(f"            {python_selector}.check()")
                lines.append(f"            expect({python_selector}).to_be_checked()")
            elif action == 'blur':
                lines.append(f"            {python_selector}.blur()")
            elif action == 'focus':
                lines.append(f"            {python_selector}.focus()")
            elif action == 'hover':
                lines.append(f"            {python_selector}.hover()")
            elif action == 'dblclick':
                lines.append(f"            {python_selector}.dblclick()")
            else:
                lines.append(f"            {python_selector}.{action}()")
            
            lines.append("            browser.close()")
        
        if not component.events:
            lines.append("    # TODO: 暂未检测到可交互元素")
        
        return '\n'.join(lines)
    
    def _convert_selector_to_python(self, selector: str) -> str:
        """将TypeScript选择器转换为Python格式"""
        if selector.startswith('getByRole'):
            # getByRole('button', { name: '登录' }) -> page.get_by_role('button', name='登录')
            role_match = re.search(r"getByRole\('([^']+)'", selector)
            name_match = re.search(r"name: '([^']+)'", selector)
            
            if role_match:
                role = role_match.group(1).lower()
                if name_match:
                    name = name_match.group(1)
                    return f"page.get_by_role('{role}', name='{name}')"
                else:
                    return f"page.get_by_role('{role}')"
        
        elif selector.startswith('getByText'):
            # getByText('帮助') -> page.get_by_text('帮助')
            text_match = re.search(r"getByText\('([^']+)'\)", selector)
            if text_match:
                text = text_match.group(1)
                return f"page.get_by_text('{text}')"
        
        elif selector.startswith('getByLabel'):
            # getByLabel('用户名') -> page.get_by_label('用户名')
            label_match = re.search(r"getByLabel\('([^']+)'\)", selector)
            if label_match:
                label = label_match.group(1)
                return f"page.get_by_label('{label}')"
        
        elif selector.startswith('getByPlaceholder'):
            # getByPlaceholder('请输入用户名') -> page.get_by_placeholder('请输入用户名')
            placeholder_match = re.search(r"getByPlaceholder\('([^']+)'\)", selector)
            if placeholder_match:
                placeholder = placeholder_match.group(1)
                return f"page.get_by_placeholder('{placeholder}')"
        
        elif selector.startswith('getByTestId'):
            # getByTestId('submit-btn') -> page.get_by_test_id('submit-btn')
            testid_match = re.search(r"getByTestId\('([^']+)'\)", selector)
            if testid_match:
                testid = testid_match.group(1)
                return f"page.get_by_test_id('{testid}')"
        
        elif selector.startswith('locator'):
            # locator('#submit-btn') -> page.locator('#submit-btn')
            locator_match = re.search(r"locator\('([^']+)'\)", selector)
            if locator_match:
                loc = locator_match.group(1)
                return f"page.locator('{loc}')"
        
        # 默认返回page.locator
        return f"page.locator('{selector}')"

    def generate_router_tests(self, router_file: str, output_dir: Optional[str] = None, language: str = 'typescript') -> str:
        """生成路由测试"""
        routes = self.vue_parser.parse_router(router_file)
        
        if language == 'typescript':
            return self._generate_typescript_router_tests(routes, output_dir)
        elif language == 'java':
            return self._generate_java_router_tests(routes, output_dir)
        else:  # python
            return self._generate_python_router_tests(routes, output_dir)

    def _generate_typescript_router_tests(self, routes: list, output_dir: Optional[str] = None) -> str:
        lines = [
            "import { test, expect } from '@playwright/test';",
            "",
            "test.describe('路由测试', () => {",
            ""
        ]
        
        for route in routes:
            lines.extend([
                f"  test('访问{route.name}页面', async ({' page '}) => {{" ,
                f"    await page.goto('{route.path}');",
                f"    await expect(page).toHaveURL('{route.path}');"
            ])
            
            if route.requires_auth:
                lines.append("    // TODO: 添加登录状态测试")
            
            lines.append("  });")
            lines.append("")
        
        lines.append("});")
        
        test_code = '\n'.join(lines)
        
        if output_dir:
            typescript_dir = os.path.join(output_dir, 'typescript')
            os.makedirs(typescript_dir, exist_ok=True)
            output_file = os.path.join(typescript_dir, 'router.spec.ts')
            self._write_file_with_merge(output_file, test_code, 'typescript')
            return output_file
        
        return test_code

    def _generate_java_router_tests(self, routes: list, output_dir: Optional[str] = None) -> str:
        lines = [
            "import com.microsoft.playwright.*;",
            "import org.junit.jupiter.api.Test;",
            "import static org.junit.jupiter.api.Assertions.*;",
            "",
            "public class RouterTest {",
            "    private Playwright playwright;",
            "    private Browser browser;",
            "    private Page page;",
            "",
            "    @BeforeEach",
            "    public void setUp() {",
            "        playwright = Playwright.create();",
            "        browser = playwright.chromium().launch();",
            "        page = browser.newPage();",
            "    }",
            "",
            "    @AfterEach",
            "    public void tearDown() {",
            "        browser.close();",
            "        playwright.close();",
            "    }"
        ]
        
        for route in routes:
            test_name = f"testVisit{route.name}Page".replace(' ', '')
            lines.extend([
                "",
                f"    @Test",
                f"    public void {test_name}() {{",
                f"        page.navigate(\"{route.path}\");",
                f"        assertEquals(\"{route.path}\", page.url());"
            ])
            
            if route.requires_auth:
                lines.append("        // TODO: 添加登录状态测试")
            
            lines.append("    }")
        
        lines.append("}")
        
        test_code = '\n'.join(lines)
        
        if output_dir:
            java_dir = os.path.join(output_dir, 'java')
            os.makedirs(java_dir, exist_ok=True)
            output_file = os.path.join(java_dir, 'RouterTest.java')
            self._write_file_with_merge(output_file, test_code, 'java')
            return output_file
        
        return test_code

    def _generate_python_router_tests(self, routes: list, output_dir: Optional[str] = None) -> str:
        lines = [
            "import logging",
            "",
            "import pytest",
            "from playwright.sync_api import Page, expect",
            "",
            "logger = logging.getLogger(__name__)",
            "",
            "",
            "class TestRouter:",
            "    logger: logging.Logger  # 由 conftest.py 的 log_config fixture 注入",
            "",
            "    @pytest.fixture(autouse=True)",
            "    def setup(self, page: Page):",
            "        self.page = page",
            "",
        ]

        for route in routes:
            test_name = f"test_visit_{route.name}_page".lower().replace(' ', '_')
            lines.extend([
                f"    def {test_name}(self):",
                f'        """访问{route.name}页面: {route.path}"""',
                f"        self.logger.info('[Router测试] 访问: %s', '{route.path}')",
                f"        self.page.goto('{route.path}')",
                f"        expect(self.page).to_have_url('{route.path}')",
            ])

            if route.requires_auth:
                lines.append('        # TODO: 该页面需要登录，current test will succeed only if user is already authenticated')
                lines.append('        self.logger.info(\'[Router测试] 需要登录验证\')')

            lines.append("")

        test_code = '\n'.join(lines)
        
        test_code = '\n'.join(lines)
        
        if output_dir:
            python_dir = os.path.join(output_dir, 'python', 'test_cases')
            os.makedirs(python_dir, exist_ok=True)
            output_file = os.path.join(python_dir, 'router_test.py')
            self._write_file_with_merge(output_file, test_code, 'python')
            return output_file
        
        return test_code

    def generate_pinia_tests(self, store_file: str, output_dir: Optional[str] = None, language: str = 'typescript') -> str:
        """生成Pinia状态管理测试"""
        stores = self.vue_parser.parse_pinia_store(store_file)
        
        if language == 'typescript':
            return self._generate_typescript_pinia_tests(stores, output_dir)
        elif language == 'java':
            return self._generate_java_pinia_tests(stores, output_dir)
        else:  # python
            return self._generate_python_pinia_tests(stores, output_dir)

    def _generate_typescript_pinia_tests(self, stores: list, output_dir: Optional[str] = None) -> str:
        lines = [
            "import { test, expect } from '@playwright/test';",
            "",
            "test.describe('Pinia状态管理测试', () => {"
        ]
        
        for store in stores:
            lines.append(f"")
            lines.append(f"  test.describe('{store.name} store', () => {{")
            
            # 测试actions
            for action in store.actions:
                lines.append(f"")
                lines.append(f"    test('测试{action}方法', async ({' page '}) => {{")
                lines.append(f"      // TODO: 实现{action}方法测试")
                lines.append(f"    }});")
            
            # 测试getters
            for getter in store.getters:
                lines.append(f"")
                lines.append(f"    test('测试{getter} getter', async ({' page '}) => {{")
                lines.append(f"      // TODO: 实现{getter}测试")
                lines.append(f"    }});")
            
            lines.append(f"  }});")
        
        lines.append("});")
        
        test_code = '\n'.join(lines)
        
        if output_dir:
            typescript_dir = os.path.join(output_dir, 'typescript')
            os.makedirs(typescript_dir, exist_ok=True)
            output_file = os.path.join(typescript_dir, 'pinia.spec.ts')
            self._write_file_with_merge(output_file, test_code, 'typescript')
            return output_file
        
        return test_code

    def _generate_java_pinia_tests(self, stores: list, output_dir: Optional[str] = None) -> str:
        lines = [
            "import org.junit.jupiter.api.Test;",
            "import static org.junit.jupiter.api.Assertions.*;",
            "",
            "public class PiniaTest {"
        ]
        
        for store in stores:
            lines.append(f"")
            lines.append(f"    public static class {store.name}StoreTest {{")
            
            # 测试actions
            for action in store.actions:
                test_name = f"test{action.capitalize()}Method"
                lines.extend([
                    "",
                    f"        @Test",
                    f"        public void {test_name}() {{",
                    f"            // TODO: 实现{action}方法测试",
                    "        }}"
                ])
            
            # 测试getters
            for getter in store.getters:
                test_name = f"test{getter.capitalize()}Getter"
                lines.extend([
                    "",
                    f"        @Test",
                    f"        public void {test_name}() {{",
                    f"            // TODO: 实现{getter}测试",
                    "        }}"
                ])
            
            lines.append("    }")
        
        lines.append("}")
        
        test_code = '\n'.join(lines)
        
        if output_dir:
            java_dir = os.path.join(output_dir, 'java')
            os.makedirs(java_dir, exist_ok=True)
            output_file = os.path.join(java_dir, 'PiniaTest.java')
            self._write_file_with_merge(output_file, test_code, 'java')
            return output_file
        
        return test_code

    def _generate_python_pinia_tests(self, stores: list, output_dir: Optional[str] = None) -> str:
        lines = [
            "import pytest",
            "",
            "class TestPinia:"
        ]
        
        for store in stores:
            class_name = f"Test{store.name.capitalize()}Store"
            lines.extend([
                "",
                f"    class {class_name}:",
            ])
            
            # 测试actions
            if store.actions:
                for action in store.actions:
                    test_name = f"test_{action}".lower()
                    lines.extend([
                        "",
                        f"        def {test_name}(self):",
                        f"            # TODO: 实现{action}方法测试",
                        f"            pass"
                    ])
            else:
                lines.append("        # TODO: 暂未检测到actions")
            
            # 测试getters
            if store.getters:
                for getter in store.getters:
                    test_name = f"test_{getter}".lower()
                    lines.extend([
                        "",
                        f"        def {test_name}(self):",
                        f"            # TODO: 实现{getter}测试",
                        f"            pass"
                    ])
            else:
                lines.append("        # TODO: 暂未检测到getters")
        
        test_code = '\n'.join(lines)
        
        if output_dir:
            python_dir = os.path.join(output_dir, 'python')
            os.makedirs(python_dir, exist_ok=True)
            output_file = os.path.join(python_dir, 'pinia_test.py')
            self._write_file_with_merge(output_file, test_code, 'python')
            return output_file
        
        return test_code

    def detect_component_type(self, file_path: str) -> str:
        """自动检测组件类型 (vue/react)

        检测策略:
        1. 文件扩展名: .vue -> vue, .jsx/.tsx -> react
        2. 文件内容检测:
           - Vue: <template>, defineComponent, ref, reactive from 'vue'
           - React: JSX, useState, useEffect, React import
        """
        file_ext = Path(file_path).suffix.lower()

        if file_ext == '.vue':
            return 'vue'
        elif file_ext in ['.jsx', '.tsx']:
            return 'react'

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read(5000)

            vue_patterns = [
                r'<template',
                r'defineComponent',
                r'from\s+[\'"]vue[\'"]',
                r'import\s+\{[^}]*\b(ref|reactive|computed|watch)\b',
                r'@Component',
                r'vue-tsc',
            ]

            react_patterns = [
                r'import\s+React',
                r'from\s+[\'"]react[\'"]',
                r'\buseState\b',
                r'\buseEffect\b',
                r'\buseRef\b',
                r'\buseCallback\b',
                r'\buseMemo\b',
                r'\bReact\.(createElement|FC|Component)',
                r'\bJSX.Element\b',
                r'\.tsx',
            ]

            vue_score = sum(1 for p in vue_patterns if re.search(p, content))
            react_score = sum(1 for p in react_patterns if re.search(p, content))

            if vue_score > react_score:
                return 'vue'
            elif react_score > vue_score:
                return 'react'
            else:
                return 'vue'
        except:
            return 'vue'

    def generate_component(self, component_file: str):
        """根据文件扩展名和内容自动检测并生成Vue或React组件对象"""
        component_type = self.detect_component_type(component_file)
        if component_type == 'react':
            return self.react_parser.parse_file(component_file)
        else:
            return self.vue_parser.parse_file(component_file)

    def generate_redux_tests(self, reducer_file: str, output_dir: Optional[str] = None, language: str = 'typescript') -> str:
        """生成Redux Reducer测试"""
        reducers = self.react_parser.parse_redux_reducer(reducer_file)

        if language == 'typescript':
            return self._generate_typescript_redux_tests(reducers, output_dir)
        elif language == 'java':
            return self._generate_java_redux_tests(reducers, output_dir)
        else:
            return self._generate_python_redux_tests(reducers, output_dir)

    def _generate_typescript_redux_tests(self, reducers: list, output_dir: Optional[str] = None) -> str:
        lines = [
            "import { test, expect } from '@playwright/test';",
            "",
            "test.describe('Redux Reducer测试', () => {"
        ]

        for reducer in reducers:
            lines.append(f"")
            lines.append(f"  test.describe('{reducer.name}', () => {{")

            for action in reducer.actions:
                lines.append(f"")
                lines.append(f"    test('测试{action} action', async () => {{")
                lines.append(f"      // TODO: 实现{action}测试")
                lines.append(f"    }});")

            lines.append(f"  }});")

        lines.append("});")

        test_code = '\n'.join(lines)

        if output_dir:
            typescript_dir = os.path.join(output_dir, 'typescript')
            os.makedirs(typescript_dir, exist_ok=True)
            output_file = os.path.join(typescript_dir, 'redux.spec.ts')
            self._write_file_with_merge(output_file, test_code, 'typescript')
            return output_file

        return test_code

    def _generate_java_redux_tests(self, reducers: list, output_dir: Optional[str] = None) -> str:
        lines = [
            "import org.junit.jupiter.api.Test;",
            "import static org.junit.jupiter.api.Assertions.*;",
            "",
            "public class ReduxTest {"
        ]

        for reducer in reducers:
            lines.append(f"")
            lines.append(f"    public static class {reducer.name}Test {{")

            for action in reducer.actions:
                test_name = f"test{action.capitalize()}Action"
                lines.extend([
                    "",
                    f"        @Test",
                    f"        public void {test_name}() {{",
                    f"            // TODO: 实现{action}测试",
                    f"        }}"
                ])

            lines.append("    }")

        lines.append("}")

        test_code = '\n'.join(lines)

        if output_dir:
            java_dir = os.path.join(output_dir, 'java')
            os.makedirs(java_dir, exist_ok=True)
            output_file = os.path.join(java_dir, 'ReduxTest.java')
            self._write_file_with_merge(output_file, test_code, 'java')
            return output_file

        return test_code

    def _generate_python_redux_tests(self, reducers: list, output_dir: Optional[str] = None) -> str:
        lines = [
            "import pytest",
            "",
            "class TestRedux:"
        ]

        for reducer in reducers:
            class_name = f"Test{reducer.name.capitalize()}"
            lines.extend([
                "",
                f"    class {class_name}:",
            ])

            if reducer.actions:
                for action in reducer.actions:
                    test_name = f"test_{action.lower()}_action"
                    lines.extend([
                        "",
                        f"        def {test_name}(self):",
                        f"            # TODO: 实现{action}测试",
                        f"            pass"
                    ])
            else:
                lines.append("        # TODO: 暂未检测到actions")

        test_code = '\n'.join(lines)

        if output_dir:
            python_dir = os.path.join(output_dir, 'python')
            os.makedirs(python_dir, exist_ok=True)
            output_file = os.path.join(python_dir, 'redux_test.py')
            self._write_file_with_merge(output_file, test_code, 'python')
            return output_file

        return test_code

    def detect_baw_scenarios(self, component: VueComponent) -> list:
        """检测组件中可能的BAW业务场景"""
        baw_configs = []

        has_username = any('username' in inp.lower() or 'user' in inp.lower() for inp in component.inputs)
        has_password = any('password' in inp.lower() for inp in component.inputs)
        has_login_event = any('login' in event.handler.lower() or 'submit' in event.handler.lower() for event in component.events)
        has_search = any('search' in event.handler.lower() or 'query' in event.handler.lower() for event in component.events)
        has_form_fields = len(component.inputs) >= 2

        if has_username and has_password and has_login_event:
            baw_configs.append(BAWConfig(
                name=f"{component.name}LoginBAW",
                component_name=component.name,
                description="登录流程",
                steps=[
                    BAWStep(pom_class=f"{to_pascal_case(component.name)}Page", method="goto", parameters={}),
                    BAWStep(pom_class=f"{to_pascal_case(component.name)}Page", method="fillUsername", parameters={"username": "username"}),
                    BAWStep(pom_class=f"{to_pascal_case(component.name)}Page", method="fillPassword", parameters={"password": "password"}),
                    BAWStep(pom_class=f"{to_pascal_case(component.name)}Page", method="clickLoginButton", parameters={}),
                ],
                parameters=[
                    {"name": "username", "type": "string", "default": "test_user"},
                    {"name": "password", "type": "string", "default": "test_password"},
                ]
            ))

        if has_search and len(component.events) >= 1:
            baw_configs.append(BAWConfig(
                name=f"{component.name}SearchBAW",
                component_name=component.name,
                description="搜索流程",
                steps=[
                    BAWStep(pom_class=f"{to_pascal_case(component.name)}Page", method="goto", parameters={}),
                    BAWStep(pom_class=f"{to_pascal_case(component.name)}Page", method="fillSearchInput", parameters={"keyword": "keyword"}),
                    BAWStep(pom_class=f"{to_pascal_case(component.name)}Page", method="clickSearchButton", parameters={}),
                ],
                parameters=[
                    {"name": "keyword", "type": "string", "default": "test keyword"},
                ]
            ))

        if has_form_fields and has_login_event and not (has_username and has_password):
            baw_configs.append(BAWConfig(
                name=f"{component.name}SubmitFormBAW",
                component_name=component.name,
                description="表单提交流程",
                steps=[
                    BAWStep(pom_class=f"{to_pascal_case(component.name)}Page", method="goto", parameters={}),
                ] + [
                    BAWStep(pom_class=f"{to_pascal_case(component.name)}Page", method=f"fill{to_pascal_case(inp)}Input", parameters={inp: inp}) 
                    for inp in component.inputs
                ] + [
                    BAWStep(pom_class=f"{to_pascal_case(component.name)}Page", method="clickSubmitButton", parameters={}),
                ],
                parameters=[{"name": inp, "type": "string", "default": f"test_{inp}"} for inp in component.inputs]
            ))

        return baw_configs

    def generate_baw(self, component: VueComponent, language: str, output_dir: Optional[str] = None) -> str:
        """生成BAW类"""
        # 生成对应的POM文件，确保BAW需要的方法都存在
        if output_dir:
            if language == 'typescript':
                self._generate_typescript_pom_file(component, output_dir)
            elif language == 'java':
                self._generate_java_pom_file(component, output_dir)
            elif language == 'python':
                self._generate_python_pom_file(component, output_dir)
        
        baw_configs = self.detect_baw_scenarios(component)
        
        if not baw_configs:
            return ""
        
        if language == 'typescript':
            return self._generate_typescript_baw(component, baw_configs, output_dir)
        elif language == 'java':
            return self._generate_java_baw(component, baw_configs, output_dir)
        elif language == 'python':
            return self._generate_python_baw(component, baw_configs, output_dir)
        
        return ""

    def _generate_typescript_baw(self, component: VueComponent, baw_configs: list, output_dir: Optional[str] = None) -> str:
        """生成TypeScript BAW"""
        page_class = f"{to_pascal_case(component.name)}Page"
        lines = [
            "import { Page } from '@playwright/test';",
            f"import {{ {page_class} }} from '../pages/{to_kebab_case(component.name)}.page';",
            "",
        ]
        
        for baw_config in baw_configs:
            page_class = f"{to_pascal_case(component.name)}Page"
            lines.extend([
                f"/**",
                f" * {baw_config.description}",
                f" * 组合POM操作：{' → '.join([step.method for step in baw_config.steps])}",
                f" */",
                f"export class {baw_config.name} {{",
                f"  private {to_camel_case(page_class)}: {page_class};",
                "",
                f"  constructor(page: Page) {{",
                f"    this.{to_camel_case(page_class)} = new {page_class}(page);",
                f"  }}",
                "",
                f"  /**",
                f"   * 执行{baw_config.description}",
            ])
            
            param_declarations = []
            param_args = []
            for param in baw_config.parameters:
                param_declarations.append(f"   * @param {param['name']} {param['type']}")
                param_args.append(f"{param['name']}: {param['type']}")
            
            lines.append(f"   */")
            lines.append(f"  async execute({', '.join(param_args)}): Promise<void> {{")
            
            for i, step in enumerate(baw_config.steps, 1):
                if step.parameters:
                    for param_name, param_value in step.parameters.items():
                        lines.append(f"    // {i}. {step.method}")
                        lines.append(f"    await this.{to_camel_case(page_class)}.{step.method}({param_name});")
                else:
                    lines.append(f"    // {i}. {step.method}")
                    lines.append(f"    await this.{to_camel_case(page_class)}.{step.method}();")
            
            lines.extend([
                f"  }}",
                f"}}",
                ""
            ])
        
        baw_code = '\n'.join(lines)
        
        if output_dir:
            ts_dir = os.path.join(output_dir, 'typescript', 'baw')
            os.makedirs(ts_dir, exist_ok=True)
            output_file = os.path.join(ts_dir, f'{to_kebab_case(component.name)}.baw.ts')
            self._write_file_with_merge(output_file, baw_code, 'typescript')
            return output_file
        
        return baw_code

    def _generate_java_baw(self, component: VueComponent, baw_configs: list, output_dir: Optional[str] = None) -> str:
        """生成Java BAW"""
        lines = [
            "import com.microsoft.playwright.Page;",
            f"import pages.{to_pascal_case(component.name)}Page;",
            "",
        ]
        
        for baw_config in baw_configs:
            page_class = f"{to_pascal_case(component.name)}Page"
            lines.extend([
                f"/**",
                f" * {baw_config.description}",
                f" * 组合POM操作：{' → '.join([step.method for step in baw_config.steps])}",
                f" */",
                f"public class {baw_config.name} {{",
                f"    private final {page_class} {to_camel_case(page_class)};",
                "",
                f"    public {baw_config.name}(Page page) {{",
                f"        this.{to_camel_case(page_class)} = new {page_class}(page);",
                f"    }}",
                "",
                f"    /**",
                f"     * 执行{baw_config.description}",
            ])
            
            param_declarations = []
            param_args = []
            for param in baw_config.parameters:
                param_declarations.append(f"     * @param {param['name']} {param['type']}")
                param_args.append(f"String {param['name']}")
            
            lines.append(f"     */")
            lines.append(f"    public void execute({', '.join(param_args)}) {{")
            
            for i, step in enumerate(baw_config.steps, 1):
                if step.parameters:
                    for param_name, param_value in step.parameters.items():
                        lines.append(f"        // {i}. {step.method}")
                        lines.append(f"        {to_camel_case(page_class)}.{step.method}({param_name});")
                else:
                    lines.append(f"        // {i}. {step.method}")
                    lines.append(f"        {to_camel_case(page_class)}.{step.method}();")
            
            lines.extend([
                f"    }}",
                f"}}",
                ""
            ])
        
        baw_code = '\n'.join(lines)
        
        if output_dir:
            java_dir = os.path.join(output_dir, 'java', 'baw')
            os.makedirs(java_dir, exist_ok=True)
            output_file = os.path.join(java_dir, f'{to_pascal_case(component.name)}BAW.java')
            self._write_file_with_merge(output_file, baw_code, 'java')
            return output_file
        
        return baw_code

    def _generate_python_baw(self, component: VueComponent, baw_configs: list, output_dir: Optional[str] = None) -> str:
        """生成Python BAW（含日志）"""
        lines = [
            "import logging",
            "from playwright.sync_api import Page, expect",
            f"from pages.{to_snake_case(component.name)}_page import {to_pascal_case(component.name)}Page",
            "",
            "logger = logging.getLogger(__name__)",
            "",
        ]

        for baw_config in baw_configs:
            page_class = f"{to_pascal_case(component.name)}Page"
            lines.extend([
                f"class {baw_config.name}:",
                f"    \"\"\"{baw_config.description}\"\"\"",
                "",
                f"    def __init__(self, page: Page):",
                f"        self.{to_snake_case(page_class)} = {page_class}(page)",
                "",
            ])

            param_parts = []
            for param in baw_config.parameters:
                param_parts.append(f"{param['name']}: str = '{param['default']}'")

            lines.append(f"    def execute(self, {', '.join(param_parts)}):")
            lines.append(f'        """')
            lines.append(f'        执行{baw_config.description}')
            lines.append(f'        """')
            lines.append(f"        logger.info('[BAW] 开始执行: {baw_config.description}')")

            for i, step in enumerate(baw_config.steps, 1):
                if step.parameters:
                    for param_name, param_value in step.parameters.items():
                        method_name = to_snake_case(step.method)
                        lines.append(f"        logger.info('[BAW]   step {i}/{len(baw_config.steps)}: {method_name}({param_name}={{{param_name}}})')")
                        lines.append(f"        self.{to_snake_case(page_class)}.{method_name}({param_name})")
                else:
                    method_name = to_snake_case(step.method)
                    lines.append(f"        logger.info('[BAW]   step {i}/{len(baw_config.steps)}: {method_name}')")
                    lines.append(f"        self.{to_snake_case(page_class)}.{method_name}()")

            lines.append(f"        logger.info('[BAW] 完成: {baw_config.description}')")
            
            lines.extend([
                "",
                ""
            ])
        
        baw_code = '\n'.join(lines)
        
        if output_dir:
            python_dir = os.path.join(output_dir, 'python', 'baw')
            os.makedirs(python_dir, exist_ok=True)
            output_file = os.path.join(python_dir, f'{to_snake_case(component.name)}_baw.py')
            self._write_file_with_merge(output_file, baw_code, 'python')
            return output_file

        return baw_code

    # -------- Scaffold: external site test skeleton (not from Vue/React) --------

    def generate_scaffold(self, name: str, base_url: str, output_dir: str, language: str = 'python', snapshot: bool = False, force: bool = False):
        """为外部网站生成 POM + BAW + Test 脚手架（不会覆盖已有文件）"""
        # 先检查文件是否已存在
        import os.path
        if language == 'python':
            test_file = os.path.join(output_dir, 'python', 'test_cases', f'test_{to_snake_case(name)}.py')
            pom_file = os.path.join(output_dir, 'python', 'pages', f'{to_snake_case(name)}_page.py')
            baw_file = os.path.join(output_dir, 'python', 'baw', f'{to_snake_case(name)}_baw.py')
            conftest_file = os.path.join(output_dir, 'python', 'conftest.py')
            all_files = [test_file, pom_file, baw_file]
            if not os.path.exists(conftest_file):
                all_files.append(conftest_file)  # conftest 不存在时也会生成
        elif language == 'typescript':
            test_file = os.path.join(output_dir, 'typescript', f'{to_kebab_case(name)}.spec.ts')
            pom_file = os.path.join(output_dir, 'typescript', 'pages', f'{to_kebab_case(name)}.page.ts')
            baw_file = os.path.join(output_dir, 'typescript', 'baw', f'{to_kebab_case(name)}.baw.ts')
        else:
            test_file = os.path.join(output_dir, 'java', f'{to_pascal_case(name)}Test.java')
            pom_file = os.path.join(output_dir, 'java', 'pages', f'{to_pascal_case(name)}Page.java')
            baw_file = os.path.join(output_dir, 'java', 'baw', f'{to_pascal_case(name)}BAW.java')

        if not force:
            existing = [f for f in [test_file, pom_file, baw_file] if os.path.exists(f)]
            if existing:
                print('[提示] 以下文件已存在，跳过（不会覆盖已有内容）:')
                for f in existing:
                    print('  - %s' % f)
                print('如需重新生成，请先手动删除这些文件，或加 --force 参数强制覆盖')
                return '%s (已存在，跳过)' % test_file

        if language == 'python':
            # 自动生成配置文件 + conftest.py
            config_file = self._generate_config_toml(output_dir)
            conftest_file = self._generate_conftest_python(output_dir)
            pom_file = self._generate_scaffold_pom_python(name, base_url, output_dir)
            baw_file = self._generate_scaffold_baw_python(name, output_dir)
            test_file = self._generate_scaffold_test_python(name, output_dir, snapshot)
            return f'{test_file} (POM: {pom_file}, BAW: {baw_file}, config: {config_file})'
        elif language == 'typescript':
            pom_file = self._generate_scaffold_pom_typescript(name, base_url, output_dir)
            baw_file = self._generate_scaffold_baw_typescript(name, output_dir)
            test_file = self._generate_scaffold_test_typescript(name, output_dir)
            return f'{test_file} (POM: {pom_file}, BAW: {baw_file})'
        else:
            pom_file = self._generate_scaffold_pom_java(name, base_url, output_dir)
            baw_file = self._generate_scaffold_baw_java(name, output_dir)
            test_file = self._generate_scaffold_test_java(name, output_dir)
            return f'{test_file} (POM: {pom_file}, BAW: {baw_file})'

    def _generate_scaffold_pom_python(self, name: str, base_url: str, output_dir: str) -> str:
        cls_name = to_pascal_case(name) + 'Page'
        file_name = to_snake_case(name)
        lines = [
            "from playwright.sync_api import Page",
            "",
            "",
            f'class {cls_name}:',
            f'    """{to_pascal_case(name)}页面对象模型"""',
            '',
            '    def __init__(self, page: Page):',
            '        self.page = page',
            '',
            '    def goto(self):',
            f'        """导航到目标页面"""',
            f"        self.page.goto('{base_url}')",
            '',
            '    # TODO: 在此添加页面元素定位器和操作方法',
            '    # 示例:',
            '    # self.search_box = page.get_by_role(\'searchbox\')',
            '    # self.search_button = page.get_by_role(\'button\', name=\'搜索\')',
            '',
        ]
        os.makedirs(os.path.join(output_dir, 'python', 'pages'), exist_ok=True)
        out = os.path.join(output_dir, 'python', 'pages', f'{file_name}_page.py')
        self._write_file_with_merge(out, '\n'.join(lines), 'python')
        return out

    def _generate_scaffold_baw_python(self, name: str, output_dir: str) -> str:
        cls_name = to_pascal_case(name) + 'BAW'
        page_cls = to_pascal_case(name) + 'Page'
        page_var = to_snake_case(name) + '_page'
        file_name = to_snake_case(name)
        lines = [
            "import logging",
            "from playwright.sync_api import Page",
            f"from pages.{file_name}_page import {page_cls}",
            "",
            "logger = logging.getLogger(__name__)",
            "",
            f'class {cls_name}:',
            f'    """{to_pascal_case(name)}业务流程"""',
            '',
            f'    def __init__(self, page: Page):',
            f'        self.logger = logging.getLogger(__name__)',
            f'        self.{page_var} = {page_cls}(page)',
            '',
            '    def execute(self):',
            '        """执行业务流程"""',
            "        self.logger.info('[BAW] 开始执行')",
            f'        self.{page_var}.goto()',
            '        # TODO: 在此添加业务流程步骤',
            "        self.logger.info('[BAW] 完成')",
            '',
        ]
        os.makedirs(os.path.join(output_dir, 'python', 'baw'), exist_ok=True)
        out = os.path.join(output_dir, 'python', 'baw', f'{file_name}_baw.py')
        self._write_file_with_merge(out, '\n'.join(lines), 'python')
        return out

    def _generate_scaffold_test_python(self, name: str, output_dir: str, snapshot: bool = False) -> str:
        cls_name = to_pascal_case(name) + 'Page'
        baw_name = to_pascal_case(name) + 'BAW'
        page_cls = cls_name
        page_var = to_snake_case(name) + '_page'
        baw_var = to_snake_case(name) + '_baw'
        file_name = to_snake_case(name)
        lines = [
            "import logging",
            "",
            "import pytest",
            "from playwright.sync_api import Page, expect",
            f"from pages.{file_name}_page import {page_cls}",
            f"from baw.{file_name}_baw import {baw_name}",
            "",
            "",
            f'class Test{to_pascal_case(name)}:',
            f'    """{to_pascal_case(name)}测试"""',
            '    logger: logging.Logger  # 由 conftest.py 的 log_config fixture 注入',
            '',
            '    @pytest.fixture(autouse=True)',
            '    def setup(self, page: Page):',
            '        self.page = page',
            f'        self.{page_var} = {page_cls}(page)',
            f'        self.{baw_var} = {baw_name}(page)',
            '',
            '    def test_basic_flow(self):',
            '        """基础流程测试"""',
            "        self.logger.info('[TEST] 执行基础流程')",
            f'        self.{baw_var}.execute()',
            '        # TODO: 在此添加断言',
            "        self.logger.info('[TEST] 验证通过')",
            '',
        ]

        # snapshot 模式：添加截图断言，图片按用例存储
        if snapshot:
            snap_name = f'{file_name}_basic_flow'
            lines.insert(-1, f'        self.logger.info("[TEST] Snapshot验证: {snap_name}")')
            lines.insert(-1, f'        snap_path.parent.mkdir(parents=True, exist_ok=True)')
            lines.insert(-1, f'        self.page.screenshot(path=str(snap_path), full_page=True)')
            # Write the snapshot variable definition before the code block
            snap_var_code = f'        snap_path = Path("__snapshots__") / "{file_name}" / "{snap_name}.png"'
            lines.insert(-1, snap_var_code)
            # Ensure Path import exists at top of file
            # 确保有 Path 导入
            has_path = any('from pathlib import Path' in l for l in lines)
            if not has_path:
                lines.insert(0, 'from pathlib import Path')

        os.makedirs(os.path.join(output_dir, 'python'), exist_ok=True)
        out = os.path.join(output_dir, 'python', 'test_cases', f'test_{file_name}.py')
        self._write_file_with_merge(out, '\n'.join(lines), 'python')
        return out

    def _generate_scaffold_pom_typescript(self, name: str, base_url: str, output_dir: str) -> str:
        cls_name = to_pascal_case(name) + 'Page'
        file_name = to_kebab_case(name)
        lines = [
            "import { type Page, type Locator } from '@playwright/test';",
            "",
            f'export class {cls_name} {{',
            '  readonly page: Page;',
            '',
            f'  constructor(page: Page) {{',
            '    this.page = page;',
            '  }',
            '',
            '  async goto() {',
            f"    await this.page.goto('{base_url}');",
            '  }',
            '}',
            '',
        ]
        os.makedirs(os.path.join(output_dir, 'typescript', 'pages'), exist_ok=True)
        out = os.path.join(output_dir, 'typescript', 'pages', f'{file_name}.page.ts')
        self._write_file_with_merge(out, '\n'.join(lines), 'typescript')
        return out

    def _generate_scaffold_baw_typescript(self, name: str, output_dir: str) -> str:
        cls_name = to_pascal_case(name) + 'BAW'
        page_cls = to_pascal_case(name) + 'Page'
        page_var = to_camel_case(name) + 'Page'
        file_name = to_kebab_case(name)
        lines = [
            "import { Page } from '@playwright/test';",
            f"import {{ {page_cls} }} from '../pages/{file_name}.page';",
            "",
            f'export class {cls_name} {{',
            f'  private {page_var}: {page_cls};',
            '',
            f'  constructor(page: Page) {{',
            f'    this.{page_var} = new {page_cls}(page);',
            '  }',
            '',
            '  async execute(): Promise<void> {',
            f'    await this.{page_var}.goto();',
            '  }',
            '}',
            '',
        ]
        os.makedirs(os.path.join(output_dir, 'typescript', 'baw'), exist_ok=True)
        out = os.path.join(output_dir, 'typescript', 'baw', f'{file_name}.baw.ts')
        self._write_file_with_merge(out, '\n'.join(lines), 'typescript')
        return out

    def _generate_scaffold_test_typescript(self, name: str, output_dir: str) -> str:
        page_cls = to_pascal_case(name) + 'Page'
        baw_name = to_pascal_case(name) + 'BAW'
        page_var = to_camel_case(name) + 'Page'
        baw_var = to_camel_case(name) + 'BAW'
        file_name = to_kebab_case(name)
        lines = [
            "import { test, expect } from '@playwright/test';",
            f"import {{ {page_cls} }} from './pages/{file_name}.page';",
            f"import {{ {baw_name} }} from './baw/{file_name}.baw';",
            "",
            f"test.describe('{to_pascal_case(name)}', () => {{",
            f'  test("basic flow", async ({{ page }}) => {{',
            f'    const {baw_var} = new {baw_name}(page);',
            f'    await {baw_var}.execute();',
            '  });',
            '});',
            '',
        ]
        os.makedirs(os.path.join(output_dir, 'typescript'), exist_ok=True)
        out = os.path.join(output_dir, 'typescript', f'{file_name}.spec.ts')
        self._write_file_with_merge(out, '\n'.join(lines), 'typescript')
        return out

    def _generate_config_toml(self, output_dir: str) -> str:
        """生成 test_config.toml 配置文件"""
        lines = [
            "[browser]",
            '# 浏览器通道：chrome, msedge, chromium, firefox',
            'channel = "chrome"',
            '# 默认无头模式（false=有头模式运行，true=后台无头运行）',
            'headless = false',
            '',
            '[logging]',
            '# 日志输出目录（相对于 tests/）',
            'directory = "logs"',
            '# 日志格式',
            'format = "%(asctime)s [%(levelname)s] %(message)s"',
            '# 日志级别：DEBUG, INFO, WARNING, ERROR',
            'level = "INFO"',
            '',
            '[environment]',
            '# 被测应用的基 URL，POM 的 goto() 会拼接此地址',
            '# 空字符串表示直接使用 goto(path) 的相对路径',
            'base_url = ""',
            '',
        ]
        os.makedirs(os.path.join(output_dir, 'python'), exist_ok=True)
        out = os.path.join(output_dir, 'python', 'test_config.toml')
        # 配置文件不用 AUTO-GENERATED 标记，直接写入
        with open(out, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines) + '\n')
        return out

    def _generate_conftest_python(self, output_dir: str) -> str:
        """生成 conftest.py（从 test_config.toml 读取配置）"""
        lines = [
            '"""pytest 全局配置：从 test_config.toml 读取配置"""',
            "",
            "import logging",
            "import tomllib",
            "from datetime import datetime",
            "from pathlib import Path",
            "",
            "import pytest",
            "",
            "",
            "# -------- 加载配置文件 --------",
            "_config_path = Path(__file__).parent / 'test_config.toml'",
            "if _config_path.exists():",
            "    with open(_config_path, 'rb') as f:",
            "        CFG = tomllib.load(f)",
            "else:",
            "    CFG = {}",
            "",
            "",
            "# -------- 浏览器配置 --------",
            "_launch_args = {}",
            "_browser_cfg = CFG.get('browser', {})",
            "if _browser_cfg.get('channel'):",
            "    _launch_args['channel'] = _browser_cfg['channel']",
            "if _browser_cfg.get('headless') is not None:",
            "    _launch_args['headless'] = _browser_cfg['headless']",
            "",
            "",
            "@pytest.fixture(scope='session')",
            "def browser_type_launch_args():",
            '    """从 test_config.toml 读取浏览器通道配置"""',
            "    return dict(_launch_args)",
            "",
            "",
            "# -------- 环境配置 --------",
            "# 将 base_url 注入环境变量，供 POM 的 goto() 读取",
            "_env_cfg = CFG.get('environment', {})",
            "if _env_cfg.get('base_url'):",
            "    import os",
            "    os.environ.setdefault('BASE_URL', _env_cfg['base_url'])",
            "",
            "",
            "# -------- 日志配置 --------",
            "_log_cfg = CFG.get('logging', {})",
            "_LOG_DIR = _log_cfg.get('directory', 'logs')",
            "_LOG_FORMAT = _log_cfg.get('format', '%(asctime)s [%(levelname)s] %(message)s')",
            "_LOG_LEVEL = getattr(logging, _log_cfg.get('level', 'INFO').upper(), logging.INFO)",
            "",
            "",
            "@pytest.fixture(scope='session', autouse=True)",
            "def log_dir():",
            '    """每个测试会话创建带时间戳的日志目录"""',
            "    dir_path = Path(_LOG_DIR) / datetime.now().strftime('%Y%m%d_%H%M%S')",
            "    dir_path.mkdir(parents=True, exist_ok=True)",
            "    return dir_path",
            "",
            "",
            "@pytest.fixture(autouse=True)",
            "def log_config(request, log_dir):",
            '    """',
            "    自动为每个测试用例配置文件日志",
            "",
            "    日志文件路径: logs/YYYYMMDD_HHMMSS/{test_name}.log",
            "    测试类通过 self.logger 使用",
            '    """',
            "    log_file = log_dir / f'{request.node.name.split(chr(91))[0]}.log'",
            "",
            "    logging.root.handlers.clear()",
            "    logging.basicConfig(",
            "        level=_LOG_LEVEL,",
            "        filename=str(log_file),",
            "        encoding='utf-8',",
            "        format=_LOG_FORMAT,",
            "        filemode='w'",
            "    )",
            "",
            "    logger = logging.getLogger('test')",
            "    logger.info('=' * 60)",
            "    logger.info('[TEST] 测试开始: %s', request.node.name)",
            "    logger.info('=' * 60)",
            "",
            "    request.instance.logger = logger",
            "    yield",
            "",
            "    logger.info('[TEST] 测试结束')",
            "    logger.info('=' * 60)",
            "",
        ]
        os.makedirs(os.path.join(output_dir, 'python'), exist_ok=True)
        out = os.path.join(output_dir, 'python', 'conftest.py')
        self._write_file_with_merge(out, '\n'.join(lines), 'python')
        return out

    def _generate_scaffold_pom_java(self, name: str, base_url: str, output_dir: str) -> str:
        cls_name = to_pascal_case(name) + 'Page'
        var_name = to_camel_case(name) + 'Page'
        lines = [
            "import com.microsoft.playwright.*;",
            "",
            f'public class {cls_name} {{',
            '    private final Page page;',
            '',
            f'    public {cls_name}(Page page) {{',
            '        this.page = page;',
            '    }',
            '',
            '    public void gotoPage() {',
            f'        page.navigate("{base_url}");',
            '    }',
            '}',
            '',
        ]
        os.makedirs(os.path.join(output_dir, 'java', 'pages'), exist_ok=True)
        out = os.path.join(output_dir, 'java', 'pages', f'{cls_name}.java')
        self._write_file_with_merge(out, '\n'.join(lines), 'java')
        return out

    def _generate_scaffold_baw_java(self, name: str, output_dir: str) -> str:
        cls_name = to_pascal_case(name) + 'BAW'
        page_cls = to_pascal_case(name) + 'Page'
        page_var = to_camel_case(name) + 'Page'
        lines = [
            "import com.microsoft.playwright.Page;",
            f"import pages.{page_cls};",
            "",
            f'public class {cls_name} {{',
            f'    private final {page_cls} {page_var};',
            '',
            f'    public {cls_name}(Page page) {{',
            f'        this.{page_var} = new {page_cls}(page);',
            '    }',
            '',
            '    public void execute() {',
            f'        {page_var}.gotoPage();',
            '    }',
            '}',
            '',
        ]
        os.makedirs(os.path.join(output_dir, 'java', 'baw'), exist_ok=True)
        out = os.path.join(output_dir, 'java', 'baw', f'{cls_name}.java')
        self._write_file_with_merge(out, '\n'.join(lines), 'java')
        return out

    def _generate_scaffold_test_java(self, name: str, output_dir: str) -> str:
        cls_name = to_pascal_case(name) + 'Test'
        page_cls = to_pascal_case(name) + 'Page'
        baw_name = to_pascal_case(name) + 'BAW'
        page_var = to_camel_case(name) + 'Page'
        baw_var = to_camel_case(name) + 'BAW'
        lines = [
            "import com.microsoft.playwright.*;",
            "import org.junit.jupiter.api.*;",
            f"import pages.{page_cls};",
            f"import baw.{baw_name};",
            "",
            f'public class {cls_name} {{',
            '    private Playwright playwright;',
            '    private Browser browser;',
            '    private Page page;',
            f'    private {baw_name} {baw_var};',
            '',
            '    @BeforeEach',
            '    public void setUp() {',
            '        playwright = Playwright.create();',
            '        browser = playwright.chromium().launch();',
            '        page = browser.newPage();',
            f'        {baw_var} = new {baw_name}(page);',
            '    }',
            '',
            '    @AfterEach',
            '    public void tearDown() {',
            '        browser.close();',
            '        playwright.close();',
            '    }',
            '',
            '    @Test',
            '    public void testBasicFlow() {',
            f'        {baw_var}.execute();',
            '    }',
            '}',
            '',
        ]
        os.makedirs(os.path.join(output_dir, 'java'), exist_ok=True)
        out = os.path.join(output_dir, 'java', f'{cls_name}.java')
        self._write_file_with_merge(out, '\n'.join(lines), 'java')
        return out


def ensure_python_deps(verbose: bool = False):
    import importlib, subprocess, sys

    required_packages = [
        ('playwright', 'playwright'),
        ('pytest', 'pytest'),
    ]
    missing = []
    for module_name, pkg_name in required_packages:
        try:
            importlib.import_module(module_name)
        except ImportError:
            missing.append(pkg_name)

    if missing:
        missing_str = ', '.join(missing)
        print('[依赖] 检测到缺失依赖: %s，正在自动安装...' % missing_str)
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'install'] + missing + ['pytest-playwright>=0.4.0'],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            print('[警告] 依赖安装失败: %s' % result.stderr.strip())
            print('   请手动运行: pip install %s pytest-playwright' % ' '.join(missing))
        elif verbose:
            print('[完成] 依赖安装完成')

    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            _ = p.chromium
    except Exception:
        print('[浏览器] 检测到 Playwright 浏览器未安装，正在自动安装 Chromium...')
        result = subprocess.run(
            [sys.executable, '-m', 'playwright', 'install', 'chromium'],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            print('[警告] Chromium 安装失败: %s' % result.stderr.strip())
            print('   请手动运行: playwright install chromium')
        elif verbose:
            print('[完成] Chromium 浏览器安装完成')


def main():
    import argparse
    import sys

    parser = argparse.ArgumentParser(description='Vue/React to Playwright Test Generator')
    parser.add_argument('input', nargs='?', default=None, help='Vue/React组件文件路径、目录或路由/状态管理配置文件')
    parser.add_argument('-o', '--output', help='输出目录', default='./tests')
    parser.add_argument('-v', '--verbose', action='store_true', help='显示详细信息')
    parser.add_argument('--router', action='store_true', help='生成路由测试')
    parser.add_argument('--store', action='store_true', help='生成Pinia状态管理测试')
    parser.add_argument('--redux', action='store_true', help='生成Redux状态管理测试')
    parser.add_argument('--language', choices=['typescript', 'java', 'python'], default='typescript', help='输出语言')
    parser.add_argument('--no-pom', action='store_true', help='不生成Page Object Model')
    parser.add_argument('--generate-baw', action='store_true', help='生成BAW（Business Action Workflow）')
    parser.add_argument('--baw-only', action='store_true', help='仅生成BAW，不生成测试')
    parser.add_argument('--install-deps', action='store_true', default=True,
                        help='自动安装缺失的依赖（默认开启，仅对 Python 语言有效）')
    parser.add_argument('--scaffold', type=str, default=None,
                        help='为外部站点生成测试脚手架（指定站点名称，配合 --base-url 使用）')
    parser.add_argument('--base-url', type=str, default=None,
                        help='外部站点的基 URL（配合 --scaffold 使用）')
    parser.add_argument('--snapshot', action='store_true', default=False,
                        help='生成截图断言（Snapshot），页面加载后截图比对基线')
    parser.add_argument('--force', action='store_true', default=False,
                        help='强制覆盖已有文件（配合 --scaffold 使用）')
    parser.add_argument('--all', action='store_true', default=False,
                        help='批量扫描 front-end-code/ 目录，生成所有组件/Router/Store 测试')

    args = parser.parse_args()

    # Fix GBK stdout encoding for Chinese output on Windows
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')

    generator = PlaywrightGenerator()

    # Scaffold mode: generate external site test skeleton
    if args.scaffold:
        if not args.base_url:
            print('错误: --scaffold 需要 --base-url 参数')
            return
        if args.language == 'python' and args.install_deps:
            ensure_python_deps(args.verbose)
        out = generator.generate_scaffold(args.scaffold, args.base_url, args.output, args.language, args.snapshot, args.force)
        print('生成: %s' % out)
        return

    # 自动安装 Python 依赖
    if args.language == 'python' and args.install_deps:
        ensure_python_deps(args.verbose)

    generate_pom = not args.no_pom

    # --all 模式：批量扫描 front-end-code/ 目录
    if args.all:
        base_dir = 'front-end-code'
        print('[批量模式] 扫描目录: %s' % base_dir)

        # 1. 扫描 Vue 组件
        vue_files = list(Path(base_dir).rglob('*.vue'))
        # 2. 扫描 React 组件
        react_files = list(Path(base_dir).rglob('*.tsx')) + list(Path(base_dir).rglob('*.jsx'))
        # 3. 扫描 Router 文件
        router_files = list(Path(base_dir).rglob('router/index.ts')) + list(Path(base_dir).rglob('router/index.js')) + list(Path(base_dir).rglob('App.tsx'))
        # 4. 扫描 Store 文件
        store_files = list(Path(base_dir).rglob('stores/*.ts')) + list(Path(base_dir).rglob('stores/*.js'))

        if args.language == 'python' and args.install_deps:
            ensure_python_deps(args.verbose)

        for rf in router_files:
            out = generator.generate_router_tests(str(rf), args.output, args.language)
            print('  路由: %s' % out)
        for sf in store_files:
            out = generator.generate_pinia_tests(str(sf), args.output, args.language)
            print('  Store: %s' % out)
        for vf in vue_files + react_files:
            out = generator.generate_from_file(str(vf), args.output, args.language, generate_pom)
            print('  组件: %s' % out)
        return

    if not args.input:
        parser.print_help()
        return

    if args.redux or 'reducer' in args.input.lower():
        output_path = generator.generate_redux_tests(args.input, args.output, args.language)
        print(f'生成Redux测试: {output_path}')
    elif args.router or args.input.endswith('router/index.ts') or args.input.endswith('router/index.js') or args.input.endswith('App.tsx') or args.input.endswith('App.jsx'):
        output_path = generator.generate_router_tests(args.input, args.output, args.language)
        print(f'生成路由测试: {output_path}')
    elif args.store or 'stores' in args.input:
        output_path = generator.generate_pinia_tests(args.input, args.output, args.language)
        print(f'生成状态管理测试: {output_path}')
    elif os.path.isdir(args.input):
        vue_files = list(Path(args.input).rglob('*.vue'))
        react_files = list(Path(args.input).rglob('*.tsx')) + list(Path(args.input).rglob('*.jsx'))
        all_files = vue_files + react_files

        for component_file in all_files:
            if args.verbose:
                print(f'处理: {component_file}')

            output_path = generator.generate_from_file(str(component_file), args.output, args.language, generate_pom)
            print(f'生成: {output_path}')

            if args.generate_baw or args.baw_only:
                component = generator.generate_component(str(component_file))
                if args.baw_only:
                    baw_path = generator.generate_baw(component, args.language, args.output)
                    if baw_path:
                        print(f'生成BAW: {baw_path}')
                else:
                    baw_path = generator.generate_baw(component, args.language, args.output)
                    if baw_path:
                        print(f'生成BAW: {baw_path}')
    else:
        output_path = generator.generate_from_file(args.input, args.output, args.language, generate_pom)
        print(f'生成: {output_path}')

        if args.generate_baw or args.baw_only:
            component = generator.generate_component(args.input)
            if args.baw_only:
                baw_path = generator.generate_baw(component, args.language, args.output)
                if baw_path:
                    print(f'生成BAW: {baw_path}')
            else:
                baw_path = generator.generate_baw(component, args.language, args.output)
                if baw_path:
                    print(f'生成BAW: {baw_path}')


if __name__ == '__main__':
    main()
