"""摘要生成器（Phase 2，支持 AI 摘要）"""

from vbiji.core.types import Document
from vbiji.core.ai.providers.base import BaseProvider, ChatMessage


DEFAULT_SUMMARIZE_PROMPT = """请对以下文档内容进行简要摘要，提取关键信息和核心观点，控制在 200 字以内：

---
{content}
---"""


def summarize_with_ai(
    doc: Document,
    llm_config,
    provider: BaseProvider,
) -> str:
    """使用 AI 生成摘要

    Args:
        doc: Document 对象
        llm_config: LLM 配置
        provider: AI Provider 实例（由调用方注入，支持 deepseek / minimax / kimi 等）

    Returns:
        str: AI 生成的摘要
    """
    messages = [
        ChatMessage(
            role="user",
            content=DEFAULT_SUMMARIZE_PROMPT.format(content=doc.content[:8000])
        )
    ]
    return provider.chat(messages, llm_config)


def summarize_local(doc: Document, lines: int = 5) -> str:
    """本地摘要：取内容前 N 行作为摘要（Phase 1）

    使用简单的抽取式摘要方法，取内容开头的非空行作为摘要。
    当没有配置 AI 时作为 fallback 使用。

    Args:
        doc: Document 对象
        lines: 摘要行数，默认 5

    Returns:
        str: 摘要文本
    """
    content_lines = doc.content.split("\n")
    content_lines = [line.strip() for line in content_lines if line.strip()]
    summary_lines = content_lines[:lines]
    return "\n".join(summary_lines)