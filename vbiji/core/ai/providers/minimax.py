"""MiniMax 模型 Provider

MiniMax 开放平台（platform.minimaxi.com）使用 OpenAI 兼容格式。
- Base URL：https://api.minimaxi.com
- 端点：/v1/text/chatcompletion_v2
- 认证：Authorization: Bearer <api_key>
- 模型：MiniMax-M2（需在套餐中开启）
"""

import httpx
import json
from typing import AsyncIterator

from .base import BaseProvider, ChatMessage, LlmConfig


class MiniMaxProvider(BaseProvider):
    """MiniMax 模型 Provider（OpenAI 兼容格式）"""

    provider_name = "minimax"
    default_base_url = "https://api.minimaxi.com"
    chat_endpoint = "/v1/text/chatcompletion_v2"
    default_model = "MiniMax-M2.7"
    context_limit = 200_000  # tokens

    def _model_id(self, config: LlmConfig) -> str:
        return config.model or self.default_model

    def _build_payload(self, config: LlmConfig, messages: list[ChatMessage], stream: bool = False) -> dict:
        payload = {
            "model": self._model_id(config),
            "messages": [{"role": m.role, "content": m.content} for m in messages],
        }
        if stream:
            payload["stream"] = True
        options = self.build_payload_options(config)
        payload.update(options)
        return payload

    def chat(self, messages: list[ChatMessage], config: LlmConfig) -> str:
        """同步调用 MiniMax API（OpenAI 兼容格式）"""
        payload = self._build_payload(config, messages)

        with httpx.Client(timeout=300.0) as client:
            response = client.post(
                self.build_url(config),
                headers=self.build_headers(config),
                json=payload,
            )
            data = response.json()
            # 检查业务错误
            if "base_resp" in data:
                code = data["base_resp"].get("status_code", 0)
                if code != 0:
                    msg = data["base_resp"].get("status_msg", "unknown error")
                    raise RuntimeError(f"MiniMax API 错误 (code={code}): {msg}")
            # 提取回复内容
            choices = data.get("choices", [])
            if not choices:
                raise RuntimeError(f"MiniMax API 无返回内容: {data}")
            return choices[0]["message"]["content"]

    async def chat_stream(
        self, messages: list[ChatMessage], config: LlmConfig
    ) -> AsyncIterator[str]:
        """流式调用"""
        payload = self._build_payload(config, messages, stream=True)

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
                        try:
                            data = json.loads(line[6:])
                            if "base_resp" in data:
                                code = data["base_resp"].get("status_code", 0)
                                if code != 0:
                                    msg = data["base_resp"].get("status_msg", "unknown error")
                                    raise RuntimeError(f"MiniMax stream error (code={code}): {msg}")
                            delta = data.get("choices", [{}])[0].get("delta", {}).get("content", "")
                            if delta:
                                yield delta
                        except json.JSONDecodeError:
                            pass
