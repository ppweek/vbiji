"""测试 LLM 配置管理（LlmManager）"""

import pytest
import sqlite3
from vbiji.core.llm.manager import LlmManager, get_db


@pytest.fixture
def fresh_llm_manager(tmp_path, monkeypatch):
    """创建使用临时数据库的 LlmManager"""
    db_path = tmp_path / "llm.db"
    conn = sqlite3.connect(str(db_path))
    conn.execute("""
        CREATE TABLE llm_configs (
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
    """)
    conn.commit()
    conn.close()

    def mock_get_db():
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        return conn

    monkeypatch.setattr("vbiji.core.llm.manager.get_db", mock_get_db)
    return LlmManager()


class TestLlmManagerAdd:
    """LlmManager.add() 测试"""

    def test_add_basic(self, fresh_llm_manager):
        """添加基本配置"""
        config = fresh_llm_manager.add("deepseek", "deepseek", "sk-test-123", model="deepseek-chat")
        assert config.name == "deepseek"
        assert config.provider == "deepseek"
        assert config.model == "deepseek-chat"
        assert config.options["max_tokens"] == 0

    def test_add_with_all_params(self, fresh_llm_manager):
        """添加完整参数配置"""
        config = fresh_llm_manager.add(
            name="minimax", provider="minimax", api_key="sk-minimax",
            base_url="https://api.minimaxi.com", model="MiniMax-M2.7",
            temperature=0.5, max_tokens=16000,
        )
        assert config.options["temperature"] == 0.5
        assert config.options["max_tokens"] == 16000

    def test_add_duplicate_raises(self, fresh_llm_manager):
        """重复名称抛异常"""
        fresh_llm_manager.add("dup", "deepseek", "sk-1")
        with pytest.raises(ValueError, match="已存在"):
            fresh_llm_manager.add("dup", "deepseek", "sk-2")


class TestLlmManagerGet:
    """LlmManager.get() 测试"""

    def test_get_existing(self, fresh_llm_manager):
        """获取已存在的配置"""
        fresh_llm_manager.add("deep", "deepseek", "sk-xxx", model="deepseek-v4-flash")
        config = fresh_llm_manager.get("deep")
        assert config.model == "deepseek-v4-flash"

    def test_get_nonexistent_raises(self, fresh_llm_manager):
        """获取不存在的名称抛异常"""
        with pytest.raises(ValueError):
            fresh_llm_manager.get("不存在的配置")


class TestLlmManagerEdit:
    """LlmManager.edit() 测试"""

    def test_edit_model(self, fresh_llm_manager):
        """修改模型名称"""
        fresh_llm_manager.add("cfg", "deepseek", "sk-xxx", model="old-model")
        config = fresh_llm_manager.edit("cfg", model="new-model")
        assert config.model == "new-model"

    def test_edit_max_tokens(self, fresh_llm_manager):
        """修改 max_tokens"""
        fresh_llm_manager.add("cfg", "deepseek", "sk-xxx", max_tokens=0)
        config = fresh_llm_manager.edit("cfg", max_tokens=8000)
        assert config.options["max_tokens"] == 8000

    def test_edit_nonexistent_raises(self, fresh_llm_manager):
        """编辑不存在的配置抛异常"""
        with pytest.raises(ValueError):
            fresh_llm_manager.edit("不存在", model="new-model")


class TestLlmManagerDelete:
    """LlmManager.delete() 测试"""

    def test_delete_existing(self, fresh_llm_manager):
        """删除已存在的配置"""
        fresh_llm_manager.add("cfg", "deepseek", "sk-xxx")
        fresh_llm_manager.delete("cfg")
        with pytest.raises(ValueError):
            fresh_llm_manager.get("cfg")

    def test_delete_nonexistent_raises(self, fresh_llm_manager):
        """删除不存在的配置抛异常"""
        with pytest.raises(ValueError):
            fresh_llm_manager.delete("不存在的配置")

class TestLlmManagerListAll:
    """LlmManager.list_all() 测试"""

    def test_list_empty(self, fresh_llm_manager):
        """空列表"""
        assert fresh_llm_manager.list_all() == []

    def test_list_multiple(self, fresh_llm_manager):
        """列出多条配置"""
        fresh_llm_manager.add("cfg1", "deepseek", "sk-1")
        fresh_llm_manager.add("cfg2", "minimax", "sk-2")
        configs = fresh_llm_manager.list_all()
        assert len(configs) == 2
        assert {c.name for c in configs} == {"cfg1", "cfg2"}