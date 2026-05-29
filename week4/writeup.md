# Week 4 Write-up
Tip: To preview this markdown file
- On Mac, press `Command (⌘) + Shift + V`
- On Windows/Linux, press `Ctrl + Shift + V`

## INSTRUCTIONS

Fill out all of the `TODO`s in this file.

## SUBMISSION DETAILS

Name: **TODO** \
SUNet ID: **TODO** \
Citations: **TODO**

This assignment took me about **TODO** hours to do. 


## YOUR RESPONSES
### Automation #1
a. Design inspiration (e.g. cite the best-practices and/or sub-agents docs)
> 子智能体最有效的用途之一是隔离那些会产生大量输出的操作。运行测试、获取文档或处理日志文件可能会消耗大量上下文。通过将这些任务委托给子智能体，冗长的输出会保留在子智能体的上下文中，而只有相关的摘要会返回到你的主对话中。（来源：sub-agents docs）主要先制作一个子智能体来完成测试任务，并生成摘要

b. Design of each automation, including goals, inputs/outputs, steps 
> 目标：运行测试、获取文档、处理日志文件等操作。
> 输入/输出：无，输出测试结果、文档、日志摘要等。
> 步骤：
> 1. 运行测试。
> 2. 获取测试结果。
> 3. 处理测试结果，提取摘要信息。

c. How to run it (exact commands), expected outputs, and rollback/safety notes
> 1. /agents
> 2. running
  3. 子智能体自动运行
  4. 子智能体返回摘要



d. Before vs. after (i.e. manual workflow vs. automated workflow)
> 手动工作流：
> 1. 打开终端，切换到项目目录
> 2. 手动运行 `pytest -q backend/tests`
> 3. 在大量输出中查找测试失败信息
> 4. 手动分析失败原因
> 5. 如果需要覆盖率，需单独运行 `coverage` 命令
>
> 自动化工作流：
> 1. 调用子代理并指定测试任务
> 2. 子代理自动运行测试和覆盖率检测
> 3. 子代理返回简洁的测试摘要，包括：
>    - 通过/失败的测试数量
>    - 失败测试的具体错误

e. How you used the automation to enhance the starter application
> 使用 test-runner 子智能体完成了以下工作：
> 1. 在添加新功能（tag 提取、note CRUD）后，通过子智能体运行测试获取摘要反馈，快速识别失败测试并修复。
> 2. 在每次代码修改后运行 `make test` 通过子智能体自动化测试流程，避免了手动分析 pytest 输出的时间。
> 3. 测试从最初的 3 个扩展到 14 个，全部通过。子智能体返回的摘要帮助快速定位了一个 validation 测试中的预期状态码错误（400 vs 422）。


### Automation #2
a. Design inspiration (e.g. cite the best-practices and/or sub-agents docs)
> CLAUDE.md 是一个特殊文件，Claude 会在每次对话开始时读取它。该文件需包含 Bash 命令、代码规范以及工作流规则，这能为 Claude 提供仅从代码中无法推断出的持久上下文。

b. Design of each automation, including goals, inputs/outputs, steps
> 目标：为 week4 项目创建 CLAUDE.md，提供代码规范和工作流指导，使 AI 能够更好地协助开发。
> 输入：项目结构信息、代码规范、工作流期望
> 输出：一份 CLAUDE.md 配置文件
> 步骤：
> 1. 分析项目结构（routers、tests、数据库等）
> 2. 确定代码规范（black/ruff 工具）
> 3. 定义工作流规则（如 typecheck 原则）
> 4. 编写 CLAUDE.md 文件

c. How to run it (exact commands), expected outputs, and rollback/safety notes
> 运行方式：当在 week4 目录开始新对话时，AI 会自动读取 CLAUDE.md
> 预期效果：
> - AI 了解如何运行应用：`make run` 或 `python -m uvicorn`
> - AI 知道测试位置：`backend/tests/`
> - AI 知道代码规范：使用 black/ruff，修改后运行 typecheck
> - AI 遵循 lint/test gates：提交前检查
> 安全注意事项：
> - 如果 CLAUDE.md 有误，可以直接编辑文件纠正
> - 不包含敏感信息，仅包含项目指引

