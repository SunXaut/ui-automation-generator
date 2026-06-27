#!/usr/bin/env python3
"""
Vue to Playwright Test Generator CLI
从 Vue 组件、Router 配置、Pinia Store 自动生成 Playwright 测试
"""

import argparse
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.generator.main_generator import TestGenerator


def main():
    parser = argparse.ArgumentParser(
        description="从 Vue 组件、Router 配置、Pinia Store 生成 Playwright 测试",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 生成 Vue 组件测试
  python vue_test_generator.py front-end-code/vue/src/views/Login.vue -o tests --language typescript

  # 生成 Router 测试
  python vue_test_generator.py front-end-code/vue/src/router/index.ts --router -o tests

  # 生成 Pinia Store 测试
  python vue_test_generator.py front-end-code/vue/src/stores/user.ts --store -o tests

  # 批量处理目录
  python vue_test_generator.py front-end-code/vue/src/views/ -o tests --language typescript
        """
    )

    parser.add_argument(
        "input",
        help="Vue 组件文件/目录、Router 配置文件或 Pinia Store 文件"
    )

    parser.add_argument(
        "-o", "--output",
        default="tests",
        help="输出目录 (默认: tests)"
    )

    parser.add_argument(
        "-l", "--language",
        choices=["typescript", "python"],
        default="typescript",
        help="生成测试的编程语言 (默认: typescript)"
    )

    parser.add_argument(
        "--router",
        action="store_true",
        help="解析 Vue Router 配置生成路由测试"
    )

    parser.add_argument(
        "--store",
        action="store_true",
        help="解析 Pinia Store 生成状态管理测试"
    )

    parser.add_argument(
        "--generate-baw",
        action="store_true",
        default=True,
        help="生成 BAW 业务流程文件 (默认: 启用)"
    )

    parser.add_argument(
        "--no-baw",
        action="store_true",
        help="不生成 BAW 文件"
    )

    args = parser.parse_args()

    # 检查输入路径
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"错误: 路径不存在: {args.input}")
        sys.exit(1)

    # 创建生成器
    generator = TestGenerator(
        output_dir=args.output,
        language=args.language,
        generate_baw=not args.no_baw
    )

    # 根据模式处理
    if args.router:
        # Router 模式
        if input_path.is_file():
            generator.generate_router_test(str(input_path))
        else:
            # 查找 router 文件
            router_files = list(input_path.rglob("index.ts")) + list(input_path.rglob("router.ts"))
            if not router_files:
                print(f"警告: 目录中没有找到 Router 配置文件")
                sys.exit(0)

            for router_file in router_files:
                print(f"\n处理 Router: {router_file}")
                generator.generate_router_test(str(router_file))

    elif args.store:
        # Store 模式
        if input_path.is_file():
            generator.generate_store_test(str(input_path))
        else:
            # 查找 store 文件
            store_files = list(input_path.rglob("*.ts"))
            store_files = [f for f in store_files if 'store' in f.name.lower() or 'store' in str(f).lower()]

            if not store_files:
                print(f"警告: 目录中没有找到 Store 文件")
                sys.exit(0)

            print(f"找到 {len(store_files)} 个 Store 文件")
            for store_file in store_files:
                print(f"\n处理 Store: {store_file}")
                generator.generate_store_test(str(store_file))

    else:
        # Vue 组件模式
        if input_path.is_file():
            generator.generate(str(input_path))
        elif input_path.is_dir():
            vue_files = list(input_path.rglob("*.vue"))
            if not vue_files:
                print(f"警告: 目录中没有找到 Vue 文件: {args.input}")
                sys.exit(0)

            print(f"找到 {len(vue_files)} 个 Vue 文件")
            for vue_file in vue_files:
                print(f"\n处理: {vue_file}")
                generator.generate(str(vue_file))

    print("\n生成完成!")


if __name__ == "__main__":
    main()
