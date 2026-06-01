# Week 6 报告
提示：预览此 Markdown 文件
- Mac：按 `Command (⌘) + Shift + V`
- Windows/Linux：按 `Ctrl + Shift + V`

## 说明

填写文件中的所有 `TODO`。

## 提交信息

姓名：**TODO** \
SUNet ID：**TODO** \
引用/致谢：**TODO**

本次作业大约花费 **TODO** 小时。


## Findings 概览

Semgrep 共报告了 **12 个 findings**，全部属于 **Code** 产品（SAST）和 **security** 类别。本次扫描未发现 Secrets 或 SCA 相关的问题。Findings 按规则类别分布如下：

| 规则类别 | 数量 | 严重程度 |
|---|---|---|
| `generic-sql-fastapi` — 动态拼接 SQL 导致注入 | 3 | Critical |
| `sqlalchemy-fastapi` — 通过 SQLAlchemy text() 导致 SQL 注入 | 1 | Critical |
| `tainted-code-stdlib-fastapi` — 通过 eval() 导致代码注入 | 1 | Critical |
| `tainted-path-traversal-stdlib-fastapi` — 路径遍历 | 1 | High |
| `tainted-os-command-stdlib-fastapi-secure-default` — 命令注入 | 1 | High |
| `subprocess-shell-true` — 危险的 subprocess shell=True 用法 | 1 | High |
| `avoid-sqlalchemy-text` — sqlalchemy.text() 绕过 ORM 保护 | 1 | High |
| `wildcard-cors` — CORS 通配符 `*` 配置 | 1 | Medium |
| `dynamic-urllib-use-detected` — 动态 urllib 调用（SSRF 风险） | 1 | Medium |
| `eval-detected` — 使用了 eval() | 1 | Medium |

大部分 findings 集中在 `week6/backend/app/routers/notes.py`，该文件包含多个故意留有漏洞的 `/debug/*` 端点（eval 执行、命令执行、任意 URL 请求、任意文件读取）。通配符 CORS 配置位于 `main.py`。`extract.py` 中硬编码的 API Token 虽然未在此次扫描中被标记为独立的 secret finding，但同样是安全隐患。

**误报 / 忽略的规则：** `db.py` 中 `apply_seed_if_needed` 的 `generic-sql-fastapi` finding 风险较低——SQL 语句来自受信任的本地 `seed.sql` 文件，而非用户输入。但作为纵深防御措施，仍然强化了文件路径解析逻辑。通配符 CORS 配置在本地开发场景下可接受，生产环境应予以限制。


## 修复 #1：SQL 注入 — unsafe_search 参数化查询

a. 文件及行号
> `week6/backend/app/routers/notes.py`，第 69–92 行（`unsafe_search` 函数）

b. Semgrep 标记的规则/类别
> `python.fastapi.db.generic-sql-fastapi` — ID 820692707、820692706、820692705（Critical / High 置信度）

c. 风险简述
> `unsafe_search` 端点通过 Python f-string 将用户输入 `q` 直接拼接进 `text()` SQL 字符串：`f"...WHERE title LIKE '%{q}%'..."`。攻击者可以构造恶意 `q` 参数（如 `' OR 1=1 --`）来绕过查询逻辑、窃取任意数据或执行破坏性 SQL 语句。这是典型的 SQL 注入漏洞。

d. 修改内容（代码 diff 与说明，AI 工具使用）
> 使用 Claude Code（VS Code 插件）将 f-string 拼接替换为 SQLAlchemy 的参数绑定。
>
> **修改前：**
> ```python
> sql = text(
>     f"""
>     SELECT id, title, content, created_at, updated_at
>     FROM notes
>     WHERE title LIKE '%{q}%' OR content LIKE '%{q}%'
>     ORDER BY created_at DESC
>     LIMIT 50
>     """
> )
> rows = db.execute(sql).all()
> ```
>
> **修改后：**
> ```python
> sql = text(
>     """
>     SELECT id, title, content, created_at, updated_at
>     FROM notes
>     WHERE title LIKE :q OR content LIKE :q
>     ORDER BY created_at DESC
>     LIMIT 50
>     """
> )
> rows = db.execute(sql, {"q": f"%{q}%"}).all()
> ```

