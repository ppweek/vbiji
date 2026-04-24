"""测试提示词管理（PromptManager）"""

import pytest
import sqlite3
from pathlib import Path
from vbiji.core.prompt.manager import PromptManager, get_db


@pytest.fixture
def fresh_pm(tmp_path, monkeypatch):
    """创建使用临时数据库的 PromptManager"""
    db_path = tmp_path / "prompts.db"
    conn = sqlite3.connect(str(db_path))
    conn.execute("""
        CREATE TABLE prompts (
            id TEXT PRIMARY KEY,
            title TEXT UNIQUE NOT NULL,
            content TEXT NOT NULL,
            description TEXT DEFAULT '',
            tags TEXT DEFAULT '[]',
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

    monkeypatch.setattr("vbiji.core.prompt.manager.get_db", mock_get_db)
    return PromptManager()


class TestPromptManagerAdd:
    """PromptManager.add() 测试"""

    def test_add_single_prompt(self, fresh_pm):
        """添加一条提示词"""
        p = fresh_pm.add("测试标题", "测试内容")
        assert p.title == "测试标题"
        assert p.content == "测试内容"

    def test_add_with_description(self, fresh_pm):
        """添加带描述的提示词"""
        p = fresh_pm.add("标题", "内容", description="这是一个描述")
        assert p.description == "这是一个描述"

    def test_add_duplicate_raises(self, fresh_pm):
        """重复添加相同标题应抛出异常"""
        fresh_pm.add("重复标题", "内容1")
        with pytest.raises(ValueError, match="已存在"):
            fresh_pm.add("重复标题", "内容2")


class TestPromptManagerGet:
    """PromptManager.get() 测试"""

    def test_get_existing(self, fresh_pm):
        """获取已存在的提示词"""
        fresh_pm.add("标题", "内容")
        p = fresh_pm.get("标题")
        assert p.title == "标题"
        assert p.content == "内容"

    def test_get_nonexistent_raises(self, fresh_pm):
        """获取不存在的标题应抛出异常"""
        with pytest.raises(ValueError, match="不存在"):
            fresh_pm.get("不存在的标题")


class TestPromptManagerEdit:
    """PromptManager.edit() 测试"""

    def test_edit_content(self, fresh_pm):
        """修改提示词内容"""
        fresh_pm.add("标题", "旧内容")
        p = fresh_pm.edit("标题", content="新内容")
        assert p.content == "新内容"

    def test_edit_description(self, fresh_pm):
        """修改提示词描述"""
        fresh_pm.add("标题", "内容", description="旧描述")
        p = fresh_pm.edit("标题", description="新描述")
        assert p.description == "新描述"

    def test_edit_nonexistent_raises(self, fresh_pm):
        """编辑不存在的标题应抛出异常"""
        with pytest.raises(ValueError):
            fresh_pm.edit("不存在", content="内容")


class TestPromptManagerDelete:
    """PromptManager.delete() 测试"""

    def test_delete_existing(self, fresh_pm):
        """删除已存在的提示词"""
        fresh_pm.add("标题", "内容")
        fresh_pm.delete("标题")
        with pytest.raises(ValueError):
            fresh_pm.get("标题")

    def test_delete_nonexistent(self, fresh_pm):
        """删除不存在的标题抛 ValueError"""
        with pytest.raises(ValueError):
            fresh_pm.delete("不存在的标题")


class TestPromptManagerListAll:
    """PromptManager.list_all() 测试"""

    def test_list_empty(self, fresh_pm):
        """空列表"""
        assert fresh_pm.list_all() == []

    def test_list_multiple(self, fresh_pm):
        """列出多条提示词"""
        fresh_pm.add("标题1", "内容1")
        fresh_pm.add("标题2", "内容2")
        results = fresh_pm.list_all()
        assert len(results) == 2
        assert {p.title for p in results} == {"标题1", "标题2"}


class TestPromptManagerImportFromFile:
    """PromptManager.import_from_file() 测试"""

    def test_import_file(self, fresh_pm, tmp_path):
        """从 MD 文件导入"""
        md_file = tmp_path / "测试导入.md"
        md_file.write_text("这是提示词内容\n第二行", encoding="utf-8")
        p = fresh_pm.import_from_file(str(md_file))
        assert p.title == "测试导入"
        assert p.content == "这是提示词内容\n第二行"

    def test_import_file_not_found(self, fresh_pm, tmp_path):
        """文件不存在时抛异常"""
        with pytest.raises(FileNotFoundError):
            fresh_pm.import_from_file("/nonexistent/file.md")

    def test_import_duplicate_title(self, fresh_pm, tmp_path):
        """导入时标题重复应抛异常"""
        fresh_pm.add("重复标题", "已有内容")
        md_file = tmp_path / "重复标题.md"
        md_file.write_text("新内容", encoding="utf-8")
        with pytest.raises(ValueError):
            fresh_pm.import_from_file(str(md_file))