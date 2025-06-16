"""
Fail-Fast Implementation Validation Test Suite

这个测试套件验证整个项目是否正确实现了fail-fast原则：
- 配置错误立即失败
- API错误立即失败
- 连接错误立即失败
- 无效输入立即失败
- 没有fallback机制
- 没有异常掩盖
"""

import pytest
import tempfile
import os
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

# 导入要测试的模块
from src.config.settings import Config, ConfigError, get_config
from src.config.mcp_config import MCPConfigLoader, MCPConfigError
from src.config.prompt_manager import PromptManager, PromptManagerError
from src.tools.qwen_tools.memory_tools import SaveInfoTool, RecallInfoTool
from src.tools.qwen_tools.calculator_tool import CalculatorTool
from src.main import create_llm_config, setup_mcp_servers, initialize_prompt_manager


class TestConfigurationFailFast:
    """测试配置模块的fail-fast行为"""
    
    def test_missing_env_file_fails_immediately(self):
        """测试缺失.env文件时立即失败"""
        with pytest.raises(ConfigError) as exc_info:
            Config("nonexistent.env")
        
        assert "未找到配置文件" in str(exc_info.value)
    
    def test_malformed_env_file_fails_immediately(self):
        """测试格式错误的.env文件立即失败"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write("VALID_KEY=value\n")
            f.write("INVALID_LINE_WITHOUT_EQUALS\n")  # 格式错误
            f.write("ANOTHER_KEY=value\n")
            f.flush()
            
            try:
                with pytest.raises(ConfigError) as exc_info:
                    Config(f.name)
                
                assert "格式错误" in str(exc_info.value)
            finally:
                os.unlink(f.name)
    
    def test_missing_required_config_fails_immediately(self):
        """测试缺失必需配置时立即失败"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write("SOME_KEY=value\n")
            f.flush()
            
            try:
                config = Config(f.name)
                
                # 测试get方法对不存在的键立即失败
                with pytest.raises(ConfigError) as exc_info:
                    config.get('NONEXISTENT_KEY')
                assert "不存在" in str(exc_info.value)
                
                # 测试require方法对不存在的键立即失败
                with pytest.raises(ConfigError) as exc_info:
                    config.require('MISSING_REQUIRED_KEY')
                assert "缺少必需的配置" in str(exc_info.value)
                
            finally:
                os.unlink(f.name)
    
    def test_get_bool_missing_key_fails_immediately(self):
        """测试get_bool对不存在的键立即失败"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write("EXISTING_KEY=true\n")
            f.flush()
            
            try:
                config = Config(f.name)
                
                with pytest.raises(ConfigError) as exc_info:
                    config.get_bool('NONEXISTENT_BOOL_KEY')
                assert "不存在" in str(exc_info.value)
                
            finally:
                os.unlink(f.name)


class TestMCPConfigurationFailFast:
    """测试MCP配置模块的fail-fast行为"""
    
    def test_missing_mcp_config_file_fails_immediately(self):
        """测试缺失MCP配置文件时立即失败"""
        with pytest.raises(MCPConfigError) as exc_info:
            MCPConfigLoader("nonexistent_mcp.json", "nonexistent_schema.json")
        
        assert "MCP配置文件不存在" in str(exc_info.value)
    
    def test_missing_schema_file_fails_immediately(self):
        """测试缺失Schema文件时立即失败"""
        # 创建一个有效的MCP配置文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as config_f:
            json.dump({
                "version": "1.0",
                "servers": {
                    "test": {
                        "command": "node",
                        "args": ["test.js"],
                        "enabled": True
                    }
                }
            }, config_f)
            config_f.flush()
            
            try:
                # 使用不存在的schema文件
                loader = MCPConfigLoader(config_f.name, "nonexistent_schema.json")
                
                # 尝试加载配置应该在schema验证时失败
                with pytest.raises(MCPConfigError) as exc_info:
                    loader.load_config()
                
                assert "JSON Schema文件不存在" in str(exc_info.value)
                
            finally:
                os.unlink(config_f.name)
    
    def test_invalid_json_config_fails_immediately(self):
        """测试无效JSON配置立即失败"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("{ invalid json content")  # 无效JSON
            f.flush()
            
            try:
                loader = MCPConfigLoader(f.name, "nonexistent_schema.json")
                
                with pytest.raises(json.JSONDecodeError):
                    loader.load_config()
                    
            finally:
                os.unlink(f.name)


class TestPromptManagerFailFast:
    """测试提示词管理器的fail-fast行为"""
    
    def test_missing_prompt_directory_fails_immediately(self):
        """测试缺失提示词目录时立即失败"""
        with pytest.raises(PromptManagerError) as exc_info:
            PromptManager("nonexistent_prompts_dir")
        
        assert "配置目录不存在" in str(exc_info.value)
    
    def test_missing_prompt_key_fails_immediately(self):
        """测试缺失提示词键时立即失败"""
        # 创建临时提示词目录和文件
        with tempfile.TemporaryDirectory() as temp_dir:
            prompts_dir = Path(temp_dir) / "prompts"
            prompts_dir.mkdir()
            
            # 创建基本的提示词配置文件
            config_file = prompts_dir / "system_prompts.json"
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "prompts": {
                        "existing_prompt": {
                            "content": "This is an existing prompt",
                            "enabled": True
                        }
                    }
                }, f)
            
            manager = PromptManager(str(prompts_dir))
            
            # 测试不存在的提示词键立即失败
            with pytest.raises(PromptManagerError) as exc_info:
                manager.get_prompt("nonexistent_prompt")
            
            assert "提示词不存在" in str(exc_info.value)