e. 为什么这样修复
> `:q` 命名占位符告诉 SQLAlchemy 将该值作为**绑定参数**处理，而非 SQL 语法的一部分。数据库驱动会在替换前对值进行安全转义，因此即使攻击者提交 `' OR 1=1 --` 作为 `q` 的值，它也会被当作普通搜索字符串而非可执行 SQL。这从根本上消除了 SQL 注入的攻击面。


## 修复 #2：代码注入 — eval() 替换为 ast.literal_eval()

a. 文件及行号
> `week6/backend/app/routers/notes.py`，第 102–107 行（`debug_eval` 函数）

b. Semgrep 标记的规则/类别
> `python.fastapi.code.tainted-code-stdlib-fastapi.tainted-code-stdlib-fastapi` — ID 820692708（Critical / High 置信度）

c. 风险简述
> `debug_eval` 端点将用户提交的 `expr` 直接传给 Python 的 `eval()`，这意味着可以执行任意 Python 表达式。攻击者可以运行 `__import__('os').system('...')` 或读取敏感文件，从而完全控制服务器进程。

d. 修改内容（代码 diff 与说明，AI 工具使用）
> 使用 Claude Code（VS Code 插件）将 `eval()` 替换为 `ast.literal_eval()`。
>
> **修改前：**
> ```python
> @router.get("/debug/eval")
> def debug_eval(expr: str) -> dict[str, str]:
>     result = str(eval(expr))  # noqa: S307
>     return {"result": result}
> ```
>
> **修改后：**
> ```python
> @router.get("/debug/eval")
> def debug_eval(expr: str) -> dict[str, str]:
>     import ast
>
>     result = str(ast.literal_eval(expr))
>     return {"result": result}
> ```

e. 为什么这样修复
> `ast.literal_eval()` 仅评估 Python **字面量**——字符串、数字、元组、列表、字典、布尔值和 `None`。任何包含函数调用、属性访问、运算符或导入的表达式都会在解析阶段抛出 `ValueError`。这意味着 `__import__('os').system('...')` 等恶意 payload 在解析时即被拒绝，彻底消除代码注入风险，同时仍允许对数据字面量进行安全评估。


## 修复 #3：SQL 注入防御加固 — apply_seed_if_needed 路径解析强化

a. 文件及行号
> `week6/backend/app/db.py`，第 43–59 行（`apply_seed_if_needed` 函数）

b. Semgrep 标记的规则/类别
> `python.fastapi.db.generic-sql-fastapi` — ID 820692706（Critical / High 置信度）

c. 风险简述
> `apply_seed_if_needed` 函数读取 SQL 文件并通过 `conn.execute(text(statement))` 逐条执行。虽然 seed 文件是受信任的本地资源（不受用户控制），但 Semgrep 的污点分析会将变量传入 `text()` 标记为潜在的 SQL 注入点。此外，原始代码使用相对路径 `./data/seed.sql`，该路径依赖当前工作目录，若工作目录受攻击者控制则存在被操控的可能。

d. 修改内容（代码 diff 与说明，AI 工具使用）
> 使用 Claude Code（VS Code 插件）强化 seed 文件路径解析并重构代码结构。
>
> **修改前：**
> ```python
> seed_file = Path("./data/seed.sql")
> if newly_created and seed_file.exists():
>     with engine.begin() as conn:
>         sql = seed_file.read_text()
>         if sql.strip():
>             for statement in [s.strip() for s in sql.split(";") if s.strip()]:
>                 conn.execute(text(statement))
> ```
>
> **修改后：**
> ```python
> seed_file = (Path(__file__).parent.parent.parent / "data" / "seed.sql").resolve()
> if newly_created and seed_file.exists():
>     sql = seed_file.read_text()
>     if not sql.strip():
>         return
>     with engine.begin() as conn:
>         for statement in sql.split(";"):
>             stmt = statement.strip()
>             if stmt:
>                 conn.execute(text(stmt))
> ```

e. 为什么这样修复
> seed 文件路径现在基于源文件位置（`__file__`）解析，而非依赖进程工作目录，因此不受工作目录操控的影响。此处的 `text()` 调用仍然必要，因为 seed 文件包含 DDL 语句（CREATE TABLE），这些无法用 SQLAlchemy ORM 构造来表达。由于 seed 文件是版本控制下的静态可信本地资源，剩余的 `text()` 用法不存在实际的 SQL 注入风险——信任边界明确位于文件系统层面，而非用户输入。
