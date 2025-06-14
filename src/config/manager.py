"""配置管理器

整合环境变量加载器和配置验证器，提供统一的配置访问接口。
"""

from typing import Optional, Dict, Any
from pathlib import Path
import logging

from .models import Settings
from .loader import ConfigLoader
from .validator import ConfigValidator, ConfigValidationError


logger = logging.getLogger(__name__)

class ConfigManager:
    """配置管理器"""
    
    def __init__(self, env_file: Optional[Path] = None):
        """初始化配置管理器"""
        self._settings: Optional[Settings] = None
        self._loader = ConfigLoader(env_file)
        self._validator = ConfigValidator()
        self._initialized = False
    
    def initialize(self) -> None:
        """初始化配置"""
        try:
            # 加载配置
            settings = self._loader.load_settings()
            
            # 验证配置
            is_valid, errors = self._validator.validate_settings(settings)
            if not is_valid:
                error_summary = self._validator.get_error_summary()
                logger.error(f"配置验证失败: {error_summary}")
                raise ConfigValidationError("configuration", error_summary)
            
            self._settings = settings
            self._initialized = True
            logger.info("配置初始化成功")
            
        except Exception as e:
            logger.error(f"配置初始化失败: {str(e)}")
            raise
    
    def reload(self) -> None:
        """重新加载配置"""
        logger.info("重新加载配置...")
        self._settings = None
        self._initialized = False
        self.initialize()
    
    @property
    def settings(self) -> Settings:
        """获取配置"""
        if not self._initialized or self._settings is None:
            self.initialize()
        return self._settings
    
    @property
    def deepseek(self):
        """获取DeepSeek配置"""
        return self.settings.deepseek
    
    @property
    def mcp(self):
        """获取MCP配置"""
        return self.settings.mcp
    
    @property
    def mem0(self):
        """获取mem0配置"""
        return self.settings.mem0
    
    @property
    def app(self):
        """获取应用配置"""
        return self.settings.app
    
    def get_env_info(self) -> Dict[str, Any]:
        """获取环境信息"""
        env_file_path = Path.cwd() / ".env"
        return {
            "env_file_exists": env_file_path.exists(),
            "env_file_path": str(env_file_path),
            "initialized": self._initialized,
            "has_settings": self._settings is not None
        }
    
    def validate_current_config(self) -> bool:
        """验证当前配置"""
        if not self._settings:
            return False
        
        is_valid, _ = self._validator.validate_settings(self._settings)
        return is_valid


# 全局配置管理器实例
config_manager = ConfigManager() 