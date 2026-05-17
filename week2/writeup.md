# Week 2 Write-up
Tip: To preview this markdown file
- On Mac, press `Command (⌘) + Shift + V`
- On Windows/Linux, press `Ctrl + Shift + V`

## INSTRUCTIONS

Fill out all of the `TODO`s in this file.

## SUBMISSION DETAILS

Name: **李勤业** \
SUNet ID: **** \
Citations: ****

This assignment took me about **4** hours to do. 


## YOUR RESPONSES
For each exercise, please include what prompts you used to generate the answer, in addition to the location of the generated response. Make sure to clearly add comments in your code documenting which parts are generated.

### Exercise 1: Scaffold a New Feature
Prompt:
```
现在需要修改的代码week2/app/services/extract.py中的extract_action_items()，
需求是将功能的实现方式改为大模型驱动，利用OLLAMA来执行要素提取操作，代码要求如下：
1. 修改函数名为"extract_action_items_llm()"
2. 生成结构化输出（字符串的JSON数组）使用 Pydantic 并通过model_json_schema()对模式进行序列化
3. 保持代码风格一致
补充：我电脑上使用的ollama大模型为"mistral-nemo:12b"
```

Generated Code Snippets:

**Modified File: `week2/app/services/extract.py`**

- **Line 8**: Added `from pydantic import BaseModel` import
- **Lines 23-24**: Added Pydantic model for structured output
  ```python
  class ActionItems(BaseModel):
      items: list[str]
  ```
- **Lines 75-99**: Added `extract_action_items_llm()` function
  ```python
  def extract_action_items_llm(text: str) -> List[str]:
      response = chat(
          messages=[
              {
                  "role": "user",
                  "content": (
                      "Extract action items from the following text. "
                      "An action item is a specific, actionable task that someone needs to complete. "
                      "Return only the actionable items as a JSON array of strings, one per item. "
                      "Do not include narrative sentences that are not tasks.\n\n"
                      f"{text}"
                  ),
              }
          ],
          model="mistral-nemo:12b",
          format=ActionItems.model_json_schema(),
      )
      result = ActionItems.model_validate_json(response.message.content)
      seen: set[str] = set()
      unique: List[str] = []
      for item in result.items:
          lowered = item.strip().lower()
          if not lowered or lowered in seen:
              continue
          seen.add(lowered)
          unique.append(item.strip())
      return unique
  ```

### Exercise 2: Add Unit Tests
Prompt: 
```
请在 week2/tests/test_extract.py 文件中，为 extract_action_items_llm() 函数编写完整单元测试，需要覆盖多种输入场景：项目符号列表、关键字前缀任务行、普通段落文本、空白空输入等边界用例，规范编写测试用例并判断提取结果正确性。
```

Generated Code Snippets:

**Modified File: `week2/tests/test_extract.py`**

- **Lines 1-7**: Added imports (`json`, `unittest.mock.MagicMock`, `unittest.mock.patch`, `extract_action_items_llm`)
- **Lines 10-13**: Added helper function `_make_chat_response()` to mock LLM responses
  ```python
  def _make_chat_response(items: list[str]) -> MagicMock:
      resp = MagicMock()
      resp.message.content = json.dumps({"items": items})
      return resp
  ```
- **Lines 31-205**: Added `TestExtractActionItemsLLM` test class with 12 test methods
  - `test_bullet_list_input` (line 33): 项目符号列表输入
  - `test_keyword_prefixed_lines` (line 56): TODO/action/next 关键字前缀行
  - `test_plain_paragraph_text` (line 77): 普通段落叙述文本
  - `test_empty_input_returns_empty_list` (line 92): 空字符串边界
  - `test_whitespace_only_input` (line 101): 仅空白字符输入
  - `test_deduplication_case_insensitive` (line 110): 大小写不敏感去重
  - `test_empty_items_filtered_from_response` (line 123): LLM 返回空项的过滤
  - `test_whitespace_trimming_on_items` (line 135): 返回项空白字符修剪
  - `test_llm_returns_no_action_items` (line 145): 非任务文本无提取结果
  - `test_mixed_input_with_checkboxes_and_narrative` (line 155): 混合复选框/关键词/叙述文本
  - `test_chat_called_with_correct_model_and_format` (line 175): 验证调用参数
  - `test_multiline_bullet_list_with_various_prefixes` (line 187): 多种项目符号前缀

