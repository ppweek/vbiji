# Vbiji

> 与 AI 一起协作的知识库，免费开源 + Agent 交互 + 本地存储

[![CI](https://github.com/ppweek/vbiji/workflows/CI/badge.svg)](https://github.com/ppweek/vbiji/actions)
[![PyPI version](https://img.shields.io/pypi/v/vbiji.svg)](https://pypi.org/project/vbiji/)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)

## 特性

- **本地优先**：文件存储在本地，无云端依赖
- **多格式支持**：PDF、Word、Markdown、TXT
- **AI 协作**：支持 DeepSeek / MiniMax / Kimi / BigModel / Qwen 等多模型
- **提示词管理**：复用、编辑、导入提示词
- **插件架构**：新增文件格式 / AI Provider 无需改动核心代码
- **三阶段规划**：CLI 原型 → AI 接入 → 桌面客户端

## 安装

```bash
pip install vbiji
```

或从源码安装：

```bash
git clone https://github.com/ppweek/vbiji.git
cd vbiji
uv sync
uv run vbiji --help
```

## 快速开始

```bash
# 配置 AI 模型
vbiji llm-add deepseek --api-key sk-xxxx --model deepseek-chat

# 读取文件
vbiji read ./report.pdf

# AI 摘要
vbiji ask ./report.pdf "请摘要" --llm deepseek
vbiji ask ./report.pdf --prompt 财报分析 --llm deepseek
vbiji ask ./report.pdf "请摘要" --llm deepseek --save              # 保存到当前目录（自动命名）
vbiji ask ./report.pdf "请摘要" --llm deepseek --save-as ./out/摘要.md  # 保存到指定路径

# 格式转换
vbiji convert ./report.pdf md

# 管理提示词
vbiji prompt-add my-prompt "提取关键条款和风险点"
vbiji prompt-import ./提示词/财报分析.md    # 文件名作为标题，全部内容作为内容
```

## 项目结构

```
vbiji/
├── vbiji/              # 主包
│   ├── cli.py          # CLI 入口（Typer）
│   └── core/
│       ├── readers/    # 格式处理器（PDF/DOCX/MD/TXT）
│       ├── llm/        # LLM 配置管理（SQLite）
│       ├── prompt/     # 提示词管理（SQLite）
│       └── ai/
│           └── providers/  # AI Provider 实现
├── tests/             # 单元测试
├── docs/               # 架构文档
└── .github/            # CI/CD + Issue/PR 模板
```

## 文档

- [架构设计](./docs/ARCHITECTURE.md)
- [IPC 通信规范](./docs/IPC_REGISTRY.md)（Phase 3 桌面客户端）

## 开发

```bash
# 安装开发依赖
uv sync --dev

# 类型检查
uv run mypy vbiji/

# 代码风格
uv run ruff check vbiji/

# 运行测试
uv run pytest tests/ -v

# 查看覆盖率
uv run pytest tests/ --cov=vbiji --cov-report=term-missing
```

## 路线图

| 阶段 | 内容 | 状态 |
|------|------|------|
| Phase 1 | CLI 工具（read / summarize / convert） | ✅ 完成 |
| Phase 2 | AI 接入（LLM 配置 / Prompt 管理 / 多模型） | ✅ 完成 |
| Phase 3 | 桌面客户端（Electron + Web UI） | 🔨 规划中 |

## 许可证

[MIT License](./LICENSE)
