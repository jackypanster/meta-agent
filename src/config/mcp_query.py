"""
MCP配置查询器

负责MCP服务器配置的查询、过滤和信息获取功能
"""

from typing import Dict, Any, Optional, List
from datetime import datetime

from src.config.mcp_loader import MCPFileLoader


class MCPQueryEngine:
    """MCP配置查询引擎
    
    专注于配置查询、过滤和服务器信息获取
    """
    
    def __init__(self, loader: MCPFileLoader) -> None:
        """初始化查询引擎
        
        Args:
            loader: MCP文件加载器实例
        """
        self.loader = loader
    
    def get_enabled_servers(self) -> Dict[str, Dict[str, Any]]:
        """获取所有启用的服务器配置
        
        Returns:
            启用的服务器配置字典，key为服务器名称
        """
        config = self.loader.load_config()
        servers = config.get('servers', {})
        
        enabled_servers = {}
        for name, server_config in servers.items():
            if server_config.get('enabled', False):
                enabled_servers[name] = server_config
                
        return enabled_servers
    
    def get_server_config(self, server_name: str) -> Optional[Dict[str, Any]]:
        """获取指定服务器的配置
        
        Args:
            server_name: 服务器名称
            
        Returns:
            服务器配置字典，如果不存在则返回None
        """
        config = self.loader.load_config()
        servers = config.get('servers', {})
        return servers.get(server_name)
    
    def get_servers_by_category(self, category: str) -> Dict[str, Dict[str, Any]]:
        """根据分类获取服务器配置
        
        Args:
            category: 服务器分类
            
        Returns:
            指定分类的服务器配置字典
        """
        config = self.loader.load_config()
        servers = config.get('servers', {})
        
        category_servers = {}
        for name, server_config in servers.items():
            if server_config.get('category') == category:
                category_servers[name] = server_config
                
        return category_servers
    
    def get_global_settings(self) -> Dict[str, Any]:
        """获取全局设置
        
        Returns:
            全局设置字典
        """
        config = self.loader.load_config()
        return config.get('global_settings', {})
    
    def get_categories(self) -> Dict[str, Dict[str, Any]]:
        """获取所有分类的服务器分组
        
        Returns:
            按分类分组的服务器字典
        """
        config = self.loader.load_config()
        servers = config.get('servers', {})
        
        categories = {}
        for name, server_config in servers.items():
            category = server_config.get('category', 'default')
            if category not in categories:
                categories[category] = {}
            categories[category][name] = server_config
            
        return categories
    
    def list_server_names(self, enabled_only: bool = True) -> List[str]:
        """列出服务器名称
        
        Args:
            enabled_only: 是否只返回启用的服务器
            
        Returns:
            服务器名称列表
        """
        config = self.loader.load_config()
        servers = config.get('servers', {})
        
        if enabled_only:
            return [name for name, server_config in servers.items() 
                   if server_config.get('enabled', False)]
        else:
            return list(servers.keys())
    
    def is_server_enabled(self, server_name: str) -> bool:
        """检查服务器是否启用
        
        Args:
            server_name: 服务器名称
            
        Returns:
            是否启用
        """
        server_config = self.get_server_config(server_name)
        if not server_config:
            return False
        return server_config.get('enabled', False)
    
    def get_config_info(self) -> Dict[str, Any]:
        """获取配置文件信息
        
        Returns:
            配置信息字典，包含统计和元数据
        """
        config = self.loader.load_config()
        servers = config.get('servers', {})
        
        enabled_count = sum(1 for s in servers.values() if s.get('enabled', False))
        categories = set(s.get('category', 'default') for s in servers.values())
        
        return {
            'config_path': str(self.loader.config_path),
            'last_modified': datetime.fromtimestamp(self.loader._last_modified or 0).isoformat(),
            'total_servers': len(servers),
            'enabled_servers': enabled_count,
            'categories': sorted(list(categories)),
            'global_settings': self.get_global_settings()
        }