"""
MCP (Model Context Protocol) 配置加载器

提供MCP服务器配置的加载、缓存、验证和热重载功能。
"""

import json
import os
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime
import jsonschema
from jsonschema import ValidationError

logger = logging.getLogger(__name__)


class MCPConfigError(Exception):
    """MCP配置相关错误"""
    pass


class MCPConfigLoader:
    """MCP配置加载器
    
    功能：
    - 加载和解析MCP服务器配置文件
    - 配置文件缓存和热重载
    - JSON Schema验证
    - 服务器过滤和查询
    """
    
    def __init__(self, config_path: str = "config/mcp_servers.json", 
                 schema_path: str = "config/mcp_servers_schema.json"):
        """初始化配置加载器
        
        Args:
            config_path: MCP配置文件路径
            schema_path: JSON Schema文件路径
        """
        self.config_path = Path(config_path)
        self.schema_path = Path(schema_path)
        self._config_cache: Optional[Dict[str, Any]] = None
        self._schema_cache: Optional[Dict[str, Any]] = None
        self._last_modified: Optional[float] = None
        
        # 确保配置文件存在
        if not self.config_path.exists():
            raise MCPConfigError(f"MCP配置文件不存在: {self.config_path}")
    
    def _load_schema(self) -> Dict[str, Any]:
        """加载JSON Schema"""
        if self._schema_cache is None and self.schema_path.exists():
            try:
                with open(self.schema_path, 'r', encoding='utf-8') as f:
                    self._schema_cache = json.load(f)
                logger.debug(f"已加载JSON Schema: {self.schema_path}")
            except Exception as e:
                logger.warning(f"无法加载JSON Schema: {e}")
                self._schema_cache = {}
        return self._schema_cache or {}
    
    def _validate_config(self, config: Dict[str, Any]) -> None:
        """验证配置文件格式"""
        schema = self._load_schema()
        if not schema:
            logger.warning("未找到JSON Schema，跳过验证")
            return
        
        try:
            jsonschema.validate(config, schema)
            logger.debug("配置文件验证通过")
        except ValidationError as e:
            error_msg = f"配置文件格式错误: {e.message}"
            if e.absolute_path:
                error_msg += f" (路径: {'.'.join(str(p) for p in e.absolute_path)})"
            raise MCPConfigError(error_msg)
    
    def load_config(self, force_reload: bool = False) -> Dict[str, Any]:
        """加载MCP配置文件
        
        Args:
            force_reload: 是否强制重新加载
            
        Returns:
            配置字典
            
        Raises:
            MCPConfigError: 配置文件加载或验证失败
        """
        try:
            current_mtime = self.config_path.stat().st_mtime
            
            # 检查是否需要重新加载
            if (self._config_cache is None or 
                force_reload or 
                current_mtime != self._last_modified):
                
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # 验证配置格式
                self._validate_config(config)
                
                # 更新缓存
                self._config_cache = config
                self._last_modified = current_mtime
                
                logger.info(f"已加载MCP配置: {self.config_path}")
                logger.debug(f"配置版本: {config.get('version', 'unknown')}")
                
                # 更新元数据中的最后修改时间
                if 'metadata' in config:
                    config['metadata']['last_modified'] = datetime.now().isoformat() + 'Z'
            
            return self._config_cache
            
        except json.JSONDecodeError as e:
            raise MCPConfigError(f"配置文件JSON格式错误: {e}")
        except FileNotFoundError:
            raise MCPConfigError(f"配置文件不存在: {self.config_path}")
        except Exception as e:
            raise MCPConfigError(f"加载配置文件失败: {e}")
    
    def get_enabled_servers(self) -> Dict[str, Dict[str, Any]]:
        """获取所有启用的MCP服务器配置
        
        Returns:
            启用的服务器配置字典
        """
        config = self.load_config()
        servers = config.get('servers', {})
        
        enabled_servers = {
            name: server_config 
            for name, server_config in servers.items()
            if server_config.get('enabled', True)  # 默认启用
        }
        
        logger.debug(f"找到 {len(enabled_servers)} 个启用的MCP服务器")
        return enabled_servers
    
    def get_server_config(self, server_name: str) -> Optional[Dict[str, Any]]:
        """获取指定服务器的配置
        
        Args:
            server_name: 服务器名称
            
        Returns:
            服务器配置字典，如果不存在或未启用则返回None
        """
        enabled_servers = self.get_enabled_servers()
        return enabled_servers.get(server_name)
    
    def get_servers_by_category(self, category: str) -> Dict[str, Dict[str, Any]]:
        """按分类获取服务器配置
        
        Args:
            category: 服务器分类
            
        Returns:
            指定分类的服务器配置字典
        """
        enabled_servers = self.get_enabled_servers()
        return {
            name: config
            for name, config in enabled_servers.items()
            if config.get('category') == category
        }
    
    def get_global_settings(self) -> Dict[str, Any]:
        """获取全局设置
        
        Returns:
            全局设置字典
        """
        config = self.load_config()
        return config.get('global_settings', {})
    
    def get_categories(self) -> Dict[str, Dict[str, Any]]:
        """获取服务器分类定义
        
        Returns:
            分类定义字典
        """
        config = self.load_config()
        return config.get('categories', {})
    
    def list_server_names(self, enabled_only: bool = True) -> List[str]:
        """列出服务器名称
        
        Args:
            enabled_only: 是否只返回启用的服务器
            
        Returns:
            服务器名称列表
        """
        if enabled_only:
            return list(self.get_enabled_servers().keys())
        else:
            config = self.load_config()
            return list(config.get('servers', {}).keys())
    
    def is_server_enabled(self, server_name: str) -> bool:
        """检查服务器是否启用
        
        Args:
            server_name: 服务器名称
            
        Returns:
            是否启用
        """
        return server_name in self.get_enabled_servers()
    
    def get_server_timeout(self, server_name: str) -> int:
        """获取服务器超时设置
        
        Args:
            server_name: 服务器名称
            
        Returns:
            超时时间（秒），如果未配置则返回全局默认值
        """
        server_config = self.get_server_config(server_name)
        if server_config and 'timeout' in server_config:
            return server_config['timeout']
        
        # 返回全局默认超时
        global_settings = self.get_global_settings()
        return global_settings.get('default_timeout', 30)
    
    def get_config_info(self) -> Dict[str, Any]:
        """获取配置文件信息
        
        Returns:
            配置文件信息字典
        """
        config = self.load_config()
        enabled_servers = self.get_enabled_servers()
        
        return {
            'config_path': str(self.config_path),
            'version': config.get('version', 'unknown'),
            'description': config.get('description', ''),
            'total_servers': len(config.get('servers', {})),
            'enabled_servers': len(enabled_servers),
            'enabled_server_names': list(enabled_servers.keys()),
            'categories': list(self.get_categories().keys()),
            'last_modified': self._last_modified,
            'global_settings': self.get_global_settings(),
            'metadata': config.get('metadata', {})
        }
    
    def reload_config(self) -> bool:
        """强制重新加载配置文件
        
        Returns:
            是否成功重新加载
        """
        try:
            old_config = self._config_cache.copy() if self._config_cache else {}
            self.load_config(force_reload=True)
            
            # 检查配置是否有变化
            new_config = self._config_cache
            if old_config != new_config:
                logger.info("配置文件已更新并重新加载")
                return True
            else:
                logger.debug("配置文件无变化")
                return False
                
        except Exception as e:
            logger.error(f"重新加载配置失败: {e}")
            return False


# 全局配置加载器实例
_global_loader: Optional[MCPConfigLoader] = None


def get_mcp_config_loader(config_path: str = "config/mcp_servers.json",
                         schema_path: str = "config/mcp_servers_schema.json") -> MCPConfigLoader:
    """获取全局MCP配置加载器实例
    
    Args:
        config_path: 配置文件路径
        schema_path: Schema文件路径
        
    Returns:
        MCPConfigLoader实例
    """
    global _global_loader
    
    if _global_loader is None:
        _global_loader = MCPConfigLoader(config_path, schema_path)
    
    return _global_loader


def reset_mcp_config_loader():
    """重置全局配置加载器实例（主要用于测试）"""
    global _global_loader
    _global_loader = None 