"""配置文件加载器"""

from pathlib import Path
from typing import Optional

import toml


class Config:
    """Vbiji 配置类

    从 ~/.vbiji/config.toml 加载配置
    """

    def __init__(self, config_path: Optional[Path] = None) -> None:
        """初始化配置

        Args:
            config_path: 配置文件路径，默认 ~/.vbiji/config.toml
        """
        if config_path is None:
            config_path = Path.home() / ".vbiji" / "config.toml"

        self.config_path = config_path
        self._config: dict = {}
        self.load()

    def load(self) -> None:
        """加载配置文件"""
        if self.config_path.exists():
            self._config = toml.load(self.config_path)
        else:
            self._config = {}

    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """获取配置值

        Args:
            key: 配置键
            default: 默认值

        Returns:
            配置值或默认值
        """
        return self._config.get(key, default)

    @property
    def data_dir(self) -> Path:
        """获取数据目录，默认 ~/.vbiji/data"""
        data_path = self.get("data_dir")
        if data_path:
            return Path(data_path)
        return Path.home() / ".vbiji" / "data"

    @property
    def log_level(self) -> str:
        """获取日志级别，默认 INFO"""
        return self.get("log_level", "INFO") or "INFO"


# 全局配置实例
_config: Optional[Config] = None


def get_config() -> Config:
    """获取全局配置实例（单例）

    Returns:
        Config: 配置对象
    """
    global _config
    if _config is None:
        _config = Config()
    return _config