"""PDF 文件读取器"""

import fitz  # PyMuPDF
from pathlib import Path
from vbiji.core.readers.base import BaseReader
from vbiji.core.types import Document


class PdfReader(BaseReader):
    """PDF 文件读取器

    使用 PyMuPDF (fitz) 提取 PDF 文本内容
    """

    format = "pdf"

    def supports(self, path: str) -> bool:
        """判断是否支持该文件

        Args:
            path: 文件路径

        Returns:
            bool: 如果是 .pdf 文件返回 True
        """
        return Path(path).suffix.lower() == ".pdf"

    def read(self, path: str) -> Document:
        """读取 PDF 文件

        Args:
            path: PDF 文件路径

        Returns:
            Document: 包含 PDF 文本内容的文档对象

        Raises:
            FileNotFoundError: 文件不存在时
        """
        file_path = Path(path)
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {path}")

        doc = fitz.open(str(file_path))
        page_count = len(doc)
        content_parts = []

        for page_num in range(page_count):
            page = doc[page_num]
            text = page.get_text()
            if text.strip():
                content_parts.append(text)

        doc.close()

        content = "\n".join(content_parts)
        metadata = {
            "pages": page_count,
        }

        return Document(
            content=content,
            title=file_path.stem,
            format=self.format,
            path=str(file_path.absolute()),
            metadata=metadata,
        )