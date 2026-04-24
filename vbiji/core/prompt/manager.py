"""提示词管理器（Phase 2）"""

import json
import sqlite3
import uuid
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

from vbiji.core.db import get_db


@dataclass
class Prompt:
    """提示词数据结构

    Attributes:
        id: 唯一标识符
        title: 提示词标题（唯一）
        content: 提示词内容
        description: 描述
        tags: 标签列表
        created_at: 创建时间（ISO 格式）
        updated_at: 更新时间（ISO 格式）
    """

    id: str
    title: str
    content: str
    description: str = ""
    tags: list[str] = None
    created_at: str = ""
    updated_at: str = ""

    def __post_init__(self) -> None:
        if self.tags is None:
            self.tags = []


class PromptManager:
    """提示词 CRUD 管理

    提供提示词的增删改查功能，数据存储在 SQLite 数据库中。
    """

    def _ensure_table(self, conn: sqlite3.Connection) -> None:
        """确保 prompts 表存在

        Args:
            conn: 数据库连接
        """
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS prompts (
                id TEXT PRIMARY KEY,
                title TEXT UNIQUE NOT NULL,
                content TEXT NOT NULL,
                description TEXT DEFAULT '',
                tags TEXT DEFAULT '[]',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

    def add(
        self,
        title: str,
        content: str,
        description: str = "",
        tags: Optional[list[str]] = None,
    ) -> Prompt:
        """新增提示词

        Args:
            title: 提示词标题（唯一）
            content: 提示词内容
            description: 描述（可选）
            tags: 标签列表（可选）

        Returns:
            Prompt: 创建的提示词对象

        Raises:
            ValueError: 如果标题已存在
        """
        conn = get_db()
        self._ensure_table(conn)

        cursor = conn.execute("SELECT id FROM prompts WHERE title = ?", (title,))
        if cursor.fetchone():
            conn.close()
            raise ValueError(f"提示词 '{title}' 已存在")

        id_ = str(uuid.uuid4())
        now = datetime.now().isoformat()
        tags_json = json.dumps(tags or [])

        conn.execute(
            """
            INSERT INTO prompts (id, title, content, description, tags, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (id_, title, content, description, tags_json, now, now),
        )
        conn.commit()
        conn.close()
        return Prompt(
            id=id_,
            title=title,
            content=content,
            description=description,
            tags=tags or [],
            created_at=now,
            updated_at=now,
        )

    def import_from_file(self, filepath: str) -> Prompt:
        """从 MD 文件导入提示词

        文件名（不含扩展名）作为标题，文件全部内容作为提示词内容。

        Args:
            filepath: MD 文件路径

        Returns:
            Prompt: 导入的提示词对象

        Raises:
            FileNotFoundError: 如果文件不存在
            ValueError: 如果标题已存在
        """
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {filepath}")

        title = path.stem
        content = path.read_text(encoding="utf-8").strip()

        return self.add(title=title, content=content)

    def edit(
        self,
        title: str,
        content: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Prompt:
        """修改提示词

        Args:
            title: 提示词标题
            content: 新的提示词内容（可选）
            description: 新的描述（可选）

        Returns:
            Prompt: 更新后的提示词对象

        Raises:
            ValueError: 如果标题不存在
        """
        conn = get_db()
        now = datetime.now().isoformat()

        if content is not None:
            conn.execute(
                "UPDATE prompts SET content = ?, updated_at = ? WHERE title = ?",
                (content, now, title),
            )
        if description is not None:
            conn.execute(
                "UPDATE prompts SET description = ?, updated_at = ? WHERE title = ?",
                (description, now, title),
            )

        row = conn.execute(
            """
            SELECT id, title, content, description, tags, created_at, updated_at
            FROM prompts WHERE title = ?
            """,
            (title,),
        ).fetchone()
        conn.commit()
        conn.close()

        if not row:
            raise ValueError(f"提示词 '{title}' 不存在")
        return Prompt(
            id=row[0],
            title=row[1],
            content=row[2],
            description=row[3],
            tags=json.loads(row[4]),
            created_at=row[5],
            updated_at=row[6],
        )

    def get(self, title: str) -> Prompt:
        """获取提示词

        Args:
            title: 提示词标题

        Returns:
            Prompt: 提示词对象

        Raises:
            ValueError: 如果标题不存在
        """
        conn = get_db()
        self._ensure_table(conn)
        row = conn.execute(
            """
            SELECT id, title, content, description, tags, created_at, updated_at
            FROM prompts WHERE title = ?
            """,
            (title,),
        ).fetchone()
        conn.close()
        if not row:
            raise ValueError(f"提示词 '{title}' 不存在")
        return Prompt(
            id=row[0],
            title=row[1],
            content=row[2],
            description=row[3],
            tags=json.loads(row[4]),
            created_at=row[5],
            updated_at=row[6],
        )

    def delete(self, title: str) -> None:
        """删除提示词

        Args:
            title: 提示词标题

        Raises:
            ValueError: 提示词不存在
        """
        conn = get_db()
        self._ensure_table(conn)
        cursor = conn.execute("SELECT 1 FROM prompts WHERE title = ?", (title,))
        if cursor.fetchone() is None:
            conn.close()
            raise ValueError(f"提示词不存在: {title}")
        conn.execute("DELETE FROM prompts WHERE title = ?", (title,))
        conn.commit()
        conn.close()

    def list_all(self) -> list[Prompt]:
        """列出所有提示词

        Returns:
            list[Prompt]: 提示词列表
        """
        conn = get_db()
        self._ensure_table(conn)
        rows = conn.execute(
            """
            SELECT id, title, content, description, tags, created_at, updated_at
            FROM prompts
            """
        ).fetchall()
        conn.close()
        return [
            Prompt(
                id=r[0],
                title=r[1],
                content=r[2],
                description=r[3],
                tags=json.loads(r[4]),
                created_at=r[5],
                updated_at=r[6],
            )
            for r in rows
        ]
