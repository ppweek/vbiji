"""Vbiji CLI 命令行接口

Vbiji - 与 AI 一起协作的知识库

使用方法:
  vbiji <命令> [选项]

文件处理:
  vbiji read <文件路径>                      读取文件内容
  vbiji summarize <文件路径>                 摘要文件内容
  vbiji convert <文件路径> --to <格式>      格式转换

LLM 配置:
  vbiji llm-add -n <名称> --provider <提供商> --apikey <密钥>
  vbiji llm-list                           列出所有 LLM 配置
  vbiji llm-del -n <名称>                   删除 LLM 配置

Prompt 管理:
  vbiji prompt-add -t <标题> -c <内容>     新增提示词
  vbiji prompt-import <文件路径>            从 MD 文件导入提示词
  vbiji prompt-edit -t <标题> -c <内容>    修改提示词
  vbiji prompt-show -t <标题>               查看提示词
  vbiji prompt-del -t <标题>                删除提示词
  vbiji prompt-list                         列出所有提示词

AI 问答:
  vbiji ask <文件路径> <提示词> --llm <配置名> [--save] [--save-as <路径>]
  vbiji ask <文件路径> --prompt <提示词标题> --llm <配置名>  使用已配置的提示词

批量处理:
  vbiji batch --to <md|json|txt> --prompt <提示词标题> --llm <配置名>  批量处理当前目录文件

详细帮助: vbiji <命令> --help
"""

import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(help="Vbiji - 与 AI 一起协作的知识库 CLI 工具", no_args_is_help=True)
console = Console()


@app.command()
def read(
    filepath: str = typer.Argument(..., help="文件路径，支持 pdf/md/txt/docx"),
    page: bool = typer.Option(False, "-p", help="分页展示"),
) -> None:
    """读取文件内容

    用法: vbiji read <文件路径> [-p]

    示例:
      vbiji read ./report.pdf       直接读取
      vbiji read ./notes.md -p     分页展示
    """
    from vbiji.core.reader import registry

    doc = registry.read(filepath)
    console.print(f"[bold blue]📄 {doc.title}[/bold blue]")
    console.print(doc.content)


@app.command()
def summarize(
    filepath: str = typer.Argument(..., help="文件路径"),
    lines: int = typer.Option(5, "--lines", help="摘要行数，默认 5"),
) -> None:
    """摘要文件内容（本地 extractive summary，取内容前 N 行）

    用法: vbiji summarize <文件路径> [--lines N]

    示例:
      vbiji summarize ./report.pdf            默认取 5 行
      vbiji summarize ./report.pdf --lines 10  取 10 行
    """
    from vbiji.core.reader import registry
    from vbiji.core.summarizer import summarize_local

    doc = registry.read(filepath)
    summary = summarize_local(doc, lines=lines)
    console.print("[bold green]📋 摘要：[/bold green]")
    console.print(summary)


@app.command()
def convert(
    filepath: str = typer.Argument(..., help="文件路径"),
    to_format: str = typer.Option(..., "--to", help="目标格式：md | json | txt"),
) -> None:
    """格式转换，将文件转为指定格式并保存到同目录

    用法: vbiji convert <文件路径> --to <md|json|txt>

    示例:
      vbiji convert ./report.pdf --to md     → report.md
      vbiji convert ./report.pdf --to json   → report.json
      vbiji convert ./report.pdf --to txt     → report.txt
    """
    from vbiji.core.reader import registry
    from vbiji.core.converter import convert_to_markdown, convert_to_json

    doc = registry.read(filepath)

    if to_format == "md":
        content = convert_to_markdown(doc)
        output_path = Path(filepath).with_suffix(".md")
    elif to_format == "json":
        content = convert_to_json(doc)
        output_path = Path(filepath).with_suffix(".json")
    elif to_format == "txt":
        content = doc.content
        output_path = Path(filepath).with_suffix(".txt")
    else:
        console.print(f"[red]不支持的格式: {to_format}，支持 md / json / txt[/red]")
        raise typer.Exit(1)

    output_path.write_text(content, encoding="utf-8")
    console.print(f"[green]✅ 已保存到: {output_path}[/green]")


