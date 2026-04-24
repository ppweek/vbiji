"""内置 Reader 注册"""

from vbiji.core.readers.pdf_reader import PdfReader
from vbiji.core.readers.docx_reader import DocxReader
from vbiji.core.readers.md_reader import MdReader
from vbiji.core.readers.txt_reader import TxtReader

__all__ = [
    "PdfReader",
    "DocxReader",
    "MdReader",
    "TxtReader",
]