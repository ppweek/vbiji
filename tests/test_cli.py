"""测试 CLI 命令（end-to-end）"""

import pytest
from typer.testing import CliRunner
from vbiji.cli import app

runner = CliRunner()


class TestCliHelp:
    """CLI --help 测试"""

    def test_main_help(self):
        """主命令 --help 正常输出"""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "Vbiji" in result.stdout
        assert "read" in result.stdout
        assert "ask" in result.stdout
        assert "batch" in result.stdout

    def test_read_help(self):
        """read --help"""
        result = runner.invoke(app, ["read", "--help"])
        assert result.exit_code == 0

    def test_ask_help(self):
        """ask --help"""
        result = runner.invoke(app, ["ask", "--help"])
        assert result.exit_code == 0
        assert "--prompt" in result.stdout
        assert "--save" in result.stdout
        assert "--save-as" in result.stdout

    def test_batch_help(self):
        """batch --help"""
        result = runner.invoke(app, ["batch", "--help"])
        assert result.exit_code == 0
        assert "--to" in result.stdout
        assert "--prompt" in result.stdout
        assert "--llm" in result.stdout

    def test_llm_add_help(self):
        """llm-add --help"""
        result = runner.invoke(app, ["llm-add", "--help"])
        assert result.exit_code == 0
        assert "--max-tokens" in result.stdout

    def test_prompt_help(self):
        """prompt-* 系列 --help"""
        for cmd in ["prompt-add", "prompt-list", "prompt-del", "prompt-show"]:
            result = runner.invoke(app, [cmd, "--help"])
            assert result.exit_code == 0, f"{cmd} --help failed"


class TestCliNoArgs:
    """无参数调用行为"""

    def test_no_args_shows_help(self):
        """不传参数时显示帮助"""
        result = runner.invoke(app, [])
        assert result.exit_code != 0


class TestConvertCommand:
    """convert 命令测试"""

    def test_convert_requires_to_option(self):
        """convert 必须指定 --to"""
        result = runner.invoke(app, ["convert", "./nonexistent.pdf"])
        assert result.exit_code == 2
        assert "Missing option" in result.stderr

    def test_convert_nonexistent_file(self, tmp_path):
        """转换不存在的文件报错"""
        result = runner.invoke(app, ["convert", str(tmp_path / "none.pdf"), "--to", "md"])
        assert result.exit_code == 1
        # Typer 将异常存在 exception 属性中
        assert result.exception is not None
        assert "不存在" in str(result.exception)


class TestPromptCommands:
    """prompt-* 系列命令测试"""

    def test_prompt_add_and_show(self):
        """prompt-add -> prompt-show 生命周期"""
        title = "测试提示词"
        content = "这是测试内容"

        # 添加
        result = runner.invoke(app, [
            "prompt-add",
            "-t", title,
            "-c", content,
            "--description", "测试描述",
        ])
        assert result.exit_code == 0
        assert "已添加" in result.stdout

        # 列出
        result = runner.invoke(app, ["prompt-list"])
        assert result.exit_code == 0
        assert title in result.stdout

        # 读取
        result = runner.invoke(app, ["prompt-show", "-t", title])
        assert result.exit_code == 0
        assert content in result.stdout

        # 编辑
        result = runner.invoke(app, [
            "prompt-edit", "-t", title, "-c", "修改后的内容"
        ])
        assert result.exit_code == 0

        # 删除
        result = runner.invoke(app, ["prompt-del", "-t", title])
        assert result.exit_code == 0
        assert "已删除" in result.stdout


class TestLlmCommands:
    """llm-* 系列命令测试"""

    def test_llm_add_and_list(self):
        """llm-add -> llm-list 生命周期"""
        result = runner.invoke(app, [
            "llm-add",
            "-n", "test-llm-cmd",
            "--provider", "deepseek",
            "--apikey", "sk-test-cmd",
            "--model", "deepseek-chat",
            "--max-tokens", "0",
        ])
        assert result.exit_code == 0
        assert "已添加" in result.stdout

        # 列出
        result = runner.invoke(app, ["llm-list"])
        assert result.exit_code == 0
        assert "test-llm-cmd" in result.stdout

        # 删除
        result = runner.invoke(app, ["llm-del", "-n", "test-llm-cmd"])
        assert result.exit_code == 0
        assert "已删除" in result.stdout


class TestAskCommand:
    """ask 命令参数验证"""

    def test_ask_requires_file(self):
        """ask 必须提供文件路径"""
        result = runner.invoke(app, ["ask"])
        assert result.exit_code == 2

    def test_ask_prompt_and_file(self, tmp_path):
        """ask 需要 prompt 或 --prompt"""
        result = runner.invoke(app, ["ask", str(tmp_path / "f.pdf")])
        assert result.exit_code == 1
        assert "必须提供" in result.stdout

    def test_ask_with_prompt_text(self, tmp_path):
        """ask 传了 prompt 但文件不存在（验证参数解析）"""
        # 文件不存在，但参数解析成功（会在读取阶段报错）
        result = runner.invoke(app, [
            "ask",
            str(tmp_path / "none.pdf"),
            "请摘要",
        ])
        assert result.exit_code == 1
        assert "不存在" in result.stdout or "读取文件失败" in result.stdout

    def test_ask_with_prompt_name_not_found(self, tmp_path):
        """ask --prompt 找不到提示词"""
        result = runner.invoke(app, [
            "ask",
            str(tmp_path / "none.pdf"),
            "--prompt", "不存在的提示词",
        ])
        assert result.exit_code == 1
        assert "未找到提示词" in result.stdout