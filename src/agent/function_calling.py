"""Function Calling处理器

处理函数调用的注册、验证和执行，支持DeepSeek的Function Calling格式。
"""

import json
import inspect
from typing import Dict, Any, Callable, List, Optional, get_type_hints
from .models import FunctionDefinition, FunctionCall


class FunctionCallError(Exception):
    """函数调用错误"""
    pass


class FunctionCallHandler:
    """Function Calling处理器"""
    
    def __init__(self):
        """初始化处理器"""
        self._functions: Dict[str, Callable] = {}
        self._schemas: Dict[str, FunctionDefinition] = {}
    
    def register_function(self, func: Callable, name: Optional[str] = None, 
                         description: Optional[str] = None) -> None:
        """注册函数"""
        func_name = name or func.__name__
        func_desc = description or func.__doc__ or "无描述"
        
        # 获取函数签名和构建Schema
        sig = inspect.signature(func)
        type_hints = get_type_hints(func)
        parameters = {"type": "object", "properties": {}, "required": []}
        
        for param_name, param in sig.parameters.items():
            param_type = type_hints.get(param_name, str)
            param_info = {"type": self._get_json_type(param_type)}
            
            if param.default == inspect.Parameter.empty:
                parameters["required"].append(param_name)
            else:
                param_info["default"] = param.default
            
            parameters["properties"][param_name] = param_info
        
        # 创建函数定义
        func_def = FunctionDefinition(
            name=func_name, description=func_desc, parameters=parameters
        )
        
        self._functions[func_name] = func
        self._schemas[func_name] = func_def
    
    def _get_json_type(self, python_type: type) -> str:
        """将Python类型转换为JSON Schema类型"""
        type_mapping = {
            str: "string", int: "integer", float: "number", 
            bool: "boolean", list: "array", dict: "object"
        }
        return type_mapping.get(python_type, "string")
    
    def get_function_definitions(self) -> List[Dict[str, Any]]:
        """获取所有函数定义"""
        return [schema.model_dump() for schema in self._schemas.values()]
    
    async def execute_function_call(self, function_call: FunctionCall) -> Any:
        """执行函数调用"""
        func_name = function_call.name
        
        if func_name not in self._functions:
            raise FunctionCallError(f"未知函数: {func_name}")
        
        try:
            arguments = json.loads(function_call.arguments)
        except json.JSONDecodeError as e:
            raise FunctionCallError(f"参数JSON解析失败: {str(e)}") from e
        
        func = self._functions[func_name]
        
        try:
            if inspect.iscoroutinefunction(func):
                return await func(**arguments)
            else:
                return func(**arguments)
        except TypeError as e:
            raise FunctionCallError(f"函数参数错误: {str(e)}") from e
        except Exception as e:
            raise FunctionCallError(f"函数执行失败: {str(e)}") from e
    
    def validate_function_call(self, function_call: FunctionCall) -> bool:
        """验证函数调用"""
        if function_call.name not in self._functions:
            return False
        
        try:
            json.loads(function_call.arguments)
            return True
        except json.JSONDecodeError:
            return False 