### Exercise 3: Refactor Existing Code for Clarity
Prompt: 
```
对后端代码进行重构，重点关注明确的 API 契约/模式、数据库层清理、应用生命周期/配置以及错误处理。
```

Generated/Modified Code Snippets:

**New File: `week2/app/schemas.py`**

创建 Pydantic schemas 定义明确的 API 契约，替换所有原始的 `Dict[str, Any]` 请求/响应：
```python
class NoteCreate(BaseModel):
    content: str = Field(..., min_length=1, description="The note content text")

class NoteRead(BaseModel):
    id: int
    content: str
    created_at: str

class ActionItemRead(BaseModel):
    id: int
    note_id: int | None = None
    text: str
    done: bool
    created_at: str

class ActionItemSummary(BaseModel):
    id: int
    text: str

class ExtractRequest(BaseModel):
    text: str = Field(..., min_length=1, description="The text to extract action items from")
    save_note: bool = Field(default=False, description="Whether to save the text as a note")

class ExtractResponse(BaseModel):
    note_id: int | None = None
    items: list[ActionItemSummary]

class MarkDoneRequest(BaseModel):
    done: bool = Field(default=True, description="Whether the action item is done")
```

**New File: `week2/app/config.py`**

创建集中式配置模块，使用 `@lru_cache` 单例模式管理所有配置项：
```python
class Settings:
    APP_TITLE: str = "Action Item Extractor"
    APP_VERSION: str = "0.1.0"
    LLM_MODEL: str = os.getenv("LLM_MODEL", "mistral-nemo:12b")
    DB_PATH: Path = BASE_DIR / "data" / os.getenv("DB_NAME", "app.db")
    DATA_DIR: Path = BASE_DIR / "data"
    FRONTEND_DIR: Path = BASE_DIR / "frontend"

@lru_cache
def get_settings() -> Settings:
    return Settings()
```

**Modified File: `week2/app/db.py`**

数据库层清理：
- 移除模块级硬编码的 `BASE_DIR`、`DATA_DIR`、`DB_PATH` 常量，改为从 `config.get_settings()` 获取
- 将 `get_connection()` 改为私有上下文管理器 `_get_connection()`，使用 `@contextmanager` + `try/finally` 确保连接总是被正确关闭
- 将 SQL DDL 语句提取为顶层常量 `SQL_CREATE_NOTES` 和 `SQL_CREATE_ACTION_ITEMS`，使 `init_db()` 更简洁
- 所有类型提示从已弃用的 `typing.List`、`typing.Optional` 迁移到现代 `list[...]`、`X | None` 语法
- 移除不再需要的 `ensure_data_directory_exists()` 公开函数，逻辑内联到 `_get_connection()` 中

**Modified File: `week2/app/main.py`**

应用生命周期/配置 + 错误处理：
- 用 `@asynccontextmanager` 的 `lifespan` 函数替代模块级 `init_db()` 调用，符合现代 FastAPI 最佳实践
- 应用 `title` 和 `version` 从 `Settings` 获取，而非硬编码字符串
- 所有路径解析通过 `_settings.FRONTEND_DIR` 进行，移除手动 `Path(__file__).resolve().parents[1]` 拼接
- 添加全局 `@app.exception_handler(Exception)`，捕获未处理异常并返回 `{"detail": "Internal server error"}` (500)，避免泄露回溯信息

**Modified File: `week2/app/routers/action_items.py`**