# ===== LLM 配置命令 =====

@app.command()
def llm_add(
    name: str = typer.Option(..., "-n", "--name", help="配置名称（唯一标识）"),
    provider: str = typer.Option(..., "--provider", help="Provider: deepseek | minimax | kimi | bigmodel | qwen"),
    api_key: str = typer.Option(..., "--apikey", help="API Key"),
    model: str = typer.Option("", "--model", help="模型 ID（可选，不填用默认值）"),
    base_url: str = typer.Option("", "--base-url", help="自定义 API 端点（可选）"),
    max_tokens: int = typer.Option(0, "--max-tokens", help="最大输出 token 数（默认 0 表示不限制）"),
) -> None:
    """新增 LLM 配置

    用法: vbiji llm-add -n <名称> --provider <提供商> --apikey <密钥> [--model <模型>] [--max-tokens <数值>]

    示例:
      vbiji llm-add -n deepseek --provider deepseek --apikey sk-xxx
      vbiji llm-add -n minimax --provider minimax --apikey sk-xxx --model MiniMax-M2.7
    """
    from vbiji.core.llm.manager import LlmManager
    manager = LlmManager()
    try:
        config = manager.add(name=name, provider=provider, api_key=api_key, model=model, base_url=base_url, max_tokens=max_tokens)
        console.print(f"[green]✅ 已添加 LLM 配置: {config.name}[/green]")
        console.print(f"[dim]  Provider: {config.provider}  模型: {config.model or '(默认)'}[/dim]")
    except ValueError as e:
        console.print(f"[red]❌ {e}[/red]")
        raise typer.Exit(1)


@app.command(name="llm-list")
def llm_list() -> None:
    """列出所有已配置的 LLM

    用法: vbiji llm-list
    """
    from vbiji.core.llm.manager import LlmManager
    manager = LlmManager()
    configs = manager.list_all()
    if not configs:
        console.print("[yellow]暂无 LLM 配置，请使用 vbiji llm-add 添加[/yellow]")
        return
    table = Table(title="已配置的 LLM")
    table.add_column("名称", style="cyan")
    table.add_column("Provider")
    table.add_column("模型")
    for cfg in configs:
        table.add_row(cfg.name, cfg.provider, cfg.model or "(默认)")
    console.print(table)


@app.command(name="llm-del")
def llm_del(
    name: str = typer.Option(..., "-n", "--name", help="配置名称"),
) -> None:
    """删除 LLM 配置

    用法: vbiji llm-del -n <名称>
    """
    from vbiji.core.llm.manager import LlmManager
    manager = LlmManager()
    try:
        manager.delete(name)
        console.print(f"[green]✅ 已删除 LLM 配置: {name}[/green]")
    except ValueError as e:
        console.print(f"[red]❌ {e}[/red]")
        raise typer.Exit(1)


# ===== Prompt 管理命令 =====

@app.command(name="prompt-add")
def prompt_add(
    title: str = typer.Option(..., "-t", "--title", help="提示词标题（唯一标识）"),
    content: str = typer.Option(..., "-c", "--content", help="提示词内容"),
    description: str = typer.Option("", "--description", help="描述（可选）"),
) -> None:
    """新增提示词

    用法: vbiji prompt-add -t <标题> -c <内容> [--description <描述>]

    示例:
      vbiji prompt-add -t summarize -c "请摘要以下内容，提取关键信息：" --description "文档摘要"
    """
    from vbiji.core.prompt.manager import PromptManager

    manager = PromptManager()
    try:
        prompt = manager.add(title=title, content=content, description=description)
        console.print(f"[green]✅ 已添加提示词: {prompt.title}[/green]")
    except ValueError as e:
        console.print(f"[red]❌ {e}[/red]")
        raise typer.Exit(1)


