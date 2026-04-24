"""格式转换器"""

import json
from vbiji.core.types import Document


def convert_to_markdown(doc: Document) -> str:
    """Document 转换为 Markdown 格式

    Args:
        doc: Document 对象

    Returns:
        str: Markdown 格式字符串，标题使用文件名
    """
    return f"# {doc.title}\n\n{doc.content}"


def convert_to_json(doc: Document) -> str:
    """Document 转换为 JSON 格式

    Args:
        doc: Document 对象

    Returns:
        str: JSON 格式字符串
    """
    return json.dumps(
        {
            "title": doc.title,
            "format": doc.format,
            "path": doc.path,
            "content": doc.content,
            "metadata": doc.metadata,
        },
        ensure_ascii=False,
        indent=2,
    )


def convert_to_text(doc: Document) -> str:
    """Document 转换为纯文本格式

    Args:
        doc: Document 对象

    Returns:
        str: 纯文本内容
    """
    return doc.content