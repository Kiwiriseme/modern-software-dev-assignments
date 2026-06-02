# Week 7 Write-up
Tip: To preview this markdown file
- On Mac, press `Command (⌘) + Shift + V`
- On Windows/Linux, press `Ctrl + Shift + V`

## Instructions

Fill out all of the `TODO`s in this file.

## Submission Details

Name: **TODO** \
SUNet ID: **TODO** \
Citations: **TODO**

This assignment took me about **TODO** hours to do. 


## Task 1: Add more endpoints and validations
a. Links to relevant commits/issues
> https://github.com/Kiwiriseme/modern-software-dev-assignments/pull/1

b. PR Description
> ## 问题描述：
-1. 原文件的notes和action_items的CRUD的功能不够完善，无法获取单条记录并删除
-2. 原文件的schema内的数据类接受无界字符串，很容易用垃圾数据填充数据库。
## 解决：
- 1. 新增端点
   - `GET    /notes/{note_id}` → 未找到时返回 404
   - `DELETE /notes/{note_id}` → 删除成功时返回 200 `{"ok": true}`
   - `GET    /action-items/{item_id}` → 未找到时返回 404
   - `DELETE /action-items/{item_id}` → 删除成功时返回 200 `{"ok": true}`
- 2. 为 `NoteCreate`、`ActionItemCreate` 和 PATCH payload 添加了 `Field(min_length=…, max_length=…)` 以及拒绝纯空白输入的 `field_validator`。限制：
-`title`：1–200 个字 ‘content`：1–5000 个字符 
-'description'：1–1000 个字符
## 建议：
本 PR 未添加新的自动化测试；建议在后续 PR 中为新的边界添加测试用例。


c. Graphite Diamond generated code review
> Platform compatibility issue: The command set PYTHONPATH=.&& pytest -q backend/tests uses Windows-specific syntax. This will fail on Unix-like systems (Linux/macOS) where the original syntax was correct.

Fix: Either keep the Unix syntax or use a platform-agnostic approach:

PYTHONPATH=. pytest -q backend/tests

## Task 2: Extend extraction logic
a. Links to relevant commits/issues
> https://github.com/Kiwiriseme/modern-software-dev-assignments/pull/2

b. PR Description
> ## 问题：
原代码仅识别**两种**行动项：
1. 以 `TODO:` / `ACTION:` 开头的行（不区分大小写）
2. 以 `!` 结尾的行
## 解决：
函数仍然在（已清理的）行上单次遍历。对于每行，它跟踪一个 `matched` 标志，以便当一行匹配多个模式时永远不会被追加两次。新规则，按优先级排序：
1. **现有：** `TODO:` / `ACTION:` 前缀 → 发出该行，设置 `matched`。
2. **现有：** 尾部 `!` → 发出该行（仅当尚未匹配时）。
3. **新增：** `[ ] ` / `[x] ` 复选框前缀 → 发出任务文本**不带** `[ ] ` / `[x] ` 标记（4 个字符），以便存储的描述是干净的（例如 `follow up with eng`）。
4. **新增：** 任何 `by <token>` 或 `due <token>` 短语（正则 `\b(by|due)\s+\S+`) → 发出该行。捕获不使用复选框或冒号标签的自然"by Friday"截止日期语言。
5. **新增：** 开头的优先级标签 `[high]` / `[medium]` / `[low]` → 发出该行（标签保留为描述的一部分；下游消费者可以剥离它以获取干净的字符串）。

c. Graphite Diamond generated code review
> Graphite found no issues

## Task 3: Try adding a new model and relationships
a. Links to relevant commits/issues
> https://github.com/Kiwiriseme/modern-software-dev-assignments/pull/3

b. PR Description
> ## 问题
`notes` 和 `action_items` 是孤立的记录。第七周基线没有办法在 `q=` 文本搜索之外组织笔记，也没有办法在笔记间共享标签
##解决
1. **Schema（`models.py`）** — 添加了：
   - `Tag` 表，包含 `id`、`name`（唯一，50 个字符）和继承的 `TimestampMixin` 列（`created_at`、`updated_at`）。
   - `note_tags` 关联表（`note_id` + `tag_id` 上的复合主键，每个都有一个指向其父表的 `ForeignKey`）。
   - `Note.tags = relationship("Tag", secondary=note_tags, back_populates="notes")` 和 `Tag.notes` 的反向关系。
2. **Pydantic（`schemas.py`）** — 添加了 `TagCreate` 和 `TagRead`，并将 `tags: list[TagRead]` 嵌入 `NoteRead`，以便现有的 `GET /notes/` payload 现在在序列化每个笔记时包含其标签。
3. **路由：**
   - `routers/tags.py`（新）— `GET /tags/`（带有 `q`、`skip`、`limit`、`sort`）和 `POST /tags/`。
   - `routers/notes.py` — 添加了 `POST /notes/{note_id}/tags/{tag_id}` 以将现有标签与现有笔记关联；如果任一方缺失则返回 404。
4. **应用 wiring（`main.py`）** — 包含了新的 `tags_router`。


c. Graphite Diamond generated code review
> Graphite found no issues

## Task 4: Improve tests for pagination and sorting
a. Links to relevant commits/issues
> https://github.com/Kiwiriseme/modern-software-dev-assignments/pull/4

b. PR Description
> ## 问题
基线测试套件（`backend/tests/test_notes.py`、`test_action_items.py`、`test_extract.py`）仅对快乐路径进行冒烟测试。分页、排序以及搜索和分页之间的交互**完全没有**覆盖，因此未来对 `list_*` 路由的重构可能悄无声息地破坏这些行为，而 CI 不会捕获它。
## 解决
一个新文件，八个测试用例，全部使用 `conftest.py` 中的现有 `client` fixture（为每个测试提供隔离的临时 SQLite DB）。
| # | 测试 | 固定内容 |
|---|---|---|
| 1 | `test_skip_limit_pagination` | 创建 5 个笔记，断言 `skip=0/limit=2`、`skip=2/limit=2`、`skip=4/limit=2` 返回 2/2/1 个项目，具有**不相交 ID**，其并集正好是创建的 5 个 ID。 |
| 2 | `test_sort_by_title_asc` | 插入 `C, A, B`，断言 `?sort=title` 返回 `A, B, C`。 |
| 3 | `test_sort_by_title_desc` | 相同数据，`?sort=-title` 返回 `C, B, A`。 |
| 4 | `test_invalid_sort_field_falls_back_to_created_at_desc` | `?sort=nonexistent_field` 返回 200 以及带种子记录的响应（路由在未知字段上回退到 `created_at` desc；此测试固定该行为）。 |
| 5 | `test_action_items_pagination_and_sort` | 为 `/action-items/` 混合 `skip+limit` 和 `sort=description`。 |
| 6 | `test_search_with_pagination` | 4 个共享关键词的笔记 + 1 个无关笔记，断言 `?q=Shared&skip=0&limit=2` 和 `?q=Shared&skip=2&limit=2` 是不相交的。 |
| 7 | `test_skip_past_end_returns_empty` | 针对单行 DB 的 `?skip=10&limit=5` 返回 `[]`，而不是错误。 |
| 8 | `test_default_sort_is_created_at_desc` | 无 `sort` 参数时，较新的项目排在前面。 |
| 9 | `test_action_items_completed_filter_with_pagination` | 将 `completed=true` 与 `skip` 和 `limit=1` 组合，断言过滤器在分页中存活。 |

c. Graphite Diamond generated code review
> Graphite found no issues

## Brief Reflection 
a. The types of comments you typically made in your manual reviews (e.g., correctness, performance, security, naming, test gaps, API shape, UX, docs).
> 正确性，测试覆盖，API设计和解决的问题

b. A comparison of **your** comments vs. **Graphite’s** AI-generated comments for each PR.
> Graphite 的检查深度有限，无法发现更深层的问题，基本只能发现代码层面的问题，且有些代码解决的也有些问题，如task1发现的问题在makefile内，这个问题我的判断主要是因为系统的差异，在windows系统上需要设置成set PYTHONPATH才能正确make run或test，这个问题也显示出AI在识别跨平台的代码问题，发现平台之间的兼容上是比人工审查更好的。

c. When the AI reviews were better/worse than yours (cite specific examples)
> AI 更好时
- 跨平台语法问题（如 Task 1 的 PYTHONPATH=.&& Windows 特殊语法）
- 机械性的代码风格问题
- 重复性检查（如多个文件中的相同模式）
AI 更差时
- 理解业务上下文：Graphite 无法理解为什么某些验证规则是业务需要的
- 复杂的交互逻辑：比如分页与搜索组合时的行为
- 测试质量评估：Graphite 只检查测试存在与否，不评估测试是否真正验证了关键行为

d. Your comfort level trusting AI reviews going forward and any heuristics for when to rely on them.
>我认为可依赖 AI 审查的场景 ：
- 语法和格式问题
- 安全漏洞扫描
- 跨平台兼容性问题
需谨慎依赖 AI 审查的场景 ：
- 业务逻辑正确性
- 测试覆盖率评估
- 性能关键代码
- API 设计决策



