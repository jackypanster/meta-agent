"""
配置管理模块

提供统一的配置访问接口，支持.env文件加载
"""

from typing import Dict, Optional

from src.config.env_loader import EnvFileLoader
from src.exceptions import ConfigError


class Config:
    """配置管理类
    
    提供统一的配置访问接口，内部使用EnvFileLoader加载配置
    """
    
    def __init__(self, env_file: str = ".env") -> None:
        """初始化配置
        
        Args:
            env_file: .env文件路径，默认为项目根目录的.env
            
        Raises:
            ConfigError: 配置文件不存在或格式错误时立即抛出
        """
        self.env_file = env_file
        self._config: Dict[str, str] = {}
        self._load_config()
    
    def _load_config(self) -> None:
        """加载配置"""
        loader = EnvFileLoader(self.env_file)
        self._config = loader.load_env_file()
    
    def get(self, key: str) -> str:
        """获取配置值 - 如果不存在则立即失败
        
        Args:
            key: 配置键名
            
        Returns:
            配置值
            
        Raises:
            ConfigError: 如果配置不存在时立即抛出
        """
        if key not in self._config:
            raise ConfigError(f"❌ 配置 '{key}' 不存在")
        return self._config[key]
    
    def require(self, key: str) -> str:
        """获取必需的配置值
        
        Args:
            key: 配置键名
            
        Returns:
            配置值
            
        Raises:
            ConfigError: 如果配置不存在时立即抛出
        """
        value = self._config.get(key)
        if value is None:
            raise ConfigError(f"缺少必需的配置: {key}")
        return value
    
    def get_bool(self, key: str) -> bool:
        """获取布尔类型配置值 - 如果不存在则立即失败
        
        Args:
            key: 配置键名
            
        Returns:
            布尔值
            
        Raises:
            ConfigError: 如果配置不存在时立即抛出
        """
        value = self.get(key)  # 这会在配置不存在时抛出异常
        return value.lower() in ['true', '1', 'yes', 'on']
    
    def get_bool_optional(self, key: str, default: bool = False) -> bool:
        """获取可选的布尔类型配置值 - 不存在时返回默认值
        
        Args:
            key: 配置键名
            default: 默认值
            
        Returns:
            布尔值或默认值
        """
        if key not in self._config:
            return default
        value = self._config[key]
        return value.lower() in ['true', '1', 'yes', 'on']
    
    def list_all(self) -> Dict[str, str]:
        """返回所有配置（用于调试）
        
        Returns:
            所有配置的副本
        """
        return self._config.copy()


# 全局配置实例
_config_instance: Optional[Config] = None


def get_config() -> Config:
    """获取全局配置实例
    
    Returns:
        Config实例
        
    Raises:
        ConfigError: 配置初始化失败时立即抛出
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance


def reload_config() -> Config:
    """重新加载配置
    
    Returns:
        新的Config实例
        
    Raises:
        ConfigError: 配置重新加载失败时立即抛出
    """
    global _config_instance
    _config_instance = None
    return get_config()