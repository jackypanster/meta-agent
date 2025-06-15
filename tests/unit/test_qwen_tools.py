"""
Qwen工具类的单元测试

测试内存管理工具和计算器工具的功能。
"""

import json
import os
import sys
from unittest.mock import MagicMock, patch

import pytest

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from tools.qwen_tools.calculator_tool import CalculatorTool
from tools.qwen_tools.memory_tools import RecallInfoTool, SaveInfoTool, get_memory_store


class TestSaveInfoTool:
    """测试SaveInfoTool工具类"""
    
    def setup_method(self):
        """每个测试前清理内存存储"""
        memory_store = get_memory_store()
        memory_store['facts'].clear()
        memory_store['preferences'].clear()
        memory_store['history'].clear()
    
    def test_save_fact_info(self):
        """测试保存事实信息"""
        tool = SaveInfoTool()
        params = json.dumps({
            'info': '我叫张三',
            'type': 'fact'
        })
        
        result = tool.call(params)
        result_data = json.loads(result)
        
        assert result_data['status'] == 'saved'
        assert '已保存fact: 我叫张三' in result_data['message']
        
        # 检查内存存储
        memory_store = get_memory_store()
        assert len(memory_store['facts']) == 1
        assert memory_store['facts'][0]['content'] == '我叫张三'
    
    def test_save_preference_info(self):
        """测试保存偏好信息"""
        tool = SaveInfoTool()
        params = json.dumps({
            'info': '我喜欢编程',
            'type': 'preference'
        })
        
        result = tool.call(params)
        result_data = json.loads(result)
        
        assert result_data['status'] == 'saved'
        assert '已保存preference: 我喜欢编程' in result_data['message']
        
        # 检查内存存储
        memory_store = get_memory_store()
        assert len(memory_store['preferences']) == 1
        assert memory_store['preferences'][0]['content'] == '我喜欢编程'
    
    def test_save_info_default_type(self):
        """测试默认信息类型为fact"""
        tool = SaveInfoTool()
        params = json.dumps({
            'info': '我在北京工作'
        })
        
        result = tool.call(params)
        result_data = json.loads(result)
        
        assert result_data['status'] == 'saved'
        
        # 检查保存到facts中
        memory_store = get_memory_store()
        assert len(memory_store['facts']) == 1
        assert memory_store['facts'][0]['content'] == '我在北京工作'
    
    def test_save_info_invalid_json(self):
        """测试无效JSON参数"""
        tool = SaveInfoTool()
        params = "invalid json"
        
        result = tool.call(params)
        result_data = json.loads(result)
        
        assert 'error' in result_data
        assert '保存失败' in result_data['error']


class TestRecallInfoTool:
    """测试RecallInfoTool工具类"""
    
    def setup_method(self):
        """每个测试前设置测试数据"""
        memory_store = get_memory_store()
        memory_store['facts'].clear()
        memory_store['preferences'].clear()
        memory_store['history'].clear()
        
        # 添加测试数据
        memory_store['facts'].append({
            'content': '我叫张三',
            'timestamp': 1234567890,
            'time_str': '2023-01-01 12:00:00'
        })
        memory_store['preferences'].append({
            'content': '我喜欢编程',
            'timestamp': 1234567891,
            'time_str': '2023-01-01 12:00:01'
        })
    
    def test_recall_found_info(self):
        """测试回忆找到的信息"""
        tool = RecallInfoTool()
        params = json.dumps({'query': '张三'})
        
        result = tool.call(params)
        result_data = json.loads(result)
        
        assert result_data['found'] is True
        assert result_data['count'] == 1
        assert len(result_data['results']) == 1
        assert result_data['results'][0]['content'] == '我叫张三'
    
    def test_recall_not_found_info(self):
        """测试回忆未找到的信息"""
        tool = RecallInfoTool()
        params = json.dumps({'query': '李四'})
        
        result = tool.call(params)
        result_data = json.loads(result)
        
        assert result_data['found'] is False
        assert result_data['message'] == '没有找到相关信息'
    
    def test_recall_multiple_matches(self):
        """测试回忆多个匹配的信息"""
        # 添加更多测试数据
        memory_store = get_memory_store()
        memory_store['facts'].append({
            'content': '我喜欢编程和读书',
            'timestamp': 1234567892,
            'time_str': '2023-01-01 12:00:02'
        })
        
        tool = RecallInfoTool()
        params = json.dumps({'query': '编程'})
        
        result = tool.call(params)
        result_data = json.loads(result)
        
        assert result_data['found'] is True
        assert result_data['count'] == 2
        assert len(result_data['results']) == 2
    
    def test_recall_case_insensitive(self):
        """测试大小写不敏感的搜索"""
        tool = RecallInfoTool()
        params = json.dumps({'query': '张三'})
        
        result = tool.call(params)
        result_data = json.loads(result)
        
        assert result_data['found'] is True
        assert result_data['count'] == 1
    
    def test_recall_invalid_json(self):
        """测试无效JSON参数"""
        tool = RecallInfoTool()
        params = "invalid json"
        
        result = tool.call(params)
        result_data = json.loads(result)
        
        assert 'error' in result_data
        assert '搜索失败' in result_data['error']


