"""LLM 配置管理器（Phase 2）"""

import sqlite3
from datetime import datetime
from typing import Optional

from vbiji.core.ai.providers.base import LlmConfig
from vbiji.core.db import get_db


class LlmManager:
    """LLM 配置 CRUD 管理

    提供 LLM配置的增删改查功能，数据存储在 SQLite 数据库中。
    """

    def _ensure_table(self, conn: sqlite3.Connection) -> None:
        """确保 llm_configs 表存在

        Args:
            conn: 数据库连接
        """
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS llm_configs (
                name TEXT PRIMARY KEY,
                provider TEXT NOT NULL,
                api_key TEXT NOT NULL,
                base_url TEXT DEFAULT '',
                model TEXT DEFAULT '',
                temperature REAL DEFAULT 0.7,
                max_tokens INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

    def add(
        self,
        name: str,
        provider: str,
        api_key: str,
        base_url: str = "",
        model: str = "",
        temperature: float = 0.7,
        max_tokens: int = 0,  # 0 表示不限制输出长度
    ) -> LlmConfig:
        """新增 LLM 配置

        Args:
            name: 配置名称（唯一）
            provider: 提供者类型
            api_key: API 密钥
            base_url: API 基础 URL（可选）
            model: 模型名称（可选）
            temperature: 温度参数（可选）
            max_tokens: 最大 token 数（可选）

        Returns:
            LlmConfig: 创建的 LLM 配置对象

        Raises:
            ValueError: 如果名称已存在
        """
        conn = get_db()
        self._ensure_table(conn)

        cursor = conn.execute("SELECT name FROM llm_configs WHERE name = ?", (name,))
        if cursor.fetchone():
            conn.close()
            raise ValueError(f"LLM 配置 '{name}' 已存在")

        now = datetime.now().isoformat()

        conn.execute(
            """
            INSERT INTO llm_configs (name, provider, api_key, base_url, model, temperature, max_tokens, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (name, provider, api_key, base_url, model, temperature, max_tokens, now, now),
        )
        conn.commit()
        conn.close()
        return LlmConfig(
            name=name,
            provider=provider,
            api_key=api_key,
            base_url=base_url,
            model=model,
            options={"temperature": temperature, "max_tokens": max_tokens},
        )

    def get(self, name: str) -> LlmConfig:
        """获取 LLM 配置

        Args:
            name: 配置名称

        Returns:
            LlmConfig: LLM 配置对象

        Raises:
            ValueError: 如果名称不存在
        """
        conn = get_db()
        self._ensure_table(conn)
        row = conn.execute(
            """
            SELECT name, provider, api_key, base_url, model, temperature, max_tokens, created_at, updated_at
            FROM llm_configs WHERE name = ?
            """,
            (name,),
        ).fetchone()
        conn.close()
        if not row:
            raise ValueError(f"LLM 配置 '{name}' 不存在")
        return LlmConfig(
            name=row[0],
            provider=row[1],
            api_key=row[2],
            base_url=row[3],
            model=row[4],
            options={"temperature": row[5], "max_tokens": row[6]},
        )

    def edit(
        self,
        name: str,
        provider: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> LlmConfig:
        """修改 LLM 配置

        Args:
            name: 配置名称
            provider: 新的提供者类型（可选）
            api_key: 新的 API 密钥（可选）
            base_url: 新的 API 基础 URL（可选）
            model: 新的模型名称（可选）
            temperature: 新的温度参数（可选）
            max_tokens: 新的最大 token 数（可选）

        Returns:
            LLMConfig: 更新后的 LLM 配置对象

        Raises:
            ValueError: 如果名称不存在
        """
        conn = get_db()
        self._ensure_table(conn)
        now = datetime.now().isoformat()

        updates = []
        params = []

        if provider is not None:
            updates.append("provider = ?")
            params.append(provider)
        if api_key is not None:
            updates.append("api_key = ?")
            params.append(api_key)
        if base_url is not None:
            updates.append("base_url = ?")
            params.append(base_url)
        if model is not None:
            updates.append("model = ?")
            params.append(model)
        if temperature is not None:
            updates.append("temperature = ?")
            params.append(temperature)
        if max_tokens is not None:
            updates.append("max_tokens = ?")
            params.append(max_tokens)

        if updates:
            updates.append("updated_at = ?")
            params.append(now)
            params.append(name)
            conn.execute(
                f"UPDATE llm_configs SET {', '.join(updates)} WHERE name = ?",
                params,
            )

        row = conn.execute(
            """
            SELECT name, provider, api_key, base_url, model, temperature, max_tokens, created_at, updated_at
            FROM llm_configs WHERE name = ?
            """,
            (name,),
        ).fetchone()
        conn.commit()
        conn.close()

        if not row:
            raise ValueError(f"LLM 配置 '{name}' 不存在")
        return LlmConfig(
            name=row[0],
            provider=row[1],
            api_key=row[2],
            base_url=row[3],
            model=row[4],
            options={"temperature": row[5], "max_tokens": row[6]},
        )

    def delete(self, name: str) -> None:
        """删除 LLM 配置

        Args:
            name: 配置名称

        Raises:
            ValueError: 配置不存在
        """
        conn = get_db()
        cursor = conn.execute("SELECT 1 FROM llm_configs WHERE name = ?", (name,))
        if cursor.fetchone() is None:
            conn.close()
            raise ValueError(f"LLM 配置不存在: {name}")
        conn.execute("DELETE FROM llm_configs WHERE name = ?", (name,))
        conn.commit()
        conn.close()

    def list_all(self) -> list[LlmConfig]:
        """列出所有 LLM 配置

        Returns:
            list[LLMConfig]: LLM 配置列表
        """
        conn = get_db()
        self._ensure_table(conn)
        rows = conn.execute(
            """
            SELECT name, provider, api_key, base_url, model, temperature, max_tokens, created_at, updated_at
            FROM llm_configs
            """
        ).fetchall()
        conn.close()
        return [
            LlmConfig(
                name=r[0],
                provider=r[1],
                api_key=r[2],
                base_url=r[3],
                model=r[4],
                options={"temperature": r[5], "max_tokens": r[6]},
            )
            for r in rows
        ]
