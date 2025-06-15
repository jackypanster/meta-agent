"""
测试MCP配置加载器
"""

import json
import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, mock_open

from src.config.mcp_config import MCPConfigLoader, MCPConfigError, get_mcp_config_loader, reset_mcp_config_loader


class TestMCPConfigLoader:
    """测试MCPConfigLoader类"""
    
    @pytest.fixture
    def sample_config(self):
        """示例配置数据"""
        return {
            "version": "1.0",
            "description": "测试配置",
            "servers": {
                "time": {
                    "command": "uvx",
                    "args": ["mcp-server-time"],
                    "enabled": True,
                    "description": "时间服务器",
                    "category": "utility",
                    "timeout": 30
                },
                "fetch": {
                    "command": "uvx",
                    "args": ["mcp-server-fetch"],
                    "enabled": True,
                    "description": "网页抓取服务器",
                    "category": "network",
                    "timeout": 60
                },
                "disabled_server": {
                    "command": "npx",
                    "args": ["-y", "some-server"],
                    "enabled": False,
                    "description": "禁用的服务器",
                    "category": "test"
                }
            },
            "global_settings": {
                "default_timeout": 30,
                "retry_attempts": 3,
                "retry_delay": 1.0,
                "log_level": "INFO"
            },
            "categories": {
                "utility": {"description": "实用工具", "color": "blue"},
                "network": {"description": "网络服务", "color": "green"}
            },
            "metadata": {
                "created_at": "2025-01-01T00:00:00Z",
                "author": "test"
            }
        }
    
    @pytest.fixture
    def sample_schema(self):
        """示例Schema数据"""
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "required": ["version", "servers", "global_settings"],
            "properties": {
                "version": {"type": "string"},
                "servers": {"type": "object"},
                "global_settings": {"type": "object"}
            }
        }
    
    @pytest.fixture
    def temp_config_files(self, sample_config, sample_schema):
        """创建临时配置文件"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "mcp_servers.json"
            schema_path = Path(temp_dir) / "mcp_servers_schema.json"
            
            # 写入配置文件
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(sample_config, f, indent=2)
            
            # 写入Schema文件
            with open(schema_path, 'w', encoding='utf-8') as f:
                json.dump(sample_schema, f, indent=2)
            
            yield str(config_path), str(schema_path)
    
    def test_init_with_existing_config(self, temp_config_files):
        """测试使用现有配置文件初始化"""
        config_path, schema_path = temp_config_files
        loader = MCPConfigLoader(config_path, schema_path)
        
        assert loader.config_path == Path(config_path)
        assert loader.schema_path == Path(schema_path)
        assert loader._config_cache is None
        assert loader._last_modified is None
    
    def test_init_with_missing_config(self):
        """测试配置文件不存在时的错误处理"""
        with pytest.raises(MCPConfigError, match="MCP配置文件不存在"):
            MCPConfigLoader("nonexistent.json")
    
    def test_load_config(self, temp_config_files, sample_config):
        """测试加载配置文件"""
        config_path, schema_path = temp_config_files
        loader = MCPConfigLoader(config_path, schema_path)
        
        config = loader.load_config()
        
        assert config["version"] == "1.0"
        assert "servers" in config
        assert "global_settings" in config
        assert loader._config_cache is not None
        assert loader._last_modified is not None
    
    def test_load_config_caching(self, temp_config_files):
        """测试配置缓存功能"""
        config_path, schema_path = temp_config_files
        loader = MCPConfigLoader(config_path, schema_path)
        
        # 第一次加载
        config1 = loader.load_config()
        first_load_time = loader._last_modified
        
        # 第二次加载（应该使用缓存）
        config2 = loader.load_config()
        second_load_time = loader._last_modified
        
        assert config1 is config2  # 应该是同一个对象
        assert first_load_time == second_load_time
    
    def test_force_reload(self, temp_config_files):
        """测试强制重新加载"""
        config_path, schema_path = temp_config_files
        loader = MCPConfigLoader(config_path, schema_path)
        
        # 第一次加载
        config1 = loader.load_config()
        
        # 强制重新加载
        config2 = loader.load_config(force_reload=True)
        
        # 内容基本相同（除了时间戳）
        assert config1["version"] == config2["version"]
        assert config1["servers"] == config2["servers"]
        assert config1 is not config2  # 但不是同一个对象
    
    def test_get_enabled_servers(self, temp_config_files):
        """测试获取启用的服务器"""
        config_path, schema_path = temp_config_files
        loader = MCPConfigLoader(config_path, schema_path)
        
        enabled_servers = loader.get_enabled_servers()
        
        assert len(enabled_servers) == 2  # time和fetch启用，disabled_server禁用
        assert "time" in enabled_servers
        assert "fetch" in enabled_servers
        assert "disabled_server" not in enabled_servers
    
    def test_get_server_config(self, temp_config_files):
        """测试获取特定服务器配置"""
        config_path, schema_path = temp_config_files
        loader = MCPConfigLoader(config_path, schema_path)
        
        # 获取启用的服务器
        time_config = loader.get_server_config("time")
        assert time_config is not None
        assert time_config["command"] == "uvx"
        assert time_config["category"] == "utility"
        
        # 获取禁用的服务器
        disabled_config = loader.get_server_config("disabled_server")
        assert disabled_config is None
        
        # 获取不存在的服务器
        nonexistent_config = loader.get_server_config("nonexistent")
        assert nonexistent_config is None
    
    def test_get_servers_by_category(self, temp_config_files):
        """测试按分类获取服务器"""
        config_path, schema_path = temp_config_files
        loader = MCPConfigLoader(config_path, schema_path)
        
        utility_servers = loader.get_servers_by_category("utility")
        assert len(utility_servers) == 1
        assert "time" in utility_servers
        
        network_servers = loader.get_servers_by_category("network")
        assert len(network_servers) == 1
        assert "fetch" in network_servers
        
        empty_category = loader.get_servers_by_category("nonexistent")
        assert len(empty_category) == 0
    
    def test_get_global_settings(self, temp_config_files):
        """测试获取全局设置"""
        config_path, schema_path = temp_config_files
        loader = MCPConfigLoader(config_path, schema_path)
        
        settings = loader.get_global_settings()
        
        assert settings["default_timeout"] == 30
        assert settings["retry_attempts"] == 3
        assert settings["log_level"] == "INFO"
    
    def test_list_server_names(self, temp_config_files):
        """测试列出服务器名称"""
        config_path, schema_path = temp_config_files
        loader = MCPConfigLoader(config_path, schema_path)
        
        # 只列出启用的服务器
        enabled_names = loader.list_server_names(enabled_only=True)
        assert set(enabled_names) == {"time", "fetch"}
        
        # 列出所有服务器
        all_names = loader.list_server_names(enabled_only=False)
        assert set(all_names) == {"time", "fetch", "disabled_server"}
    
    def test_is_server_enabled(self, temp_config_files):
        """测试检查服务器是否启用"""
        config_path, schema_path = temp_config_files
        loader = MCPConfigLoader(config_path, schema_path)
        
        assert loader.is_server_enabled("time") is True
        assert loader.is_server_enabled("fetch") is True
        assert loader.is_server_enabled("disabled_server") is False
        assert loader.is_server_enabled("nonexistent") is False
    
    def test_get_server_timeout(self, temp_config_files):
        """测试获取服务器超时设置"""
        config_path, schema_path = temp_config_files
        loader = MCPConfigLoader(config_path, schema_path)
        
        # 服务器有自定义超时
        assert loader.get_server_timeout("time") == 30
        assert loader.get_server_timeout("fetch") == 60
        
        # 禁用的服务器返回全局默认值
        assert loader.get_server_timeout("disabled_server") == 30
        
        # 不存在的服务器返回全局默认值
        assert loader.get_server_timeout("nonexistent") == 30
    
    def test_get_config_info(self, temp_config_files):
        """测试获取配置信息"""
        config_path, schema_path = temp_config_files
        loader = MCPConfigLoader(config_path, schema_path)
        
        info = loader.get_config_info()
        
        assert info["version"] == "1.0"
        assert info["total_servers"] == 3
        assert info["enabled_servers"] == 2
        assert set(info["enabled_server_names"]) == {"time", "fetch"}
        assert set(info["categories"]) == {"utility", "network"}
    
    def test_invalid_json(self, temp_config_files):
        """测试无效JSON格式的错误处理"""
        config_path, schema_path = temp_config_files
        
        # 写入无效JSON
        with open(config_path, 'w') as f:
            f.write("invalid json content")
        
        loader = MCPConfigLoader(config_path, schema_path)
        
        with pytest.raises(MCPConfigError, match="配置文件JSON格式错误"):
            loader.load_config()
    
    def test_schema_validation_error(self, temp_config_files):
        """测试Schema验证错误"""
        config_path, schema_path = temp_config_files
        
        # 写入不符合Schema的配置
        invalid_config = {"invalid": "config"}
        with open(config_path, 'w') as f:
            json.dump(invalid_config, f)
        
        loader = MCPConfigLoader(config_path, schema_path)
        
        with pytest.raises(MCPConfigError, match="配置文件格式错误"):
            loader.load_config()
    
    def test_reload_config(self, temp_config_files, sample_config):
        """测试重新加载配置"""
        config_path, schema_path = temp_config_files
        loader = MCPConfigLoader(config_path, schema_path)
        
        # 初始加载
        loader.load_config()
        
        # 修改配置文件
        modified_config = sample_config.copy()
        modified_config["version"] = "2.0"
        with open(config_path, 'w') as f:
            json.dump(modified_config, f)
        
        # 重新加载
        result = loader.reload_config()
        assert result is True
        
        # 验证配置已更新
        config = loader.load_config()
        assert config["version"] == "2.0"


class TestGlobalLoader:
    """测试全局配置加载器"""
    
    @pytest.fixture
    def sample_config(self):
        """示例配置数据"""
        return {
            "version": "1.0",
            "description": "测试配置",
            "servers": {
                "time": {
                    "command": "uvx",
                    "args": ["mcp-server-time"],
                    "enabled": True,
                    "description": "时间服务器",
                    "category": "utility",
                    "timeout": 30
                }
            },
            "global_settings": {
                "default_timeout": 30,
                "retry_attempts": 3,
                "retry_delay": 1.0,
                "log_level": "INFO"
            },
            "categories": {
                "utility": {"description": "实用工具", "color": "blue"}
            },
            "metadata": {
                "created_at": "2025-01-01T00:00:00Z",
                "author": "test"
            }
        }
    
    @pytest.fixture
    def sample_schema(self):
        """示例Schema数据"""
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "required": ["version", "servers", "global_settings"],
            "properties": {
                "version": {"type": "string"},
                "servers": {"type": "object"},
                "global_settings": {"type": "object"}
            }
        }
    
    @pytest.fixture
    def temp_config_files(self, sample_config, sample_schema):
        """创建临时配置文件"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "mcp_servers.json"
            schema_path = Path(temp_dir) / "mcp_servers_schema.json"
            
            # 写入配置文件
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(sample_config, f, indent=2)
            
            # 写入Schema文件
            with open(schema_path, 'w', encoding='utf-8') as f:
                json.dump(sample_schema, f, indent=2)
            
            yield str(config_path), str(schema_path)
    
    def teardown_method(self):
        """每个测试后重置全局加载器"""
        reset_mcp_config_loader()
    
    def test_get_global_loader(self, temp_config_files):
        """测试获取全局配置加载器"""
        config_path, schema_path = temp_config_files
        
        loader1 = get_mcp_config_loader(config_path, schema_path)
        loader2 = get_mcp_config_loader(config_path, schema_path)
        
        # 应该返回同一个实例
        assert loader1 is loader2
    
    def test_reset_global_loader(self, temp_config_files):
        """测试重置全局配置加载器"""
        config_path, schema_path = temp_config_files
        
        loader1 = get_mcp_config_loader(config_path, schema_path)
        reset_mcp_config_loader()
        loader2 = get_mcp_config_loader(config_path, schema_path)
        
        # 重置后应该是不同的实例
        assert loader1 is not loader2 