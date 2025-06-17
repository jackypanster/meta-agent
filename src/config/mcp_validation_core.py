"""
MCP配置验证核心模块

提供基础的验证功能和异常定义
"""

import json
from typing import Dict, Any, List, Optional
from pathlib import Path


class MCPValidationError(Exception):
    """MCP配置验证错误"""
    
    def __init__(self, message: str, field_path: str = "", suggestions: List[str] = None):
        self.message = message
        self.field_path = field_path
        self.suggestions = suggestions or []
        super().__init__(self.message)
    
    def __str__(self):
        return f"❌ {self.message} (字段: {self.field_path})"


class MCPValidationBase:
    """MCP验证基础类
    
    提供通用的验证方法和Schema加载功能
    """
    
    def __init__(self, schema_path: Optional[str] = None):
        """初始化验证器
        
        Args:
            schema_path: JSON Schema文件路径
        """
        self.schema_path = Path(schema_path) if schema_path else None
        self._schema_cache: Optional[Dict[str, Any]] = None
    
    def _load_schema(self) -> Dict[str, Any]:
        """加载验证Schema
        
        Returns:
            Schema字典
            
        Raises:
            MCPValidationError: Schema加载失败时立即抛出
        """
        if not self.schema_path or not self.schema_path.exists():
            return {}
        
        if self._schema_cache is None:
            with open(self.schema_path, 'r', encoding='utf-8') as f:
                self._schema_cache = json.load(f)
        
        return self._schema_cache
    
    def _validate_required_field(self, config: Dict[str, Any], field: str, 
                                field_path: str = "") -> None:
        """验证必需字段
        
        Args:
            config: 配置字典
            field: 字段名
            field_path: 字段路径
            
        Raises:
            MCPValidationError: 字段缺失时立即抛出
        """
        if field not in config:
            raise MCPValidationError(
                f"缺少必需字段: {field}",
                field_path or field,
                [f"请添加 '{field}' 字段"]
            )
    
    def _validate_field_type(self, value: Any, expected_type: type, 
                           field_path: str, field_name: str = "") -> None:
        """验证字段类型
        
        Args:
            value: 字段值
            expected_type: 期望类型
            field_path: 字段路径
            field_name: 字段名称
            
        Raises:
            MCPValidationError: 类型不匹配时立即抛出
        """
        if not isinstance(value, expected_type):
            raise MCPValidationError(
                f"字段类型错误: 期望 {expected_type.__name__}，实际 {type(value).__name__}",
                field_path,
                [f"将 {field_name} 改为 {expected_type.__name__} 类型"]
            )
    
    def _validate_string_not_empty(self, value: str, field_path: str) -> None:
        """验证字符串非空
        
        Args:
            value: 字符串值
            field_path: 字段路径
            
        Raises:
            MCPValidationError: 字符串为空时立即抛出
        """
        if not value or not value.strip():
            raise MCPValidationError(
                "字符串字段不能为空",
                field_path,
                ["请提供有效的字符串值"]
            )