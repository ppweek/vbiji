"""测试 Reader 注册和读取功能"""

import pytest
from pathlib import Path
from vbiji.core.reader import registry
from vbiji.core.readers import PdfReader, DocxReader, MdReader, TxtReader
from vbiji.exceptions import UnsupportedFormatError


class TestReaderRegistry:
    """ReaderRegistry 测试"""

    def test_registry_has_readers(self):
        """测试注册表有注册的 readers"""
        assert len(registry._readers) == 4

    def test_registry_has_pdf_reader(self):
        """测试注册表包含 PDF reader"""
        assert any(isinstance(r, PdfReader) for r in registry._readers)

    def test_registry_has_docx_reader(self):
        """测试注册表包含 Docx reader"""
        assert any(isinstance(r, DocxReader) for r in registry._readers)

    def test_registry_has_md_reader(self):
        """测试注册表包含 Markdown reader"""
        assert any(isinstance(r, MdReader) for r in registry._readers)

    def test_registry_has_txt_reader(self):
        """测试注册表包含 Txt reader"""
        assert any(isinstance(r, TxtReader) for r in registry._readers)


class TestPdfReader:
    """PdfReader 测试"""

    def test_supports_pdf_file(self):
        """测试支持 .pdf 文件"""
        reader = PdfReader()
        assert reader.supports("test.pdf") is True
        assert reader.supports("test.PDF") is True

    def test_not_supports_other_files(self):
        """测试不支持其他文件"""
        reader = PdfReader()
        assert reader.supports("test.txt") is False
        assert reader.supports("test.docx") is False
        assert reader.supports("test.md") is False


class TestDocxReader:
    """DocxReader 测试"""

    def test_supports_docx_file(self):
        """测试支持 .docx 文件"""
        reader = DocxReader()
        assert reader.supports("test.docx") is True
        assert reader.supports("test.DOCX") is True

    def test_not_supports_other_files(self):
        """测试不支持其他文件"""
        reader = DocxReader()
        assert reader.supports("test.txt") is False
        assert reader.supports("test.pdf") is False


class TestMdReader:
    """MdReader 测试"""

    def test_supports_md_files(self):
        """测试支持 .md 和 .markdown 文件"""
        reader = MdReader()
        assert reader.supports("test.md") is True
        assert reader.supports("test.markdown") is True
        assert reader.supports("test.MD") is True

    def test_not_supports_other_files(self):
        """测试不支持其他文件"""
        reader = MdReader()
        assert reader.supports("test.txt") is False
        assert reader.supports("test.pdf") is False


class TestTxtReader:
    """TxtReader 测试"""

    def test_supports_txt_file(self):
        """测试支持 .txt 文件"""
        reader = TxtReader()
        assert reader.supports("test.txt") is True
        assert reader.supports("test.TXT") is True

    def test_not_supports_other_files(self):
        """测试不支持其他文件"""
        reader = TxtReader()
        assert reader.supports("test.pdf") is False
        assert reader.supports("test.docx") is False


class TestUnsupportedFormat:
    """不支持格式测试"""

    def test_unsupported_format_raises_error(self):
        """测试不支持的格式抛出 UnsupportedFormatError"""
        with pytest.raises(UnsupportedFormatError):
            registry.read("/path/to/file.unsupported")