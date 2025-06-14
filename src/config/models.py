"""配置数据模型

使用Pydantic定义配置项的类型和验证规则。
"""

from typing import Optional, Literal
from pydantic import BaseModel, Field, field_validator, HttpUrl, ConfigDict


class DeepSeekConfig(BaseModel):
    """DeepSeek API配置"""
    
    model_config = ConfigDict(
        env_prefix="QWEN_",
        case_sensitive=False,
        validate_assignment=True
    )
    
    api_key: str = Field(..., description="DeepSeek API密钥")
    base_url: HttpUrl = Field(
        default="https://api.deepseek.com",
        description="DeepSeek API基础URL"
    )
    model_name: str = Field(
        default="deepseek-reasoner",
        description="模型名称(DeepSeek-R1-0528推理模型)"
    )
    max_tokens: int = Field(
        default=4000,
        gt=0,
        le=32768,
        description="最大token数"
    )
    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="温度参数"
    )
    
    @field_validator('api_key')
    @classmethod
    def validate_api_key(cls, v: str) -> str:
        """验证API密钥格式"""
        if not v or len(v.strip()) == 0:
            raise ValueError("API密钥不能为空")
        if len(v) < 10:
            raise ValueError("API密钥长度不能少于10个字符")
        return v.strip()


class McpConfig(BaseModel):
    """MCP服务器配置"""
    
    server_url: HttpUrl = Field(
        default="https://mcp.context7.com/sse",
        description="MCP服务器URL"
    )
    timeout: int = Field(
        default=30,
        gt=0,
        le=300,
        description="连接超时时间(秒)"
    )
    max_retries: int = Field(
        default=3,
        ge=0,
        le=10,
        description="最大重试次数"
    )


class AppConfig(BaseModel):
    """应用配置"""
    
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(
        default="INFO",
        description="日志级别"
    )
    memory_size: int = Field(
        default=1000,
        gt=0,
        description="最大内存条目数"
    )


class Settings(BaseModel):
    """应用程序设置"""
    
    model_config = ConfigDict(
        env_prefix="QWEN_",
        case_sensitive=False,
        validate_assignment=True
    )
    
    deepseek: DeepSeekConfig
    mcp: McpConfig = Field(default_factory=McpConfig)
    app: AppConfig = Field(default_factory=AppConfig) 