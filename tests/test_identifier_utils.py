"""
identifier_utils 单元测试
验证标识符规范化和转换功能
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.identifier_utils import (
    normalize_identifier,
    to_snake_case,
    to_camel_case,
    to_kebab_case,
    get_action,
    _handle_chinese,
)


class TestNormalizeIdentifier:
    """测试标识符规范化"""

    def test_empty_string(self):
        result = normalize_identifier('')
        assert result == 'Element'  # normalize_identifier 返回 title case

    def test_simple_text(self):
        result = normalize_identifier('button')
        assert result == 'Button'

    def test_hyphenated_text(self):
        """连字符应保留单词边界"""
        result = normalize_identifier('username-input')
        assert 'Username' in result and 'Input' in result

    def test_underscored_text(self):
        """下划线应保留单词边界"""
        result = normalize_identifier('username_input')
        assert 'Username' in result and 'Input' in result

    def test_chinese_text(self):
        """中文应转换为英文"""
        result = normalize_identifier('登录')
        assert result == 'Login'

    def test_chinese_with_context(self):
        """中文+英文混合"""
        result = normalize_identifier('忘记密码')
        assert result == 'ForgotPassword'

    def test_html_tags_removed(self):
        """HTML 标签应被移除"""
        result = normalize_identifier('<span>text</span>')
        assert '<' not in result and '>' not in result

    def test_vue_interpolation_removed(self):
        """Vue 插值表达式应被移除"""
        result = normalize_identifier('{{ value }}')
        assert '{{' not in result

    def test_event_modifiers_removed(self):
        """事件修饰符应被移除"""
        result = normalize_identifier('click.prevent')
        assert '.prevent' not in result

    def test_starts_with_number(self):
        """数字开头应添加前缀"""
        result = normalize_identifier('123abc')
        assert result[0].isalpha()

    def test_prefix_and_suffix(self):
        """前缀和后缀应正确添加"""
        result = normalize_identifier('button', prefix='click_', suffix='_handler')
        assert result.startswith('click_')
        assert result.endswith('_handler')


class TestToSnakeCase:
    """测试 snake_case 转换"""

    def test_simple(self):
        assert to_snake_case('button') == 'button'

    def test_camel_case_input(self):
        result = to_snake_case('UsernameInput')
        assert result == 'username_input'

    def test_hyphenated_input(self):
        """连字符应转换为下划线"""
        result = to_snake_case('username-input')
        assert result == 'username_input'

    def test_chinese_input(self):
        """中文应先转英文再转 snake_case"""
        result = to_snake_case('登录')
        assert result == 'login'

    def test_mixed_input(self):
        result = to_snake_case('wechat-login')
        assert result == 'wechat_login'


class TestToCamelCase:
    """测试 camelCase 转换"""

    def test_simple(self):
        result = to_camel_case('button')
        assert result == 'button'

    def test_hyphenated_input(self):
        result = to_camel_case('username-input')
        assert result == 'usernameInput'

    def test_starts_lowercase(self):
        result = to_camel_case('UsernameInput')
        assert result[0].islower()


class TestToKebabCase:
    """测试 kebab-case 转换"""

    def test_simple(self):
        result = to_kebab_case('button')
        assert result == 'button'

    def test_camel_input(self):
        result = to_kebab_case('LoginPage')
        assert result == 'login-page'

    def test_hyphenated_input(self):
        result = to_kebab_case('username-input')
        assert '-' in result


class TestGetAction:
    """测试 action 映射"""

    def test_click_ts(self):
        assert get_action('click', 'ts') == 'click'

    def test_dblclick_ts(self):
        assert get_action('dblclick', 'ts') == 'doubleClick'

    def test_input_ts(self):
        assert get_action('input', 'ts') == 'fill'

    def test_click_py(self):
        assert get_action('click', 'py') == 'click'

    def test_dblclick_py(self):
        assert get_action('dblclick', 'py') == 'double_click'

    def test_input_py(self):
        assert get_action('input', 'py') == 'fill'

    def test_event_with_modifier(self):
        """带修饰符的事件应正确提取"""
        assert get_action('click.prevent', 'ts') == 'click'
        assert get_action('submit.prevent.stop', 'py') == 'submit'

    def test_unknown_event(self):
        """未知事件应返回原始名称"""
        assert get_action('custom', 'ts') == 'custom'


class TestHandleChinese:
    """测试中文处理"""

    def test_login(self):
        assert _handle_chinese('登录') == 'Login'

    def test_forgot_password(self):
        result = _handle_chinese('忘记密码')
        assert 'ForgotPassword' in result

    def test_reset(self):
        assert _handle_chinese('重置') == 'Reset'

    def test_mixed_chinese_english(self):
        result = _handle_chinese('点击登录')
        assert 'Login' in result

    def test_no_chinese(self):
        assert _handle_chinese('button') == 'button'

    def test_unknown_chinese(self):
        """未知中文应被移除"""
        result = _handle_chinese('龘靐')
        assert result == ''


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
