"""
MCP配置集成测试

验证main.py与MCP配置系统的集成
"""

import pytest
import sys
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

# 确保src目录在Python路径中
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from src.main import setup_mcp_servers, create_tools_list, MCPConfigError
from src.config.mcp_config import get_mcp_config_loader, reset_mcp_config_loader


class TestMCPIntegration:
    """MCP配置集成测试类"""
    
    def setup_method(self):
        """每个测试前的设置"""
        # 重置全局配置加载器
        reset_mcp_config_loader()
    
    def test_mcp_config_loading_with_valid_config(self):
        """测试有效配置的加载"""
        # 确保配置文件存在
        config_file = Path("config/mcp_servers.json")
        assert config_file.exists(), "配置文件不存在"
        
        # 测试配置加载
        mcp_servers = setup_mcp_servers()
        
        # 验证结果
        assert isinstance(mcp_servers, dict)
        assert len(mcp_servers) > 0
        
        # 验证每个服务器配置格式
        for server_name, server_config in mcp_servers.items():
            assert 'command' in server_config
            assert 'args' in server_config
            assert isinstance(server_config['args'], list)
    
    def test_tools_list_creation(self):
        """测试工具列表创建"""
        tools = create_tools_list()
        
        # 验证工具列表结构
        assert isinstance(tools, list)
        assert len(tools) >= 4  # 至少包含基本工具
        
        # 查找MCP服务器配置
        mcp_tool = None
        for tool in tools:
            if isinstance(tool, dict) and 'mcpServers' in tool:
                mcp_tool = tool
                break
        
        assert mcp_tool is not None, "未找到MCP服务器配置"
        assert 'mcpServers' in mcp_tool
        assert len(mcp_tool['mcpServers']) > 0
    
    def test_fallback_behavior_when_config_missing(self):
        """测试配置文件缺失时的后备行为"""
        # 临时移动配置文件
        config_file = Path("config/mcp_servers.json")
        backup_file = Path("config/mcp_servers.json.backup")
        
        if config_file.exists():
            config_file.rename(backup_file)
        
        try:
            # 重置配置加载器以触发重新加载
            reset_mcp_config_loader()
            
            # 测试后备配置
            mcp_servers = setup_mcp_servers()
            
            # 验证后备配置
            assert isinstance(mcp_servers, dict)
            assert len(mcp_servers) > 0
            
            # 验证包含基本服务器
            expected_servers = ['time', 'fetch', 'memory']
            for server in expected_servers:
                assert server in mcp_servers
            
        finally:
            # 恢复配置文件
            if backup_file.exists():
                backup_file.rename(config_file)
    
    def test_server_configuration_format(self):
        """测试服务器配置格式"""
        config_loader = get_mcp_config_loader()
        enabled_servers = config_loader.get_enabled_servers()
        
        for server_name, server_config in enabled_servers.items():
            # 验证必需字段
            assert 'command' in server_config
            assert 'args' in server_config
            
            # 验证字段类型
            assert isinstance(server_config['command'], str)
            assert isinstance(server_config['args'], list)
            
            # 验证可选字段
            if 'enabled' in server_config:
                assert isinstance(server_config['enabled'], bool)
            
            if 'timeout' in server_config:
                assert isinstance(server_config['timeout'], (int, float))
                assert server_config['timeout'] > 0
            
            if 'category' in server_config:
                assert isinstance(server_config['category'], str)
    
    def test_qwen_agent_format_conversion(self):
        """测试转换为Qwen-Agent格式"""
        mcp_servers = setup_mcp_servers()
        
        # 验证Qwen-Agent格式
        for server_name, server_config in mcp_servers.items():
            # 必需字段
            assert 'command' in server_config
            assert 'args' in server_config
            
            # 验证类型
            assert isinstance(server_config['command'], str)
            assert isinstance(server_config['args'], list)
            
            # 验证args中的所有元素都是字符串
            for arg in server_config['args']:
                assert isinstance(arg, str)
            
            # 可选的环境变量字段
            if 'env' in server_config:
                assert isinstance(server_config['env'], dict)
    
    def test_error_handling_graceful_degradation(self):
        """测试错误处理和优雅降级"""
        # 模拟配置加载错误
        with patch('src.config.mcp_config.get_mcp_config_loader') as mock_loader:
            mock_loader.side_effect = Exception("模拟错误")
            
            # 应该返回默认配置而不是抛出异常
            mcp_servers = setup_mcp_servers()
            
            assert isinstance(mcp_servers, dict)
            assert len(mcp_servers) > 0
            
            # 验证包含基本服务器
            expected_servers = ['time', 'fetch', 'memory']
            for server in expected_servers:
                assert server in mcp_servers
    
    def test_tools_list_with_fallback(self):
        """测试工具列表在后备模式下的创建"""
        # 模拟MCP配置错误
        with patch('src.main.setup_mcp_servers') as mock_setup:
            mock_setup.side_effect = MCPConfigError("模拟配置错误")
            
            # 应该返回基本工具列表
            tools = create_tools_list()
            
            assert isinstance(tools, list)
            assert len(tools) >= 4  # 基本工具数量
            
            # 验证包含基本工具
            tool_names = [tool for tool in tools if isinstance(tool, str)]
            assert 'custom_save_info' in tool_names
            assert 'custom_recall_info' in tool_names
            assert 'custom_math_calc' in tool_names
            assert 'code_interpreter' in tool_names
    
    def test_configuration_validation_integration(self):
        """测试配置验证集成"""
        config_loader = get_mcp_config_loader()
        
        # 加载配置
        config = config_loader.load_config()
        
        # 验证配置结构
        assert 'version' in config
        assert 'servers' in config
        assert 'global_settings' in config
        
        # 验证服务器配置
        servers = config['servers']
        assert len(servers) > 0
        
        for server_name, server_config in servers.items():
            assert 'command' in server_config
            assert 'args' in server_config
    
    def test_enabled_servers_filtering(self):
        """测试启用服务器的过滤"""
        config_loader = get_mcp_config_loader()
        
        # 获取所有服务器
        all_servers = config_loader.load_config()['servers']
        
        # 获取启用的服务器
        enabled_servers = config_loader.get_enabled_servers()
        
        # 验证过滤逻辑
        for server_name, server_config in all_servers.items():
            is_enabled = server_config.get('enabled', True)  # 默认启用
            
            if is_enabled:
                assert server_name in enabled_servers
            else:
                assert server_name not in enabled_servers
    
    def test_server_timeout_handling(self):
        """测试服务器超时处理"""
        config_loader = get_mcp_config_loader()
        enabled_servers = config_loader.get_enabled_servers()
        
        for server_name in enabled_servers:
            timeout = config_loader.get_server_timeout(server_name)
            assert isinstance(timeout, (int, float))
            assert timeout > 0
    
    def test_config_info_retrieval(self):
        """测试配置信息获取"""
        config_loader = get_mcp_config_loader()
        config_info = config_loader.get_config_info()
        
        # 验证配置信息结构
        required_fields = [
            'config_path', 'version', 'total_servers', 
            'enabled_servers', 'enabled_server_names'
        ]
        
        for field in required_fields:
            assert field in config_info
        
        # 验证数据类型
        assert isinstance(config_info['total_servers'], int)
        assert isinstance(config_info['enabled_servers'], int)
        assert isinstance(config_info['enabled_server_names'], list)
        assert config_info['enabled_servers'] <= config_info['total_servers'] 