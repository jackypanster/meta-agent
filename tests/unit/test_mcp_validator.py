"""
MCP配置验证器单元测试
"""

import pytest
import tempfile
import json
from pathlib import Path
from src.config.mcp_validator import MCPConfigValidator, MCPValidationError


class TestMCPConfigValidator:
    """MCP配置验证器测试类"""
    
    @pytest.fixture
    def validator(self):
        """创建验证器实例"""
        return MCPConfigValidator()
    
    @pytest.fixture
    def valid_config(self):
        """有效的配置示例"""
        return {
            "version": "1.0",
            "servers": {
                "time": {
                    "command": "npx",
                    "args": ["@modelcontextprotocol/server-time"],
                    "enabled": True,
                    "timeout": 30,
                    "category": "utility"
                },
                "fetch": {
                    "command": "uvx",
                    "args": ["mcp-server-fetch"],
                    "enabled": True,
                    "timeout": 60
                }
            },
            "global_settings": {
                "default_timeout": 30,
                "retry_attempts": 3,
                "retry_delay": 1.0,
                "log_level": "INFO",
                "max_concurrent_servers": 10
            },
            "categories": {
                "utility": {
                    "description": "实用工具服务器",
                    "color": "blue"
                }
            },
            "metadata": {
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            }
        }
    
    @pytest.fixture
    def schema_file(self):
        """创建临时的JSON Schema文件"""
        schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "required": ["version", "servers", "global_settings"],
            "properties": {
                "version": {"type": "string"},
                "servers": {"type": "object"},
                "global_settings": {"type": "object"}
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(schema, f)
            return f.name
    
    def test_valid_config_passes_validation(self, validator, valid_config):
        """测试有效配置通过验证"""
        is_valid, errors = validator.validate_config(valid_config)
        assert is_valid
        assert len(errors) == 0
    
    def test_missing_required_fields(self, validator):
        """测试缺少必需字段的情况"""
        config = {"version": "1.0"}  # 缺少servers和global_settings
        
        is_valid, errors = validator.validate_config(config)
        assert not is_valid
        assert len(errors) > 0
        assert "servers" in errors[0] or "global_settings" in errors[0]
    
    def test_invalid_version_format(self, validator, valid_config):
        """测试无效的版本号格式"""
        valid_config["version"] = "invalid_version"
        
        is_valid, errors = validator.validate_config(valid_config)
        assert not is_valid
        assert "版本号格式无效" in errors[0]
    
    def test_empty_servers(self, validator, valid_config):
        """测试空的服务器配置"""
        valid_config["servers"] = {}
        
        is_valid, errors = validator.validate_config(valid_config)
        assert not is_valid
        assert "至少需要配置一个MCP服务器" in errors[0]
    
    def test_invalid_server_name(self, validator, valid_config):
        """测试无效的服务器名称"""
        # 添加一个以数字开头的服务器名称
        valid_config["servers"]["123invalid"] = {
            "command": "npx",
            "args": ["test"]
        }
        
        is_valid, errors = validator.validate_config(valid_config)
        assert not is_valid
        assert "服务器名称格式无效" in errors[0]
    
    def test_missing_server_command(self, validator, valid_config):
        """测试缺少服务器命令"""
        valid_config["servers"]["test"] = {
            "args": ["test"]  # 缺少command
        }
        
        is_valid, errors = validator.validate_config(valid_config)
        assert not is_valid
        assert "缺少必需字段: command" in errors[0]
    
    def test_missing_server_args(self, validator, valid_config):
        """测试缺少服务器参数"""
        valid_config["servers"]["test"] = {
            "command": "npx"  # 缺少args
        }
        
        is_valid, errors = validator.validate_config(valid_config)
        assert not is_valid
        assert "缺少必需字段: args" in errors[0]
    
    def test_invalid_server_args_type(self, validator, valid_config):
        """测试无效的服务器参数类型"""
        valid_config["servers"]["test"] = {
            "command": "npx",
            "args": "not_a_list"  # 应该是列表
        }
        
        is_valid, errors = validator.validate_config(valid_config)
        assert not is_valid
        assert "参数必须是数组" in errors[0]
    
    def test_invalid_timeout_value(self, validator, valid_config):
        """测试无效的超时值"""
        valid_config["global_settings"]["default_timeout"] = -1
        
        is_valid, errors = validator.validate_config(valid_config)
        assert not is_valid
        assert "默认超时时间无效" in errors[0]
    
    def test_invalid_retry_attempts(self, validator, valid_config):
        """测试无效的重试次数"""
        valid_config["global_settings"]["retry_attempts"] = -1
        
        is_valid, errors = validator.validate_config(valid_config)
        assert not is_valid
        assert "重试次数无效" in errors[0]
    
    def test_invalid_log_level(self, validator, valid_config):
        """测试无效的日志级别"""
        valid_config["global_settings"]["log_level"] = "INVALID"
        
        is_valid, errors = validator.validate_config(valid_config)
        assert not is_valid
        assert "日志级别无效" in errors[0]
    
    def test_category_consistency(self, validator, valid_config):
        """测试分类一致性验证"""
        # 服务器引用不存在的分类
        valid_config["servers"]["test"] = {
            "command": "npx",
            "args": ["test"],
            "category": "nonexistent"
        }
        
        is_valid, errors = validator.validate_config(valid_config)
        assert not is_valid
        assert "引用了不存在的分类" in errors[0]
    
    def test_schema_validation_with_file(self, validator, valid_config, schema_file):
        """测试使用Schema文件进行验证"""
        validator_with_schema = MCPConfigValidator(schema_file)
        
        is_valid, errors = validator_with_schema.validate_config(valid_config)
        assert is_valid
        assert len(errors) == 0
        
        # 清理临时文件
        Path(schema_file).unlink()
    
    def test_validation_error_with_suggestions(self, validator):
        """测试验证错误包含建议"""
        config = {"version": "1.0"}  # 缺少必需字段
        
        is_valid, errors = validator.validate_config(config)
        assert not is_valid
        assert len(errors) > 0
        
        # 验证错误信息包含建议
        error_msg = errors[0]
        assert "建议:" in error_msg or "请" in error_msg
    
    def test_validation_summary(self, validator, valid_config):
        """测试验证摘要功能"""
        summary = validator.get_validation_summary(valid_config)
        
        assert "total_servers" in summary
        assert "enabled_servers" in summary
        assert "disabled_servers" in summary
        assert "categories" in summary
        assert "version" in summary
        
        assert summary["total_servers"] == 2
        assert summary["enabled_servers"] == 2
        assert summary["disabled_servers"] == 0
        assert summary["categories"] == 1
        assert summary["version"] == "1.0"
    
    def test_server_timeout_validation(self, validator, valid_config):
        """测试服务器超时验证"""
        # 测试过长的超时时间
        valid_config["servers"]["time"]["timeout"] = 400  # 超过5分钟
        
        # 这应该通过验证但会有警告
        is_valid, errors = validator.validate_config(valid_config)
        assert is_valid  # 仍然有效，只是会有警告
    
    def test_environment_variables_validation(self, validator, valid_config):
        """测试环境变量验证"""
        valid_config["servers"]["test"] = {
            "command": "python",
            "args": ["test.py"],
            "env": {
                "API_KEY": "test_key",
                "DEBUG": "true"
            }
        }
        
        is_valid, errors = validator.validate_config(valid_config)
        assert is_valid
        
        # 测试无效的环境变量
        valid_config["servers"]["test"]["env"][""] = "invalid_name"
        
        is_valid, errors = validator.validate_config(valid_config)
        assert not is_valid
        assert "环境变量名无效" in errors[0]
    
    def test_multiple_validation_errors(self, validator):
        """测试多个验证错误的情况"""
        config = {
            "version": "invalid",  # 无效版本
            "servers": {},  # 空服务器
            "global_settings": {
                "default_timeout": -1  # 无效超时
            }
        }
        
        is_valid, errors = validator.validate_config(config)
        assert not is_valid
        # 应该只返回第一个错误（版本号错误）
        assert len(errors) == 1
        assert "版本号格式无效" in errors[0] 