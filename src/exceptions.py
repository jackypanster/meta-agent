"""
应用程序异常定义

所有自定义异常类的定义，遵循fail-fast原则
"""


class ConfigError(Exception):
    """配置错误"""
    pass


class APIConnectionError(Exception):
    """API连接错误"""
    pass


class ModelConfigError(Exception):
    """模型配置错误"""
    pass


class MCPConfigError(Exception):
    """MCP配置错误"""
    pass