class TestCalculatorTool:
    """测试CalculatorTool工具类"""
    
    def test_simple_arithmetic(self):
        """测试简单算术运算"""
        tool = CalculatorTool()
        params = json.dumps({'expression': '2 + 3'})
        
        result = tool.call(params)
        result_data = json.loads(result)
        
        assert result_data['expression'] == '2 + 3'
        assert result_data['result'] == 5
    
    def test_complex_expression(self):
        """测试复杂表达式"""
        tool = CalculatorTool()
        params = json.dumps({'expression': '15 * 8 + 32'})
        
        result = tool.call(params)
        result_data = json.loads(result)
        
        assert result_data['expression'] == '15 * 8 + 32'
        assert result_data['result'] == 152
    
    def test_math_functions(self):
        """测试数学函数"""
        tool = CalculatorTool()
        params = json.dumps({'expression': 'sin(0)'})
        
        result = tool.call(params)
        result_data = json.loads(result)
        
        assert result_data['expression'] == 'sin(0)'
        assert abs(result_data['result'] - 0) < 1e-10
    
    def test_builtin_functions(self):
        """测试内建函数"""
        tool = CalculatorTool()
        params = json.dumps({'expression': 'abs(-5)'})
        
        result = tool.call(params)
        result_data = json.loads(result)
        
        assert result_data['expression'] == 'abs(-5)'
        assert result_data['result'] == 5
    
    def test_invalid_expression(self):
        """测试无效表达式"""
        tool = CalculatorTool()
        params = json.dumps({'expression': '2 +'})
        
        result = tool.call(params)
        result_data = json.loads(result)
        
        assert 'error' in result_data
        assert '计算错误' in result_data['error']
    
    def test_unsafe_expression(self):
        """测试不安全的表达式"""
        tool = CalculatorTool()
        # 尝试使用被禁止的函数
        params = json.dumps({'expression': '__import__("os")'})
        
        result = tool.call(params)
        result_data = json.loads(result)
        
        assert 'error' in result_data
        assert '计算错误' in result_data['error']
    
    def test_invalid_json(self):
        """测试无效JSON参数"""
        tool = CalculatorTool()
        params = "invalid json"
        
        result = tool.call(params)
        result_data = json.loads(result)
        
        assert 'error' in result_data
        assert '计算错误' in result_data['error']


class TestMemoryStore:
    """测试内存存储功能"""
    
    def test_get_memory_store(self):
        """测试获取内存存储"""
        memory_store = get_memory_store()
        
        assert isinstance(memory_store, dict)
        assert 'facts' in memory_store
        assert 'preferences' in memory_store
        assert 'history' in memory_store
    
    def test_memory_store_persistence(self):
        """测试内存存储的持久性"""
        memory_store1 = get_memory_store()
        memory_store2 = get_memory_store()
        
        # 应该是同一个对象
        assert memory_store1 is memory_store2 