使用 Pydantic schemas 重构：
- `POST /extract` 端点：`payload: Dict[str, Any]` → `payload: ExtractRequest`，返回类型显式标记为 `-> ExtractResponse`
- `GET /action-items` 端点：返回类型从 `List[Dict[str, Any]]` 变为 `list[ActionItemRead]`，添加 `response_model=list[ActionItemRead]`
- `POST /{action_item_id}/done` 端点：`payload: Dict[str, Any]` → `payload: MarkDoneRequest`
- 移除手动的 `str(payload.get(...))` 类型转换和手动验证逻辑，改用 Pydantic 自动验证
- 移除未使用的 `HTTPException` import

**Modified File: `week2/app/routers/notes.py`**

使用 Pydantic schemas 重构 + 新增端点：
- `POST /notes` 端点：`payload: Dict[str, Any]` → `payload: NoteCreate`，返回 `NoteRead`
- 新增 `GET /notes` 端点（`list_all_notes`）：返回所有笔记列表，响应模型 `list[NoteRead]`
- `GET /notes/{note_id}` 端点：返回类型变为 `NoteRead`
- 所有类型提示使用现代 `list[...]` 语法

**Modified File: `week2/app/services/extract.py`**

配置集中化 + 导入清理：
- 移除分散在各处的 `from dotenv import load_dotenv` / `load_dotenv()` 调用，统一由 `config.py` 管理
- 移除未使用的导入：`os`、`json`、`Any`
- LLM 模型名称从硬编码 `"mistral-nemo:12b"` 改为从 `_settings.LLM_MODEL` 读取
- 所有类型提示从 `List` 迁移到 `list`


### Exercise 4: Use Agentic Mode to Automate a Small Task
Prompt: 
```
完成一下两个前后端开发任务1.后端接口开发：- 将现有的基于大语言模型的行动项提取逻辑，封装成一个新的 RESTful API 接口端点，该接口接收笔记文本作为输入，调用 LLM 进行处理，并返回提取出的行动项结果。- 新增一个用于获取所有便签数据的接口端点，该接口返回系统中存储的全部便签列表。2. 前端界面更新：- 在当前的笔记输入页面中，添加一个名为 "提取大语言模型" 的按钮。点击该按钮时，前端应调用上述新的 LLM 提取接口，触发提取流程，并将返回的行动项结果清晰地展示给用户。- 再添加一个名为 "列出便签" 的按钮。点击该按钮时，前端应调用获取所有便签的接口，拉取并在页面上展示全部便签数据。
``` 

Generated Code Snippets:

**Modified File: `week2/app/routers/action_items.py`**

- **Line 13**: 更新导入，添加 `extract_action_items_llm`
  ```python
  from ..services.extract import extract_action_items, extract_action_items_llm
  ```
- **Lines 33-45**: 新增 `POST /action-items/extract-llm` 端点，调用 LLM 驱动的 `extract_action_items_llm()` 函数进行行动项提取
  ```python
  @router.post("/extract-llm", response_model=ExtractResponse)
  def extract_llm(payload: ExtractRequest) -> ExtractResponse:
      note_id: int | None = None
      if payload.save_note:
          note_id = db.insert_note(payload.text)

      items = extract_action_items_llm(payload.text)
      ids = db.insert_action_items(items, note_id=note_id)
      return ExtractResponse(
          note_id=note_id,
          items=[ActionItemSummary(id=i, text=t) for i, t in zip(ids, items)],
      )
  ```

**Existing File: `week2/app/routers/notes.py`**

- **Lines 19-29**: `GET /notes` 端点（`list_all_notes`）已存在于代码库中，返回全部便签列表，响应模型 `list[NoteRead]`，无需额外修改即可满足需求。

**Modified File: `week2/frontend/index.html`**

- **Line 13**: 更新 `.row` CSS 类，添加 `flex-wrap: wrap` 以支持按钮换行
- **Lines 14-17**: 新增 CSS 类用于便签列表展示
  ```css
  .section { margin-top: 1.5rem; }
  .section-title { font-weight: 600; margin-bottom: 0.5rem; }
  .note-card { border: 1px solid #e5e7eb; border-radius: 6px; padding: 0.75rem; margin-bottom: 0.5rem; }
  .note-content { white-space: pre-wrap; word-break: break-word; }
  .note-meta { color: #9ca3af; font-size: 0.75rem; margin-top: 0.25rem; }
  ```