@app.command(name="prompt-import")
def prompt_import(
    filepath: str = typer.Argument(..., help="MD 文件路径"),
) -> None:
    """从 MD 文件导入提示词（文件名作为标题，文件全部内容作为内容）

    用法: vbiji prompt-import <文件路径>

    示例:
      vbiji prompt-import ./提示词/财报分析.md
      vbiji prompt-import "./路径/含空格的文件.md"
    """
    from vbiji.core.prompt.manager import PromptManager

    manager = PromptManager()
    try:
        prompt = manager.import_from_file(filepath)
        console.print(f"[green]✅ 已导入提示词: {prompt.title}[/green]")
    except (ValueError, FileNotFoundError) as e:
        console.print(f"[red]❌ {e}[/red]")
        raise typer.Exit(1)


@app.command(name="prompt-edit")
def prompt_edit(
    title: str = typer.Option(..., "-t", "--title", help="提示词标题"),
    content: Optional[str] = typer.Option(None, "-c", "--content", help="新的提示词内容（可选）"),
    description: Optional[str] = typer.Option(None, "--description", help="新的描述（可选）"),
) -> None:
    """修改提示词（至少指定 -c 或 --description 之一）

    用法: vbiji prompt-edit -t <标题> [-c <新内容>] [--description <新描述>]

    示例:
      vbiji prompt-edit -t summarize -c "请详细摘要以下内容："
    """
    from vbiji.core.prompt.manager import PromptManager

    if content is None and description is None:
        console.print("[red]❌ 至少需要指定 -c 或 --description 之一[/red]")
        raise typer.Exit(1)

    manager = PromptManager()
    try:
        prompt = manager.edit(title=title, content=content, description=description)
        console.print(f"[green]✅ 已修改提示词: {prompt.title}[/green]")
    except ValueError as e:
        console.print(f"[red]❌ {e}[/red]")
        raise typer.Exit(1)


@app.command(name="prompt-show")
def prompt_show(
    title: str = typer.Option(..., "-t", "--title", help="提示词标题"),
) -> None:
    """查看提示词内容

    用法: vbiji prompt-show -t <标题>
    """
    from vbiji.core.prompt.manager import PromptManager

    manager = PromptManager()
    try:
        prompt = manager.get(title)
        console.print(f"[bold cyan]📝 {prompt.title}[/bold cyan]")
        if prompt.description:
            console.print(f"[dim]{prompt.description}[/dim]")
        console.print(f"\n{prompt.content}")
    except ValueError as e:
        console.print(f"[red]❌ {e}[/red]")
        raise typer.Exit(1)


@app.command(name="prompt-del")
def prompt_del(
    title: str = typer.Option(..., "-t", "--title", help="提示词标题"),
) -> None:
    """删除提示词

    用法: vbiji prompt-del -t <标题>
    """
    from vbiji.core.prompt.manager import PromptManager

    manager = PromptManager()
    try:
        manager.delete(title)
        console.print(f"[green]✅ 已删除提示词: {title}[/green]")
    except ValueError as e:
        console.print(f"[red]❌ {e}[/red]")
        raise typer.Exit(1)


@app.command(name="prompt-list")
def prompt_list() -> None:
    """列出所有已保存的提示词

    用法: vbiji prompt-list
    """
    from vbiji.core.prompt.manager import PromptManager

    manager = PromptManager()
    prompts = manager.list_all()
    if not prompts:
        console.print("[yellow]暂无提示词，请使用 vbiji prompt-add 添加[/yellow]")
        return
    table = Table(title="已保存的提示词")
    table.add_column("标题", style="cyan")
    table.add_column("描述", style="dim")
    for p in prompts:
        table.add_row(p.title, p.description or "-")
    console.print(table)


# ===== AI 问答命令 =====

