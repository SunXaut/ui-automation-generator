"""
BAW (Business Action Workflow) 生成器
生成 TypeScript 和 Python 的业务操作流程
"""

from typing import List, Dict, Optional
from dataclasses import dataclass, field
from src.parser.vue_parser import VueComponent, VueElement
from src.utils.naming_service import NamingService
from src.utils.identifier_utils import to_camel_case, to_snake_case, to_kebab_case


@dataclass
class BusinessFlow:
    """业务流程定义"""
    name: str
    description: str
    steps: List[str] = field(default_factory=list)
    parameters: List[Dict[str, str]] = field(default_factory=list)


class BAWDetector:
    """业务流程检测器"""

    def detect(self, component: VueComponent) -> List[BusinessFlow]:
        """检测组件中的业务流程"""
        flows = []

        # 检测登录流程
        login_flow = self._detect_login_flow(component)
        if login_flow:
            flows.append(login_flow)

        # 检测搜索流程
        search_flow = self._detect_search_flow(component)
        if search_flow:
            flows.append(search_flow)

        # 检测表单提交流程
        submit_flow = self._detect_submit_flow(component)
        if submit_flow:
            flows.append(submit_flow)

        return flows

    def _detect_login_flow(self, component: VueComponent) -> Optional[BusinessFlow]:
        """检测登录流程"""
        has_username = False
        has_password = False
        has_submit = False

        for element in component.elements:
            if element.tag == 'input':
                placeholder = element.attributes.get('placeholder', '').lower()
                if '用户名' in placeholder or 'username' in placeholder.lower():
                    has_username = True
                if '密码' in placeholder or 'password' in placeholder.lower():
                    has_password = True
            if element.tag == 'button' and element.text_content == '登录':
                has_submit = True

        if has_username and has_password and has_submit:
            return BusinessFlow(
                name="Login",
                description="登录业务流程",
                steps=[
                    "打开登录页面",
                    "输入用户名",
                    "输入密码",
                    "点击登录按钮"
                ],
                parameters=[
                    {"name": "username", "type": "string", "description": "用户名"},
                    {"name": "password", "type": "string", "description": "密码"}
                ]
            )
        return None

    def _detect_search_flow(self, component: VueComponent) -> Optional[BusinessFlow]:
        """检测搜索流程"""
        has_search_input = False
        has_search_button = False

        for element in component.elements:
            if element.tag == 'input' and element.attributes.get('type') == 'search':
                has_search_input = True
            if element.tag == 'button' and element.text_content == '搜索':
                has_search_button = True

        if has_search_input and has_search_button:
            return BusinessFlow(
                name="Search",
                description="搜索业务流程",
                steps=[
                    "打开搜索页面",
                    "输入搜索关键词",
                    "点击搜索按钮"
                ],
                parameters=[
                    {"name": "query", "type": "string", "description": "搜索关键词"}
                ]
            )
        return None

    def _detect_submit_flow(self, component: VueComponent) -> Optional[BusinessFlow]:
        """检测表单提交流程"""
        has_form = False
        has_submit = False
        input_count = 0

        for element in component.elements:
            if element.tag == 'form':
                has_form = True
            if element.tag == 'button' and element.attributes.get('type') == 'submit':
                has_submit = True
            if element.tag == 'input':
                input_count += 1

        if has_form and has_submit and input_count >= 2:
            return BusinessFlow(
                name="SubmitForm",
                description="表单提交流程",
                steps=[
                    "打开表单页面",
                    "填写表单字段",
                    "点击提交按钮"
                ],
                parameters=[
                    {"name": "form_data", "type": "dict", "description": "表单数据"}
                ]
            )
        return None


