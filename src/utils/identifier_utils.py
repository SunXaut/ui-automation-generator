"""
标识符规范化工具
将包含中文和特殊字符的文本转换为合法的代码标识符
"""

import re
import unicodedata
from typing import Dict


# 统一的 action 映射表（TypeScript 风格）
ACTION_MAP_TS: Dict[str, str] = {
    'click': 'click',
    'dblclick': 'doubleClick',
    'input': 'fill',
    'change': 'change',
    'blur': 'blur',
    'focus': 'focus',
    'submit': 'submit',
}

# 统一的 action 映射表（Python 风格）
ACTION_MAP_PY: Dict[str, str] = {
    'click': 'click',
    'dblclick': 'double_click',
    'input': 'fill',
    'change': 'change',
    'blur': 'blur',
    'focus': 'focus',
    'submit': 'submit',
}

# 统一的 action 映射表（测试名称风格）
ACTION_MAP_NAME: Dict[str, str] = {
    'click': 'click',
    'dblclick': 'double click',
    'input': 'input',
    'change': 'change',
    'blur': 'blur',
    'focus': 'focus',
    'submit': 'submit',
}


def get_action(event: str, lang: str = "ts") -> str:
    """获取事件对应的 action 名称"""
    base_event = event.split('.')[0]
    if lang == "ts":
        return ACTION_MAP_TS.get(base_event, base_event)
    elif lang == "py":
        return ACTION_MAP_PY.get(base_event, base_event)
    else:
        return ACTION_MAP_NAME.get(base_event, base_event)


def normalize_identifier(text: str, prefix: str = "", suffix: str = "") -> str:
    """
    规范化标识符，移除非法字符

    Args:
        text: 原始文本
        prefix: 前缀（如 'click', 'fill' 等）
        suffix: 后缀

    Returns:
        规范化的标识符
    """
    if not text:
        text = "element"

    # 移除 HTML 标签
    text = re.sub(r'<[^>]+>', '', text)

    # 移除 Vue 插值表达式
    text = re.sub(r'\{\{[^}]+\}\}', '', text)

    # 移除事件修饰符（如 .prevent, .stop）
    text = re.sub(r'\.\w+', '', text)

    # 先处理中文
    text = _handle_chinese(text)

    # 在 camelCase 边界处插入空格（保留已有单词边界）
    text = re.sub(r'([a-z0-9])([A-Z])', r'\1 \2', text)
    text = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1 \2', text)

    # 将连字符和下划线转换为空格
    text = re.sub(r'[-_]', ' ', text)

    # 移除其他特殊字符（保留空格和字母数字）
    text = re.sub(r'[^\w\s]', '', text)

    # 将每个单词首字母大写（PascalCase）
    words = text.split()
    if not words:
        text = "element"
    else:
        text = ''.join(word.capitalize() for word in words)

    # 确保以字母开头
    if text and not text[0].isalpha():
        text = "elem" + text

    return prefix + text + suffix


def _handle_chinese(text: str) -> str:
    """处理中文文本，转换为英文描述"""
    # 常见中文词汇映射
    chinese_map = {
        '登录': 'Login',
        '注册': 'Register',
        '提交': 'Submit',
        '取消': 'Cancel',
        '确认': 'Confirm',
        '关闭': 'Close',
        '删除': 'Delete',
        '编辑': 'Edit',
        '保存': 'Save',
        '搜索': 'Search',
        '重置': 'Reset',
        '刷新': 'Refresh',
        '首页': 'Home',
        '关于': 'About',
        '设置': 'Settings',
        '用户': 'User',
        '密码': 'Password',
        '邮箱': 'Email',
        '手机号': 'Phone',
        '验证码': 'Code',
        '忘记密码': 'ForgotPassword',
        '退出': 'Logout',
        '返回': 'Back',
        '下一页': 'Next',
        '上一页': 'Previous',
        '确定': 'OK',
        '选择': 'Select',
        '上传': 'Upload',
        '下载': 'Download',
        '添加': 'Add',
        '修改': 'Modify',
        '查看': 'View',
        '详情': 'Detail',
        '列表': 'List',
        '表格': 'Table',
        '表单': 'Form',
        '按钮': 'Button',
        '输入': 'Input',
        '下拉': 'Dropdown',
        '菜单': 'Menu',
        '标签': 'Tab',
        '弹窗': 'Modal',
        '提示': 'Tooltip',
        '消息': 'Message',
        '通知': 'Notification',
        '加载': 'Load',
        '初始化': 'Init',
        '验证': 'Validate',
        '过滤': 'Filter',
        '排序': 'Sort',
        '分页': 'Pagination',
    }
    
    # 检查是否包含中文
    has_chinese = any('\u4e00' <= char <= '\u9fff' for char in text)
    
    if has_chinese:
        # 按长度降序排序，优先匹配更长的词汇（如"忘记密码"优先于"密码"）
        sorted_map = sorted(chinese_map.items(), key=lambda x: len(x[0]), reverse=True)
        for cn, en in sorted_map:
            if cn in text:
                text = text.replace(cn, en)
        
        # 移除剩余的中文字符
        text = re.sub(r'[\u4e00-\u9fff]+', '', text)
    
    return text


def to_camel_case(text: str) -> str:
    """转换为 camelCase"""
    # 先规范化
    text = normalize_identifier(text)
    # 转换为小写开头的 camelCase
    if text:
        return text[0].lower() + text[1:]
    return text


def to_snake_case(text: str) -> str:
    """转换为 snake_case"""
    # 先规范化
    text = normalize_identifier(text)
    # 插入下划线
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', text)
    result = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    return result


def to_kebab_case(text: str) -> str:
    """转换为 kebab-case"""
    # 先规范化
    text = normalize_identifier(text)
    # 插入连字符
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1-\2', text)
    result = re.sub('([a-z0-9])([A-Z])', r'\1-\2', s1).lower()
    return result
