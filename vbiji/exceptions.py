"""自定义异常类"""


class VbijiError(Exception):
    """Vbiji 基础异常类"""

    def __init__(self, message: str = "未知错误"):
        self.message = message
        super().__init__(self.message)


class UnsupportedFormatError(VbijiError):
    """不支持的文件格式异常"""

    def __init__(self, path: str):
        self.path = path
        supported_formats = ["pdf", "docx", "md", "markdown", "txt"]
        message = f"不支持的文件格式: {path}\n支持的格式: {', '.join(supported_formats)}"
        super().__init__(message)