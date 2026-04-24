"""DeepSeek 模型 Provider"""

import httpx
import json
from typing import AsyncIterator

from .base import BaseProvider, ChatMessage, LlmConfig


class DeepSeekProvider(BaseProvider):
    """DeepSeek 模型 Provider"""

    provider_name = "deepseek"
    default_base_url = "https://api.deepseek.com/v1"
    chat_endpoint = "/chat/completions"
    default_model = "deepseek-v4-flash"  # 1M token 输入上限
    context_limit = 1_000_000  # tokens

    def _model_id(self, config: LlmConfig) -> str:
        return config.model or self.default_model

    def chat(self, messages: list[ChatMessage], config: LlmConfig) -> str:
        """同步调用 DeepSeek API"""
        payload = {
            "model": self._model_id(config),
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            **self.build_payload_options(config),
        }

        with httpx.Client(timeout=300.0) as client:
            response = client.post(
                self.build_url(config),
                headers=self.build_headers(config),
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]

    def _stream_payload(self, config: LlmConfig, messages: list[ChatMessage]) -> dict:
        return {
            "model": self._model_id(config),
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "stream": True,
            **self.build_payload_options(config),
        }

    async def chat_stream(
        self, messages: list[ChatMessage], config: LlmConfig
    ) -> AsyncIterator[str]:
        """流式调用"""

        payload = self._stream_payload(config, messages)

        async with httpx.AsyncClient(timeout=300.0) as client:
            async with client.stream(
                "POST",
                self.build_url(config),
                headers=self.build_headers(config),
                json=payload,
            ) as response:
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        if line == "data: [DONE]":
                            break
                        data = json.loads(line[6:])
                        delta = data["choices"][0]["delta"].get("content", "")
                        if delta:
                            yield delta