@app.command()
def ask(
    filepath: str = typer.Argument(..., help="文件路径"),
    prompt_text: str = typer.Argument(None, help="提示词内容（直接指定）"),
    llm_name: str = typer.Option("default", "--llm", help="LLM 配置名称（默认 default）"),
    stream: bool = typer.Option(False, "--stream", help="开启流式输出"),
    prompt_name: str = typer.Option(None, "-p", "--prompt", help="已配置提示词的标题（从数据库读取内容）"),
    save: bool = typer.Option(False, "--save", help="保存结果到当前目录（文件名自动生成）"),
    save_as: Optional[str] = typer.Option(
        None, "--save-as", help="保存结果到指定路径（支持 .md/.txt/.json/.csv）"
    ),
) -> None:
    """AI 问答：结合文件内容和提示词提交给 AI 处理

    用法: vbiji ask <文件路径> <提示词> [--llm <配置名>] [--stream] [--save]
    用法: vbiji ask <文件路径> --prompt <提示词标题> [--llm <配置名>] [--stream]
    用法: vbiji ask <文件路径> <提示词> --save-as <保存路径>    # 保存到指定路径

    示例:
      vbiji ask ./report.pdf "请摘要" --llm deepseek
      vbiji ask ./contract.pdf --prompt 财报分析 --llm deepseek
      vbiji ask ./report.pdf "请摘要" --llm deepseek --save           # 保存到当前目录
      vbiji ask ./report.pdf "请摘要" --llm deepseek --save-as ./out.txt  # 保存到指定路径
    """
    from pathlib import Path

    from vbiji.core.reader import registry
    from vbiji.core.llm.manager import LlmManager
    from vbiji.core.prompt.manager import PromptManager

    # 0. 解析提示词来源
    if prompt_name:
        pm = PromptManager()
        try:
            prompt_obj = pm.get(prompt_name)
            prompt_text = prompt_obj.content
        except ValueError:
            console.print(f"[red]❌ 未找到提示词: '{prompt_name}'[/red]")
            raise typer.Exit(1)
    elif prompt_text is None:
        console.print("[red]❌ 必须提供提示词（位置参数）或使用 --prompt 指定已配置的提示词标题[/red]")
        raise typer.Exit(1)

    # 1. 读取文件
    try:
        doc = registry.read(filepath)
    except Exception as e:
        console.print(f"[red]❌ 读取文件失败: {e}[/red]")
        raise typer.Exit(1)

    # 2. 获取 LLM 配置
    llm_manager = LlmManager()
    try:
        llm_config = llm_manager.get(llm_name)
    except ValueError:
        console.print(f"[red]❌ LLM 配置 '{llm_name}' 不存在，请先使用 vbiji llm-add 添加[/red]")
        raise typer.Exit(1)

    # 3. 调用 AI
    from vbiji.core.ai.client import ai_client

    try:
        chat = ai_client.create_chat(llm_config)
    except ValueError as e:
        console.print(f"[red]❌ {e}[/red]")
        raise typer.Exit(1)

    console.print(f"[dim]📄 文件: {filepath}（{doc.metadata.get('pages', 1)} 页）[/dim]")
    console.print(f"[dim]🤖 模型: {llm_config.provider} / {llm_config.model or '(默认)'}[/dim]")
    if prompt_name:
        console.print(f"[dim]📝 提示词: {prompt_name}[/dim]")

    # 4. 收集回复内容（非流式直接收集，流式则拼接所有 token）
    result = ""
    try:
        if stream:
            console.print("[bold green]🤖 AI 回答（流式）：[/bold green]\n")
            import asyncio

            async def stream_output():
                nonlocal result
                async for token in chat.ask_stream(prompt_text, context=doc.content):
                    console.print(token, end="")
                    result += token

            asyncio.run(stream_output())
            console.print()
        else:
            console.print("[bold green]🤖 AI 回答：[/bold green]")
            result = chat.ask(prompt_text, context=doc.content)
            console.print(result)
    except Exception as e:
        console.print(f"[red]❌ AI 调用失败: {e}[/red]")
        raise typer.Exit(1)

    # 5. 保存结果（--save / --save-as）
    if save_as:
        save_path = Path(save_as)
    elif save:
        src = Path(filepath)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        save_path = Path.cwd() / f"{src.stem}_{ts}.md"
    else:
        save_path = None

    if save_path:
        save_path = save_path.expanduser().resolve()
        save_path.parent.mkdir(parents=True, exist_ok=True)

        ext = save_path.suffix.lower()
        if ext == ".json":
            output_content = json.dumps(
                {
                    "source_file": str(Path(filepath).resolve()),
                    "prompt": prompt_text,
                    "llm": llm_name,
                    "answer": result,
                },
                ensure_ascii=False,
                indent=2,
            )
        elif ext == ".csv":
            lines = [row.strip() for row in result.split("\n") if row.strip()]
            with save_path.open("w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["内容"])
                for line in lines:
                    writer.writerow([line])
            console.print(f"[dim]💾 已保存为 CSV: {save_path}[/dim]")
            return
        else:
            output_content = result

        save_path.write_text(output_content, encoding="utf-8")
        console.print(f"[dim]💾 已保存: {save_path}[/dim]")


@app.command(name="batch")
def batch(
    to_format: str = typer.Option(
        ...,
        "--to",
        help="目标格式（md / json / txt）",
    ),
    prompt_name: str = typer.Option(
        ...,
        "-p",
        "--prompt",
        help="已配置的提示词标题",
    ),
    llm_name: str = typer.Option("default", "--llm", help="LLM 配置名称（默认 default）"),
    directory: str = typer.Option(".", "-d", "--dir", help="要处理的目录路径（默认当前目录）"),
) -> None:
    """批量处理当前目录下所有可解析的文件

    处理流程：
    1. 扫描统计：统计 PDF / MD / TXT 文件数量和大小
    2. 格式转换：将所有文件转为指定格式，保存到 vbiji_raw/ 子目录
    3. AI 提炼：对每个转换后的文件用提示词和大模型提炼，结果保存到 vbiji_llm/ 子目录

    用法: vbiji batch --to <格式> --prompt <提示词标题> --llm <配置名> [-d <目录>]

    示例:
      vbiji batch --to md --prompt 财报分析 --llm deepseek
      vbiji batch --to md --prompt 财报分析 --llm deepseek -d /path/to/files
    """
    from vbiji.core.reader import registry
    from vbiji.core.llm.manager import LlmManager
    from vbiji.core.prompt.manager import PromptManager

    dir_path = Path(directory).expanduser().resolve()
    if not dir_path.is_dir():
        console.print(f"[red]❌ 目录不存在: {dir_path}[/red]")
        raise typer.Exit(1)

    # 创建子目录
    raw_dir = dir_path / "vbiji_raw"
    llm_dir = dir_path / "vbiji_llm"
    raw_dir.mkdir(exist_ok=True)
    llm_dir.mkdir(exist_ok=True)

    # ── 阶段 0：获取 LLM 和提示词配置 ──────────────────────────────
    try:
        llm_manager = LlmManager()
        llm_config = llm_manager.get(llm_name)
    except ValueError:
        console.print(f"[red]❌ LLM 配置 '{llm_name}' 不存在[/red]")
        raise typer.Exit(1)

    try:
        pm = PromptManager()
        prompt_obj = pm.get(prompt_name)
        prompt_text = prompt_obj.content
    except ValueError:
        console.print(f"[red]❌ 未找到提示词: '{prompt_name}'[/red]")
        raise typer.Exit(1)

    from vbiji.core.ai.client import ai_client

    try:
        chat = ai_client.create_chat(llm_config)
    except ValueError as e:
        console.print(f"[red]❌ {e}[/red]")
        raise typer.Exit(1)

    # ── 阶段 1：扫描统计 ────────────────────────────────────────────
    extensions = ["pdf", "md", "txt", "docx"]
    files_info: list[dict] = []

    for ext in extensions:
        for f in dir_path.glob(f"*.{ext}"):
            files_info.append(
                {
                    "path": f,
                    "ext": ext,
                    "size": f.stat().st_size,
                    "name": f.name,
                }
            )

    total_size = sum(f["size"] for f in files_info)
    total_count = len(files_info)
    ext_count: dict[str, int] = {}
    for f in files_info:
        ext_count[f["ext"]] = ext_count.get(f["ext"], 0) + 1

    console.print("\n[bold]📊 批量处理统计[/bold]")
    console.print(f"  目录: {dir_path}")
    console.print(f"  总文件数: {total_count}")
    console.print(f"  总大小: {_format_size(total_size)}")
    for ext, cnt in sorted(ext_count.items()):
        console.print(f"    - {ext.upper()}: {cnt} 个")

    if total_count == 0:
        console.print("[yellow]⚠️  当前目录无可处理文件[/yellow]")
        raise typer.Exit(0)

    console.print(f"\n[bold]🤖 模型: {llm_config.provider} / {llm_config.model or '(默认)'}[/bold]")
    console.print(f"[bold]📝 提示词: {prompt_name}[/bold]")
    console.print(f"[bold]📦 目标格式: {to_format.upper()}[/bold]")
    console.print()

    # ── 阶段 2：逐条处理 ────────────────────────────────────────────
    results: list[dict] = []
    for i, file_info in enumerate(files_info, 1):
        src = file_info["path"]
        ext = file_info["ext"]

        console.print(f"[cyan][{i}/{total_count}][/cyan] ▶ {src.name}")

        # 步骤 A：读取内容
        try:
            doc = registry.read(str(src))
        except Exception as e:
            console.print(f"  [red]❌ 读取失败: {e}[/red]")
            results.append({"file": src.name, "status": "failed", "reason": "读取失败"})
            continue

        # 步骤 B：转为目标格式并保存到 vbiji_raw/
        target_content = _convert_to_format(doc.content, ext, to_format)
        if target_content is None:
            console.print(f"  [yellow]⚠️  跳过（不支持的格式或转换失败）[/yellow]")
            results.append({"file": src.name, "status": "skipped", "reason": "格式不支持"})
            continue

        converted_name = f"{src.stem}.{to_format}"
        converted_path = raw_dir / converted_name
        converted_path.write_text(target_content, encoding="utf-8")

        # 步骤 C：AI 提炼
        try:
            refined = chat.ask(prompt_text, context=target_content)
        except Exception as e:
            console.print(f"  [red]❌ AI 提炼失败: {e}[/red]")
            results.append({"file": src.name, "status": "failed", "reason": "AI 失败"})
            continue

        # 步骤 D：保存提炼结果到 vbiji_llm/
        refined_name = f"{src.stem}.md"
        refined_path = llm_dir / refined_name
        refined_path.write_text(refined, encoding="utf-8")

        console.print(f"  [green]✅ 已保存: vbiji_raw/{converted_name}[/green]")
        console.print(f"  [green]✅ 已保存: vbiji_llm/{refined_name}[/green]")
        results.append({"file": src.name, "status": "success", "converted": converted_name, "refined": refined_name})

    # ── 阶段 3：统计结果 ────────────────────────────────────────────
    success = sum(1 for r in results if r["status"] == "success")
    failed = sum(1 for r in results if r["status"] == "failed")
    skipped = sum(1 for r in results if r["status"] == "skipped")

    console.print("\n[bold]📊 处理完成[/bold]")
    console.print(f"  ✅ 成功: {success}")
    console.print(f"  ❌ 失败: {failed}")
    console.print(f"  ⚠️  跳过: {skipped}")


def _format_size(size: int) -> str:
    """格式化文件大小"""
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


def _convert_to_format(content: str, src_ext: str, target: str) -> Optional[str]:
    """将内容转换为目标格式"""
    if target == "md":
        return content
    elif target == "txt":
        return content
    elif target == "json":
        return json.dumps(
            {"content": content, "source_format": src_ext},
            ensure_ascii=False,
            indent=2,
        )
    return None


if __name__ == "__main__":
    app()