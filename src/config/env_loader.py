"""
环境变量文件加载器

专门负责.env文件的解析和加载
"""

from pathlib import Path
from typing import Dict

from src.exceptions import ConfigError


class EnvFileLoader:
    """环境变量文件加载器
    
    专注于.env文件的解析和变量提取
    """
    
    def __init__(self, env_file: str = ".env") -> None:
        """初始化文件加载器
        
        Args:
            env_file: .env文件路径
        """
        self.env_file = env_file
    
    def load_env_file(self) -> Dict[str, str]:
        """从.env文件加载配置
        
        Returns:
            配置字典
            
        Raises:
            ConfigError: 配置文件不存在或格式错误时立即抛出
        """
        env_path = self._resolve_env_path()
        
        if not env_path.exists():
            raise ConfigError(f"未找到配置文件: {env_path}")
        
        config = {}
        
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
                    value = self._remove_quotes(value)
                    config[key] = value
                else:
                    # 格式错误应该导致立即失败，而不是警告
                    raise ConfigError(f"❌ .env文件第{line_num}行格式错误: {line}")
        
        print(f"✓ 已从 {env_path} 加载配置")
        return config
    
    def _resolve_env_path(self) -> Path:
        """解析环境变量文件路径
        
        Returns:
            解析后的文件路径
        """
        env_path = Path(self.env_file)
        
        # 如果不是绝对路径，则相对于项目根目录查找
        if not env_path.is_absolute():
            # 从当前文件位置向上查找项目根目录
            current_dir = Path(__file__).parent.parent.parent  # src/config -> src -> root
            env_path = current_dir / self.env_file
        
        return env_path
    
    def _remove_quotes(self, value: str) -> str:
        """移除值两边的引号
        
        Args:
            value: 原始值
            
        Returns:
            移除引号后的值
        """
        if value.startswith('"') and value.endswith('"'):
            return value[1:-1]
        elif value.startswith("'") and value.endswith("'"):
            return value[1:-1]
        return value