from dataclasses import dataclass, field


@dataclass
class Document:
    """统一的文档数据结构

    Attributes:
        content: 纯文本内容
        title: 文件标题（不含扩展名）
        format: 原始格式：pdf / docx / md / txt
        path: 文件绝对路径
        metadata: 元数据（页数/字数等）
    """

    content: str
    title: str
    format: str
    path: str
    metadata: dict = field(default_factory=dict)