d. Before vs. after (i.e. manual workflow vs. automated workflow)
> **手动工作流（Before）：**
> 1. 每次新对话开始时，需要手动告诉 AI：
>    - 如何运行应用
>    - 测试在哪里
>    - 代码规范是什么
> 2. 重复解释相同的基础信息，浪费时间
> 3. AI 可能不知道项目特定的工具和命令
>
> **自动化工作流（After）：**
> 1. 在 week4 目录创建 CLAUDE.md
> 2. 新对话开始时 AI 自动读取
> 3. AI 立即知道：
>    - 项目结构和入口点
>    - 代码规范和工具
>    - 推荐的工作流

e. How you used the automation to enhance the starter application
> 使用 week4/CLAUDE.md 自动化增强了开发工作流：
> 1. 创建了 week4/CLAUDE.md，包含项目结构、运行命令、代码规范和工作流规则，使 AI 在每次对话时自动获得项目上下文。
> 2. AI 自动知道使用 `make run` 启动应用、`make test` 运行测试、`make format` 和 `make lint` 检查代码质量。
> 3. 工作流规则（如 "先写测试再实现"、"修改后运行格式化"）确保代码变更一致性和质量。

### Automation #3
a. Design inspiration (e.g. cite the best-practices and/or sub-agents docs)
> 自定义斜杠命令让你能创建可复用的 Markdown 文件工作流，放在 `.claude/commands/` 目录下。这些命令可通过 `/` 调用，为重复性任务提供快速入口。最佳实践建议：保持命令聚焦、使用 `$ARGUMENTS`、偏好幂等步骤。（来源：Claude Code 最佳实践文档）

b. Design of each automation, including goals, inputs/outputs, steps
> 目标：创建两个自定义斜杠命令，用于测试运行和代码格式化检查。
> - `/tests`: 运行 pytest 测试套件，收集覆盖率数据，输出测试摘要和失败详情。
> - `/format`: 运行 black 和 ruff 进行代码格式化和 lint 检查，报告修改的文件和剩余问题。
> 输入：无（或可选的测试标记/路径）
> 输出：测试通过/失败统计、覆盖率报告、格式化修改文件列表

c. How to run it (exact commands), expected outputs, and rollback/safety notes
> 运行方式：
> 1. `/tests` — 在 Claude Code 对话中输入，自动执行 make test 和覆盖率检测
> 2. `/format` — 在 Claude Code 对话中输入，自动执行 black . 和 ruff check . --fix
> 预期输出：
> - `/tests`: 测试结果摘要、失败详情、覆盖率百分比
> - `/format`: 被 black 修改的文件列表、剩余 ruff 违规项
> 安全注意：
> - 只运行在项目目录内，不会修改项目外的文件
> - 格式化是可逆的（git checkout 可恢复）

d. Before vs. after (i.e. manual workflow vs. automated workflow)
> 手动工作流：
> 1. 打开终端，cd 到 week4 目录
> 2. 手动输入 `make test` 或 `make format`
> 3. 在大量输出中查找关键信息
>
> 自动化工作流：
> 1. 在 Claude Code 输入 `/tests` 或 `/format`
> 2. AI 自动执行命令、解析输出、提供结构化摘要
> 3. 节省时间，减少遗漏关键信息的风险

e. How you used the automation to enhance the starter application
> 使用自定义斜杠命令自动化增强了开发工作流：
> 1. `/tests` 命令在每次代码修改后运行，快速验证 14 个测试全部通过，在 Tag 提取、Note CRUD、Validation 等功能开发中持续使用。
> 2. `/format` 命令确保所有代码通过 black 和 ruff 检查，在添加新文件（.pre-commit-config.yaml、API.md）后运行，保持代码风格一致。
>