class TypeScriptBAWGenerator:
    """TypeScript BAW 生成器"""

    def __init__(self, naming_service: NamingService = None):
        self.naming_service = naming_service or NamingService()

    def generate(self, component: VueComponent, flow: BusinessFlow) -> str:
        """生成 TypeScript BAW 文件"""
        self.naming_service.reset()
        page_var = to_camel_case(component.name) + "Page"

        lines = [
            "import { Page } from '@playwright/test';",
            f"import {component.name}Page from '../pages/{to_kebab_case(component.name)}.page';",
            "",
            "/**",
            f" * {flow.description}",
            f" * 组合POM操作：{' → '.join(flow.steps)}",
            " */",
            f"export class {flow.name}BAW {{",
            f"  private {page_var}: {component.name}Page;",
            "",
            "  constructor(page: Page) {",
            f"    this.{page_var} = new {component.name}Page(page);",
            "  }",
            "",
            "  /**",
            "   * 执行流程",
        ]

        for param in flow.parameters:
            lines.append(f"   * @param {param['name']} {param['description']}")

        lines.append("   */")

        # 生成 execute 方法签名
        params = ", ".join(f"{p['name']}: {p['type']}" for p in flow.parameters)
        lines.append(f"  async execute({params}): Promise<void> {{")

        # 根据流程类型生成实际 POM 调用
        step_calls = self._generate_step_calls(component, flow, page_var, "ts")
        for i, call in enumerate(step_calls, 1):
            lines.append(f"    // {i}. {call['comment']}")
            lines.append(f"    {call['code']}")

        lines.append("  }")
        lines.append("}")

        return "\n".join(lines)

    def _generate_step_calls(self, component: VueComponent, flow: BusinessFlow, page_var: str, lang: str) -> List[Dict[str, str]]:
        """根据流程步骤生成实际的 POM 方法调用"""
        calls = []
        flow_name = flow.name.lower()

        if flow_name == "login":
            # 找到用户名、密码输入框和登录按钮
            username_elem = None
            password_elem = None
            submit_elem = None
            for elem in component.elements:
                if elem.tag == 'input':
                    placeholder = elem.attributes.get('placeholder', '').lower()
                    if '用户名' in placeholder or 'username' in placeholder:
                        username_elem = elem
                    if '密码' in placeholder or 'password' in placeholder:
                        password_elem = elem
                if elem.tag == 'button' and elem.text_content == '登录':
                    submit_elem = elem

            calls.append({"comment": "打开登录页面", "code": f"await this.{page_var}.goto();"})
            if username_elem:
                method = self.naming_service.get_method_name(username_elem, 'input', lang)
                calls.append({"comment": "输入用户名", "code": f"await this.{page_var}.{method}(username);"})
            if password_elem:
                method = self.naming_service.get_method_name(password_elem, 'input', lang)
                calls.append({"comment": "输入密码", "code": f"await this.{page_var}.{method}(password);"})
            if submit_elem:
                method = self.naming_service.get_method_name(submit_elem, 'click', lang)
                calls.append({"comment": "点击登录按钮", "code": f"await this.{page_var}.{method}();"})

        elif flow_name == "search":
            search_input = None
            search_btn = None
            for elem in component.elements:
                if elem.tag == 'input' and elem.attributes.get('type') == 'search':
                    search_input = elem
                if elem.tag == 'button' and elem.text_content == '搜索':
                    search_btn = elem

            calls.append({"comment": "打开搜索页面", "code": f"await this.{page_var}.goto();"})
            if search_input:
                method = self.naming_service.get_method_name(search_input, 'input', lang)
                calls.append({"comment": "输入搜索关键词", "code": f"await this.{page_var}.{method}(query);"})
            if search_btn:
                method = self.naming_service.get_method_name(search_btn, 'click', lang)
                calls.append({"comment": "点击搜索按钮", "code": f"await this.{page_var}.{method}();"})

        elif flow_name == "submitform":
            calls.append({"comment": "打开表单页面", "code": f"await this.{page_var}.goto();"})
            # 为每个 input 生成 fill 调用
            input_idx = 0
            for elem in component.elements:
                if elem.tag == 'input':
                    method = self.naming_service.get_method_name(elem, 'input', lang)
                    if lang == "ts":
                        calls.append({"comment": f"填写字段 {input_idx + 1}", "code": f"await this.{page_var}.{method}(form_data.field{input_idx});"})
                    else:
                        calls.append({"comment": f"填写字段 {input_idx + 1}", "code": f"self.{page_var}.{method}(form_data['field{input_idx}'])"})
                    input_idx += 1
            # 找提交按钮
            for elem in component.elements:
                if elem.tag == 'button' and elem.attributes.get('type') == 'submit':
                    method = self.naming_service.get_method_name(elem, 'click', lang)
                    calls.append({"comment": "点击提交按钮", "code": f"await this.{page_var}.{method}();" if lang == "ts" else f"self.{page_var}.{method}()"})
                    break

        return calls


