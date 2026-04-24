# IPC Channel Registry — IPC 通道注册表

> 本文档记录所有 Electron IPC 通道命名空间，由 Architect 设计，Backend Dev Agent 实现。

---

## 命名空间总览

| 命名空间 | 说明 | 文件 | 状态 |
|---------|------|------|------|
| `ai:*` | AI 模型调用相关 | `ipc/ai.ipc.ts` | - |
| `chat:*` | 聊天会话 CRUD | `ipc/chat.ipc.ts` | - |
| `assistant:*` | 助手管理 | `ipc/assistant.ipc.ts` | - |
| `settings:*` | 系统设置 | `ipc/settings.ipc.ts` | - |
| `file:*` | 文件上传下载 | `ipc/file.ipc.ts` | - |
| `system:*` | 系统能力（快捷键/托盘/更新） | `ipc/system.ipc.ts` | - |

---

## 通道详情

### AI 通道 (`ai:*`)

| 通道 | 说明 | 参数 | 返回值 |
|------|------|------|--------|
| `ai:list-models` | 获取可用模型列表 | - | `Model[]` |
| `ai:chat` | 发送对话请求 | `{ messages, model, temperature }` | `StreamResponse` |
| `ai:abort` | 中止当前请求 | - | `{ success: boolean }` |

### Chat 通道 (`chat:*`)

| 通道 | 说明 | 参数 | 返回值 |
|------|------|------|--------|
| `chat:list` | 获取会话列表 | `{ limit?, offset? }` | `Chat[]` |
| `chat:get` | 获取单个会话 | `{ id }` | `Chat` |
| `chat:create` | 创建会话 | `{ title?, assistantId? }` | `Chat` |
| `chat:update` | 更新会话 | `{ id, title }` | `Chat` |
| `chat:delete` | 删除会话 | `{ id }` | `{ success: boolean }` |

### Assistant 通道 (`assistant:*`)

| 通道 | 说明 | 参数 | 返回值 |
|------|------|------|--------|
| `assistant:list` | 获取助手列表 | `{ type? }` | `Assistant[]` |
| `assistant:get` | 获取助手详情 | `{ id }` | `Assistant` |
| `assistant:create` | 创建助手 | `CreateAssistantParams` | `Assistant` |
| `assistant:update` | 更新助手 | `{ id, ...updates }` | `Assistant` |
| `assistant:delete` | 删除助手 | `{ id }` | `{ success: boolean }` |

### Settings 通道 (`settings:*`)

| 通道 | 说明 | 参数 | 返回值 |
|------|------|------|--------|
| `settings:get` | 获取设置项 | `{ key }` | `unknown` |
| `settings:set` | 设置设置项 | `{ key, value }` | `{ success: boolean }` |
| `settings:get-all` | 获取全部设置 | - | `SettingsMap` |
| `settings:reset` | 重置设置 | - | `{ success: boolean }` |

### File 通道 (`file:*`)

| 通道 | 说明 | 参数 | 返回值 |
|------|------|------|--------|
| `file:select` | 选择文件 | `{ filters? }` | `FilePath[]` |
| `file:select-directory` | 选择目录 | - | `string` |
| `file:read` | 读取文件内容 | `{ path, encoding? }` | `string` |
| `file:write` | 写入文件 | `{ path, content }` | `{ success: boolean }` |
| `file:save-dialog` | 保存文件对话框 | `{ defaultPath, filters? }` | `string \| null` |

### System 通道 (`system:*`)

| 通道 | 说明 | 参数 | 返回值 |
|------|------|------|--------|
| `system:platform` | 获取平台信息 | - | `string` |
| `system:version` | 获取应用版本 | - | `string` |
| `system:check-update` | 检查更新 | - | `UpdateInfo \| null` |
| `system:install-update` | 安装更新 | - | `{ success: boolean }` |
| `system:register-shortcut` | 注册快捷键 | `{ accelerator, action }` | `{ success: boolean }` |
| `system:unregister-shortcut` | 注销快捷键 | `{ accelerator }` | `{ success: boolean }` |
| `system:show-notification` | 显示通知 | `{ title, body }` | `{ success: boolean }` |
| `system:open-external` | 打开外部链接 | `{ url }` | `{ success: boolean }` |

---

## Preload 暴露的 API

```typescript
// window.electronAPI 暴露的接口
interface ElectronAPI {
  invoke: (channel: string, ...args: unknown[]) => Promise<unknown>;
  on: (channel: string, callback: (...args: unknown[]) => void) => () => void;
  removeListener: (channel: string) => void;
  getPlatform: () => string;
}
```

---

## 注册顺序

1. 在 `src/main/index.ts` 中导入所有 handler
2. 在 `registerAllIpcHandlers()` 中按序调用
3. 顺序建议：`db` → `services` → `ipc handlers`
