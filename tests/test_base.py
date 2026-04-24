"""测试 token 估算和截断工具函数"""

import pytest
from vbiji.core.ai.providers.base import estimate_tokens, truncate_to_token_limit


class TestEstimateTokens:
    """estimate_tokens 函数测试"""

    def test_pure_english(self):
        """纯英文按 4 字符/Token"""
        assert estimate_tokens("hello world") == 3  # 11 chars / 4 ≈ 3

    def test_pure_chinese(self):
        """纯中文按 2 字符/Token"""
        assert estimate_tokens("你好世界") == 2  # 4 chars / 2 = 2

    def test_mixed_text(self):
        """中英混合文本"""
        text = "Hello你好World世界"  # 5 non-chinese + 4 chinese = 9 non-chinese
        result = estimate_tokens(text)
        # 4 chinese / 2 + 9 non-chinese / 4 = 2 + 2.25 = 4.25 → round = 4
        assert result == 4

    def test_empty_string(self):
        """空字符串返回 0"""
        assert estimate_tokens("") == 0

    def test_numbers_and_symbols(self):
        """数字和符号算作非中文字符"""
        assert estimate_tokens("12345678") == 2  # 8/4 = 2

    def test_long_chinese_text(self):
        """长中文文本"""
        long_text = "中" * 1000
        assert estimate_tokens(long_text) == 500


class TestTruncateToTokenLimit:
    """truncate_to_token_limit 函数测试"""

    def test_under_limit_returns_original(self):
        """未超过上限返回原文"""
        text = "你好"
        result, orig, cut = truncate_to_token_limit(text, 10)
        assert result == text
        assert orig == 1
        assert cut == 0

    def test_exact_limit(self):
        """恰好等于上限"""
        text = "中" * 100
        result, orig, cut = truncate_to_token_limit(text, 50)
        assert orig == 50
        assert cut == 0

    def test_over_limit_truncates(self):
        """超过上限时截断"""
        text = "中" * 1000
        result, orig, cut = truncate_to_token_limit(text, 100)
        assert orig == 500
        assert cut == 400
        # 截断后 token 数应该 <= limit
        assert estimate_tokens(result) <= 100

    def test_mixed_text_truncation(self):
        """混合文本截断"""
        text = "hello你好world你好" * 50
        result, orig, cut = truncate_to_token_limit(text, 50)
        # 截断后 token 数 <= 50
        assert estimate_tokens(result) <= 50

    def test_very_small_limit(self):
        """极小上限"""
        text = "中" * 100
        result, orig, cut = truncate_to_token_limit(text, 1)
        assert orig == 50
        assert cut == 49

    def test_preserves_ending(self):
        """截断保留文本开头，删掉末尾超量部分"""
        text = "文本" * 50
        truncated, _, _ = truncate_to_token_limit(text, 10)
        # 截断从末尾删（保留开头），所以开头应该保留
        assert truncated.startswith("文本文本")
        # 末尾部分被截掉，所以不一定以"文本"结尾
        assert len(truncated) < len(text)