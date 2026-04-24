"""文件读取器抽象基类"""

from abc import ABC, abstractmethod
from vbiji.core.types import Document


class BaseReader(ABC):
    """Reader 抽象基类，所有格式处理器继承此接口

    子类需要:
    1. 设置 format 类属性为支持的格式名
    2. 实现 supports() 方法判断是否支持该文件
    3. 实现 read() 方法读取文件并返回 Document
    """

    format: str = ""  # 子类覆盖：支持的格式名

    @abstractmethod
    def supports(self, path: str) -> bool:
        """判断是否支持该文件

        Args:
            path: 文件路径

        Returns:
            bool: 如果支持返回 True，否则 False
        """
        ...

    @abstractmethod
    def read(self, path: str) -> Document:
        """读取文件，返回统一 Document

        Args:
            path: 文件路径

        Returns:
            Document: 统一格式的文档对象

        Raises:
            FileNotFoundError: 文件不存在时
            UnsupportedFormatError: 格式不支持时
        """
        ...