# Vbiji 架构文档

> 最后更新：2026-04-23
> 架构版本：v1.0
> 阶段：Phase 1 + Phase 2 设计，Phase 3 扩展点预留

---

## 目录

1. [项目概述](#1-项目概述)
2. [分阶段路线图](#2-分阶段路线图)
3. [Phase 1 技术架构](#3-phase-1-技术架构)
4. [Phase 2 技术架构](#4-phase-2-技术架构)
5. [Phase 3 扩展点设计](#5-phase-3-扩展点设计)
6. [核心模块详细设计](#6-核心模块详细设计)
7. [数据库设计](#7-数据库设计)
8. [AI Provider 抽象层](#8-ai-provider-抽象层)
9. [配置系统](#9-配置系统)
10. [CLI 命令设计](#10-cli-命令设计)
11. [Agent 分工安排](#11-agent-分工安排)
12. [变更记录](#12-变更记录)

---

## 1. 项目概述

### 1.1 核心定位

| 字段 | 内容 |
|------|------|
| **项目名称** | Vbiji（笔记 + AI 协作） |
| **项目简介** | 与 AI 一起协作的知识库，免费开源 + Agent 交互 + 本地存储 |
| **核心价值** | 将本地文件作为上下文交给 AI 处理，实现信息加工自动化 |
| **Phase 1 定位** | CLI 原型工具，验证文件处理核心逻辑 |
| **Phase 2/3 定位** | AI 接入 + GUI 客户端 |

### 1.2 设计原则

```
核心原则一：核心与接口分离
  └→ core/ 模块不依赖任何接口层（CLI / HTTP / GUI）
  └→ Phase 1 的 CLI 只是 core 的第一个"入口"

核心原则二：配置与代码分离
  └→ 所有用户数据（LLM 配置、提示词）存在 ~/.vbiji/
  └→ 代码仓库不包含任何密钥或用户数据

核心原则三：渐进式扩展
  └→ Phase 1 验证核心逻辑
  └→ Phase 2 在 core 上叠加 AI 层
  └→ Phase 3 新增接口层，不改动 core
```

---

## 2. 分阶段路线图

```
Phase 1（CLI 原型）          Phase 2（AI 接入）           Phase 3（客户端）
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│  vbiji read     │         │  + LLM 配置管理  │         │  + HTTP API 层   │
│  vbiji summarize│   →     │  + Prompt 管理   │    →    │  + Web UI /     │
│  vbiji convert  │         │  + AI 问答      │         │    Electron GUI  │
└─────────────────┘         │  + RAG 知识库    │         │  + 批量处理      │
                            └─────────────────┘         └─────────────────┘
核心：core/reader/           叠加：core/ai/               叠加：server/ + ui/
纯 Python，无 AI，无 GUI     Python + AI SDK              Python + FastAPI/Web
预计工期：1-2 周             预计工期：2-4 周              预计工期：4-8 周
```

---

## 3. Phase 1 技术架构

### 3.1 技术选型

| 组件 | 选型 | 版本 | 说明 |
|------|------|------|------|
| **核心语言** | Python | 3.11+ | 文件处理库最成熟 |
| **CLI 框架** | Typer | 0.12+ | 基于 Click，类型安全，自动生成 CLI 文档 |
| **PDF 解析** | PyMuPDF (fitz) | 1.24+ | 速度快，支持文本和图片提取 |
| **Word 解析** | python-docx | 1.1+ | Word .docx 解析 |
| **Markdown** | mistune / markdown-it | - | Markdown 解析与渲染 |
| **JSON 处理** | 标准库 json | - | 内置支持 |
| **配置管理** | TOML | - | pyproject.toml 标准 + 用户配置 |
| **日志** | Loguru | 0.5+ | 比 logging 更简洁 |
| **测试** | Pytest | 8+ | 单元测试 + 集成测试 |
| **包管理** | uv | - | 比 pip 更快 |
| **打包** | PyInstaller / shiv | - | 单文件 CLI 分发 |

### 3.2 目录结构（Phase 1）

```
vbiji/
├── pyproject.toml               # 项目定义（uv / pip 安装）
├── README.md
├── CHANGELOG.md
├── vbiji/                       # 主包
│   ├── __init__.py
│   ├── __main__.py             # python -m vbiji 入口
│   ├── cli.py                   # Typer CLI 定义（命令入口）
│   │
│   ├── core/                    # ★ 核心逻辑（与接口无关）
│   │   ├── __init__.py
│   │   ├── reader.py           # 文件读取抽象接口
│   │   ├── readers/            # 格式处理器（插件式）
│   │   │   ├── __init__.py
│   │   │   ├── base.py        # Reader 抽象基类
│   │   │   ├── pdf_reader.py  # PDF 处理器
│   │   │   ├── docx_reader.py # Word 处理器
│   │   │   ├── md_reader.py   # Markdown 处理器
│   │   │   └── txt_reader.py  # 纯文本处理器
│   │   │
│   │   ├── converter.py        # 格式转换器
│   │   ├── summarizer.py      # 摘要器（Phase 1 本地，Phase 2 AI）
│   │   │
│   │   └── types.py            # 核心类型定义
│   │
│   ├── config.py                # 配置加载（~/.vbiji/config.toml）
│   │
│   └── utils.py                 # 通用工具函数
│
├── tests/                       # 测试
│   ├── unit/
│   └── integration/
│
└── scripts/
    └── build.sh                 # PyInstaller 打包脚本
```

### 3.3 核心接口设计

```python
# core/reader.py — 统一的文件读取接口
from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class Document:
    """统一的文档数据结构"""
    content: str           # 纯文本内容
    title: str            # 文件标题（从文件名提取）
    format: str           # 原始格式：pdf / docx / md / txt
    path: str             # 文件绝对路径
    metadata: dict         # 元数据（页数/字数/创建时间等）

class BaseReader(ABC):
    """Reader 抽象基类，所有格式处理器继承此接口"""
    format: str = ""      # 子类覆盖：支持的格式名

    @abstractmethod
    def read(self, path: str) -> Document:
        """读取文件，返回统一 Document"""
        ...

    @abstractmethod
    def supports(self, path: str) -> bool:
        """判断是否支持该文件"""
        ...

# core/readers/pdf_reader.py 示例
class PdfReader(BaseReader):
    format = "pdf"

    def supports(self, path: str) -> bool:
        return path.lower().endswith('.pdf')

    def read(self, path: str) -> Document:
        import fitz
        doc = fitz.open(path)
        content = "\n".join([page.get_text() for page in doc])
        return Document(
            content=content,
            title=Path(path).stem,
            format=self.format,
            path=str(Path(path).resolve()),
            metadata={"pages": len(doc), "chars": len(content)}
        )
```

### 3.4 Phase 1 数据流

```
用户输入
   │
   │  vbiji read ./report.pdf
   ▼
cli.py（Typer 命令）
   │
   │  dispatch_command("read", filepath)
   ▼
core/reader.py（ReaderRegistry 查找处理器）
   │
   │  registry.get_handler(filepath)
   ▼
core/readers/pdf_reader.py（具体格式处理器）
   │
   │  read() → Document
   ▼
core/summarizer.py（本地摘要，Phase 1 用 extractive summary）
   │
   ▼
输出到终端（Rich 彩色输出）
```

---

## 4. Phase 2 技术架构

### 4.1 技术选型（增量叠加）

| 组件 | 选型 | 说明 |
|------|------|------|
| **AI SDK** | Vercel AI SDK Python (`ai`) 或 `litellm` | 统一多模型调用 |
| **本地向量库** | `chromadb` 或 `qdrant-client`（可选） | RAG 知识库 |
| **Embedding** | `sentence-transformers`（本地）或云端 API | 文本向量化 |
| **配置存储** | SQLite（DuckDB 嵌入式）或 TOML | LLM / Prompt 配置持久化 |
| **加密存储** | `cryptography.fernet` | 加密 API Key（可选本地加密）|

### 4.2 Phase 2 目录结构（增量）

```
vbiji/（在 Phase 1 基础上新增）
├── core/
│   ├── reader.py               # Phase 1 已存在
│   ├── readers/               # Phase 1 已存在
│   │
│   ├── ai/                    # ★ Phase 2 新增：AI 层
│   │   ├── __init__.py
│   │   ├── client.py         # AI 客户端（统一接口）
│   │   ├── providers/        # Provider 适配器
│   │   │   ├── base.py       # Provider 抽象基类
│   │   │   ├── deepseek.py   # DeepSeek
│   │   │   ├── minimax.py    # MiniMax
│   │   │   ├── kimi.py       # Kimi (Moonshot)
│   │   │   ├── bigmodel.py   # 智谱 BigModel
│   │   │   └── qwen.py       # 通义千问
│   │   │
│   │   ├── chat.py           # 对话封装
│   │   └── summarizer.py     # AI 摘要（替代 Phase 1 本地摘要）
│   │
│   ├── prompt/                # ★ Phase 2 新增：提示词管理
│   │   ├── __init__.py
│   │   ├── store.py          # 提示词存储（SQLite）
│   │   ├── manager.py        # 提示词 CRUD
│   │   └── templates.py      # 内置提示词模板
│   │
│   ├── llm/                  # ★ Phase 2 新增：LLM 配置管理
│   │   ├── __init__.py
│   │   ├── store.py          # LLM 配置存储（SQLite）
│   │   └── manager.py        # LLM 配置 CRUD
│   │
│   └── rag/                  # ★ Phase 2 新增：RAG 知识库
│       ├── __init__.py
│       ├── indexer.py        # 文档索引
│       ├── retriever.py       # 检索
│       └── engine.py         # RAG 执行引擎
│
├── server/                    # ★ Phase 3 新增：HTTP 服务（扩展点）
│   └── api.py
│
└── ui/                        # ★ Phase 3 新增：Web UI（扩展点）
    └── index.html
```

### 4.3 Phase 2 数据流

```
Phase 1 数据流不变，叠加 AI 层：

用户输入
   │
   │  vbiji ask -p summarize ./report.pdf
   ▼
cli.py
   │
   │  dispatch_command("ask", prompt_title, filepath)
   ▼
core/llm/manager.py            # 加载 LLM 配置
   │
   │  get_llm_config("deepseek-chat")
   ▼
core/prompt/manager.py         # 加载提示词
   │
   │  get_prompt("summarize")
   ▼
core/reader.py                  # 读取文件 → Document
   │
   │  content = doc.content
   ▼
core/ai/client.py              # 构造 AI 请求
   │
   │  build_messages(prompt_template, content, user_query)
   ▼
core/ai/providers/deepseek.py  # 调用 DeepSeek API
   │
   │  chat(messages, model="deepseek-chat")
   ▼
输出到终端（流式输出 ANSI 支持）
```

---

## 5. Phase 3 扩展点设计

### 5.1 核心设计：同一套 core，多个接口

```
┌─────────────────────────────────────────────────────────┐
│                    core/（不变）                         │
│  reader.py / ai/ / prompt/ / llm/ / rag/               │
└─────────────────────────────────────────────────────────┘
         │                        │
         ▼                        ▼
┌──────────────────┐    ┌────────────────────────────┐
│  CLI 接口（Phase 1）│    │  HTTP API（Phase 3 新增）    │
│  vbiji cli.py     │    │  FastAPI / uvicorn          │
└──────────────────┘    └────────────────────────────┘
                                  │
                                  ▼
                        ┌────────────────────────────┐
                        │  Web UI（Phase 3 新增）       │
                        │  React / Vue / 任意前端框架   │
                        └────────────────────────────┘
```

### 5.2 Phase 3 HTTP API 设计

```python
# server/api.py — FastAPI 接口（Phase 3 实现）
from fastapi import FastAPI
from vbiji.core import ReaderRegistry, AiClient

app = FastAPI(title="Vbiji API", version="1.0.0")
registry = ReaderRegistry()
ai_client = AiClient()

@app.get("/api/read")
def read_file(path: str):
    doc = registry.read(path)
    return {"title": doc.title, "content": doc.content, "format": doc.format}

@app.post("/api/ask")
def ask_file(prompt: str, file_path: str, llm: str = "default"):
    doc = registry.read(file_path)
    result = ai_client.ask(prompt=prompt, context=doc.content, llm=llm)
    return {"result": result}

@app.get("/api/llm")
def list_llms():
    from vbiji.core.llm.manager import LlmManager
    return LlmManager().list_all()

@app.post("/api/llm")
def add_llm(name: str, api_key: str, base_url: str = "", model: str = ""):
    from vbiji.core.llm.manager import LlmManager
    return LlmManager().add(name, api_key, base_url, model)
```

### 5.3 Phase 3 批量处理设计

```python
# core/batch.py — 批量处理引擎（Phase 3 实现）
class BatchProcessor:
    """批量处理：给定目录 + 提示词，批量 AI 处理"""

    def __init__(self, llm_manager: LlmManager, prompt_manager: PromptManager):
        self.llm = llm_manager
        self.prompt = prompt_manager

    def process_directory(
        self,
        directory: str,
        prompt_title: str,
        llm_name: str,
        output_dir: str,
        file_format: str = "md"
    ) -> BatchResult:
        """
        1. 扫描目录（支持 glob 过滤 *.pdf/*.md）
        2. 逐文件读取 → 交给 AI 处理
        3. 结果保存到 output_dir
        """
        files = glob(f"{directory}/**/*", recursive=True)
        files = [f for f in files if f.endswith(('.pdf', '.md', '.docx'))]

        results = []
        for file_path in tqdm(files, desc="Processing"):
            doc = registry.read(file_path)
            result = ai_client.ask(
                prompt=self.prompt.get(prompt_title),
                context=doc.content,
                llm=llm_name
            )
            output_path = Path(output_dir) / f"{Path(file_path).stem}.{file_format}"
            output_path.write_text(result)
            results.append({"file": file_path, "output": str(output_path)})

        return BatchResult(total=len(files), results=results)
```

---

## 6. 核心模块详细设计

### 6.1 Reader 注册中心（插件化设计）

```python
# core/reader.py
from pathlib import Path
from .readers.base import BaseReader, Document

class ReaderRegistry:
    """文件读取注册中心，支持插件式添加新格式"""

    def __init__(self):
        self._readers: list[BaseReader] = []

    def register(self, reader: BaseReader):
        """注册新的 Reader（插件机制）"""
        self._readers.append(reader)

    def get_handler(self, path: str) -> BaseReader:
        """根据文件路径找到对应的 Reader"""
        for reader in self._readers:
            if reader.supports(path):
                return reader
        raise UnsupportedFormatError(
            f"不支持的文件格式: {Path(path).suffix}。"
            f"支持格式: {[r.format for r in self._readers]}"
        )

    def read(self, path: str) -> Document:
        """统一读取接口"""
        handler = self.get_handler(path)
        return handler.read(path)

# 启动时自动注册内置 Reader
registry = ReaderRegistry()
registry.register(PdfReader())
registry.register(DocxReader())
registry.register(MdReader())
registry.register(TxtReader())

# 用户可通过 core.extend_reader() 注册自定义 Reader（Phase 3 插件扩展点）
```

### 6.2 AI Provider 抽象

详见第 8 节。

### 6.3 配置加载优先级

```
命令行参数（--config / --llm）
  ↓
环境变量（VBIJI_CONFIG / VBIJI_LLM）
  ↓
项目配置（./.vbiji.toml）← Phase 3 批量处理时有用
  ↓
用户配置（~/.vbiji/config.toml）
  ↓
默认配置（内置 defaults.toml）
```

---

## 7. 数据库设计

### 7.1 SQLite Schema（Phase 2+）

```sql
-- LLM 模型配置表
CREATE TABLE llm_configs (
    id          TEXT PRIMARY KEY,
    name        TEXT NOT NULL UNIQUE,    -- 用户自定义名称，如 "deepseek-chat"
    provider    TEXT NOT NULL,            -- deepseek / minimax / kimi / bigmodel / qwen
    model       TEXT NOT NULL,            -- 模型 ID，如 "deepseek-chat"
    api_key     TEXT NOT NULL,            -- 加密存储
    base_url    TEXT,                     -- 自定义 API 端点（可选）
    enabled     INTEGER DEFAULT 1,
    created_at  TEXT NOT NULL,
    updated_at  TEXT NOT NULL
);

-- 提示词配置表
CREATE TABLE prompts (
    id          TEXT PRIMARY KEY,
    title       TEXT NOT NULL UNIQUE,     -- 提示词标题（唯一标识）
    content     TEXT NOT NULL,            -- 提示词内容
    description TEXT,                     -- 描述（可选）
    tags        TEXT,                     -- JSON 数组 ["summarize", "extract"]
    created_at  TEXT NOT NULL,
    updated_at  TEXT NOT NULL
);

-- RAG 知识库索引表（Phase 2 简化版）
CREATE TABLE rag_index (
    id          TEXT PRIMARY KEY,
    file_path   TEXT NOT NULL,
    chunk_text  TEXT NOT NULL,
    chunk_hash  TEXT NOT NULL,
    embedding   BLOB,                     -- 向量数据（可省略，用外部向量库）
    indexed_at  TEXT NOT NULL
);

CREATE INDEX idx_rag_file ON rag_index(file_path);
CREATE INDEX idx_rag_hash ON rag_index(chunk_hash);

-- 辅助表
CREATE TABLE metadata (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
```

### 7.2 存储位置

```
~/.vbiji/                         # 用户数据根目录（与代码分离）
├── config.toml                    # 全局配置（是否加密可选择）
├── vbiji.db                       # SQLite 数据库
│   ├── llm_configs               # LLM 配置表
│   ├── prompts                   # 提示词表
│   └── rag_index                 # RAG 索引表
├── prompts/                      # 提示词 MD 文件（导入来源）
└── cache/                        # 缓存（可清理）
```

---

## 8. AI Provider 抽象层

### 8.1 Provider 接口

```python
# core/ai/providers/base.py
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import AsyncIterator

@dataclass
class LlmConfig:
    name: str           # 配置名称（如 "deepseek-chat"）
    provider: str        # provider 标识
    model: str           # 模型 ID
    api_key: str         # API Key
    base_url: str        # API 端点（可空）
    options: dict        # temperature / max_tokens 等

@dataclass
class ChatMessage:
    role: str    # system / user / assistant
    content: str

class BaseProvider(ABC):
    """AI Provider 抽象基类"""

    provider_name: str = ""  # 子类覆盖

    @abstractmethod
    def chat(self, messages: list[ChatMessage], config: LlmConfig) -> str:
        """同步聊天，返回完整响应"""
        ...

    @abstractmethod
    def chat_stream(
        self, messages: list[ChatMessage], config: LlmConfig
    ) -> AsyncIterator[str]:
        """流式聊天，yield 每个 token"""
        ...

    def build_url(self, config: LlmConfig) -> str:
        """构造 API URL"""
        base = config.base_url or self.default_base_url
        return f"{base.rstrip('/')}/{self.chat_endpoint}"
```

### 8.2 Provider 注册表

```python
# core/ai/client.py
class AiClient:
    """统一的 AI 客户端"""

    def __init__(self):
        self._providers: dict[str, type[BaseProvider]] = {}
        self._llm_manager = LlmManager()   # 从 SQLite 加载配置

    def register_provider(self, provider: type[BaseProvider]):
        self._providers[provider.provider_name] = provider

    def ask(
        self,
        prompt: str,
        context: str = "",
        llm_name: str = "default",
        system_prompt: str = ""
    ) -> str:
        """统一的 ask 接口"""
        # 1. 加载 LLM 配置
        llm_config = self._llm_manager.get(llm_name)

        # 2. 获取 Provider
        provider_cls = self._providers.get(llm_config.provider)
        if not provider_cls:
            raise UnsupportedProviderError(
                f"不支持的 Provider: {llm_config.provider}"
            )
        provider = provider_cls()

        # 3. 构造消息
        messages = []
        if system_prompt:
            messages.append(ChatMessage(role="system", content=system_prompt))
        if context:
            messages.append(ChatMessage(
                role="user",
                content=f"{prompt}\n\n【文件内容】\n{context}"
            ))
        else:
            messages.append(ChatMessage(role="user", content=prompt))

        # 4. 调用
        return provider.chat(messages, llm_config)

# 自动注册内置 Provider
client = AiClient()
client.register_provider(DeepSeekProvider)
client.register_provider(MiniMaxProvider)
client.register_provider(KimiProvider)
client.register_provider(BigModelProvider)
client.register_provider(QwenProvider)
```

### 8.3 Provider 实现对照表

| Provider | base_url 示例 | 模型 ID 示例 | 认证方式 |
|----------|-------------|------------|---------|
| DeepSeek | `https://api.deepseek.com/v1` | `deepseek-chat` | API Key Header |
| MiniMax | `https://api.minimax.chat/v1` | `MiniMax-Text-01` | API Key Header |
| Kimi | `https://api.moonshot.cn/v1` | `moonshot-v1-8k` | API Key Header |
| BigModel | `https://open.bigmodel.cn/api/paas/v4` | `glm-4-flash` | API Key Header |
| Qwen | `https://dashscope.aliyuncs.com/api/v1` | `qwen-turbo` | API Key Header |

---

## 9. 配置系统

### 9.1 全局配置（~/.vbiji/config.toml）

```toml
# ~/.vbiji/config.toml
[general]
version = "1.0.0"
data_dir = "~/.vbiji"          # 数据目录
cache_dir = "~/.vbiji/cache"   # 缓存目录
log_level = "INFO"             # DEBUG / INFO / WARNING / ERROR
log_file = "~/.vbiji/logs/vbiji.log"

[reader]
default_encoding = "utf-8"
pdf_extract_images = false      # 是否提取 PDF 图片
max_file_size_mb = 100          # 单文件大小限制

[ai]
default_llm = "deepseek-chat"   # 默认 LLM
stream_output = true            # 流式输出
timeout_seconds = 120           # 请求超时

[rag]
enabled = false                 # 是否启用 RAG
vector_db = "local"            # local / chromadb / qdrant
chunk_size = 500               # 分块大小
chunk_overlap = 50             # 分块重叠
```

---

## 10. CLI 命令设计

### 10.1 Phase 1 命令

```bash
# 文件读取
vbiji read <filepath>              # 读取并展示内容
vbiji read <filepath> -p            # 分页展示（less 风格）

# 内容摘要
vbiji summarize <filepath>          # 本地 extractive summary（Phase 1）
vbiji summarize <filepath> --lines 10  # 摘要行数

# 格式转换
vbiji convert <filepath> --to md    # → 同目录 .md 文件
vbiji convert <filepath> --to json  # → 同目录 .json 文件
vbiji convert <filepath> --to txt   # → 同目录 .txt 文件

# 全局选项
vbiji --config <path>               # 指定配置文件
vbiji --verbose                     # 详细输出
vbiji --help                        # 帮助
```

### 10.2 Phase 2 命令

```bash
# ===== LLM 配置管理 =====
vbiji llm add -n <name> --apikey <key> [--provider deepseek] [--base-url <url>]
vbiji llm list                       # 列出所有已配置的 LLM
vbiji llm del -n <name>              # 删除某个 LLM 配置
vbiji llm test -n <name>            # 测试 LLM 连通性

# ===== 提示词管理 =====
vbiji prompt add -t <title> -c <content>        # 新增提示词
vbiji prompt import <filepath>                   # 从 MD 文件导入提示词
vbiji prompt edit -t <title> -c <content>       # 修改提示词
vbiji prompt show -t <title>                    # 查看提示词
vbiji prompt del -t <title>                     # 删除提示词
vbiji prompt list                               # 列出所有提示词

# ===== AI 问答 =====
vbiji ask -p <prompt_title> <filepath>          # 提示词 + 文件 → AI 处理
vbiji ask <prompt_content> <filepath>           # 内联提示词 + 文件 → AI 处理
vbiji ask <prompt_content> --llm <llm_name>     # 指定 LLM
vbiji ask <prompt_content> --stream              # 流式输出

# ===== RAG 知识库（Phase 2 后期）=====
vbiji rag build <directory>                     # 构建知识库索引
vbiji rag query "<question>"                    # 知识库问答
vbiji rag clear                                  # 清空索引
```

### 10.3 命令执行流程（Phase 2 ask 命令）

```
vbiji ask -p summarize ./report.pdf
       │
       ▼
cli.py → ask_command()
       │
       │  1. LlmManager.get("default") → LlmConfig
       │  2. PromptManager.get("summarize") → prompt_content
       │  3. ReaderRegistry.read("./report.pdf") → Document
       │  4. AiClient.ask(prompt + context) → response
       │
       ▼
Rich 彩色输出 / 流式 token 打印
```

---

## 11. Agent 分工安排

### 11.1 Phase 1 工作分配

| Agent | Phase 1 任务 | 产出 |
|-------|------------|------|
| **Architect** | 设计 core/ 抽象层接口（Reader 基类、插件机制）| ARCHITECTURE.md（本文档）|
| **Backend Dev** | 实现 core/reader.py + 所有 readers + cli.py | Phase 1 可运行 CLI 工具 |
| **DevOps/QA** | 搭建 Pytest 测试框架 + CI（GitHub Actions）| 测试用例 + CI 流水线 |
| **OS Maintainer** | 编写 README.md + 使用文档 | 用户文档、CLI 帮助文档 |
| **Frontend Dev** | **暂不参与** | — |
| **AI/SDK Specialist** | **暂不参与** | — |

### 11.2 Phase 2 工作分配

| Agent | Phase 2 任务 | 产出 |
|-------|------------|------|
| **Architect** | 审查 Phase 1 架构，设计 AI 层扩展方案 | AI 层架构补充文档 |
| **Backend Dev** | 实现 core/ai/ + core/prompt/ + core/llm/ | AI 对话、LLM 配置、Prompt 管理 |
| **AI/SDK Specialist** | 实现 core/ai/providers/ 下所有 Provider | DeepSeek/MiniMax/Kimi/BigModel/Qwen 适配器 |
| **DevOps/QA** | AI Provider Mock 测试、集成测试 | Provider 测试覆盖率报告 |
| **OS Maintainer** | 补充 Phase 2 文档 | LLM 配置指南、Prompt 使用文档 |

### 11.3 Phase 3 工作分配

| Agent | Phase 3 任务 | 产出 |
|-------|------------|------|
| **Architect** | 设计 HTTP API 规范、Web UI 架构 | server/api 设计文档 |
| **Backend Dev** | 实现 server/api.py + BatchProcessor | HTTP 服务、批量处理引擎 |
| **Frontend Dev** | 实现 Web UI / Electron 客户端 | 用户界面、文件目录管理表单 |
| **AI/SDK Specialist** | **辅助** | AI 调用性能优化 |
| **DevOps/QA** | E2E 测试 + 打包发布 | Playwright E2E + CI 完整流水线 |
| **OS Maintainer** | 完整用户文档、贡献指南 | 完整文档体系 |

### 11.4 依赖关系图

```
Backend Dev（Phase 1 核心）
    ↓ 完成后
AI/SDK Specialist（Phase 2 接入）
    ↓ 完成后
Frontend Dev（Phase 3 UI）
    ↑ 依赖
Architect（全程设计 + Code Review）
    ↑ 审查
DevOps/QA（全周期 CI/CD + 测试）
OS Maintainer（全周期文档 + 社区运营）
```

---

## 12. 变更记录

| 日期 | 版本 | 变更内容 | 作者 |
|------|------|----------|------|
| 2026-04-23 | v1.0 | 初始架构文档，涵盖 Phase 1 + Phase 2 设计，Phase 3 扩展点 | Architect Agent |

---

## 附录：核心技术决策

### A. 为什么选择 Python 而非 TypeScript/Node.js？

| 考量 | Python | TypeScript/Node.js |
|------|--------|------------------|
| PDF/DOCX 处理库 | PyMuPDF、python-docx（成熟稳定）| pdf-parse（功能较弱）|
| AI SDK 生态 | Vercel AI Python / LangChain / litellm | Vercel AI SDK JS（更完善）|
| CLI 框架 | Typer/Click（优秀）| Commander.js（可用）|
| Phase 1 开发速度 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| Phase 2 AI 接入 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Phase 3 GUI 集成 | 需通过 HTTP API 或 Pyodide | ⭐⭐⭐⭐⭐（与 Electron 同构）|

**决策**：Phase 1/2 用 Python（开发效率优先），Phase 3 GUI 可选择：
- 方案 A：Python HTTP API + React Web UI
- 方案 B：Electron + Pyodide（Python 运行在 WASM）
- 方案 C：TypeScript 重写 core/ + Electron

### B. 为什么选择 SQLite 而非 JSON 配置文件？

- LLM 配置和提示词数量增长后，JSON 文件管理不便
- SQLite 支持全文搜索（FTS5），便于提示词检索
- 支持原子性写入，避免 JSON 文件并发写入损坏
- 数据量小（千级记录），SQLite 完全够用
- 用户可直接用 sqlite3 命令行查看和修改数据
