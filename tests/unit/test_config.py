"""配置模块单元测试"""

import os
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
from pydantic import ValidationError

from src.config import (
    Settings, DeepSeekConfig, McpConfig, AppConfig,
    EnvironmentLoader, ConfigValidator, ConfigValidationError,
    ConfigManager
)


class TestDeepSeekConfig:
    """测试DeepSeek配置模型"""
    
    def test_valid_config(self):
        """测试有效配置"""
        config = DeepSeekConfig(api_key="sk-test1234567890")
        assert config.api_key == "sk-test1234567890"
        assert config.model_name == "deepseek-reasoner"
        assert config.max_tokens == 4000
    
    def test_invalid_api_key(self):
        """测试无效API密钥"""
        with pytest.raises(ValidationError):
            DeepSeekConfig(api_key="")
        
        with pytest.raises(ValidationError):
            DeepSeekConfig(api_key="short")


class TestEnvironmentLoader:
    """测试环境变量加载器"""
    
    def setup_method(self):
        """测试前设置"""
        self.loader = EnvironmentLoader()
    
    @patch.dict(os.environ, {"DEEPSEEK_API_KEY": "sk-test1234567890"})
    def test_load_settings_success(self):
        """测试成功加载配置"""
        # 模拟没有.env文件
        with patch.object(self.loader, 'load_env_file', return_value=False):
            settings = self.loader.load_settings()
            assert isinstance(settings, Settings)
            assert settings.deepseek.api_key == "sk-test1234567890"
    
    def test_missing_required_env_var(self):
        """测试缺少必需环境变量"""
        # 模拟没有.env文件且没有环境变量
        with patch.object(self.loader, 'load_env_file', return_value=False):
            with patch.dict(os.environ, {}, clear=True):
                with pytest.raises(ValueError, match="必需的环境变量"):
                    self.loader.load_settings()
    
    @patch.dict(os.environ, {
        "DEEPSEEK_API_KEY": "sk-test1234567890",
        "DEEPSEEK_MAX_TOKENS": "invalid"
    })
    def test_invalid_numeric_env_var(self):
        """测试无效数值环境变量使用默认值"""
        with patch.object(self.loader, 'load_env_file', return_value=False):
            settings = self.loader.load_settings()
            assert settings.deepseek.max_tokens == 4000  # 默认值


class TestConfigValidator:
    """测试配置验证器"""
    
    def setup_method(self):
        """测试前设置"""
        self.validator = ConfigValidator()
    
    def test_validate_api_key_success(self):
        """测试API密钥验证成功"""
        assert self.validator.validate_api_key("sk-test1234567890", "Test") is True
        assert len(self.validator.errors) == 0
    
    def test_validate_api_key_failure(self):
        """测试API密钥验证失败"""
        assert self.validator.validate_api_key("", "Test") is False
        assert len(self.validator.errors) == 1
        assert "API密钥不能为空" in self.validator.errors[0].message
    
    def test_validate_url_success(self):
        """测试URL验证成功"""
        assert self.validator.validate_url("https://api.example.com", "test_url") is True
        assert len(self.validator.errors) == 0
    
    def test_validate_url_failure(self):
        """测试URL验证失败"""
        assert self.validator.validate_url("invalid-url", "test_url") is False
        assert len(self.validator.errors) == 1


class TestConfigManager:
    """测试配置管理器"""
    
    def setup_method(self):
        """测试前设置"""
        self.manager = ConfigManager()
    
    @patch.dict(os.environ, {"DEEPSEEK_API_KEY": "sk-test1234567890"})
    def test_initialize_success(self):
        """测试初始化成功"""
        with patch.object(self.manager._loader, 'load_env_file', return_value=False):
            self.manager.initialize()
            assert self.manager._initialized is True
            assert self.manager.settings is not None
    
    def test_initialize_failure(self):
        """测试初始化失败"""
        # 模拟没有.env文件且没有环境变量
        with patch.object(self.manager._loader, 'load_env_file', return_value=False):
            with patch.dict(os.environ, {}, clear=True):
                with pytest.raises((ValueError, ConfigValidationError)):
                    self.manager.initialize()
    
    @patch.dict(os.environ, {"DEEPSEEK_API_KEY": "sk-test1234567890"})
    def test_property_access(self):
        """测试属性访问"""
        with patch.object(self.manager._loader, 'load_env_file', return_value=False):
            self.manager.initialize()
            assert self.manager.deepseek.api_key == "sk-test1234567890"
            assert self.manager.mcp.timeout == 30
            assert self.manager.app.log_level == "INFO" 