"""
MCP服务器配置验证模块

专门负责MCP服务器配置的验证逻辑
"""

import re
from typing import Dict, Any, List

from src.config.mcp_validation_core import MCPValidationBase, MCPValidationError


class MCPServerValidator(MCPValidationBase):
    """MCP服务器配置验证器
    
    专注于服务器配置的详细验证
    """
    
    def validate_servers(self, config: Dict[str, Any]) -> None:
        """验证服务器配置部分
        
        Args:
            config: 完整配置字典
            
        Raises:
            MCPValidationError: 服务器配置验证失败时立即抛出
        """
        if 'servers' not in config:
            raise MCPValidationError(
                "缺少servers配置部分",
                "servers",
                ["添加servers配置: {\"servers\": {}}"]
            )
        
        servers = config['servers']
        self._validate_field_type(servers, dict, "servers", "servers")
        
        if not servers:
            raise MCPValidationError(
                "servers配置不能为空",
                "servers",
                ["至少添加一个服务器配置"]
            )
        
        # 验证每个服务器配置
        for server_name, server_config in servers.items():
            self._validate_server_name(server_name)
            self._validate_server_config(server_name, server_config)
    
    def _validate_server_name(self, server_name: str) -> None:
        """验证服务器名称
        
        Args:
            server_name: 服务器名称
            
        Raises:
            MCPValidationError: 服务器名称无效时立即抛出
        """
        if not isinstance(server_name, str):
            raise MCPValidationError(
                "服务器名称必须是字符串",
                f"servers.{server_name}",
                ["使用有效的字符串作为服务器名称"]
            )
        
        if not server_name.strip():
            raise MCPValidationError(
                "服务器名称不能为空",
                "servers",
                ["提供有效的服务器名称"]
            )
        
        # 检查名称格式（只允许字母、数字、下划线、连字符）
        if not re.match(r'^[a-zA-Z0-9_-]+$', server_name):
            raise MCPValidationError(
                f"服务器名称包含无效字符: {server_name}",
                f"servers.{server_name}",
                ["使用字母、数字、下划线或连字符"]
            )
    
    def _validate_server_config(self, server_name: str, server_config: Dict[str, Any]) -> None:
        """验证单个服务器配置
        
        Args:
            server_name: 服务器名称
            server_config: 服务器配置字典
            
        Raises:
            MCPValidationError: 服务器配置验证失败时立即抛出
        """
        field_path = f"servers.{server_name}"
        
        self._validate_field_type(server_config, dict, field_path, "server_config")
        
        # 验证必需字段
        self._validate_required_field(server_config, 'command', field_path)
        self._validate_required_field(server_config, 'args', field_path)
        
        # 验证command字段
        command = server_config['command']
        self._validate_field_type(command, str, f"{field_path}.command", "command")
        self._validate_string_not_empty(command, f"{field_path}.command")
        
        # 验证args字段
        args = server_config['args']
        self._validate_field_type(args, list, f"{field_path}.args", "args")
        
        for i, arg in enumerate(args):
            if not isinstance(arg, str):
                raise MCPValidationError(
                    f"args中的参数必须是字符串: {arg}",
                    f"{field_path}.args[{i}]",
                    ["确保所有参数都是字符串类型"]
                )
        
        # 验证可选字段
        if 'enabled' in server_config:
            enabled = server_config['enabled']
            self._validate_field_type(enabled, bool, f"{field_path}.enabled", "enabled")
        
        if 'description' in server_config:
            description = server_config['description']
            self._validate_field_type(description, str, f"{field_path}.description", "description")
        
        if 'category' in server_config:
            category = server_config['category']
            self._validate_field_type(category, str, f"{field_path}.category", "category")
            self._validate_string_not_empty(category, f"{field_path}.category")
        
        if 'env' in server_config:
            env = server_config['env']
            self._validate_field_type(env, dict, f"{field_path}.env", "env")
            
            for env_key, env_value in env.items():
                if not isinstance(env_key, str):
                    raise MCPValidationError(
                        f"环境变量名必须是字符串: {env_key}",
                        f"{field_path}.env.{env_key}",
                        ["使用字符串作为环境变量名"]
                    )
                
                if not isinstance(env_value, str):
                    raise MCPValidationError(
                        f"环境变量值必须是字符串: {env_value}",
                        f"{field_path}.env.{env_key}",
                        ["使用字符串作为环境变量值"]
                    )
        
        if 'timeout' in server_config:
            timeout = server_config['timeout']
            self._validate_field_type(timeout, (int, float), f"{field_path}.timeout", "timeout")
            
            if timeout <= 0:
                raise MCPValidationError(
                    f"timeout必须大于0: {timeout}",
                    f"{field_path}.timeout",
                    ["使用正数作为timeout值"]
                )