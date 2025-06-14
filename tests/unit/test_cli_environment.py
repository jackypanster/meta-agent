"""环境变量模块的单元测试"""

import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from src.cli.environment import (
    _validate_required_variables,
    load_environment,
    show_setup_instructions,
)


@pytest.mark.unit
class TestLoadEnvironment:
    """测试环境变量加载功能"""

    @patch("src.cli.environment.load_dotenv")
    @patch("src.cli.environment.console")
    def test_load_environment_success(self, mock_console, mock_load_dotenv):
        """测试成功加载环境变量"""
        # 创建临时.env文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write("DEEPSEEK_API_KEY=test-key\n")
            f.write("MCP_SERVER_URL=test-url\n")
            temp_env_path = f.name

        # Mock Path.exists() 返回True
        with patch("src.cli.environment.Path") as mock_path:
            mock_path.return_value.parent.parent.parent = Path(temp_env_path).parent
            mock_path.return_value.parent.parent.parent.__truediv__.return_value.exists.return_value = True
            
            # Mock环境变量
            with patch.dict(os.environ, {
                "DEEPSEEK_API_KEY": "test-key",
                "MCP_SERVER_URL": "test-url"
            }):
                result = load_environment()
                
        assert result is True
        mock_console.print.assert_called()
        
        # 清理
        os.unlink(temp_env_path)

    @patch("src.cli.environment.console")
    def test_load_environment_no_file(self, mock_console):
        """测试.env文件不存在的情况"""
        with patch("src.cli.environment.Path") as mock_path:
            mock_path.return_value.parent.parent.parent.__truediv__.return_value.exists.return_value = False
            
            result = load_environment()
            
        assert result is False
        mock_console.print.assert_called_with(
            "⚠️ No .env file found. Please copy .env.example to .env and configure it.",
            style="yellow"
        )


@pytest.mark.unit
class TestValidateRequiredVariables:
    """测试环境变量验证功能"""

    @patch("src.cli.environment.console")
    def test_validate_with_valid_variables(self, mock_console):
        """测试有效环境变量验证"""
        with patch.dict(os.environ, {
            "DEEPSEEK_API_KEY": "valid-key",
            "MCP_SERVER_URL": "valid-url"
        }):
            result = _validate_required_variables()
            
        assert result is True

    @patch("src.cli.environment.console")
    def test_validate_with_missing_variables(self, mock_console):
        """测试缺少环境变量的验证"""
        with patch.dict(os.environ, {}, clear=True):
            result = _validate_required_variables()
            
        assert result is False
        mock_console.print.assert_called_with(
            "❌ Missing or not configured: DEEPSEEK_API_KEY, MCP_SERVER_URL",
            style="red"
        )

    @patch("src.cli.environment.console")
    def test_validate_with_placeholder_values(self, mock_console):
        """测试占位符值的验证"""
        with patch.dict(os.environ, {
            "DEEPSEEK_API_KEY": "your_deepseek_api_key_here",
            "MCP_SERVER_URL": "valid-url"
        }):
            result = _validate_required_variables()
            
        assert result is False


@pytest.mark.unit
class TestShowSetupInstructions:
    """测试设置指导显示功能"""

    @patch("src.cli.environment.console")
    def test_show_setup_instructions(self, mock_console):
        """测试显示设置指导"""
        show_setup_instructions()
        
        expected_calls = [
            (("\n💡 Setup instructions:",), {}),
            (("1. Copy .env.example to .env: cp .env.example .env",), {}),
            (("2. Edit .env with your actual API keys",), {}),
            (("3. Restart the application",), {})
        ]
        
        assert mock_console.print.call_count == 4
        for i, (args, kwargs) in enumerate(expected_calls):
            assert mock_console.print.call_args_list[i] == (args, kwargs) 