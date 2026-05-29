### 前提条件
- Python 3.10+

- `httpx` 库（异步 HTTP 客户端）

- `mcp` 库（Model Context Protocol 框架）
### 环境安装
~~~
open powershell/cmd

uv init 项目名

cd 项目名

uv venv

.venv\Scripts\activate

uv add mcp[cli]

uv add httpx(普通网络接口)/pymysql(sqlite3)(调用数据库)/openai(调用AI大模型API)
##按需安装

在目标位置新建python文件（例：weather.py/forcast.py...）
~~~
### 运行方式（本地）
~~~
# 进入项目目录
cd project
python project.py
~~~
### MCP客户端配置（TRAE）
~~~
##点击TRAE页面右上角设置
##选项MCP
##添加/手动配置
##示例1,配置json
{

  "mcpServers": {

    "dog_image": {

      "command": "uv",

      "args": [

        "--directory",

##"D:\\project\\cs146s\\modern-software-dev-assignments\\week3\\server_file\\MCP\\MCP_tools",
##该位置定位到具体python文件存放位置 

        "run",

        "dog_image.py"

      ]

    }

  }

}
##示例2，配置json
{

  "mcpServers": {

    "github_issues": {

      "command": "uv",

      "args": [

        "--directory",

## "D:\\project\\cs146s\\modern-software-dev-assignments\\week3\\server_file\\MCP\\MCP_tools",
##同上
        "run",

        "github_issue.py"

      ]

    }

  }

}
~~~
### 工具参考
#### 1.随机小狗图像生成（dog_image）
- 参数 /breed: str/ (狗的品种)
- ~~~
  示例输入：给我一张拉布拉多犬的图片
  大模型调用
  {
  "breed": "labrador"
  }
  示例函数输出:https://images.dog.ceo/breeds/labrador/n02099712_5965.jpg
  大模型输出:
  Here is a Labrador Retriever image:

  <img src="https://images.dog.ceo/breeds/labrador/n02099712_5965.jpg" alt="拉布拉多犬"/>

  Image URL: https://images.dog.ceo/breeds/labrador/n02099712_5965.jpg
  预期行为：函数接收到图片链接，大模型输出图片
  ~~~

#### 2.github用户信息获取
- 功能：已知用户名，获取用户信息；已知用户名
- 遇到的问题: TOKEN不知道如何安全的融入到代码中（1.使用永久环境变量（未知原因失败）2. 新建config.py文件将token存放此处被文件调用）
- ~~~
  get_users_info()
  参数：user: str
  get_users_repos_info()
  参数: owner: str
  get_repo_info()
  参数: owner: str, repo:str
  ~~~
- ~~~
  示例输入 1.查询用户mihail911的github仓库
  大模型输入:
  {
  "owner": "mihail911"
  }
    ~~~
大模型输出:
![[Pasted image 20260518135226.png]]
~~~
  示例输入 2.查询用户mihail911的信息
  大模型输入:
  {
  "user": "mihail911"
  }
  输出:
  Username: mihail911
Bio: Head of AI. Creator of Stanford's First AI Software Course. 
Past lives: cofounder Storia AI, senior Machine Learning Scientist @alexa, researcher @stanfordnlp
Public Repos: 91
Repository URL: N/A
Profile: https://github.com/mihail911
~~~
大模型输出:
![[Pasted image 20260518135544.png]]

~~~
  示例输入 3.查询用户mihail911的名为仓库的信息
  大模型输入:
  {
  "owner": "mihail911",
  "repo": "modern-software-dev-assignments"
  }
  响应：
  FullName=mihail911/modern-software-dev-assignments
    Created=2025-08-07T07:14:35Z
    Updated=2026-05-18T01:50:48Z
    Language=Python
~~~
大模型输出:![[Pasted image 20260518135826.png]]
### 错误处理
#### 1. dog_image.py 错误处理
- 简化策略 ：使用统一的异常捕获，返回 None 表示失败
- 检查方式 ：调用方通过检查返回值是否为 None 或 status != "success" 判断是否出错
#### 2.github_issue.py 错误处理
- 分层策略 ：区分 HTTP 错误、网络错误和未知错误
- 详细策略 ：返回结构化错误信息，便于调试和用户理解
- 检查方式 ：通过检查返回字典中是否包含 "error" 键判断是否出错

### 项目结构
week3/
├── assignment.md                    # 作业要求文档
└── server_file/
    └── MCP/
        ├── main.py                 # 入口文件
        ├── pyproject.toml        # 项目配置
        ├── uv.lock                 # 依赖锁定文件
        ├── README.md               # 项目文档
        ├── .python-version         # Python 版本指定
        └── MCP_tools/              # MCP 工具实现目录
            ├── dog_image.py        # 小狗随机图片工具
            ├── github_issue.py     # GitHub Issue 工具
            ├── train_tickets.py    # 火车票工具（api失效）
            └── weather.py          # 天气工具（案例）