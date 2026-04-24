"""通义千问 Provider"""

import httpx
import json
from typing import AsyncIterator

from .base import BaseProvider, ChatMessage, LlmConfig


class QwenProvider(BaseProvider):
    """通义千问 Provider"""

    provider_name = "qwen"
    default_base_url = "https://dashscope.aliyuncs.com/api/v1"
    chat_endpoint = "/chat/completions"
    default_model = "qwen-turbo"
    context_limit = 128_000  # qwen-turbo 上限，可按需覆盖

    def _model_id(self, config: LlmConfig) -> str:
        return config.model or self.default_model

    def chat(self, messages: list[ChatMessage], config: LlmConfig) -> str:
        """同步调用通义千问 API"""
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

    async def chat_stream(
        self, messages: list[ChatMessage], config: LlmConfig
    ) -> AsyncIterator[str]:
        """流式调用"""
        payload = {
            "model": self._model_id(config),
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "stream": True,
            **self.build_payload_options(config),
        }

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