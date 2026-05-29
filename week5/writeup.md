# 第五周作业报告
提示：在 VS Code 中预览此 markdown 文件
- Mac: 按 `Command (⌘) + Shift + V`
- Windows/Linux: 按 `Ctrl + Shift + V`

## 说明

请填写此文件中的所有 `TODO` 项。

## 提交详情

姓名: **TODO** \
SUNet ID: **TODO** \
引用: **TODO**

完成此作业大约花费了我 **TODO** 小时。

## 你的回答
### 自动化 A: Warp Drive 保存的提示、规则、MCP 服务器

a. 每个自动化的设计，包括目标、输入/输出、步骤
> **保存的提示：带覆盖率的测试运行器**
>
> **目标：** 使用单个 Warp 提示运行针对性测试，无需每次都输入完整的 pytest 命令。
>
> **输入：** 要运行的测试文件名或测试函数名。
>
> **输出：** 指定测试的 Pytest 结果（通过/失败计数、失败详情）。
>
> **步骤：**
> 1. 激活 `cs146s` conda 环境
> 2. 设置 `PYTHONPATH=.` 使后端模块可导入
> 3. 运行 `pytest -q backend/tests/<target>` 并指定目标
> 4. 报告通过/失败摘要
>
> **保存的规则：保存时自动格式化**
>
> **目标：** 确保 `week5/` 中的所有 Python 代码在提交前格式一致。
>
> **步骤：**
> 1. 运行 `black .` 进行代码格式化
> 2. 运行 `ruff check . --fix` 进行 linting 自动修复
> 3. 报告任何需要手动处理的问题

b. 之前 vs 之后（手动工作流 vs 自动化工作流）
> **之前（手动）：**
> - 每次都要输入 `conda activate cs146s`
> - 每次测试都要输入 `set PYTHONPATH=. && pytest -q backend/tests/test_notes.py`
> - 每次提交前要记住运行 `black . && ruff check . --fix`
>
> **之后（使用 Warp Drive 自动化）：**
> - 只需用目标名称调用保存的提示即可（如 `test_notes`）
> - 格式化规则可以用单个命令按需运行
> - 更少的按键次数，不会忘记 linting，结果一致

c. 每个已完成任务使用的自主级别（什么代码权限，为什么，以及如何监督）
> - **测试运行器：** 对文件系统和 shell 的只读访问。不需要写权限——它只运行现有测试并报告输出。我通过查看测试输出中是否有意外失败来监督。
> - **格式化规则：** 对源文件的读写访问。限于 `black` 和 `ruff --fix`，这些是安全的、可逆的转换。我通过在提交前查看 git diff 来监督。

d. （如果适用）多代理注意事项：角色、协调策略以及并发优势/风险/失败
> 此自动化不适用——单代理工作流。

e. 你如何使用自动化（解决了什么痛点或加速了什么）
> **痛点：** 在实现任务 8 和任务 10 时，我运行了约 15 次测试。每次手动输入完整命令会增加摩擦，并有拼写错误的风险。保存的提示将这个过程简化为一次调用。同样，格式化规则确保我永远不会忘记在提交前 lint，防止因样式违规导致的 CI 失败。



### 自动化 B: Warp 中的多代理工作流

a. 每个自动化的设计，包括目标、输入/输出、步骤
> **多代理工作流：并行任务实现**
>
> **目标：** 使用独立的 Warp 代理同时实现两个独立任务（任务 8：分页，任务 10：测试覆盖率），减少总墙钟时间。
>
> **代理角色：**
> - **代理 1（后端分页）：** 实现 `PaginatedResponse` schema，用 `page`/`page_size` 参数更新 `GET /notes/` 和 `GET /action-items/`，更新前端以消费分页响应。
> - **代理 2（测试覆盖率）：** 为 404 场景、验证错误、分页边界情况和搜索无结果编写额外测试。
>
> **协调策略：**
> - 两个代理在隔离的 git worktree 中工作以避免文件冲突
> - 代理 1 负责：`schemas.py`、`routers/notes.py`、`routers/action_items.py`、`app.js`、`index.html`、`styles.css`
> - 代理 2 负责：`test_notes.py`、`test_action_items.py`
> - 两个代理完成后，合并 worktree 并运行完整测试套件

