# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [0.1.0] - YYYY-MM-DD

### Features
- **cli**: 支持 `read` / `summarize` / `convert` 命令（Phase 1 完成）
- **cli**: 支持 `ask` 命令，AI 问答 + 提示词引用 + 结果保存
- **cli**: 支持 `batch` 批量处理，输出到 `vbiji_raw/` 和 `vbiji_llm/` 子目录
- **cli**: 支持 `llm-add/edit/del/list` LLM 配置管理
- **cli**: 支持 `prompt-add/edit/del/list/import` 提示词管理
- **reader**: 支持 PDF / DOCX / Markdown / TXT 文件读取
- **reader**: Reader 插件化架构，新增格式无需改动核心代码
- **converter**: 支持导出为 Markdown / JSON / TXT 格式
- **ai**: 支持 DeepSeek / MiniMax / Kimi / BigModel / Qwen 多模型
- **ai**: 自动上下文截断，超长文件智能压缩
- **ai**: 流式输出支持（`--stream`）
- **config**: `max_tokens=0` 表示不限制输出（自动映射为空参数）
- **db**: 共享数据库模块 `vbiji.core.db`，消除代码重复

### Bug Fixes
- **cli**: `prompt-import` 改用文件名（不含扩展名）作为标题
- **cli**: `ask --save` / `--save-as` 参数修复（`--save` 为布尔标志，`--save-as` 接受路径）
- **cli**: `prompt-del` / `llm-del` 补充存在性检查与异常处理
- **cli**: `__name__ == "__main__"` 移至文件末尾
- **manager**: `LlmManager.edit()` 补充 `_ensure_table()` 调用
- **manager**: `LlmManager.delete()` / `PromptManager.delete()` 补充存在性检查
- **ai**: `DeepSeekProvider` 不再硬编码，支持调用方注入 Provider
- **ai**: HTTP 超时从 120s 提升至 300s
- **ai**: Token 限制更新（DeepSeek 1M / MiniMax 200K / Kimi 260K）

### Documentation
- README 完整更新，含安装、快速开始、路线图
- CLAUDE.md 供 AI Agent 理解项目结构
- CONTRIBUTING.md 贡献指南

### Testing
- 93 个单元测试，覆盖 base/token 工具、prompt manager、llm manager、AI chat、providers、CLI

### Infrastructure
- GitHub Actions CI（lint + typecheck + pytest + coverage gate）
- pytest-cov 覆盖率门禁（PR > 60%，main > 70%）
- uv 包管理
