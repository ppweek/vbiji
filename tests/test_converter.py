"""测试格式转换功能"""

import pytest
from vbiji.core.converter import convert_to_markdown, convert_to_json, convert_to_text
from vbiji.core.types import Document


class TestConverter:
    """转换器测试"""

    @pytest.fixture
    def sample_document(self):
        """创建示例 Document"""
        return Document(
            content="这是测试内容\n第二行内容",
            title="测试文档",
            format="txt",
            path="/path/to/test.txt",
            metadata={"lines": 2},
        )

    def test_convert_to_markdown(self, sample_document):
        """测试转换为 Markdown 格式"""
        result = convert_to_markdown(sample_document)
        assert result.startswith("# 测试文档")
        assert "这是测试内容" in result
        assert "第二行内容" in result

    def test_convert_to_json(self, sample_document):
        """测试转换为 JSON 格式"""
        result = convert_to_json(sample_document)
        import json

        data = json.loads(result)
        assert data["title"] == "测试文档"
        assert data["format"] == "txt"
        assert data["content"] == "这是测试内容\n第二行内容"
        assert data["metadata"]["lines"] == 2

    def test_convert_to_text(self, sample_document):
        """测试转换为纯文本格式"""
        result = convert_to_text(sample_document)
        assert result == "这是测试内容\n第二行内容"