# Vbiji — AI 协作知识库 CLI 工具

> 本文件供 AI Agent 理解项目结构和开发规范。
> 架构文档：`docs/ARCHITECTURE.md`

---

## 项目概述

Vbiji 是一个与 AI 协作的本地知识库工具，支持：
- 读取本地文件（PDF、DOCX、Markdown、TXT）
- 内容摘要与格式转换
- AI 问答（多模型支持：DeepSeek / MiniMax / Kimi / BigModel / Qwen）
- 提示词管理（增删改查 + 文件导入）
- LLM 配置管理（SQLite 持久化）
- 自动上下文截断（超长文件智能压缩）

**当前阶段**：Phase 1 ✅ + Phase 2 ✅ 已完成，共 93 个测试

---

## 技术栈

| 组件 | 选型 |
|------|------|
| 核心语言 | Python 3.11+ |
| CLI 框架 | Typer 0.12+ |
| PDF 解析 | PyMuPDF (fitz) |
| Word 解析 | python-docx |
| HTTP 客户端 | httpx（AI 模型调用） |
| 配置存储 | TOML + SQLite |
| 包管理 | uv |
| 测试 | Pytest（93 个测试） |

---

## 目录结构

```
vbiji/                        # 项目根目录
├── vbiji/                    # 主包
│   ├── __main__.py           # python -m vbiji 入口
│   ├── cli.py                # Typer CLI 命令定义
│   ├── exceptions.py         # 自定义异常
│   ├── config.py             # 配置加载（~/.vbiji/config.toml）
│   └── core/                 # ★ 核心逻辑（无 CLI/HTTP/GUI 依赖）
│       ├── db.py            # SQLite 连接共享模块
│       ├── types.py         # dataclass 类型定义（Document）
│       ├── reader.py        # Reader 抽象基类 + 注册中心
│       ├── converter.py     # 格式转换器
│       ├── summarizer.py    # 摘要生成器（local + AI）
│       ├── readers/         # 格式处理器（插件式）
│       │   ├── base.py     # BaseReader 抽象基类
│       │   ├── pdf_reader.py
│       │   ├── docx_reader.py
│       │   ├── md_reader.py
│       │   └── txt_reader.py
│       ├── llm/             # LLM 配置管理
│       │   └── manager.py   # LlmManager（CRUD + SQLite）
│       ├── prompt/          # 提示词管理
│       │   └── manager.py   # PromptManager（CRUD + SQLite）
│       └── ai/              # AI 层
│           ├── chat.py      # AiChat 对话封装（含上下文截断）
│           ├── client.py    # AI 客户端（统一入口）
│           └── providers/   # AI Provider 实现
│               ├── base.py  # BaseProvider + token 工具函数
│               ├── deepseek.py
│               ├── minimax.py
│               ├── kimi.py
│               ├── bigmodel.py
│               └── qwen.py
├── tests/                    # Pytest 测试（93 个）
│   ├── test_base.py         # token 估算 / 截断
│   ├── test_reader.py       # Reader 抽象基类
│   ├── test_converter.py    # 格式转换
│   ├── test_prompt_manager.py
│   ├── test_llm_manager.py
│   ├── test_chat.py         # AI chat + 截断
│   ├── test_providers.py    # 各 Provider
│   └── test_cli.py          # CLI 命令
├── docs/
│   ├── ARCHITECTURE.md      # 架构文档
│   └── IPC_REGISTRY.md      # IPC 通信规范（Phase 3）
├── db/                       # Phase 3 数据库 Schema
├── electron/                 # Phase 3 桌面端代码
└── .github/
    ├── workflows/           # CI/CD
    ├── ISSUE_TEMPLATE/     # Bug / Feature 模板
    └── PULL_REQUEST_TEMPLATE.md
```

**Phase 3 将新增**：`server/`（HTTP API）+ `ui/`（React Web UI）

---

## 架构原则

1. **核心与接口分离**：`core/` 模块不依赖 CLI / HTTP / GUI
2. **用户数据隔离**：`~/.vbiji/` 存放所有用户数据（配置、LLM 密钥、提示词）
3. **插件式设计**：新增文件格式支持只需注册新 Reader，无需修改核心代码
4. **渐进式扩展**：Phase 1 → Phase 2 → Phase 3 层层叠加，core 不变
5. **Provider 注入**：AI 相关函数接收 `BaseProvider` 实例，不硬编码具体 Provider

---

## 常用命令

```bash
# 安装
uv pip install -e .

# 开发
uv run python -m vbiji read ./file.pdf
uv run python -m vbiji summarize ./file.pdf
uv run python -m vbiji convert ./file.pdf --to md
uv run python -m vbiji ask ./file.pdf "请摘要" --llm deepseek
uv run python -m vbiji ask ./file.pdf --prompt 财报分析 --llm deepseek --save
uv run python -m vbiji batch ./docs --to md --llm deepseek

# LLM / 提示词管理
uv run python -m vbiji llm-add deepseek --provider deepseek --apikey sk-xxx --model deepseek-chat
uv run python -m vbiji prompt-import ./提示词/财报分析.md

# 测试
uv run pytest tests/ -v
uv run pytest tests/ --cov=vbiji --cov-report=term-missing

# 类型检查 / 代码风格
uv run mypy vbiji/
uv run ruff check vbiji/

# 打包发布
uv build
```

---

## 核心接口约定

### Reader 抽象

```python
from vbiji.core.reader import registry
doc = registry.read("./file.pdf")  # 自动选择处理器
```

### AI 对话

```python
from vbiji.core.ai.chat import AiChat
from vbiji.core.ai.providers.deepseek import DeepSeekProvider
from vbiji.core.llm.manager import LlmManager

provider = DeepSeekProvider()
config = LlmManager().get("deepseek")
chat = AiChat(provider, config)
result = chat.ask("请摘要", context=doc.content)
```

### Token 限制约定

| 场景 | 约定 |
|------|------|
| 不限制输出 | `max_tokens=0`（自动从 API payload 中移除） |
| 自动截断输入 | 调用方传入 `max_context_tokens` 或使用 Provider 默认值 |
| Token 估算 | 中文 ≈ 2 字符/Token，英文/数字 ≈ 4 字符/Token |

---

## 配置位置

- 全局配置：`~/.vbiji/config.toml`
- SQLite 数据库：`~/.vbiji/vbiji.db`
- 日志文件：`~/.vbiji/logs/vbiji.log`

---

## 开发规范

- 类型注解：所有公开函数必须带类型注解
- Docstring：所有类和公开方法必须有 docstring
- 异常处理：使用自定义异常类（`VbijiError` 的子类）
- 日志：使用 `loguru`，不直接 `print`
- 测试：每个模块对应一个测试文件，覆盖率 > 80%（当前 93 个测试）

---

## CI/CD

- CI 配置：`.github/workflows/ci.yml`
- 运行 CI：push 代码后自动触发
- 手动运行：fork 仓库后配置 GitHub Secrets

### CI 检查项

| 检查项 | PR | main | 覆盖率要求 |
|--------|-----|------|-----------|
| mypy 类型检查 | 警告 | 必须通过 | - |
| ruff lint | 必须通过 | 必须通过 | - |
| pytest | 警告 | 必须通过 | PR > 60%，main > 70% |

---

## 相关文档

- 架构文档：`docs/ARCHITECTURE.md`
- IPC 通信规范：`docs/IPC_REGISTRY.md`（Phase 3 桌面客户端）
- CHANGELOG：`CHANGELOG.md`
