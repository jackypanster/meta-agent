"""
配置管理的单元测试

测试从.env文件直接加载配置的功能。
"""

import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from config.settings import Config, ConfigError, get_config, reload_config


class TestConfig:
    """测试Config配置类"""
    
    def test_load_valid_env_file(self):
        """测试加载有效的.env文件"""
        env_content = """
# 测试配置文件
DEEPSEEK_API_KEY=sk-test-123
OPENROUTER_API_KEY=sk-or-test-456
USE_DEEPSEEK_R1=true
DEBUG=false
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write(env_content)
            f.flush()
            
            try:
                config = Config(f.name)
                
                assert config.get('DEEPSEEK_API_KEY') == 'sk-test-123'
                assert config.get('OPENROUTER_API_KEY') == 'sk-or-test-456'
                assert config.get_bool('USE_DEEPSEEK_R1') is True
                assert config.get_bool('DEBUG') is False
                
            finally:
                os.unlink(f.name)
    
    def test_load_env_with_quotes(self):
        """测试处理带引号的配置值"""
        env_content = '''
API_KEY_1="sk-test-with-double-quotes"
API_KEY_2='sk-test-with-single-quotes'
NORMAL_KEY=sk-test-without-quotes
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write(env_content)
            f.flush()
            
            try:
                config = Config(f.name)
                
                assert config.get('API_KEY_1') == 'sk-test-with-double-quotes'
                assert config.get('API_KEY_2') == 'sk-test-with-single-quotes'
                assert config.get('NORMAL_KEY') == 'sk-test-without-quotes'
                
            finally:
                os.unlink(f.name)
    
    def test_skip_comments_and_empty_lines(self):
        """测试跳过注释和空行"""
        env_content = """
# 这是注释行
API_KEY=sk-test-123

# 另一个注释
ANOTHER_KEY=value

"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write(env_content)
            f.flush()
            
            try:
                config = Config(f.name)
                
                assert config.get('API_KEY') == 'sk-test-123'
                assert config.get('ANOTHER_KEY') == 'value'
                
                # 确保只有这两个配置
                all_config = config.list_all()
                assert len(all_config) == 2
                
            finally:
                os.unlink(f.name)
    
    def test_missing_env_file(self):
        """测试.env文件不存在的情况"""
        with pytest.raises(ConfigError) as exc_info:
            Config("nonexistent.env")
        
        assert "未找到配置文件" in str(exc_info.value)
    
    def test_get_method(self):
        """测试get方法"""
        env_content = "EXISTING_KEY=existing_value"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write(env_content)
            f.flush()
            
            try:
                config = Config(f.name)
                
                # 测试存在的键
                assert config.get('EXISTING_KEY') == 'existing_value'
                
                # 测试不存在的键
                assert config.get('NONEXISTENT_KEY') is None
                
                # 测试带默认值的情况
                assert config.get('NONEXISTENT_KEY', 'default') == 'default'
                
            finally:
                os.unlink(f.name)
    
    def test_require_method(self):
        """测试require方法"""
        env_content = "REQUIRED_KEY=required_value"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write(env_content)
            f.flush()
            
            try:
                config = Config(f.name)
                
                # 测试存在的必需键
                assert config.require('REQUIRED_KEY') == 'required_value'
                
                # 测试不存在的必需键
                with pytest.raises(ConfigError) as exc_info:
                    config.require('MISSING_REQUIRED_KEY')
                
                assert "缺少必需的配置" in str(exc_info.value)
                
            finally:
                os.unlink(f.name)
    
    def test_get_bool_method(self):
        """测试get_bool方法"""
        env_content = """
TRUE_1=true
TRUE_2=True
TRUE_3=1
TRUE_4=yes
TRUE_5=YES
TRUE_6=on
FALSE_1=false
FALSE_2=False
FALSE_3=0
FALSE_4=no
FALSE_5=off
EMPTY_VALUE=
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write(env_content)
            f.flush()
            
            try:
                config = Config(f.name)
                
                # 测试真值
                assert config.get_bool('TRUE_1') is True
                assert config.get_bool('TRUE_2') is True
                assert config.get_bool('TRUE_3') is True
                assert config.get_bool('TRUE_4') is True
                assert config.get_bool('TRUE_5') is True
                assert config.get_bool('TRUE_6') is True
                
                # 测试假值
                assert config.get_bool('FALSE_1') is False
                assert config.get_bool('FALSE_2') is False
                assert config.get_bool('FALSE_3') is False
                assert config.get_bool('FALSE_4') is False
                assert config.get_bool('FALSE_5') is False
                assert config.get_bool('EMPTY_VALUE') is False
                
                # 测试不存在的键
                assert config.get_bool('NONEXISTENT') is False
                assert config.get_bool('NONEXISTENT', True) is True
                
            finally:
                os.unlink(f.name)
    
    def test_malformed_line_warning(self, capsys):
        """测试格式错误的行会产生警告"""
        env_content = """
VALID_KEY=valid_value
malformed line without equals
ANOTHER_KEY=another_value
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write(env_content)
            f.flush()
            
            try:
                config = Config(f.name)
                
                # 检查有效配置加载成功
                assert config.get('VALID_KEY') == 'valid_value'
                assert config.get('ANOTHER_KEY') == 'another_value'
                
                # 检查警告输出
                captured = capsys.readouterr()
                assert "警告" in captured.out
                assert "格式错误" in captured.out
                
            finally:
                os.unlink(f.name)


class TestGlobalConfig:
    """测试全局配置函数"""
    
    def test_get_config_singleton(self):
        """测试get_config返回单例"""
        # 重置全局实例
        reload_config()
        
        config1 = get_config()
        config2 = get_config()
        
        # 应该是同一个实例
        assert config1 is config2
    
    def test_reload_config(self):
        """测试重新加载配置"""
        config1 = get_config()
        config2 = reload_config()
        
        # 应该是不同的实例
        assert config1 is not config2
        
        # 后续调用应该返回新实例
        config3 = get_config()
        assert config2 is config3


class TestConfigIntegration:
    """测试配置集成场景"""
    
    def test_deepseek_config_scenario(self):
        """测试DeepSeek配置场景"""
        env_content = """
DEEPSEEK_API_KEY=sk-da85e6f63dc1462eb575e0d4357ab63e
USE_DEEPSEEK_R1=true
OPENROUTER_API_KEY=sk-or-v1-test
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write(env_content)
            f.flush()
            
            try:
                config = Config(f.name)
                
                # 验证DeepSeek配置
                assert config.require('DEEPSEEK_API_KEY') == 'sk-da85e6f63dc1462eb575e0d4357ab63e'
                assert config.get_bool('USE_DEEPSEEK_R1') is True
                assert config.get('OPENROUTER_API_KEY') == 'sk-or-v1-test'
                
            finally:
                os.unlink(f.name)

 