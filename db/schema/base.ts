import { sqliteTable, text, integer } from 'drizzle-orm/sqlite-core';

/**
 * 基础 Schema 包含所有表共有的字段
 * 所有业务表应使用 baseTable() 作为父表
 */
export const baseTable = sqliteTable('__base', {
  id: text('id').primaryKey(),           // UUID 主键
  createdAt: integer('created_at', { mode: 'timestamp' })
    .notNull()
    .$defaultFn(() => new Date()),      // 创建时间
  updatedAt: integer('updated_at', { mode: 'timestamp' })
    .notNull()
    .$defaultFn(() => new Date()),      // 更新时间
});

/**
 * 生成 UUID 的工具函数
 */
export function generateId(): string {
  return crypto.randomUUID();
}

/**
 * 更新时间戳的工具
 */
export function updateTimestamp() {
  return new Date();
}

// ========== 常用类型导出 ==========

export type BaseTable = typeof baseTable;
export type BaseTableRow = {
  id: string;
  createdAt: Date;
  updatedAt: Date;
};
