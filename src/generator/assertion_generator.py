"""
智能断言生成器
根据组件逻辑自动生成合理的 Playwright 断言
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
from src.parser.vue_parser import VueComponent, VueElement


@dataclass
class Assertion:
    """断言定义"""
    type: str  # visibility, text, url, attribute, count
    target: str  # 目标元素或属性
    expected: str  # 期望值
    description: str  # 断言描述


class AssertionGenerator:
    """智能断言生成器"""

    def __init__(self):
        # 常见验证模式
        self.validation_patterns = {
            'error': ['error', '错误', 'invalid', '无效'],
            'success': ['success', '成功', 'welcome', '欢迎'],
            'loading': ['loading', '加载中', 'spinner'],
            'empty': ['empty', '暂无', '没有数据'],
        }

    def generate_assertions(self, component: VueComponent, element: VueElement, event: str) -> List[Assertion]:
        """为元素和事件生成断言"""
        assertions = []

        # 根据元素类型生成断言
        if element.tag == 'button':
            assertions.extend(self._generate_button_assertions(component, element, event))
        elif element.tag == 'input':
            assertions.extend(self._generate_input_assertions(component, element, event))
        elif element.tag == 'form':
            assertions.extend(self._generate_form_assertions(component, element, event))
        elif element.tag == 'a':
            assertions.extend(self._generate_link_assertions(component, element, event))

        # 根据事件类型生成断言
        assertions.extend(self._generate_event_assertions(component, element, event))

        # 根据组件方法生成断言
        assertions.extend(self._generate_method_assertions(component, element, event))

        return assertions

    def _generate_button_assertions(self, component: VueComponent, element: VueElement, event: str) -> List[Assertion]:
        """生成按钮相关断言"""
        assertions = []
        text = element.text_content

        # 登录按钮
        if text == '登录':
            assertions.append(Assertion(
                type='url',
                target='page',
                expected='/dashboard',
                description='验证跳转到仪表盘页面'
            ))
            assertions.append(Assertion(
                type='text',
                target='body',
                expected='欢迎',
                description='验证显示欢迎信息'
            ))

        # 提交按钮
        elif text == '提交' or 'submit' in text.lower():
            assertions.append(Assertion(
                type='visibility',
                target='success-message',
                expected='visible',
                description='验证显示成功消息'
            ))

        # 搜索按钮
        elif text == '搜索':
            assertions.append(Assertion(
                type='count',
                target='.results li',
                expected='>0',
                description='验证显示搜索结果'
            ))

        # 删除按钮
        elif '删除' in text or 'delete' in text.lower():
            assertions.append(Assertion(
                type='visibility',
                target=element.text_content,
                expected='hidden',
                description='验证元素被删除'
            ))

        return assertions

    def _generate_input_assertions(self, component: VueComponent, element: VueElement, event: str) -> List[Assertion]:
        """生成输入框相关断言"""
        assertions = []
        placeholder = element.attributes.get('placeholder', '').lower()

        # 用户名输入框 - blur 事件验证错误信息
        if '用户名' in placeholder and event.startswith('blur'):
            assertions.append(Assertion(
                type='visibility',
                target='error-message',
                expected='visible',
                description='验证显示用户名错误信息'
            ))

        # 密码输入框
        elif '密码' in placeholder and event.startswith('blur'):
            assertions.append(Assertion(
                type='visibility',
                target='password-error',
                expected='visible',
                description='验证显示密码错误信息'
            ))

        # 搜索输入框
        elif '搜索' in placeholder:
            assertions.append(Assertion(
                type='attribute',
                target='input',
                expected='value',
                description='验证输入框值已更新'
            ))

        return assertions

    def _generate_form_assertions(self, component: VueComponent, element: VueElement, event: str) -> List[Assertion]:
        """生成表单相关断言"""
        assertions = []

        if event == 'submit':
            # 表单提交后验证
            assertions.append(Assertion(
                type='visibility',
                target='success-message',
                expected='visible',
                description='验证表单提交成功'
            ))

        return assertions

    def _generate_link_assertions(self, component: VueComponent, element: VueElement, event: str) -> List[Assertion]:
        """生成链接相关断言"""
        assertions = []

        if event == 'click':
            # 根据链接文本推断目标页面
            text = element.text_content
            if '登录' in text:
                assertions.append(Assertion(
                    type='url',
                    target='page',
                    expected='/login',
                    description='验证跳转到登录页面'
                ))
            elif '注册' in text:
                assertions.append(Assertion(
                    type='url',
                    target='page',
                    expected='/register',
                    description='验证跳转到注册页面'
                ))
            elif '忘记' in text:
                assertions.append(Assertion(
                    type='url',
                    target='page',
                    expected='/forgot-password',
                    description='验证跳转到忘记密码页面'
                ))

        return assertions

    def _generate_event_assertions(self, component: VueComponent, element: VueElement, event: str) -> List[Assertion]:
        """根据事件类型生成断言"""
        assertions = []

        # 验证事件处理函数名
        handler = element.events.get(event, '')

        # 根据处理函数名推断断言
        if 'validate' in handler.lower():
            assertions.append(Assertion(
                type='visibility',
                target='error-message',
                expected='visible',
                description='验证显示验证错误'
            ))

        if 'clear' in handler.lower():
            assertions.append(Assertion(
                type='visibility',
                target='error-message',
                expected='hidden',
                description='验证清除错误信息'
            ))

        if 'reset' in handler.lower():
            assertions.append(Assertion(
                type='attribute',
                target='input',
                expected='empty',
                description='验证输入框已清空'
            ))

        if 'success' in handler.lower():
            assertions.append(Assertion(
                type='visibility',
                target='success-message',
                expected='visible',
                description='验证显示成功消息'
            ))

        return assertions

    def _generate_method_assertions(self, component: VueComponent, element: VueElement, event: str) -> List[Assertion]:
        """根据组件方法生成断言"""
        assertions = []

        # 检查事件处理函数
        handler = element.events.get(event, '')

        # 验证方法
        if handler in component.methods:
            # 分析方法名推断行为
            if 'login' in handler.lower():
                assertions.append(Assertion(
                    type='url',
                    target='page',
                    expected='/dashboard',
                    description='验证登录成功后跳转'
                ))

            if 'search' in handler.lower():
                assertions.append(Assertion(
                    type='count',
                    target='.results li',
                    expected='>0',
                    description='验证显示搜索结果'
                ))

            if 'save' in handler.lower():
                assertions.append(Assertion(
                    type='visibility',
                    target='save-success',
                    expected='visible',
                    description='验证保存成功提示'
                ))

        return assertions

    def generate_ts_assertion_code(self, assertion: Assertion) -> str:
        """生成 TypeScript 断言代码"""
        if assertion.type == 'visibility':
            if assertion.expected == 'visible':
                return f"    await expect(page.getByText('{assertion.target}')).toBeVisible();"
            else:
                return f"    await expect(page.getByText('{assertion.target}')).toBeHidden();"

        elif assertion.type == 'text':
            return f"    await expect(page.locator('{assertion.target}')).toContainText('{assertion.expected}');"

        elif assertion.type == 'url':
            return f"    await expect(page).toHaveURL(/^{assertion.expected.replace('/', '\\/')}/);"

        elif assertion.type == 'attribute':
            if assertion.expected == 'empty':
                return f"    await expect(page.locator('{assertion.target}')).toHaveValue('');"
            else:
                return f"    await expect(page.locator('{assertion.target}')).toHaveAttribute('value', /./);"

        elif assertion.type == 'count':
            return f"    await expect(page.locator('{assertion.target}')).toHaveCount({assertion.expected});"

        return f"    // TODO: {assertion.description}"

    def generate_py_assertion_code(self, assertion: Assertion) -> str:
        """生成 Python 断言代码"""
        if assertion.type == 'visibility':
            if assertion.expected == 'visible':
                return f"        expect(page.get_by_text('{assertion.target}')).to_be_visible()"
            else:
                return f"        expect(page.get_by_text('{assertion.target}')).to_be_hidden()"

        elif assertion.type == 'text':
            return f"        expect(page.locator('{assertion.target}')).to_contain_text('{assertion.expected}')"

        elif assertion.type == 'url':
            return f"        expect(page).to_have_url(r'^{assertion.expected}')"

        elif assertion.type == 'attribute':
            if assertion.expected == 'empty':
                return f"        expect(page.locator('{assertion.target}')).to_have_value('')"
            else:
                return f"        expect(page.locator('{assertion.target}')).to_have_attribute('value', /.+/)"

        elif assertion.type == 'count':
            return f"        expect(page.locator('{assertion.target}')).to_have_count({assertion.expected})"

        return f"        # TODO: {assertion.description}"