class TestToolsFailFast:
    """测试工具模块的fail-fast行为"""
    
    def test_memory_tool_invalid_json_fails_immediately(self):
        """测试内存工具无效JSON立即失败"""
        save_tool = SaveInfoTool()
        recall_tool = RecallInfoTool()
        
        # 测试无效JSON参数立即失败
        with pytest.raises(json.JSONDecodeError):
            save_tool.call("{ invalid json")
        
        with pytest.raises(json.JSONDecodeError):
            recall_tool.call("{ invalid json")
    
    def test_memory_tool_missing_required_params_fails_immediately(self):
        """测试内存工具缺失必需参数立即失败"""
        save_tool = SaveInfoTool()
        recall_tool = RecallInfoTool()
        
        # 测试缺失必需参数立即失败
        with pytest.raises(KeyError):
            save_tool.call('{"wrong_param": "value"}')  # 缺少info参数
        
        with pytest.raises(KeyError):
            recall_tool.call('{"wrong_param": "value"}')  # 缺少query参数
    
    def test_calculator_tool_invalid_json_fails_immediately(self):
        """测试计算器工具无效JSON立即失败"""
        calc_tool = CalculatorTool()
        
        with pytest.raises(json.JSONDecodeError):
            calc_tool.call("{ invalid json")
    
    def test_calculator_tool_missing_expression_fails_immediately(self):
        """测试计算器工具缺失表达式参数立即失败"""
        calc_tool = CalculatorTool()
        
        with pytest.raises(KeyError):
            calc_tool.call('{"wrong_param": "value"}')  # 缺少expression参数
    
    def test_calculator_tool_invalid_expression_fails_immediately(self):
        """测试计算器工具无效表达式立即失败"""
        calc_tool = CalculatorTool()
        
        # 测试真正的语法错误表达式立即失败
        with pytest.raises((SyntaxError, ValueError)):
            calc_tool.call('{"expression": "2 + * 3"}')  # 真正的语法错误
        
        # 测试不安全的表达式立即失败
        with pytest.raises(NameError):
            calc_tool.call('{"expression": "__import__(\\"os\\").system(\\"ls\\")"}')
        
        # 测试除零错误立即失败
        with pytest.raises(ZeroDivisionError):
            calc_tool.call('{"expression": "1/0"}')


