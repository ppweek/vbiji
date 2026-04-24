"""Markdown 文件读取器"""

from pathlib import Path
from vbiji.core.readers.base import BaseReader
from vbiji.core.types import Document as DocDocument


class MdReader(BaseReader):
    """Markdown 文件读取器

    使用标准库读取 .md / .markdown 文件
    """

    format = "md"

    def supports(self, path: str) -> bool:
        """判断是否支持该文件

        Args:
            path: 文件路径

        Returns:
            bool: 如果是 .md 或 .markdown 文件返回 True
        """
        suffix = Path(path).suffix.lower()
        return suffix in (".md", ".markdown")

    def read(self, path: str) -> DocDocument:
        """读取 Markdown 文件

        Args:
            path: Markdown 文件路径

        Returns:
            DocDocument: 包含文档文本内容的文档对象

        Raises:
            FileNotFoundError: 文件不存在时
        """
        file_path = Path(path)
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {path}")

        content = file_path.read_text(encoding="utf-8")
        lines = content.split("\n")
        metadata = {
            "lines": len(lines),
        }

        return DocDocument(
            content=content,
            title=file_path.stem,
            format=self.format,
            path=str(file_path.absolute()),
            metadata=metadata,
        )