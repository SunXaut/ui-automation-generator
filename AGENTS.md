# Agents

## 全局Skills存储结构

所有全局skills存储在 `D:\code\skills` 目录下，按照来源分为两个子文件夹：

```
D:\code\skills\
├── external\          # 外部来源的skills（从GitHub等克隆）
│   ├── superpowers\   # Superpowers框架
│   └── playwright-skill\  # Playwright测试技能
└── custom\            # 自己构建的skills
    └── skill-configurator\  # Skill配置器（本项目本地存储）
```

## 全局Skills引用

### Superpowers Skills

Superpowers是一个完整的软件开发工作流框架，提供了一系列可组合的"技能"（Skills），用于增强Agent的开发能力。

**安装位置**：`D:\code\skills\external\superpowers`
**Skills链接**：`~/.agents/skills/superpowers`

#### 核心工作流技能

1. **brainstorming（头脑风暴）**
   - 在编写代码前激活
   - 通过提问提炼粗略想法，探索替代方案
   - 将设计分段展示以供验证
   - 保存设计文档

2. **using-git-worktrees（使用Git工作树）**
   - 在设计批准后激活
   - 在新分支上创建隔离工作空间
   - 运行项目设置，验证干净的测试基线

3. **writing-plans（编写计划）**
   - 在获得批准的设计后激活
   - 将工作分解为小块任务（每个2-5分钟）
   - 每个任务包含确切的文件路径、完整代码、验证步骤

4. **subagent-driven-development（子代理驱动开发）/ executing-plans（执行计划）**
   - 在有计划时激活
   - 为每个任务分派新的子代理，进行两阶段审查（规范合规性，然后代码质量）
   - 或批量执行并设置人工检查点

5. **test-driven-development（测试驱动开发）**
   - 在实现期间激活
   - 强制执行RED-GREEN-REFACTOR：编写失败的测试，观察失败，编写最小代码，观察通过，提交
   - 删除测试前编写的代码

6. **requesting-code-review（请求代码审查）**
   - 在任务之间激活
   - 根据计划进行审查，按严重程度报告问题
   - 严重问题阻止进展

7. **finishing-a-development-branch（完成开发分支）**
   - 在任务完成时激活
   - 验证测试，呈现选项（合并/PR/保留/丢弃），清理工作树

#### 技能库

**测试技能**：
- `test-driven-development` - RED-GREEN-REFACTOR循环（包括测试反模式参考）

**调试技能**：
- `systematic-debugging` - 4阶段根因分析流程（包括根因追踪、深度防御、基于条件的等待技术）
- `verification-before-completion` - 确保问题真正修复

**协作技能**：
- `brainstorming` - 苏格拉底式设计提炼
- `writing-plans` - 详细的实现计划
- `executing-plans` - 带检查点的批量执行
- `dispatching-parallel-agents` - 并发子代理工作流
- `requesting-code-review` - 预审查检查清单
- `receiving-code-review` - 响应代码审查

**开发技能**：
- `subagent-driven-development` - 子代理驱动开发
- `using-git-worktrees` - 使用Git工作树
- `finishing-a-development-branch` - 完成开发分支

**元技能**：
- `using-superpowers` - 使用Superpowers
- `writing-skills` - 编写技能

### Playwright Skill

Playwright Skill是一个AI驱动的Playwright测试最佳实践指南集合，提供70+个测试指南，涵盖E2E、API、组件、视觉、可访问性和安全测试。

**安装位置**：`D:\code\skills\external\playwright-skill`
**Skills链接**：`~/.agents/skills/playwright-skill`

#### Skill Packs

**Core（核心）- 46个指南**
- **定位器和断言**：locators、assertions-and-waiting、locator-strategy
- **测试组织**：fixtures-and-hooks、test-organization、test-data-management、test-architecture
- **认证和API**：authentication、auth-flows、api-testing、network-mocking
- **UI测试**：forms-and-validation、drag-and-drop、file-upload-download
- **框架集成**：react、vue、angular、nextjs
- **高级测试**：visual-regression、accessibility、component-testing、performance-testing、security-testing
- **调试**：debugging、error-index、flaky-tests、common-pitfalls

**CI（持续集成）- 9个指南**
- GitHub Actions、GitLab CI、CircleCI、Azure DevOps、Jenkins
- Docker和容器、并行和分片、报告和产物、测试覆盖率

**POM（页面对象模型）- 2个指南**
- Page Object Model模式、POM vs Fixtures vs Helpers

**Migration（迁移）- 2个指南**
- 从Cypress迁移、从Selenium迁移

**Playwright CLI - 11个指南**
- CLI浏览器自动化、截图、追踪、会话管理、设备模拟

### Compound Engineering

Compound Engineering是一个让AI Agent自动学习的框架，通过提取会话中的模式和经验教训，随时间复利增长知识。

**核心理念**：今天的Agent审查自己的工作，提取模式和教训，更新指令。明天的Agent比今天更聪明。

#### 复利循环

```
┌─────────────────────────────────────────┐
│           日常工作                       │
│  会话、聊天、任务、决策                    │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│        夜间回顾 (每天晚上10:30)          │
│  • 扫描过去24小时的所有会话                │
│  • 提取学习成果和模式                      │
│  • 更新MEMORY.md和AGENTS.md              │
│  • 提交并推送更改                         │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│        第二天                            │
│  Agent读取更新的指令                      │
│  受益于昨天的学习成果                      │
└─────────────────────────────────────────┘
```

#### 提取内容

