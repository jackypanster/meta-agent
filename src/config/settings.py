"""
配置管理模块

直接从 .env 文件加载配置变量，避免依赖系统环境变量。
"""

from pathlib import Path
from typing import Dict, Optional


class ConfigError(Exception):
    """配置错误"""


class Config:
    """配置管理类"""
    
    def __init__(self, env_file: str = ".env"):
        """
        初始化配置
        
        Args:
            env_file: .env文件路径，默认为项目根目录的.env
        """
        self.env_file = env_file
        self._config: Dict[str, str] = {}
        self._load_env_file()
    
    def _load_env_file(self):
        """从.env文件加载配置"""
        # 查找.env文件路径
        env_path = Path(self.env_file)
        
        # 如果不是绝对路径，则相对于项目根目录查找
        if not env_path.is_absolute():
            # 从当前文件位置向上查找项目根目录
            current_dir = Path(__file__).parent.parent.parent  # src/config -> src -> root
            env_path = current_dir / self.env_file
        
        if not env_path.exists():
            raise ConfigError(f"未找到配置文件: {env_path}")
        
        # 解析.env文件 - 任何错误都应该立即失败
        with open(env_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                
                # 跳过空行和注释
                if not line or line.startswith('#'):
                    continue
                
                # 解析键值对
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # 移除引号
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                    
                    self._config[key] = value
                else:
                    # 格式错误应该导致立即失败，而不是警告
                    raise ConfigError(f"❌ .env文件第{line_num}行格式错误: {line}")
        
        print(f"✓ 已从 {env_path} 加载配置")
    
    def get(self, key: str) -> str:
        """
        获取配置值 - 如果不存在则立即失败
        
        Args:
            key: 配置键名
            
        Returns:
            配置值
            
        Raises:
            ConfigError: 如果配置不存在
        """
        if key not in self._config:
            raise ConfigError(f"❌ 配置 '{key}' 不存在")
        return self._config[key]
    
    def require(self, key: str) -> str:
        """
        获取必需的配置值
        
        Args:
            key: 配置键名
            
        Returns:
            配置值
            
        Raises:
            ConfigError: 如果配置不存在
        """
        value = self._config.get(key)
        if value is None:
            raise ConfigError(f"缺少必需的配置: {key}")
        return value
    
    def get_bool(self, key: str) -> bool:
        """
        获取布尔类型配置值 - 如果不存在则立即失败
        
        Args:
            key: 配置键名
            
        Returns:
            布尔值
            
        Raises:
            ConfigError: 如果配置不存在
        """
        value = self.get(key)  # 这会在配置不存在时抛出异常
        return value.lower() in ['true', '1', 'yes', 'on']
    
    def list_all(self) -> Dict[str, str]:
        """返回所有配置（用于调试）"""
        return self._config.copy()


# 全局配置实例
_config_instance: Optional[Config] = None


def get_config() -> Config:
    """获取全局配置实例"""
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance


def reload_config():
    """重新加载配置"""
    global _config_instance
    _config_instance = None
    return get_config() 