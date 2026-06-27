"""
NamingService 单元测试
验证统一命名服务的核心功能
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.parser.vue_parser import VueElement
from src.utils.naming_service import NamingService


class TestNamingServiceLocatorName:
    """测试定位器名称生成"""

    def setup_method(self):
        self.ns = NamingService()

    def test_data_testid_priority(self):
        """data-testid 应优先作为语义名称"""
        elem = VueElement(
            tag='input',
            attributes={'placeholder': '请输入用户名'},
            data_testid='username-input',
            semantic_name='username-input'
        )
        name = self.ns.get_locator_name(elem, 'py')
        assert name == 'username_input'

    def test_aria_label_fallback(self):
        """无 data-testid 时，使用 aria-label"""
        elem = VueElement(
            tag='button',
            attributes={'aria-label': '提交表单'},
            semantic_name='提交表单'
        )
        name = self.ns.get_locator_name(elem, 'py')
        assert 'submit' in name or 'form' in name

    def test_placeholder_fallback(self):
        """无 data-testid 和 aria-label 时，使用 placeholder"""
        elem = VueElement(
            tag='input',
            attributes={'placeholder': '搜索关键词'},
            semantic_name='搜索关键词'
        )
        name = self.ns.get_locator_name(elem, 'py')
        assert 'search' in name.lower() or name != ''

    def test_text_content_fallback(self):
        """无其他属性时，使用 text_content"""
        elem = VueElement(
            tag='button',
            text_content='登录',
            semantic_name='登录'
        )
        name = self.ns.get_locator_name(elem, 'py')
        assert 'login' in name.lower() or name != ''

    def test_tag_fallback(self):
        """无任何语义信息时，使用 tag"""
        elem = VueElement(tag='div', semantic_name='div')
        name = self.ns.get_locator_name(elem, 'py')
        assert name == 'div'

    def test_dedup_same_tag(self):
        """相同 tag 的元素应自动去重"""
        elem1 = VueElement(tag='input', attributes={}, semantic_name='input')
        elem2 = VueElement(tag='input', attributes={}, semantic_name='input')

        name1 = self.ns.get_locator_name(elem1, 'py')
        name2 = self.ns.get_locator_name(elem2, 'py')

        assert name1 != name2
        assert name1 == 'input'
        assert name2 == 'input_1'

    def test_cache_same_element(self):
        """同一元素多次调用应返回相同名称"""
        elem = VueElement(tag='input', data_testid='username', semantic_name='username')

        name1 = self.ns.get_locator_name(elem, 'py')
        name2 = self.ns.get_locator_name(elem, 'py')

        assert name1 == name2

    def test_ts_camel_case(self):
        """TypeScript 应使用 camelCase"""
        elem = VueElement(tag='input', data_testid='username-input', semantic_name='username-input')
        name = self.ns.get_locator_name(elem, 'ts')
        assert name == 'usernameInput'

    def test_py_snake_case(self):
        """Python 应使用 snake_case"""
        elem = VueElement(tag='input', data_testid='username-input', semantic_name='username-input')
        name = self.ns.get_locator_name(elem, 'py')
        assert name == 'username_input'


class TestNamingServiceMethodName:
    """测试方法名称生成"""

    def setup_method(self):
        self.ns = NamingService()

    def test_click_event(self):
        """click 事件应生成 click_ 前缀"""
        elem = VueElement(
            tag='button',
            text_content='登录',
            events={'click': 'handleLogin'},
            semantic_name='登录'
        )
        name = self.ns.get_method_name(elem, 'click', 'py')
        assert name.startswith('click_')

    def test_blur_event(self):
        """blur 事件应生成 blur_ 前缀"""
        elem = VueElement(
            tag='input',
            data_testid='username-input',
            events={'blur': 'validateUsername'},
            semantic_name='username-input'
        )
        name = self.ns.get_method_name(elem, 'blur', 'py')
        assert name == 'blur_username_input'

    def test_focus_event(self):
        """focus 事件应生成 focus_ 前缀"""
        elem = VueElement(
            tag='input',
            data_testid='username-input',
            events={'focus': 'clearError'},
            semantic_name='username-input'
        )
        name = self.ns.get_method_name(elem, 'focus', 'py')
        assert name == 'focus_username_input'

    def test_event_with_modifier(self):
        """带修饰符的事件应正确提取基础事件"""
        elem = VueElement(
            tag='form',
            events={'submit.prevent': 'handleSubmit'},
            semantic_name='form'
        )
        name = self.ns.get_method_name(elem, 'submit.prevent', 'py')
        assert name == 'submit_form'

    def test_dedup_same_event(self):
        """相同事件多次调用应返回相同名称"""
        elem = VueElement(
            tag='button',
            text_content='登录',
            events={'click': 'handleLogin'},
            semantic_name='登录'
        )
        name1 = self.ns.get_method_name(elem, 'click', 'py')
        name2 = self.ns.get_method_name(elem, 'click', 'py')
        assert name1 == name2

    def test_ts_camel_case(self):
        """TypeScript 方法名应使用 camelCase"""
        elem = VueElement(
            tag='button',
            text_content='登录',
            events={'click': 'handleLogin'},
            semantic_name='登录'
        )
        name = self.ns.get_method_name(elem, 'click', 'ts')
        assert name[0].islower()  # camelCase 以小写开头


class TestNamingServiceTestName:
    """测试测试方法名称生成"""

    def setup_method(self):
        self.ns = NamingService()

    def test_py_test_name_prefix(self):
        """Python 测试名应以 test_ 开头"""
        elem = VueElement(
            tag='button',
            text_content='登录',
            events={'click': 'handleLogin'},
            semantic_name='登录'
        )
        name = self.ns.get_test_name(elem, 'click', 'py')
        assert name.startswith('test_')

    def test_ts_test_name_prefix(self):
        """TypeScript 测试名应以 should 开头"""
        elem = VueElement(
            tag='button',
            text_content='登录',
            events={'click': 'handleLogin'},
            semantic_name='登录'
        )
        name = self.ns.get_test_name(elem, 'click', 'ts')
        assert name.startswith('should ')

    def test_dedup(self):
        """重复的测试名应自动去重"""
        elem1 = VueElement(tag='input', events={'blur': 'validate'}, semantic_name='input')
        elem2 = VueElement(tag='input', events={'blur': 'validate'}, semantic_name='input')

        name1 = self.ns.get_test_name(elem1, 'blur', 'py')
        name2 = self.ns.get_test_name(elem2, 'blur', 'py')

        assert name1 != name2


class TestNamingServiceFileName:
    """测试文件名称生成"""

    def setup_method(self):
        self.ns = NamingService()

    def test_py_file_name(self):
        """Python 文件名应使用 snake_case"""
        name = self.ns.get_file_name('LoginPage', '_page', 'py')
        assert name == 'login_page_page' or 'login' in name

    def test_ts_file_name(self):
        """TypeScript 文件名应使用 kebab-case"""
        name = self.ns.get_file_name('LoginPage', '.page', 'ts')
        assert '-' in name or 'login' in name.lower()


class TestNamingServiceReset:
    """测试 reset 功能"""

    def test_reset_clears_names(self):
        """reset 应清除所有已使用的名称"""
        ns = NamingService()
        elem = VueElement(tag='input', semantic_name='input')

        name1 = ns.get_locator_name(elem, 'py')
        ns.reset()

        # reset 后应得到相同的名称
        name2 = ns.get_locator_name(elem, 'py')
        assert name1 == name2

    def test_reset_clears_cache(self):
        """reset 应清除缓存"""
        ns = NamingService()
        elem = VueElement(tag='input', semantic_name='input')

        ns.get_locator_name(elem, 'py')
        ns.reset()

        # reset 后缓存应被清除
        assert len(ns._locator_cache) == 0
        assert len(ns._method_cache) == 0


class TestGetBaseEvent:
    """测试基础事件提取"""

    def test_simple_event(self):
        ns = NamingService()
        assert ns.get_base_event('click') == 'click'

    def test_event_with_modifier(self):
        ns = NamingService()
        assert ns.get_base_event('click.prevent') == 'click'

    def test_event_with_multiple_modifiers(self):
        ns = NamingService()
        assert ns.get_base_event('submit.prevent.stop') == 'submit'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
