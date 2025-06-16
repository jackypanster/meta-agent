"""
基本功能测试

验证项目的基本功能和配置加载。
"""

import pytest
import tempfile
import os
from pathlib import Path

from src.config.settings import Config, ConfigError


class TestBasicFunctionality:
    """测试基本功能"""
    
    def test_config_loading_with_valid_env(self):
        """测试有效环境变量的配置加载"""
        # 创建临时.env文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write("DEEPSEEK_API_KEY=test_key_123\n")
            f.write("USE_DEEPSEEK_R1=true\n")
            temp_env_path = f.name
        
        try:
            # 测试配置加载
            config = Config(temp_env_path)
            
            # 验证配置值
            assert config.require("DEEPSEEK_API_KEY") == "test_key_123"
            assert config.get_bool("USE_DEEPSEEK_R1") is True
            
        finally:
            # 清理临时文件
            os.unlink(temp_env_path)
    
    def test_config_fails_fast_on_missing_file(self):
        """测试缺失配置文件时立即失败"""
        with pytest.raises(ConfigError, match="未找到配置文件"):
            Config("nonexistent.env")
    
    def test_config_fails_fast_on_missing_required_key(self):
        """测试缺失必需配置键时立即失败"""
        # 创建空的.env文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write("# 空配置文件\n")
            temp_env_path = f.name
        
        try:
            config = Config(temp_env_path)
            
            # 测试获取不存在的必需键立即失败
            with pytest.raises(ConfigError, match="缺少必需的配置"):
                config.require("DEEPSEEK_API_KEY")
                
        finally:
            # 清理临时文件
            os.unlink(temp_env_path)
    
    def test_config_boolean_parsing(self):
        """测试布尔值解析"""
        # 创建包含布尔值的.env文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write("BOOL_TRUE=true\n")
            f.write("BOOL_FALSE=false\n")
            f.write("BOOL_YES=yes\n")
            f.write("BOOL_NO=no\n")
            f.write("BOOL_1=1\n")
            f.write("BOOL_0=0\n")
            temp_env_path = f.name
        
        try:
            config = Config(temp_env_path)
            
            # 验证布尔值解析
            assert config.get_bool("BOOL_TRUE") is True
            assert config.get_bool("BOOL_FALSE") is False
            assert config.get_bool("BOOL_YES") is True
            assert config.get_bool("BOOL_NO") is False
            assert config.get_bool("BOOL_1") is True
            assert config.get_bool("BOOL_0") is False
            
        finally:
            # 清理临时文件
            os.unlink(temp_env_path)


class TestProjectStructure:
    """测试项目结构"""
    
    def test_required_files_exist(self):
        """测试必需文件存在"""
        project_root = Path(__file__).parent.parent
        
        # 检查关键文件存在
        assert (project_root / "src" / "main.py").exists()
        assert (project_root / "src" / "config" / "settings.py").exists()
        assert (project_root / "config" / "mcp_servers.json").exists()
        assert (project_root / "env.template").exists()
        assert (project_root / "README.md").exists()
        assert (project_root / "pyproject.toml").exists()
    
    def test_src_directory_structure(self):
        """测试src目录结构"""
        project_root = Path(__file__).parent.parent
        src_dir = project_root / "src"
        
        # 检查src目录结构
        assert (src_dir / "config").is_dir()
        assert (src_dir / "tools").is_dir()
        assert (src_dir / "ui").is_dir()
        
        # 检查配置模块文件
        config_dir = src_dir / "config"
        assert (config_dir / "settings.py").exists()
        assert (config_dir / "mcp_config.py").exists()
        assert (config_dir / "prompt_manager.py").exists()
        
        # 检查工具模块文件
        tools_dir = src_dir / "tools" / "qwen_tools"
        assert (tools_dir / "calculator_tool.py").exists()
        assert (tools_dir / "memory_tools.py").exists()


class TestFailFastPrinciples:
    """测试fail-fast原则"""
    
    def test_config_get_fails_on_missing_key(self):
        """测试配置get方法对不存在的键立即失败"""
        # 创建空配置文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write("# 空配置\n")
            temp_env_path = f.name
        
        try:
            config = Config(temp_env_path)
            
            # 测试get方法对不存在的键立即失败
            with pytest.raises(ConfigError, match="配置.*不存在"):
                config.get("NONEXISTENT_KEY")
            
            # 测试require方法对不存在的键立即失败
            with pytest.raises(ConfigError, match="缺少必需的配置"):
                config.require("NONEXISTENT_KEY")
                
        finally:
            os.unlink(temp_env_path)
    
    def test_config_format_errors_fail_immediately(self):
        """测试配置格式错误立即失败"""
        # 创建格式错误的.env文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write("VALID_KEY=valid_value\n")
            f.write("INVALID_LINE_WITHOUT_EQUALS\n")  # 无效行
            f.write("ANOTHER_VALID=value\n")
            temp_env_path = f.name
        
        try:
            # 配置加载应该立即失败
            with pytest.raises(ConfigError, match="格式错误"):
                Config(temp_env_path)
                
        finally:
            os.unlink(temp_env_path) 