"""数据库公共模块"""

import sqlite3
from pathlib import Path

# 数据库路径（用户数据隔离）
_VBIJI_DIR = Path.home() / ".vbiji"
_VBIJI_DIR.mkdir(exist_ok=True)
_DB_PATH = _VBIJI_DIR / "vbiji.db"


def get_db() -> sqlite3.Connection:
    """获取数据库连接

    Returns:
        sqlite3.Connection: 数据库连接（row_factory = sqlite3.Row）
    """
    conn = sqlite3.connect(str(_DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn