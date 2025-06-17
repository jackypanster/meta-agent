"""
MCP配置验证器

统一的MCP配置验证接口，整合所有验证功能
"""

import jsonschema
from typing import Dict, Any, Optional

from src.config.mcp_validation_core import MCPValidationBase, MCPValidationError
from src.config.mcp_validation_servers import MCPServerValidator
from src.config.mcp_validation_config import MCPConfigSettingsValidator


class MCPConfigValidator(MCPValidationBase):
    """MCP配置验证器
    
    组合所有验证组件，提供完整的MCP配置验证功能
    """
    
    def __init__(self, schema_path: Optional[str] = None):
        """初始化验证器
        
        Args:
            schema_path: JSON Schema文件路径
        """
        super().__init__(schema_path)
        self.server_validator = MCPServerValidator(schema_path)
        self.config_validator = MCPConfigSettingsValidator(schema_path)
    
    def validate_schema(self, config: Dict[str, Any]) -> None:
        """使用JSON Schema验证配置
        
        Args:
            config: 配置字典
            
        Raises:
            MCPValidationError: Schema验证失败时立即抛出
        """
        schema = self._load_schema()
        if not schema:
            return  # 没有Schema文件，跳过验证
        
        try:
            jsonschema.validate(config, schema)
        except jsonschema.ValidationError as e:
            raise MCPValidationError(
                f"JSON Schema验证失败: {e.message}",
                e.absolute_path[-1] if e.absolute_path else "root",
                ["检查配置文件格式是否正确"]
            )
    
    def validate_config(self, config: Dict[str, Any]) -> None:
        """验证完整的MCP配置
        
        Args:
            config: 配置字典
            
        Raises:
            MCPValidationError: 任何验证失败时立即抛出
        """
        # 1. JSON Schema验证
        self.validate_schema(config)
        
        # 2. 版本验证
        self.config_validator.validate_version(config)
        
        # 3. 服务器配置验证
        self.server_validator.validate_servers(config)
        
        # 4. 全局设置验证
        self.config_validator.validate_global_settings(config)
        
        # 5. 一致性验证
        self.config_validator.validate_consistency(config)
    
    def get_validation_summary(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """获取验证摘要信息
        
        Args:
            config: 配置字典
            
        Returns:
            验证摘要字典
        """
        return self.config_validator.get_validation_summary(config)