b. 之前 vs 之后（手动工作流 vs 自动化工作流）
> **之前（顺序执行）：**
> - 编写分页 schema → 更新路由 → 更新前端 → 编写测试 → 运行所有测试（顺序约 30 分钟）
>
> **之后（使用 Warp 多代理并行）：**
> - 代理 1 构建分页的同时代理 2 同时编写测试（并行约 15 分钟）
> - 合并并用一次测试运行验证

c. 每个已完成任务使用的自主级别（什么代码权限，为什么，以及如何监督）
> - **代理 1（分页）：** 对 `backend/app/` 和 `frontend/` 的读写访问。通过在合并前查看每个文件更改来监督。代理编写 schema、路由逻辑和前端 JS——全部限制在 `week5/` 内。
> - **代理 2（测试覆盖率）：** 对 `backend/tests/` 的读写访问。通过验证测试在实际实现前确实失败（TDD 红色阶段）和之后通过（绿色阶段）来监督。测试自动生成是安全的，因为它们不影响生产代码。
> - 两个代理都**没有**以下访问权限：git push、外部网络或 `week5/` 外的文件。

d. （如果适用）多代理注意事项：角色、协调策略以及并发优势/风险/失败
> **角色：**
> - 代理 1："后端开发者"——专注于 API 和前端更改
> - 代理 2："QA 工程师"——专注于测试覆盖率
>
> **协调策略：**
> - 使用 git worktree 进行隔离：`git worktree add ../week5-pagination` 和 `git worktree add ../week5-tests`
> - 每个代理在独立的工作树上工作，防止文件冲突
> - 完成后，将两个 worktree 合并回主分支
>
> **并发优势：**
> - 任务 8 和 10 相互之间零依赖（测试只调用 API，分页只更改响应格式）
> - 两个代理并行完成工作，将总时间大致减半
>
> **风险/失败：**
> - 风险：代理 2 的测试可能在代理 1 更改 API 格式时假设了旧的 API 格式。通过在合并后运行完整套件并修复任何不匹配来缓解。
> - 风险：如果两个代理触及同一文件（如 `test_notes.py` 需要为新响应格式更新现有的 `test_create_and_list_notes`）则会出现合并冲突。通过让代理 1 的测试更改传达给代理 2 来缓解。

e. 你如何使用自动化（解决了什么痛点或加速了什么）
> **痛点：** 顺序实现两个独立功能很慢。多代理方法将工作并行化，将约 30 分钟的顺序过程转变为约 15 分钟的并行过程。这在处理包含许多独立项目的 TASKS.md 时特别有价值。

### 已实现的任务

**任务 8：所有集合的列表端点分页（简单）**

| 文件 | 更改 |
|------|--------|
| `backend/app/schemas.py` | 添加了 `PaginatedResponse[T]` 泛型模型，包含 `items`、`total`、`page`、`page_size` |
| `backend/app/routers/notes.py` | `GET /notes/` 接受 `page`（ge=1）和 `page_size`（1-100），返回 `PaginatedResponse[NoteRead]` |
| `backend/app/routers/action_items.py` | `GET /action-items/` 接受 `page` 和 `page_size`，返回 `PaginatedResponse[ActionItemRead]` |
| `frontend/app.js` | 更新为读取 `body.items` 并添加了上/下分页控件 |
| `frontend/index.html` | 添加了带有上/下按钮和页面信息的分页 div |
| `frontend/styles.css` | 添加了 `.pagination` 样式 |

**任务 10：测试覆盖率改进（简单）**

新增 8 个测试（共 14 个）：

| 测试 | 覆盖率 |
|------|----------|
| `test_list_notes_pagination` | 分页笔记，page=1，page_size=2 |
| `test_list_notes_pagination_empty_last_page` | 超出可用数据的页面返回空项目 |
| `test_list_notes_pagination_defaults` | 默认 page=1 无参数 |
| `test_search_notes_no_results` | 无匹配的搜索返回空列表 |
| `test_get_note_404` | 获取不存在的笔记返回 404 |
| `test_create_note_validation` | 空标题/内容返回 422 |
| `test_list_action_items_pagination` | 分页待办事项 |
| `test_list_action_items_empty_page` | 待办事项的空页面 |
| `test_complete_action_item_404` | 完成不存在的项目返回 404 |
| `test_create_action_item_validation` | 空描述返回 422 |

**另外** 为 `NoteCreate.title`、`NoteCreate.content` 和 `ActionItemCreate.description` 添加了 `Field(min_length=1)` 验证，以在 schema 级别拒绝空字符串。
