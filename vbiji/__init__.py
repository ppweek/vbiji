"""Vbiji - 与 AI 一起协作的知识库 CLI 工具"""

from vbiji.core.types import Document
from vbiji.core.reader import registry
from vbiji.core.converter import convert_to_markdown, convert_to_json
from vbiji.core.summarizer import summarize_local

__version__ = "0.1.0"

__all__ = [
    "Document",
    "registry",
    "convert_to_markdown",
    "convert_to_json",
    "summarize_local",
]