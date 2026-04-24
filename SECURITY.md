# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

如果您发现了安全漏洞，请**不要**在 GitHub Issue 中公开报告。

请通过以下方式私下联系我们：

1. 发送邮件至 `68409250@qq.com`
2. 标题注明 `[SECURITY]`

我们将在 **48 小时内** 确认收到报告，并在 **7 天内** 提供修复计划。

## 安全最佳实践

- **API Key 管理**：Vbiji 将 API Key 存储在本地 SQLite 数据库中，请勿将数据库文件分享给他人
- **数据存储**：所有数据默认存储在 `~/.vbiji/` 目录，请妥善保管该目录的访问权限
- **网络请求**：AI 请求直接发送至各模型服务商，请确保网络环境安全