- **Lines 83-84**: 在按钮行中新增 "Extract LLM" 按钮
  ```html
  <button id="extract-llm">Extract LLM</button>
  ```
- **Lines 89-92**: 新增 "List Notes" 按钮及便签结果展示区域
  ```html
  <div class="section">
    <button id="list-notes">List Notes</button>
  </div>
  <div class="section" id="notes-section"></div>
  ```
- **Lines 99-105**: 新增 `escapeHtml()` 辅助函数，对用户输入文本进行安全转义，防止 XSS
- **Lines 107-120**: 抽取 `renderItems()` 通用渲染函数，复用原有的行动项复选框渲染逻辑
- **Lines 122-134**: 重构原有 "Extract" 按钮事件处理，调用 `renderItems()` 渲染结果
- **Lines 136-150**: 新增 "Extract LLM" 按钮事件处理，调用 `POST /action-items/extract-llm` 接口并用 `renderItems()` 渲染结果
- **Lines 152-173**: 新增 "List Notes" 按钮事件处理，调用 `GET /notes` 接口，以卡片形式展示全部便签（包含内容、ID 和时间戳）


### Exercise 5: Generate a README from the Codebase
Prompt: 
```
分析当前代码库，生成一份结构清晰，完整规范的 README.md 文件，文件内容需要包含以下部分：1. 项目概述：用简洁的语言介绍项目的背景、目标与主要功能。2. 项目安装与运行指南：详细说明如何配置环境、安装依赖，以及启动 / 运行项目的完整步骤。3. API 接口说明：列出项目中的所有主要 API 端点，说明每个接口的功能、请求方式与核心作用。4. 测试运行说明：提供运行项目测试套件的具体命令和步骤，说明如何执行单元测试。
``` 

Generated Code Snippets:

**New File: `week2/README.md`**

- **Lines 1-4**: 项目概述 — 介绍 Action Item Extractor 为 FastAPI 应用，支持规则和 LLM 两种行动项提取策略，持久化到 SQLite 并通过 RESTful API 和前端展示
- **Lines 6-18**: Quickstart / 前置条件 — 列出 Python 3.10+、Ollama 安装与运行、`ollama pull mistral-nemo:12b` 拉取模型
- **Lines 20-35**: Setup 安装步骤 — 包含 conda 环境创建、Poetry 依赖安装、`.env` 可选配置（`LLM_MODEL` / `DB_NAME`）
- **Lines 37-47**: Run the Application — `uvicorn week2.app.main:app --reload --port 8000` 启动命令，前端与 Swagger UI 入口地址
- **Lines 49-67**: Project Structure — 以 ASCII 树形图展示 `week2/` 目录结构，标注每个文件职责
- **Lines 69-130**: API Endpoints — 以表格列出全部 7 个端点：
  - Notes: `POST /notes`、`GET /notes`、`GET /notes/{note_id}`
  - Action Items: `POST /action-items/extract`、`POST /action-items/extract-llm`、`GET /action-items`、`POST /action-items/{action_item_id}/done`
  - Root: `GET /`
  - 并附带了请求/响应 JSON 示例
- **Lines 132-166**: Tests — 说明使用 pytest 运行测试的命令（`pytest week2/tests/ -v`），列出 `test_extract.py` 覆盖的规则提取和 LLM 提取（12 种场景）测试用例


## SUBMISSION INSTRUCTIONS
1. Hit a `Command (⌘) + F` (or `Ctrl + F`) to find any remaining `TODO`s in this file. If no results are found, congratulations – you've completed all required fields. 
2. Make sure you have all changes pushed to your remote repository for grading.
3. Submit via Gradescope. 