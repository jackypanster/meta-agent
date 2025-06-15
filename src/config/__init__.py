"""配置管理模块

提供简单的 .env 文件配置加载功能。
"""

from .settings import get_config, ConfigError

__all__ = ['get_config', 'ConfigError']
