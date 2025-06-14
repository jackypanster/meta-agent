"""环境变量加载器

负责从.env文件和系统环境变量中加载配置数据。
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any, Union
from dotenv import load_dotenv

from .models import Settings, DeepSeekConfig, McpConfig, AppConfig


class EnvironmentLoader:
    """环境变量加载器"""
    
    def __init__(self, env_file: Optional[Union[str, Path]] = None) -> None:
        """初始化加载器"""
        self.env_file = env_file or ".env"
        self._loaded = False
    
    def load_env_file(self) -> bool:
        """加载.env文件"""
        try:
            env_path = Path(self.env_file)
            if env_path.exists():
                load_dotenv(env_path)
                self._loaded = True
                return True
            return False
        except Exception:
            return False
    
    def get_env_var(
        self, 
        key: str, 
        default: Optional[str] = None,
        required: bool = False
    ) -> str:
        """获取环境变量"""
        value = os.getenv(key, default)
        if required and not value:
            raise ValueError(f"必需的环境变量 {key} 未设置")
        return value or ""
    
    def _get_int(self, key: str, default: str) -> int:
        """获取整数类型环境变量"""
        try:
            return int(self.get_env_var(key, default))
        except ValueError:
            return int(default)
    
    def _get_float(self, key: str, default: str) -> float:
        """获取浮点数类型环境变量"""
        try:
            return float(self.get_env_var(key, default))
        except ValueError:
            return float(default)
    
    def load_settings(self) -> Settings:
        """加载完整配置"""
        # 确保环境变量已加载
        if not self._loaded:
            self.load_env_file()
        
        # DeepSeek配置
        deepseek = DeepSeekConfig(
            api_key=self.get_env_var("DEEPSEEK_API_KEY", required=True),
            base_url=self.get_env_var("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
            model_name=self.get_env_var("DEEPSEEK_MODEL", "deepseek-reasoner"),
            max_tokens=self._get_int("DEEPSEEK_MAX_TOKENS", "4000"),
            temperature=self._get_float("DEEPSEEK_TEMPERATURE", "0.7")
        )
        
        # MCP配置
        mcp = McpConfig(
            server_url=self.get_env_var("MCP_SERVER_URL", "https://mcp.context7.com/sse"),
            timeout=self._get_int("MCP_TIMEOUT", "30"),
            max_retries=self._get_int("MCP_MAX_RETRIES", "3")
        )
        
        # 应用配置
        app = AppConfig(
            log_level=self.get_env_var("LOG_LEVEL", "INFO"),
            memory_size=self._get_int("MEMORY_SIZE", "1000")
        )
        
        return Settings(deepseek=deepseek, mcp=mcp, app=app) 