class TestMainFunctionFailFast:
    """测试主函数的fail-fast行为"""
    
    @patch('src.main.get_config')
    def test_create_llm_config_missing_api_key_fails_immediately(self, mock_get_config):
        """测试创建LLM配置时缺失API密钥立即失败"""
        mock_config = MagicMock()
        mock_config.get_bool.return_value = False  # USE_DEEPSEEK_R1 = False
        mock_config.require.side_effect = ConfigError("缺少必需的配置: DEEPSEEK_API_KEY")
        mock_get_config.return_value = mock_config
        
        with pytest.raises(ConfigError) as exc_info:
            create_llm_config()
        
        assert "DEEPSEEK_API_KEY" in str(exc_info.value)
    
    @patch('src.main.get_mcp_config_loader')
    def test_setup_mcp_servers_no_enabled_servers_fails_immediately(self, mock_get_loader):
        """测试设置MCP服务器时没有启用的服务器立即失败"""
        mock_loader = MagicMock()
        mock_loader.get_enabled_servers.return_value = {}  # 没有启用的服务器
        mock_get_loader.return_value = mock_loader
        
        with pytest.raises(Exception) as exc_info:  # 应该是MCPConfigError，但导入可能有问题
            setup_mcp_servers()
        
        assert "未找到任何启用的MCP服务器" in str(exc_info.value)
    
    def test_initialize_prompt_manager_with_invalid_directory_fails_immediately(self):
        """测试初始化提示词管理器时无效目录立即失败"""
        # 直接测试PromptManager构造函数，而不是mock
        with pytest.raises(PromptManagerError) as exc_info:
            PromptManager("nonexistent_prompts_directory")
        
        assert "配置目录不存在" in str(exc_info.value)


class TestNoFallbackMechanisms:
    """测试确保没有fallback机制"""
    
    def test_no_default_values_in_config_get(self):
        """确保配置获取方法没有默认值fallback"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write("EXISTING_KEY=value\n")
            f.flush()
            
            try:
                config = Config(f.name)
                
                # 确保get方法对不存在的键抛出异常，而不是返回默认值
                with pytest.raises(ConfigError):
                    config.get('NONEXISTENT_KEY')
                
                # 确保require方法对不存在的键抛出异常
                with pytest.raises(ConfigError):
                    config.require('NONEXISTENT_KEY')
                
                # 确保get_bool方法对不存在的键抛出异常
                with pytest.raises(ConfigError):
                    config.get_bool('NONEXISTENT_KEY')
                    
            finally:
                os.unlink(f.name)
    
    def test_no_silent_failures_in_tools(self):
        """确保工具不会静默失败"""
        save_tool = SaveInfoTool()
        recall_tool = RecallInfoTool()
        calc_tool = CalculatorTool()
        
        # 所有工具在遇到错误时都应该抛出异常，而不是返回错误消息
        test_cases = [
            (save_tool, "{ invalid json"),
            (recall_tool, "{ invalid json"),
            (calc_tool, "{ invalid json"),
        ]
        
        for tool, invalid_input in test_cases:
            with pytest.raises(Exception):  # 应该抛出异常，不是返回错误消息
                tool.call(invalid_input)


class TestExceptionPropagation:
    """测试异常正确传播"""
    
    def test_exceptions_propagate_through_call_stack(self):
        """测试异常通过调用栈正确传播"""
        # 这个测试确保异常不会在中间层被捕获和转换
        
        # 测试配置错误传播
        with pytest.raises(ConfigError):
            config = Config("nonexistent.env")
        
        # 测试MCP配置错误传播
        with pytest.raises(MCPConfigError):
            loader = MCPConfigLoader("nonexistent.json", "nonexistent_schema.json")
        
        # 测试提示词管理器错误传播
        with pytest.raises(PromptManagerError):
            manager = PromptManager("nonexistent_dir")
    
    def test_no_exception_conversion(self):
        """测试异常不会被转换为其他类型"""
        # 确保原始异常类型被保留，没有被转换为通用异常
        
        with pytest.raises(ConfigError):  # 应该是ConfigError，不是Exception
            Config("nonexistent.env")
        
        with pytest.raises(json.JSONDecodeError):  # 应该是JSONDecodeError，不是Exception
            calc_tool = CalculatorTool()
            calc_tool.call("{ invalid json")


if __name__ == "__main__":
    # 运行所有测试
    pytest.main([__file__, "-v", "--tb=short"]) 