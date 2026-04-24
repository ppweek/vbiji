/**
 * Preload Script — 预加载脚本
 *
 * 职责：在渲染进程与主进程之间建立安全的通信桥梁
 * 原则：最小权限原则 — 只暴露必要的 API
 *
 * @example
 * // 在渲染进程中使用：
 * const { invoke, on, getPlatform } = window.electronAPI;
 * const chats = await invoke('chat:list');
 * const removeListener = on('chat:updated', (data) => console.log(data));
 */

import { contextBridge, ipcRenderer } from 'electron';

// ========== 类型定义 ==========

/**
 * IPC 通道白名单 — 所有允许调用的通道
 * 禁止调用未列入白名单的通道
 */
const ALLOWED_CHANNELS = [
  // AI
  'ai:list-models',
  'ai:chat',
  'ai:abort',
  // Chat
  'chat:list',
  'chat:get',
  'chat:create',
  'chat:update',
  'chat:delete',
  // Assistant
  'assistant:list',
  'assistant:get',
  'assistant:create',
  'assistant:update',
  'assistant:delete',
  // Settings
  'settings:get',
  'settings:set',
  'settings:get-all',
  'settings:reset',
  // File
  'file:select',
  'file:select-directory',
  'file:read',
  'file:write',
  'file:save-dialog',
  // System
  'system:platform',
  'system:version',
  'system:check-update',
  'system:install-update',
  'system:register-shortcut',
  'system:unregister-shortcut',
  'system:show-notification',
  'system:open-external',
] as const;

type AllowedChannel = typeof ALLOWED_CHANNELS[number];

/**
 * ElectronAPI 暴露给渲染进程的接口
 */
export interface ElectronAPI {
  invoke: <T = unknown>(channel: AllowedChannel, ...args: unknown[]) => Promise<T>;
  on: (channel: AllowedChannel, callback: (...args: unknown[]) => void) => () => void;
  removeListener: (channel: AllowedChannel) => void;
  getPlatform: () => string;
}

// ========== 实现 ==========

/**
 * 验证通道是否在白名单中
 */
function validateChannel(channel: string): asserts channel is AllowedChannel {
  if (!ALLOWED_CHANNELS.includes(channel as AllowedChannel)) {
    throw new Error(`IPC channel "${channel}" is not allowed. Use one of: ${ALLOWED_CHANNELS.join(', ')}`);
  }
}

/**
 * 安全地调用主进程的 IPC handler
 */
async function safeInvoke<T>(channel: AllowedChannel, ...args: unknown[]): Promise<T> {
  validateChannel(channel);
  return ipcRenderer.invoke(channel, ...args) as Promise<T>;
}

/**
 * 安全地监听主进程的 IPC 事件
 * 返回一个注销函数
 */
function safeOn(channel: AllowedChannel, callback: (...args: unknown[]) => void): () => void {
  validateChannel(channel);
  const subscription = (_e: Electron.IpcRendererEvent, ...args: unknown[]) => callback(...args);
  ipcRenderer.on(channel, subscription);
  return () => {
    ipcRenderer.removeListener(channel, subscription);
  };
}

/**
 * 安全地移除监听器
 */
function safeRemoveListener(channel: AllowedChannel): void {
  validateChannel(channel);
  ipcRenderer.removeAllListeners(channel);
}

/**
 * 获取当前平台
 */
function getPlatform(): string {
  return process.platform;
}

// ========== 暴露 API 到渲染进程 ==========

const electronAPI: ElectronAPI = {
  invoke: safeInvoke,
  on: safeOn,
  removeListener: safeRemoveListener,
  getPlatform,
} as const;

contextBridge.exposeInMainWorld('electronAPI', electronAPI);

// ========== 全局类型声明 ==========

declare global {
  interface Window {
    electronAPI: ElectronAPI;
  }
}
