"""配置验证器

验证配置项的有效性并提供友好的错误信息。
"""

import re
from typing import Optional, List, Tuple
from urllib.parse import urlparse

from .models import Settings


class ConfigValidationError(Exception):
    """配置验证错误"""
    
    def __init__(self, field: str, message: str, value: Optional[str] = None):
        self.field = field
        self.message = message
        self.value = value
        super().__init__(f"{field}: {message}")


class ConfigValidator:
    """配置验证器"""
    
    def __init__(self):
        self.errors: List[ConfigValidationError] = []
    
    def validate_api_key(self, api_key: str, provider: str = "API") -> bool:
        """验证API密钥格式"""
        if not api_key or not api_key.strip():
            self.errors.append(
                ConfigValidationError(f"{provider}_api_key", "API密钥不能为空")
            )
            return False
        
        if len(api_key.strip()) < 10:
            self.errors.append(
                ConfigValidationError(
                    f"{provider}_api_key",
                    "API密钥长度太短（至少10个字符）"
                )
            )
            return False
        
        # 检查是否包含非法字符
        if not re.match(r'^[a-zA-Z0-9\-_\.]+$', api_key.strip()):
            self.errors.append(
                ConfigValidationError(f"{provider}_api_key", "API密钥包含非法字符")
            )
            return False
        
        return True
    
    def validate_url(self, url: str, field_name: str) -> bool:
        """验证URL格式"""
        try:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                self.errors.append(
                    ConfigValidationError(field_name, "URL格式无效", url)
                )
                return False
            
            if parsed.scheme not in ['http', 'https']:
                self.errors.append(
                    ConfigValidationError(field_name, "URL必须使用http或https协议", url)
                )
                return False
            
            return True
        except Exception as e:
            self.errors.append(
                ConfigValidationError(field_name, f"URL解析失败: {str(e)}", url)
            )
            return False
    
    def validate_settings(self, settings: Settings) -> Tuple[bool, List[ConfigValidationError]]:
        """验证完整配置"""
        self.errors.clear()
        
        # 验证DeepSeek配置
        self.validate_api_key(settings.deepseek.api_key, "DeepSeek")
        self.validate_url(str(settings.deepseek.base_url), "deepseek_base_url")
        
        # 验证MCP配置
        self.validate_url(str(settings.mcp.server_url), "mcp_server_url")
        
        return len(self.errors) == 0, self.errors.copy()
    
    def get_error_summary(self) -> str:
        """获取错误摘要"""
        if not self.errors:
            return "配置验证通过"
        
        summary = f"发现 {len(self.errors)} 个配置错误:\n"
        for i, error in enumerate(self.errors, 1):
            summary += f"{i}. {error.message}\n"
        
        return summary 