# Vue 组件解析模块
from pathlib import Path

# 使用相对导入或直接导入
try:
    from .vue_parser import VueParser, VueComponent, VueElement
    from .router_parser import RouterParser, RouterConfig, RouterTestGenerator
    from .pinia_parser import PiniaParser, PiniaStore, PiniaTestGenerator
except ImportError:
    # fallback for direct execution
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from parser.vue_parser import VueParser, VueComponent, VueElement
    from parser.router_parser import RouterParser, RouterConfig, RouterTestGenerator
    from parser.pinia_parser import PiniaParser, PiniaStore, PiniaTestGenerator

__all__ = [
    'VueParser', 'VueComponent', 'VueElement',
    'RouterParser', 'RouterConfig', 'RouterTestGenerator',
    'PiniaParser', 'PiniaStore', 'PiniaTestGenerator'
]
