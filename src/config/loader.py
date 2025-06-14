"""环境变量配置加载器

从环境变量和.env文件加载配置。
"""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

from .models import Settings, DeepSeekConfig, McpConfig, Mem0Config, AppConfig


class ConfigLoader:
    """配置加载器类"""
    
    def __init__(self, env_file: Optional[Path] = None):
        """初始化配置加载器
        
        Args:
            env_file: .env文件路径，默认在当前目录查找
        """
        if env_file is None:
            env_file = Path.cwd() / ".env"
        
        # 加载.env文件（如果存在）
        if env_file.exists():
            load_dotenv(env_file)
    
    def get_env_var(self, key: str, default: Optional[str] = None) -> str:
        """获取环境变量
        
        Args:
            key: 环境变量名
            default: 默认值
            
        Returns:
            环境变量值
            
        Raises:
            ValueError: 当必需的环境变量不存在时
        """
        value = os.getenv(key, default)
        if value is None:
            raise ValueError(f"Environment variable {key} is required")
        return value.strip()
    
    def load_settings(self) -> Settings:
        """加载完整配置
        
        Returns:
            Settings: 完整的应用配置
            
        Raises:
            ValueError: 当必需配置缺失时
        """
        # 加载DeepSeek配置
        deepseek_config = DeepSeekConfig(
            api_key=self.get_env_var("DEEPSEEK_API_KEY"),
            base_url=self.get_env_var("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
            model_name=self.get_env_var("DEEPSEEK_MODEL", "deepseek-reasoner"),
            max_tokens=int(self.get_env_var("DEEPSEEK_MAX_TOKENS", "4000")),
            temperature=float(self.get_env_var("DEEPSEEK_TEMPERATURE", "0.7"))
        )
        
        # 加载MCP配置
        mcp_config = McpConfig(
            server_url=self.get_env_var("MCP_SERVER_URL", "https://mcp.context7.com/sse"),
            timeout=int(self.get_env_var("MCP_TIMEOUT", "30")),
            max_retries=int(self.get_env_var("MCP_MAX_RETRIES", "3"))
        )
        
        # 加载mem0配置
        mem0_config = Mem0Config(
            api_key=self.get_env_var("MEM0_API_KEY")
        )
        
        # 加载应用配置
        app_config = AppConfig(
            log_level=self.get_env_var("LOG_LEVEL", "INFO"),
            memory_size=int(self.get_env_var("MEMORY_SIZE", "1000"))
        )
        
        return Settings(
            deepseek=deepseek_config,
            mcp=mcp_config,
            mem0=mem0_config,
            app=app_config
        ) 