"""AI Provider 抽象基类"""

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import AsyncIterator


@dataclass
class LlmConfig:
    """LLM 配置"""
    name: str           # 配置名称，如 "deepseek-chat"
    provider: str       # provider 标识：deepseek / minimax / kimi / bigmodel / qwen
    model: str          # 模型 ID
    api_key: str        # API Key
    base_url: str = ""  # 自定义 API 端点（可选）
    options: dict = field(default_factory=dict)  # temperature / max_tokens 等


@dataclass
class ChatMessage:
    """聊天消息"""
    role: str     # system / user / assistant
    content: str


def estimate_tokens(text: str) -> int:
    """估算文本的 token 数量（粗略估计）

    中文 ≈ 2 字符/Token，英文/数字 ≈ 4 字符/Token。
    适用于大多数中文为主的文档场景。

    Args:
        text: 输入文本

    Returns:
        估算的 token 数
    """
    chinese = len(re.findall(r"[\u4e00-\u9fff]", text))
    non_chinese = len(text) - chinese
    return round(chinese / 2 + non_chinese / 4)


def truncate_to_token_limit(text: str, limit: int) -> tuple[str, int, int]:
    """截断文本使其 token 数不超过上限（从末尾往前截）

    Args:
        text: 输入文本
        limit: token 上限

    Returns:
        (截断后文本, 原始token数, 截断掉的token数)
    """
    original = estimate_tokens(text)
    if original <= limit:
        return text, original, 0

    # 按字符数估算：limit tokens 对应的字符数
    # 先按中文场景估算（保守），再做二分逼近
    target_chars = limit * 2  # 假设全是中文
    truncated = text[:target_chars]

    # 二分逼近，找到恰好不超过 limit 的最大截断点
    low, high = 0, len(text)
    while low < high:
        mid = (low + high + 1) // 2
        if estimate_tokens(text[:mid]) <= limit:
            low = mid
        else:
            high = mid - 1

    truncated = text[:low]
    remaining = estimate_tokens(truncated)
    return truncated, original, original - remaining


class BaseProvider(ABC):
    """AI Provider 抽象基类"""

    provider_name: str = ""  # 子类覆盖
    default_base_url: str = ""  # 子类覆盖
    chat_endpoint: str = "/chat/completions"  # 子类可覆盖
    default_model: str = ""  # 子类覆盖
    context_limit: int = 64_000  # 输入 token 上限，子类覆盖

    def build_payload_options(self, config: LlmConfig) -> dict:
        """构造 API payload 的 options，过滤掉 max_tokens=0（表示不限制）"""
        options = dict(config.options)
        if options.get("max_tokens") == 0:
            options.pop("max_tokens", None)
        return options

    @abstractmethod
    def chat(self, messages: list[ChatMessage], config: LlmConfig) -> str:
        """同步聊天，返回完整响应文本"""
        ...

    @abstractmethod
    def chat_stream(
        self, messages: list[ChatMessage], config: LlmConfig
    ) -> AsyncIterator[str]:
        """流式聊天，yield 每个 token"""
        ...

    def build_url(self, config: LlmConfig) -> str:
        """构造 API URL"""
        base = config.base_url or self.default_base_url
        return f"{base.rstrip('/')}{self.chat_endpoint}"

    def build_headers(self, config: LlmConfig) -> dict:
        """构造 HTTP 请求头"""
        return {
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "application/json",
        }