class PythonBAWGenerator:
    """Python BAW 生成器"""

    def __init__(self, naming_service: NamingService = None):
        self.naming_service = naming_service or NamingService()

    def generate(self, component: VueComponent, flow: BusinessFlow) -> str:
        """生成 Python BAW 文件"""
        self.naming_service.reset()
        page_var = to_snake_case(component.name) + "_page"

        lines = [
            "from playwright.sync_api import Page",
            f"from pages.{to_snake_case(component.name)}_page import {component.name}Page",
            "",
            "",
            f"class {flow.name}BAW:",
            '    """',
            f"    {flow.description}",
            f"    组合POM操作：{' → '.join(flow.steps)}",
            '    """',
            "",
            f"    def __init__(self, page: Page):",
            f"        self.{page_var} = {component.name}Page(page)",
            "",
            "    def execute(self,",
        ]

        for param in flow.parameters:
            # 转换类型注解
            py_type = self._convert_type(param['type'], 'py')
            lines.append(f"            {param['name']}: {py_type},  # {param['description']}")

        lines.append("            ):")
        lines.append('        """')
        lines.append("        执行流程")
        lines.append('        """')

        # 根据流程类型生成实际 POM 调用
        step_calls = self._generate_step_calls(component, flow, page_var, "py")
        for i, call in enumerate(step_calls, 1):
            lines.append(f"        # {i}. {call['comment']}")
            lines.append(f"        {call['code']}")

        return "\n".join(lines)

    def _generate_step_calls(self, component: VueComponent, flow: BusinessFlow, page_var: str, lang: str) -> List[Dict[str, str]]:
        """根据流程步骤生成实际的 POM 方法调用"""
        calls = []
        flow_name = flow.name.lower()

        if flow_name == "login":
            username_elem = None
            password_elem = None
            submit_elem = None
            for elem in component.elements:
                if elem.tag == 'input':
                    placeholder = elem.attributes.get('placeholder', '').lower()
                    if '用户名' in placeholder or 'username' in placeholder:
                        username_elem = elem
                    if '密码' in placeholder or 'password' in placeholder:
                        password_elem = elem
                if elem.tag == 'button' and elem.text_content == '登录':
                    submit_elem = elem

            calls.append({"comment": "打开登录页面", "code": f"self.{page_var}.goto()"})
            if username_elem:
                method = self.naming_service.get_method_name(username_elem, 'input', lang)
                calls.append({"comment": "输入用户名", "code": f"self.{page_var}.{method}(username)"})
            if password_elem:
                method = self.naming_service.get_method_name(password_elem, 'input', lang)
                calls.append({"comment": "输入密码", "code": f"self.{page_var}.{method}(password)"})
            if submit_elem:
                method = self.naming_service.get_method_name(submit_elem, 'click', lang)
                calls.append({"comment": "点击登录按钮", "code": f"self.{page_var}.{method}()"})

        elif flow_name == "search":
            search_input = None
            search_btn = None
            for elem in component.elements:
                if elem.tag == 'input' and elem.attributes.get('type') == 'search':
                    search_input = elem
                if elem.tag == 'button' and elem.text_content == '搜索':
                    search_btn = elem

            calls.append({"comment": "打开搜索页面", "code": f"self.{page_var}.goto()"})
            if search_input:
                method = self.naming_service.get_method_name(search_input, 'input', lang)
                calls.append({"comment": "输入搜索关键词", "code": f"self.{page_var}.{method}(query)"})
            if search_btn:
                method = self.naming_service.get_method_name(search_btn, 'click', lang)
                calls.append({"comment": "点击搜索按钮", "code": f"self.{page_var}.{method}()"})

        elif flow_name == "submitform":
            calls.append({"comment": "打开表单页面", "code": f"self.{page_var}.goto()"})
            input_idx = 0
            for elem in component.elements:
                if elem.tag == 'input':
                    method = self.naming_service.get_method_name(elem, 'input', lang)
                    calls.append({"comment": f"填写字段 {input_idx + 1}", "code": f"self.{page_var}.{method}(form_data['field{input_idx}'])"})
                    input_idx += 1
            for elem in component.elements:
                if elem.tag == 'button' and elem.attributes.get('type') == 'submit':
                    method = self.naming_service.get_method_name(elem, 'click', lang)
                    calls.append({"comment": "点击提交按钮", "code": f"self.{page_var}.{method}()"})
                    break

        return calls

    def _convert_type(self, vue_type: str, lang: str) -> str:
        """将 Vue 类型转换为目标语言类型"""
        type_map = {
            'string': {'py': 'str', 'ts': 'string'},
            'number': {'py': 'int', 'ts': 'number'},
            'boolean': {'py': 'bool', 'ts': 'boolean'},
            'object': {'py': 'dict', 'ts': 'object'},
            'array': {'py': 'list', 'ts': 'any[]'},
        }
        return type_map.get(vue_type, {}).get(lang, vue_type)
