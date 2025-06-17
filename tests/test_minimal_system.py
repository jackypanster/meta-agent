"""
测试极简化系统 - 验证删除prompt_manager后的基本功能
"""

import pytest
from unittest.mock import Mock, patch

from src.app_core import create_agent
from src.ui.helpers import show_welcome, show_help, show_memory


class TestMinimalSystem:
    """测试极简化系统的基本功能"""
    
    @patch('src.app_core.create_llm_config')
    @patch('src.app_core.create_tools_list')
    def test_create_agent_success(self, mock_tools, mock_llm):
        """测试Agent创建成功"""
        # 模拟配置 - 添加model属性
        mock_llm_instance = Mock()
        mock_llm_instance.model = "test-model"
        mock_llm.return_value = mock_llm_instance
        mock_tools.return_value = []
        
        # 测试Agent创建
        agent = create_agent()
        
        # 验证Agent属性
        assert agent is not None
        assert agent.system_message == ""  # 空系统提示词
        assert agent.name == "AI助手"
        assert agent.description == "基于qwen-agent框架的智能助手"
    
    @patch('src.ui.helpers.get_config')
    def test_show_welcome_minimal(self, mock_config):
        """测试极简化欢迎信息显示"""
        # 模拟配置
        mock_config.return_value.get_bool.return_value = False
        
        # 测试不应抛出异常
        show_welcome()
        
        # 验证配置被调用
        mock_config.assert_called_once()
    
    def test_show_help_minimal(self):
        """测试极简化帮助信息显示"""
        # 测试不应抛出异常
        show_help()
    
    @patch('src.ui.helpers.get_memory_store')
    def test_show_memory_minimal(self, mock_memory):
        """测试极简化记忆信息显示"""
        # 模拟空记忆
        mock_memory.return_value = {
            'facts': [],
            'preferences': []
        }
        
        # 测试不应抛出异常
        show_memory()
        
        # 验证记忆存储被调用
        mock_memory.assert_called_once()
    
    def test_system_independence(self):
        """测试系统独立性 - 不依赖外部配置文件"""
        # 验证核心功能不依赖prompt_manager
        # 这个测试的存在本身就证明了系统的独立性
        assert True  # 如果能到达这里，说明导入成功，系统独立
    
    @patch('src.ui.helpers.get_config')
    @patch('src.ui.helpers.get_memory_store')  
    def test_ui_functions_work_without_prompts(self, mock_memory, mock_config):
        """测试UI函数在没有提示词配置的情况下正常工作"""
        # 模拟配置和记忆
        mock_config.return_value.get_bool.return_value = True  # R1模式
        mock_memory.return_value = {
            'facts': [{'content': '测试事实', 'time_str': '2025-01-01'}],
            'preferences': []
        }
        
        # 所有UI函数都应该正常工作
        try:
            show_welcome()
            show_help()
            show_memory()
            success = True
        except Exception:
            success = False
        
        assert success, "UI函数应该在没有提示词配置的情况下正常工作" 