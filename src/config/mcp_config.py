"""
MCP (Model Context Protocol) 配置管理

统一的MCP配置加载和查询接口
"""

from typing import Dict, Any, Optional, List

from src.config.mcp_loader import MCPFileLoader
from src.config.mcp_query import MCPQueryEngine


class MCPConfigLoader:
    """MCP配置加载器
    
    组合文件加载器和查询引擎，提供完整的MCP配置管理功能
    """
    
    def __init__(self, config_path: str = "config/mcp_servers.json", 
                 schema_path: str = "config/mcp_servers_schema.json") -> None:
        """初始化配置加载器
        
        Args:
            config_path: MCP配置文件路径
            schema_path: JSON Schema文件路径
            
        Raises:
            MCPConfigError: 配置文件不存在时立即抛出
        """
        self.file_loader = MCPFileLoader(config_path, schema_path)
        self.query_engine = MCPQueryEngine(self.file_loader)
    
    # 文件加载相关方法
    def load_config(self, force_reload: bool = False) -> Dict[str, Any]:
        """加载MCP配置文件"""
        return self.file_loader.load_config(force_reload)
    
    def reload_config(self) -> None:
        """重新加载配置文件"""
        self.file_loader.reload_config()
    
    # 查询相关方法 - 直接委托给查询引擎
    def get_enabled_servers(self) -> Dict[str, Dict[str, Any]]:
        """获取所有启用的服务器配置"""
        return self.query_engine.get_enabled_servers()
    
    def get_server_config(self, server_name: str) -> Optional[Dict[str, Any]]:
        """获取指定服务器的配置"""
        return self.query_engine.get_server_config(server_name)
    
    def get_servers_by_category(self, category: str) -> Dict[str, Dict[str, Any]]:
        """根据分类获取服务器配置"""
        return self.query_engine.get_servers_by_category(category)
    
    def get_global_settings(self) -> Dict[str, Any]:
        """获取全局设置"""
        return self.query_engine.get_global_settings()
    
    def get_categories(self) -> Dict[str, Dict[str, Any]]:
        """获取所有分类的服务器分组"""
        return self.query_engine.get_categories()
    
    def list_server_names(self, enabled_only: bool = True) -> List[str]:
        """列出服务器名称"""
        return self.query_engine.list_server_names(enabled_only)
    
    def is_server_enabled(self, server_name: str) -> bool:
        """检查服务器是否启用"""
        return self.query_engine.is_server_enabled(server_name)
    
    def get_config_info(self) -> Dict[str, Any]:
        """获取配置文件信息"""
        return self.query_engine.get_config_info()


# 全局配置加载器实例
_mcp_config_loader: Optional[MCPConfigLoader] = None


def get_mcp_config_loader(config_path: str = "config/mcp_servers.json",
                         schema_path: str = "config/mcp_servers_schema.json") -> MCPConfigLoader:
    """获取MCP配置加载器实例
    
    Args:
        config_path: MCP配置文件路径
        schema_path: Schema文件路径
        
    Returns:
        MCPConfigLoader实例
    """
    global _mcp_config_loader
    if _mcp_config_loader is None:
        _mcp_config_loader = MCPConfigLoader(config_path, schema_path)
    return _mcp_config_loader


def reset_mcp_config_loader() -> None:
    """重置MCP配置加载器实例（主要用于测试）"""
    global _mcp_config_loader
    _mcp_config_loader = None