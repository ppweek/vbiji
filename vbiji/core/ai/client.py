"""统一的 AI 客户端"""

from .providers.base import LlmConfig, ChatMessage
from .providers.deepseek import DeepSeekProvider
from .providers.minimax import MiniMaxProvider
from .providers.kimi import KimiProvider
from .providers.bigmodel import BigModelProvider
from .providers.qwen import QwenProvider
from .chat import AiChat


class AiClient:
    """统一的 AI 客户端"""

    def __init__(self):
        """初始化 AI 客户端"""
        self._providers: dict[str, type] = {}
        self._register_default_providers()

    def _register_default_providers(self):
        """注册默认的 Providers"""
        self._providers["deepseek"] = DeepSeekProvider
        self._providers["minimax"] = MiniMaxProvider
        self._providers["kimi"] = KimiProvider
        self._providers["bigmodel"] = BigModelProvider
        self._providers["qwen"] = QwenProvider

    def create_chat(self, config: LlmConfig) -> AiChat:
        """创建对话实例

        Args:
            config: LLM 配置

        Returns:
            AiChat 实例

        Raises:
            ValueError: 不支持的 Provider
        """
        provider_cls = self._providers.get(config.provider)
        if not provider_cls:
            raise ValueError(f"不支持的 Provider: {config.provider}")
        return AiChat(provider_cls(), config)


# 全局客户端（单例）
ai_client = AiClient()