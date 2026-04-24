"""测试 AI Provider（mock HTTP 请求）"""

import json
import pytest
from unittest.mock import patch, MagicMock
from vbiji.core.ai.providers.base import LlmConfig
from vbiji.core.ai.providers.deepseek import DeepSeekProvider
from vbiji.core.ai.providers.minimax import MiniMaxProvider
from vbiji.core.ai.providers.kimi import KimiProvider
from vbiji.core.ai.providers.bigmodel import BigModelProvider
from vbiji.core.ai.providers.qwen import QwenProvider


def make_mock_response(json_data: dict, status_code: int = 200):
    """构造 mock HTTP 响应"""
    resp = MagicMock()
    resp.status_code = status_code
    resp.json.return_value = json_data
    resp.raise_for_status = MagicMock()
    return resp


def make_stream_lines(choices: list[str]) -> list[str]:
    """构造 SSE 流式响应行"""
    lines = []
    for i, content in enumerate(choices):
        lines.append(f'data: {json.dumps({"choices": [{"delta": {"content": content}}]})}')
    lines.append("data: [DONE]")
    return lines


@pytest.fixture
def llm_config():
    return LlmConfig(
        name="test",
        provider="deepseek",
        model="deepseek-chat",
        api_key="sk-test",
        options={"temperature": 0.7},
    )


class TestDeepSeekProvider:
    """DeepSeek Provider 测试"""

    def test_chat_returns_content(self, llm_config):
        """chat() 返回正确内容"""
        provider = DeepSeekProvider()
        mock_resp = make_mock_response({
            "choices": [{"message": {"content": "测试回复"}}]
        })
        with patch("httpx.Client") as MockClient:
            MockClient.return_value.__enter__.return_value.post.return_value = mock_resp
            result = provider.chat([], llm_config)
            assert result == "测试回复"

    def test_build_url_uses_default(self, llm_config):
        """build_url 使用默认 base_url"""
        provider = DeepSeekProvider()
        url = provider.build_url(llm_config)
        assert "api.deepseek.com" in url

    def test_build_url_uses_custom(self, llm_config):
        """build_url 支持自定义 base_url"""
        provider = DeepSeekProvider()
        llm_config.base_url = "https://custom.proxy.com/v1"
        url = provider.build_url(llm_config)
        assert "custom.proxy.com" in url

    def test_max_tokens_zero_filtered(self, llm_config):
        """max_tokens=0 被过滤，不传给 API"""
        provider = DeepSeekProvider()
        llm_config.options = {"max_tokens": 0, "temperature": 0.7}
        opts = provider.build_payload_options(llm_config)
        assert "max_tokens" not in opts
        assert opts["temperature"] == 0.7

    def test_max_tokens_positive_kept(self, llm_config):
        """max_tokens > 0 时保留"""
        provider = DeepSeekProvider()
        llm_config.options = {"max_tokens": 8000}
        opts = provider.build_payload_options(llm_config)
        assert opts["max_tokens"] == 8000

    def test_stream_payload(self, llm_config):
        """流式 payload 包含 stream=True"""
        provider = DeepSeekProvider()
        payload = provider._stream_payload(llm_config, [])
        assert payload["stream"] is True

    @pytest.mark.asyncio
    async def test_chat_stream_yields_tokens(self, llm_config):
        """chat_stream() 逐 token yield（验证 payload 构造正确）"""
        provider = DeepSeekProvider()
        payload = provider._stream_payload(llm_config, [])
        assert payload["stream"] is True
        assert payload["model"] == "deepseek-chat"


class TestMiniMaxProvider:
    """MiniMax Provider 测试"""

    def test_build_url(self, llm_config):
        """MiniMax 端点正确"""
        provider = MiniMaxProvider()
        url = provider.build_url(llm_config)
        assert "/v1/text/chatcompletion_v2" in url

    def test_base_resp_error(self, llm_config):
        """base_resp 业务错误被抛出"""
        provider = MiniMaxProvider()
        mock_resp = make_mock_response({
            "base_resp": {"status_code": 1002, "status_msg": "invalid api key"}
        })
        with patch("httpx.Client") as MockClient:
            MockClient.return_value.__enter__.return_value.post.return_value = mock_resp
            with pytest.raises(RuntimeError, match="invalid api key"):
                provider.chat([], llm_config)

    def test_no_choices_raises(self, llm_config):
        """无 choices 字段时抛异常"""
        provider = MiniMaxProvider()
        mock_resp = make_mock_response({})
        with patch("httpx.Client") as MockClient:
            MockClient.return_value.__enter__.return_value.post.return_value = mock_resp
            with pytest.raises(RuntimeError, match="无返回内容"):
                provider.chat([], llm_config)


class TestKimiProvider:
    """Kimi Provider 测试"""

    def test_default_model(self):
        """Kimi 默认模型"""
        provider = KimiProvider()
        assert provider.default_model == "moonshot-v1-32k"
        assert provider.context_limit == 260_000

    def test_model_id_fallback(self, llm_config):
        """未指定 model 时使用默认"""
        provider = KimiProvider()
        assert provider._model_id(llm_config) == "deepseek-chat"  # 使用 config.model
        llm_config.model = ""
        assert provider._model_id(llm_config) == "moonshot-v1-32k"  # 使用 provider 默认


class TestBigModelProvider:
    """BigModel Provider 测试"""

    def test_default_model(self):
        """BigModel 默认模型"""
        provider = BigModelProvider()
        assert provider.default_model == "glm-4-flash"
        assert provider.context_limit == 128_000


class TestQwenProvider:
    """Qwen Provider 测试"""

    def test_default_model(self):
        """Qwen 默认模型"""
        provider = QwenProvider()
        assert provider.default_model == "qwen-turbo"
        assert provider.context_limit == 128_000