- **Patterns（模式）**：重复出现的有效方法
- **Gotchas（陷阱）**：失败或导致问题的事项
- **Preferences（偏好）**：发现的用户偏好
- **Decisions（决策）**：关键决策及其理由
- **TODOs（待办）**：未完成的事项需要记住

#### 使用命令

```bash
# 回顾过去24小时并更新memory
npx compound-engineering review

# 创建每小时memory快照
npx compound-engineering snapshot

# 设置自动化夜间回顾（cron）
npx compound-engineering setup-cron
```

#### Memory文件结构

**MEMORY.md（长期记忆）**
- Patterns That Work - 要重复的方法
- Gotchas to Avoid - 要避免的事项
- User Preferences - 用户偏好
- Project Context - 项目上下文

**memory/YYYY-MM-DD.md（每日记忆）**
- Sessions - 会话记录
- Decisions - 决策记录
- Learnings - 学习成果
- Open Items - 未完成事项

### Skill Configurator

Skill Configurator是一个自定义skill，用于快速在新工程中配置Agents Skills环境。

**本地位置**：`d:\code\python_project\面试\booster\.skills\skill-configurator`
**目标全局位置**：`D:\code\skills\custom\skill-configurator`

> ⚠️ 注意：由于权限限制，当前skill仅存在于项目本地。如需同步到全局位置，请手动复制SKILL.md到 `D:\code\skills\custom\skill-configurator\` 目录。

#### 功能

1. 创建项目AGENTS.md文件
2. 创建MEMORY.md文件
3. 创建memory目录结构
4. 配置虚拟环境（可选）
5. 链接全局skills到项目

#### 使用方法

当用户要求在新项目中配置skills时触发，执行以下步骤：

1. **询问项目信息**：项目名称、路径、Python版本、是否需要虚拟环境
2. **创建目录结构**：在项目目录下创建 memory/ 目录
3. **创建AGENTS.md**：包含全局Skills存储结构、引用、使用示例
4. **创建MEMORY.md**：包含Patterns That Work、Gotchas to Avoid、User Preferences、Project Context
5. **创建当日memory文件**：memory/YYYY-MM-DD.md
6. **链接全局Skills**：创建skills的junction链接

#### 触发条件

当用户说以下内容时触发此Skill：
- "配置项目的AGENTS"
- "为新项目配置skills"
- "设置项目环境"
- "初始化项目配置"
- "帮我配置skill"

### OpenAI Skills

OpenAI提供了一系列技能（Skills）相关的功能，这些技能可以被Agent调用以增强其能力。

#### 技能管理

- **Skills资源**：位于`openai.resources.skills`模块中，提供了技能的创建、管理和使用功能。
- **技能版本控制**：通过`openai.resources.skills.versions`模块管理技能的不同版本。
- **技能内容**：通过`openai.resources.skills.content`模块处理技能的内容。

#### 技能引用

在Agent中引用技能时，可以使用`SkillReference`类型，该类型定义在`openai.types.responses.skill_reference`模块中。

### 本地环境中的技能

- **本地环境**：通过`local_environment`模块管理本地环境中的技能。
- **容器**：通过`containers`模块管理包含技能的容器。

## Agent使用Skills的示例

```python
from openai import OpenAI
from openai.types.responses.skill_reference import SkillReference

client = OpenAI()

# 创建一个Agent并引用技能
def create_agent_with_skills():
    agent = client.agents.create(
        name="My Agent",
        instructions="You are a helpful assistant.",
        tools=[
            {
                "type": "skill",
                "skill_reference": SkillReference(
                    skill_id="skill_123",
                    version_id="version_123"
                )
            }
        ]
    )
    return agent
```

## 技能的类型和用途

1. **工具技能**：提供特定功能的工具，如文件操作、网络请求等。
2. **知识技能**：提供特定领域的知识，如数学、科学等。
3. **流程技能**：提供特定业务流程的处理能力。

## 技能的开发和部署

1. **创建技能**：使用OpenAI API创建自定义技能。
2. **测试技能**：在本地环境中测试技能的功能。
3. **部署技能**：将技能部署到生产环境中供Agent使用。

## 最佳实践

- **模块化设计**：将复杂功能拆分为多个小型、专注的技能。
- **版本控制**：对技能进行版本控制，确保向后兼容性。
- **文档化**：为每个技能提供详细的文档，包括用途、参数和返回值。
- **测试**：为技能编写单元测试，确保其功能正常。
- **知识复利**：使用Compound Engineering定期回顾和更新知识。
- **分类存储**：外部skills放在`external`目录，自定义skills放在`custom`目录。

## 更新和维护

### Superpowers更新

```bash
cd D:\code\skills\external\superpowers && git pull
```

技能通过symlink即时更新。

### Compound Engineering回顾

```bash
# 手动触发回顾
npx compound-engineering review

# 创建快照
npx compound-engineering snapshot
```

### 添加新的外部Skill

```bash
# 克隆到external目录
git clone <repository-url> D:\code\skills\external\<skill-name>

# 创建junction链接
New-Item -ItemType Junction -Path "$env:USERPROFILE\.agents\skills\<skill-name>" -Target "D:\code\skills\external\<skill-name>\skills"
```

### 添加新的自定义Skill

```bash
# 在custom目录创建skill文件夹
New-Item -ItemType Directory -Path "D:\code\skills\custom\<skill-name>"

# 创建SKILL.md文件和其他必要文件
# ...

# 创建junction链接
New-Item -ItemType Junction -Path "$env:USERPROFILE\.agents\skills\<skill-name>" -Target "D:\code\skills\custom\<skill-name>"
```