"""Function Calling处理器测试

测试函数调用注册、验证和执行功能。
"""

import pytest
import json
from src.agent.models import FunctionCall
from src.agent.function_calling import FunctionCallHandler, FunctionCallError


class TestFunctionCallHandler:
    """测试Function Calling处理器"""
    
    @pytest.fixture
    def handler(self):
        """创建处理器"""
        return FunctionCallHandler()
    
    def test_register_simple_function(self, handler):
        """测试注册简单函数"""
        def test_func() -> str:
            """测试函数"""
            return "test result"
        
        handler.register_function(test_func)
        
        definitions = handler.get_function_definitions()
        assert len(definitions) == 1
        
        func_def = definitions[0]
        assert func_def["name"] == "test_func"
        assert func_def["description"] == "测试函数"
        assert func_def["parameters"]["type"] == "object"
        assert len(func_def["parameters"]["required"]) == 0
    
    def test_register_function_with_params(self, handler):
        """测试注册带参数的函数"""
        def add_numbers(a: int, b: int, operation: str = "add") -> int:
            """数学运算函数"""
            if operation == "add":
                return a + b
            elif operation == "multiply":
                return a * b
            return 0
        
        handler.register_function(add_numbers, description="数学运算")
        
        definitions = handler.get_function_definitions()
        func_def = definitions[0]
        
        assert func_def["name"] == "add_numbers"
        assert func_def["description"] == "数学运算"
        
        params = func_def["parameters"]["properties"]
        assert "a" in params
        assert "b" in params
        assert "operation" in params
        
        assert params["a"]["type"] == "integer"
        assert params["b"]["type"] == "integer"
        assert params["operation"]["type"] == "string"
        
        required = func_def["parameters"]["required"]
        assert "a" in required
        assert "b" in required
        assert "operation" not in required  # 有默认值
    
    def test_register_function_with_custom_name(self, handler):
        """测试使用自定义名称注册函数"""
        def internal_func() -> str:
            return "result"
        
        handler.register_function(internal_func, name="public_func", description="公开函数")
        
        definitions = handler.get_function_definitions()
        func_def = definitions[0]
        
        assert func_def["name"] == "public_func"
        assert func_def["description"] == "公开函数"
    
    @pytest.mark.asyncio
    async def test_execute_function_call_success(self, handler):
        """测试成功执行函数调用"""
        def multiply(x: int, y: int) -> int:
            return x * y
        
        handler.register_function(multiply)
        
        function_call = FunctionCall(
            name="multiply",
            arguments='{"x": 6, "y": 7}'
        )
        
        result = await handler.execute_function_call(function_call)
        assert result == 42
    
    @pytest.mark.asyncio
    async def test_execute_async_function(self, handler):
        """测试执行异步函数"""
        async def async_func(message: str) -> str:
            return f"Async: {message}"
        
        handler.register_function(async_func)
        
        function_call = FunctionCall(
            name="async_func",
            arguments='{"message": "hello"}'
        )
        
        result = await handler.execute_function_call(function_call)
        assert result == "Async: hello"
    
    @pytest.mark.asyncio
    async def test_execute_unknown_function(self, handler):
        """测试执行未知函数"""
        function_call = FunctionCall(name="unknown_func", arguments="{}")
        
        with pytest.raises(FunctionCallError) as exc_info:
            await handler.execute_function_call(function_call)
        
        assert "未知函数" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_execute_invalid_json_arguments(self, handler):
        """测试执行包含无效JSON参数的函数"""
        def test_func() -> str:
            return "test"
        
        handler.register_function(test_func)
        
        function_call = FunctionCall(name="test_func", arguments="invalid json")
        
        with pytest.raises(FunctionCallError) as exc_info:
            await handler.execute_function_call(function_call)
        
        assert "参数JSON解析失败" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_execute_function_with_wrong_params(self, handler):
        """测试执行参数错误的函数"""
        def requires_param(name: str) -> str:
            return f"Hello {name}"
        
        handler.register_function(requires_param)
        
        function_call = FunctionCall(
            name="requires_param",
            arguments='{"wrong_param": "value"}'
        )
        
        with pytest.raises(FunctionCallError) as exc_info:
            await handler.execute_function_call(function_call)
        
        assert "函数参数错误" in str(exc_info.value)
    
    def test_validate_function_call_valid(self, handler):
        """测试验证有效函数调用"""
        def test_func() -> str:
            return "test"
        
        handler.register_function(test_func)
        
        function_call = FunctionCall(name="test_func", arguments="{}")
        assert handler.validate_function_call(function_call) is True
    
    def test_validate_function_call_invalid(self, handler):
        """测试验证无效函数调用"""
        # 未注册的函数
        function_call = FunctionCall(name="unknown_func", arguments="{}")
        assert handler.validate_function_call(function_call) is False
        
        # 无效JSON
        def test_func() -> str:
            return "test"
        
        handler.register_function(test_func)
        function_call = FunctionCall(name="test_func", arguments="invalid json")
        assert handler.validate_function_call(function_call) is False 