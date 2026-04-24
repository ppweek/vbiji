# 贡献指南

欢迎参与 Vbiji 的开发！请遵循以下规范。

## 开发环境

```bash
git clone https://github.com/ppweek/vbiji.git
cd vbiji
uv sync --dev
```

## 代码规范

- **类型检查**：`uv run mypy vbiji/`（必须通过）
- **代码风格**：`uv run ruff check vbiji/ --fix`（自动修复）
- **提交规范**：提交信息遵循 [Conventional Commits](https://www.conventionalcommits.org/)

## 分支策略

| 分支 | 用途 |
|------|------|
| `main` | 稳定版本 |
| `develop` | 开发分支 |
| `feature/*` | 新功能 |
| `fix/*` | Bug 修复 |

## 测试门禁

- 单元测试覆盖率：PR ≥ 75%，合并到 main ≥ 80%
- 必须通过 mypy 类型检查
- 必须通过 ruff 检查

## Pull Request 流程

1. Fork 并创建 feature 分支
2. 编写测试和代码
3. 确保通过 CI 所有检查项
4. 提交 PR 并描述改动内容
5. 等待 Code Review

## Issue

- 提交 Bug 请使用 [bug-report 模板](./.github/ISSUE_TEMPLATE/bug-report.md)
- 功能请求请使用 [feature-request 模板](./.github/ISSUE_TEMPLATE/feature-request.md)
