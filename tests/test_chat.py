"""测试 AI Chat 封装（AiChat）"""

import pytest
from unittest.mock import MagicMock, AsyncMock
from vbiji.core.ai.chat import AiChat, _truncate_context
from vbiji.core.ai.providers.base import LlmConfig, ChatMessage, BaseProvider


class FakeProvider(BaseProvider):
    """测试用 Fake Provider"""

    provider_name = "fake"
    default_base_url = "https://fake.api"
    chat_endpoint = "/chat"
    default_model = "fake-model"
    context_limit = 100  # 设为很小方便测试截断

    def chat(self, messages: list[ChatMessage], config: LlmConfig) -> str:
        return "fake response"

    async def chat_stream(self, messages: list[ChatMessage], config: LlmConfig):
        for token in ["f", "a", "k", "e"]:
            yield token


@pytest.fixture
def fake_provider():
    return FakeProvider()


@pytest.fixture
def llm_config():
    return LlmConfig(
        name="test",
        provider="fake",
        model="fake-model",
        api_key="test-key",
        options={},
    )


class TestTruncateContext:
    """_truncate_context 辅助函数测试"""

    def test_under_limit(self, fake_provider, llm_config):
        """未超限不截断"""
        text = "短文本"
        result, orig, cut = _truncate_context(text, fake_provider, llm_config)
        assert result == text
        assert cut == 0

    def test_over_limit_truncates(self, fake_provider, llm_config):
        """超限后截断"""
        text = "中" * 500  # 约 250 tokens，超过 context_limit=100
        result, orig, cut = _truncate_context(text, fake_provider, llm_config)
        assert cut > 0
        # 截断后 token 数 <= 100
        from vbiji.core.ai.providers.base import estimate_tokens
        assert estimate_tokens(result) <= 100

    def test_custom_max_context_tokens(self, fake_provider):
        """通过 config.options 自定义上限"""
        config = LlmConfig(
            name="test",
            provider="fake",
            model="fake-model",
            api_key="test-key",
            options={"max_context_tokens": 5},
        )
        text = "中" * 100  # 约 50 tokens，超过自定义的 5
        result, orig, cut = _truncate_context(text, fake_provider, config)
        assert cut > 0


class TestAiChatAsk:
    """AiChat.ask() 测试"""

    def test_ask_without_context(self, fake_provider, llm_config):
        """无 context 时直接发送 prompt"""
        chat = AiChat(fake_provider, llm_config)
        result = chat.ask("你好")
        assert result == "fake response"

    def test_ask_with_context(self, fake_provider, llm_config):
        """有 context 时组合 prompt"""
        chat = AiChat(fake_provider, llm_config)
        result = chat.ask("请摘要", context="文件内容")
        assert result == "fake response"

    def test_ask_with_system_prompt(self, fake_provider, llm_config):
        """系统提示词"""
        chat = AiChat(fake_provider, llm_config)
        result = chat.ask("问题", system_prompt="你是一个助手")
        assert result == "fake response"


class TestAiChatAskStream:
    """AiChat.ask_stream() 测试"""

    @pytest.mark.asyncio
    async def test_stream_returns_tokens(self, fake_provider, llm_config):
        """流式输出每个 token"""
        chat = AiChat(fake_provider, llm_config)
        tokens = []
        async for token in chat.ask_stream("你好"):
            tokens.append(token)
        assert tokens == ["f", "a", "k", "e"]

    @pytest.mark.asyncio
    async def test_stream_with_context(self, fake_provider, llm_config):
        """流式带 context"""
        chat = AiChat(fake_provider, llm_config)
        tokens = []
        async for token in chat.ask_stream("请摘要", context="文件内容"):
            tokens.append(token)
        assert tokens == ["f", "a", "k", "e"]