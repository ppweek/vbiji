"""文件读取注册中心"""

from pathlib import Path
from vbiji.core.readers.base import BaseReader
from vbiji.core.readers import PdfReader, DocxReader, MdReader, TxtReader
from vbiji.core.types import Document
from vbiji.exceptions import UnsupportedFormatError


class ReaderRegistry:
    """文件读取注册中心，插件式设计

    支持动态注册新的 Reader 处理器，用于处理不同格式的文件读取

    Example:
        registry = ReaderRegistry()
        registry.register(PdfReader())
        doc = registry.read("/path/to/file.pdf")
    """

    def __init__(self) -> None:
        """初始化注册表"""
        self._readers: list[BaseReader] = []

    def register(self, reader: BaseReader) -> None:
        """注册一个 Reader 处理器

        Args:
            reader: BaseReader 子类实例
        """
        self._readers.append(reader)

    def get_handler(self, path: str) -> BaseReader:
        """获取适合该文件路径的 Handler

        Args:
            path: 文件路径

        Returns:
            BaseReader: 支持该格式的 Reader 实例

        Raises:
            UnsupportedFormatError: 没有支持的 Reader 时
        """
        file_path = Path(path)
        for reader in self._readers:
            if reader.supports(str(file_path)):
                return reader
        raise UnsupportedFormatError(path)

    def read(self, path: str) -> Document:
        """读取文件并返回统一 Document

        Args:
            path: 文件路径

        Returns:
            Document: 统一格式的文档对象

        Raises:
            UnsupportedFormatError: 格式不支持时
            FileNotFoundError: 文件不存在时
        """
        handler = self.get_handler(path)
        return handler.read(path)


# 全局注册表（单例）
registry = ReaderRegistry()
registry.register(PdfReader())
registry.register(DocxReader())
registry.register(MdReader())
registry.register(TxtReader())