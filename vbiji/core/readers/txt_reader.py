"""纯文本文件读取器"""

from pathlib import Path
from vbiji.core.readers.base import BaseReader
from vbiji.core.types import Document as DocDocument


class TxtReader(BaseReader):
    """纯文本文件读取器

    使用标准库读取 .txt 文件，支持多种编码
    """

    format = "txt"

    SUPPORTED_ENCODINGS = ["utf-8", "gbk", "gb2312", "utf-16"]

    def supports(self, path: str) -> bool:
        """判断是否支持该文件

        Args:
            path: 文件路径

        Returns:
            bool: 如果是 .txt 文件返回 True
        """
        return Path(path).suffix.lower() == ".txt"

    def _read_with_encoding(self, file_path: Path, encoding: str) -> str:
        """尝试使用指定编码读取文件

        Args:
            file_path: 文件路径
            encoding: 编码名称

        Returns:
            str: 文件内容
        """
        return file_path.read_text(encoding=encoding)

    def read(self, path: str) -> DocDocument:
        """读取纯文本文件

        Args:
            path: 文本文件路径

        Returns:
            DocDocument: 包含文档文本内容的文档对象

        Raises:
            FileNotFoundError: 文件不存在时
        """
        file_path = Path(path)
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {path}")

        content = ""
        for encoding in self.SUPPORTED_ENCODINGS:
            try:
                content = self._read_with_encoding(file_path, encoding)
                break
            except UnicodeDecodeError:
                continue

        if not content:
            content = file_path.read_text(encoding="utf-8", errors="ignore")

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