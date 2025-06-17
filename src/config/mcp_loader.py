"""
MCP配置文件加载器

负责基础的文件加载、缓存和验证功能
"""

import json
import os
from typing import Dict, Any, Optional
from pathlib import Path
import jsonschema
from jsonschema import ValidationError

from src.exceptions import MCPConfigError


class MCPFileLoader:
    """MCP配置文件基础加载器
    
    专注于文件加载、缓存和JSON Schema验证
    """
    
    def __init__(self, config_path: str = "config/mcp_servers.json", 
                 schema_path: str = "config/mcp_servers_schema.json") -> None:
        """初始化文件加载器
        
        Args:
            config_path: MCP配置文件路径
            schema_path: JSON Schema文件路径
            
        Raises:
            MCPConfigError: 配置文件不存在时立即抛出
        """
        self.config_path = Path(config_path)
        self.schema_path = Path(schema_path)
        self._config_cache: Optional[Dict[str, Any]] = None
        self._schema_cache: Optional[Dict[str, Any]] = None
        self._last_modified: Optional[float] = None
        
        # 验证配置文件存在
        if not self.config_path.exists():
            raise MCPConfigError(f"❌ MCP配置文件不存在: {self.config_path}")
        
        # Schema文件是可选的
        self._schema_available = self.schema_path.exists()
    
    def _load_schema(self) -> Dict[str, Any]:
        """加载JSON Schema文件
        
        Returns:
            Schema字典
            
        Raises:
            MCPConfigError: Schema文件加载失败时立即抛出
        """
        if not self._schema_available:
            return {}
        
        if self._schema_cache is None:
            with open(self.schema_path, 'r', encoding='utf-8') as f:
                self._schema_cache = json.load(f)
        
        return self._schema_cache
    
    def _validate_config(self, config: Dict[str, Any]) -> None:
        """验证配置文件格式
        
        Args:
            config: 配置字典
            
        Raises:
            MCPConfigError: 验证失败时立即抛出
        """
        if not self._schema_available:
            return
        
        schema = self._load_schema()
        if not schema:
            return
            
        jsonschema.validate(config, schema)
    
    def load_config(self, force_reload: bool = False) -> Dict[str, Any]:
        """加载MCP配置文件
        
        Args:
            force_reload: 是否强制重新加载
            
        Returns:
            配置字典
            
        Raises:
            MCPConfigError: 加载或验证失败时立即抛出
        """
        # 检查是否需要重新加载
        current_mtime = os.path.getmtime(self.config_path)
        
        if (not force_reload and 
            self._config_cache is not None and 
            self._last_modified is not None and 
            current_mtime <= self._last_modified):
            return self._config_cache
        
        # 加载配置文件
        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 验证配置格式
        self._validate_config(config)
        
        # 更新缓存
        self._config_cache = config
        self._last_modified = current_mtime
        
        return config
    
    def reload_config(self) -> None:
        """重新加载配置文件
        
        Raises:
            MCPConfigError: 重新加载失败时立即抛出
        """
        self._config_cache = None
        self._last_modified = None
        self.load_config(force_reload=True)