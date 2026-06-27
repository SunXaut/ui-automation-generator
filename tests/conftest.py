"""tests 根目录配置：确保 test_cases/ 下能正常导入 pages/ 和 baw/"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'python'))