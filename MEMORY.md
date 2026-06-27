# Long-Term Memory

## Patterns That Work
- 使用Python虚拟环境管理项目依赖
- 使用Git进行版本控制
- 使用Superpowers框架进行系统化开发
- 全局skills统一存储在`D:\code\skills`，按来源分为`external`和`custom`两个子目录
- 外部skills通过git clone安装到external目录，然后创建junction链接
- 自定义skill封装常用操作流程
- Write工具在某些路径存在权限限制

## Gotchas to Avoid
- 安装包时注意正确的包名（如llama-index而非lammaindex）
- Windows下使用junction而非symlink
- 移动skills时需要同步更新junction链接
- 某些路径（如D:\code\skills\custom）可能有权限限制，无法直接写入

## User Preferences
- 使用Python 3.12
- 使用中文进行技术文档编写
- 偏好系统化的开发流程
- 全局skills存储位置: `D:\code\skills`

## Project Context
- **Main project**: Vue to Playwright Test Generator
- Project path: `d:\code\python_project\ui-automation-generator`
- Python version: 3.12
- Core functionality: Generates Playwright tests from Vue components
- Documentation files:
  - `claude.md` - Quick reference for Claude Code
  - `CODE_WIKI.md` - Comprehensive code documentation
  - `AGENTS.md` - Skills configuration
- 全局Skills存储结构:
  ```
  D:\code\skills\
  ├── external\          # 外部来源的skills
  │   ├── superpowers\   # Superpowers框架
  │   └── playwright-skill\  # Playwright测试技能
  └── custom\            # 自己构建的skills
  ```
- 本项目自定义Skills:
  - skill-configurator - 用于快速配置新项目的Agents环境（存储在项目本地.skills目录）
  - uicode-to-automation-test - 从Vue/React组件生成Playwright自动化测试（存储在.claude/skills/），已修复Python import路径、事件去重、测试命名、移植了智能断言生成器，整合了playwright-skill完整指南
- playwright-skill - 通过junction链接到.claude/skills/playwright-skill/，作为uicode-to-automation-test的引用依赖