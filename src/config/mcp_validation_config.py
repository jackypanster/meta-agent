"""
MCP配置整体验证模块

负责版本、全局设置和一致性验证
"""

from typing import Dict, Any, List

from src.config.mcp_validation_core import MCPValidationBase, MCPValidationError


class MCPConfigSettingsValidator(MCPValidationBase):
    """MCP配置整体验证器
    
    专注于配置文件的版本、全局设置和一致性验证
    """
    
    def validate_version(self, config: Dict[str, Any]) -> None:
        """验证配置文件版本
        
        Args:
            config: 配置字典
            
        Raises:
            MCPValidationError: 版本验证失败时立即抛出
        """
        if 'version' not in config:
            raise MCPValidationError(
                "缺少version字段",
                "version",
                ["添加version字段，例如: \"version\": \"1.0\""]
            )
        
        version = config['version']
        self._validate_field_type(version, str, "version", "version")
        self._validate_string_not_empty(version, "version")
        
        # 验证版本格式（简单的x.y格式）
        import re
        if not re.match(r'^\d+\.\d+$', version):
            raise MCPValidationError(
                f"版本格式无效: {version}",
                "version",
                ["使用x.y格式，例如: \"1.0\", \"2.1\""]
            )
    
    def validate_global_settings(self, config: Dict[str, Any]) -> None:
        """验证全局设置
        
        Args:
            config: 配置字典
            
        Raises:
            MCPValidationError: 全局设置验证失败时立即抛出
        """
        if 'global_settings' not in config:
            return  # 全局设置是可选的
        
        global_settings = config['global_settings']
        self._validate_field_type(global_settings, dict, "global_settings", "global_settings")
        
        # 验证max_concurrent_servers
        if 'max_concurrent_servers' in global_settings:
            max_concurrent = global_settings['max_concurrent_servers']
            self._validate_field_type(max_concurrent, int, "global_settings.max_concurrent_servers", "max_concurrent_servers")
            
            if max_concurrent <= 0:
                raise MCPValidationError(
                    f"max_concurrent_servers必须大于0: {max_concurrent}",
                    "global_settings.max_concurrent_servers",
                    ["使用正整数，例如: 10"]
                )
        
        # 验证default_timeout
        if 'default_timeout' in global_settings:
            default_timeout = global_settings['default_timeout']
            self._validate_field_type(default_timeout, (int, float), "global_settings.default_timeout", "default_timeout")
            
            if default_timeout <= 0:
                raise MCPValidationError(
                    f"default_timeout必须大于0: {default_timeout}",
                    "global_settings.default_timeout",
                    ["使用正数，例如: 30.0"]
                )
        
        # 验证log_level
        if 'log_level' in global_settings:
            log_level = global_settings['log_level']
            self._validate_field_type(log_level, str, "global_settings.log_level", "log_level")
            
            valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
            if log_level.upper() not in valid_levels:
                raise MCPValidationError(
                    f"无效的log_level: {log_level}",
                    "global_settings.log_level",
                    [f"使用有效的日志级别: {', '.join(valid_levels)}"]
                )
    
    def validate_consistency(self, config: Dict[str, Any]) -> None:
        """验证配置一致性
        
        Args:
            config: 配置字典
            
        Raises:
            MCPValidationError: 一致性验证失败时立即抛出
        """
        servers = config.get('servers', {})
        
        # 检查是否至少有一个启用的服务器
        enabled_servers = [name for name, server_config in servers.items() 
                         if server_config.get('enabled', False)]
        
        if not enabled_servers:
            raise MCPValidationError(
                "没有启用的服务器",
                "servers",
                ["至少启用一个服务器: \"enabled\": true"]
            )
        
        # 检查服务器名称是否重复（这在字典中是自动保证的，但我们可以检查其他重复）
        categories = []
        for server_config in servers.values():
            if 'category' in server_config:
                categories.append(server_config['category'])
        
        # 统计分类信息（用于调试）
        category_counts = {}
        for category in categories:
            category_counts[category] = category_counts.get(category, 0) + 1
    
    def get_validation_summary(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """获取验证摘要信息
        
        Args:
            config: 配置字典
            
        Returns:
            验证摘要字典
        """
        servers = config.get('servers', {})
        enabled_count = sum(1 for s in servers.values() if s.get('enabled', False))
        
        categories = set()
        for server_config in servers.values():
            if 'category' in server_config:
                categories.add(server_config['category'])
        
        return {
            'total_servers': len(servers),
            'enabled_servers': enabled_count,
            'disabled_servers': len(servers) - enabled_count,
            'categories': sorted(list(categories)),
            'has_global_settings': 'global_settings' in config,
            'version': config.get('version', 'unknown')
        }