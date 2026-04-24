"""AI 对话封装"""

from typing import AsyncIterator

from .providers.base import LlmConfig, ChatMessage, BaseProvider, estimate_tokens, truncate_to_token_limit


def _truncate_context(context: str, provider: BaseProvider, config: LlmConfig) -> tuple[str, int, int]:
    """截断 context 使其不超过 provider 的 token 上限"""
    limit = config.options.get("max_context_tokens") or provider.context_limit
    return truncate_to_token_limit(context, limit)


class AiChat:
    """AI 对话封装"""

    def __init__(self, provider: BaseProvider, config: LlmConfig):
        """初始化 AI 对话

        Args:
            provider: AI Provider 实例
            config: LLM 配置
        """
        self.provider = provider
        self.config = config

    def ask(
        self,
        prompt: str,
        context: str = "",
        system_prompt: str = "",
    ) -> str:
        """同步问答

        Args:
            prompt: 用户问题
            context: 文件内容上下文
            system_prompt: 系统提示词

        Returns:
            AI 响应文本
        """
        messages = []
        if system_prompt:
            messages.append(ChatMessage(role="system", content=system_prompt))

        if context:
            # 自动截断
            truncated, orig, cut = _truncate_context(context, self.provider, self.config)
            if cut > 0:
                # 提示词也要加上
                prompt_with_ctx = f"{prompt}\n\n【文件内容（已截断，原 {orig} tokens → {orig - cut} tokens）】\n{truncated}"
            else:
                prompt_with_ctx = f"{prompt}\n\n【文件内容】\n{context}"
            messages.append(ChatMessage(role="user", content=prompt_with_ctx))
        else:
            messages.append(ChatMessage(role="user", content=prompt))

        return self.provider.chat(messages, self.config)

    async def ask_stream(
        self,
        prompt: str,
        context: str = "",
        system_prompt: str = "",
    ) -> AsyncIterator[str]:
        """流式问答

        Args:
            prompt: 用户问题
            context: 文件内容上下文
            system_prompt: 系统提示词

        Yields:
            每个 token
        """
        messages = []
        if system_prompt:
            messages.append(ChatMessage(role="system", content=system_prompt))

        if context:
            truncated, orig, cut = _truncate_context(context, self.provider, self.config)
            if cut > 0:
                prompt_with_ctx = f"{prompt}\n\n【文件内容（已截断，原 {orig} tokens → {orig - cut} tokens）】\n{truncated}"
            else:
                prompt_with_ctx = f"{prompt}\n\n【文件内容】\n{context}"
            messages.append(ChatMessage(role="user", content=prompt_with_ctx))
        else:
            messages.append(ChatMessage(role="user", content=prompt))

        async for token in self.provider.chat_stream(messages, self.config):
            yield token