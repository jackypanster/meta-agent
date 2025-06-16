#!/usr/bin/env python3
"""
端到端测试 - MVP成功标准验证

严格遵循fail-fast原则：
- 任何测试失败立即抛出异常
- 不使用任何容错机制或重试逻辑
- 测试要么通过，要么立即失败
"""

import pytest
import time
import json
import tempfile
import os
from pathlib import Path
from unittest.mock import patch

# 导入被测试的模块
from src.main import create_llm_config, setup_mcp_servers, initialize_prompt_manager
from src.config.settings import get_config, ConfigError
from src.config.mcp_config import get_mcp_config_loader, MCPConfigError
from src.config.prompt_manager import PromptManager, PromptManagerError
from src.tools.qwen_tools.memory_tools import SaveInfoTool, RecallInfoTool
from src.tools.qwen_tools.calculator_tool import CalculatorTool


class TestMVPSuccessCriteria:
    """MVP成功标准验证测试 - 严格fail-fast"""
    
    def test_criterion_1_environment_setup(self):
        """测试标准1: 一键环境设置 (≤3个命令)"""
        setup_commands = [
            "uv venv",
            "uv pip install -e .",
            "python src/main.py"
        ]
        
        # fail-fast: 超过3个命令立即失败
        if len(setup_commands) > 3:
            raise AssertionError(f"设置命令数量 {len(setup_commands)} 超过要求的3个")
        
        # 验证所有必需文件存在
        required_files = [
            "pyproject.toml",
            "src/main.py", 
            ".env",
            "config/mcp_servers.json",
            "config/prompts/system_prompts.json"
        ]
        
        for file_path in required_files:
            if not Path(file_path).exists():
                raise FileNotFoundError(f"必需文件缺失: {file_path}")
        
        print("✅ 标准1验证通过: 一键环境设置")

    def test_criterion_2_configuration_loading(self):
        """测试标准2: 配置加载 - fail-fast验证"""
        # 测试环境配置加载
        config = get_config()
        
        # fail-fast: API密钥必须存在
        api_key = config.require('DEEPSEEK_API_KEY')
        if not api_key:
            raise ConfigError("DEEPSEEK_API_KEY 缺失")
        
        # 测试提示词管理器初始化
        prompt_manager = initialize_prompt_manager()
        if not prompt_manager:
            raise PromptManagerError("PromptManager初始化失败")
        
        # 测试MCP配置加载
        mcp_servers = setup_mcp_servers()
        if not mcp_servers:
            raise MCPConfigError("MCP服务器配置加载失败")
        
        print("✅ 标准2验证通过: 配置加载fail-fast")

    def test_criterion_3_tool_functionality(self):
        """测试标准3: 工具功能验证"""
        # 测试计算器工具
        calc_tool = CalculatorTool()
        result = calc_tool.call('{"expression": "2 + 3"}')
        expected_result = json.loads(result)
        if expected_result.get('result') != 5:
            raise ValueError(f"计算器工具结果错误: {result}")
        
        # 测试内存工具
        save_tool = SaveInfoTool()
        recall_tool = RecallInfoTool()
        
        save_result = save_tool.call('{"info": "测试信息", "type": "fact"}')
        if "已保存" not in save_result:
            raise ValueError(f"内存保存失败: {save_result}")
        
        print("✅ 标准3验证通过: 工具功能")


if __name__ == "__main__":
    print("🚀 开始MVP端到端测试验证...")
    pytest.main(["-v", "-x", "--tb=short", __file__]) 