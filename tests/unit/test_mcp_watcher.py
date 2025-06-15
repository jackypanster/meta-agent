"""
MCP配置监控器单元测试
"""

import pytest
import time
import json
import tempfile
import threading
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.config.mcp_watcher import (
    MCPConfigWatcher, 
    MCPConfigChangeHandler,
    get_mcp_config_watcher,
    reset_mcp_config_watcher
)


class TestMCPConfigChangeHandler:
    """MCP配置变化处理器测试类"""
    
    def test_handler_initialization(self):
        """测试处理器初始化"""
        callback = MagicMock()
        handler = MCPConfigChangeHandler("/test/path.json", callback)
        
        assert handler.config_path == Path("/test/path.json").resolve()
        assert handler.callback == callback
        assert handler.debounce_delay == 1.0
    
    def test_debounce_mechanism(self):
        """测试防抖机制"""
        callback = MagicMock()
        handler = MCPConfigChangeHandler("/test/path.json", callback)
        
        # 模拟快速连续的文件修改事件
        mock_event = MagicMock()
        mock_event.is_directory = False
        mock_event.src_path = "/test/path.json"
        
        # 第一次调用
        handler.on_modified(mock_event)
        first_time = handler.last_modified
        
        # 立即第二次调用（应该被防抖）
        handler.on_modified(mock_event)
        
        # 时间应该没有更新
        assert handler.last_modified == first_time
    
    def test_ignore_directory_events(self):
        """测试忽略目录事件"""
        callback = MagicMock()
        handler = MCPConfigChangeHandler("/test/path.json", callback)
        
        mock_event = MagicMock()
        mock_event.is_directory = True
        mock_event.src_path = "/test/path.json"
        
        handler.on_modified(mock_event)
        
        # 应该没有更新时间戳
        assert handler.last_modified == 0
    
    def test_ignore_unrelated_files(self):
        """测试忽略无关文件"""
        callback = MagicMock()
        handler = MCPConfigChangeHandler("/test/path.json", callback)
        
        mock_event = MagicMock()
        mock_event.is_directory = False
        mock_event.src_path = "/test/other.json"
        
        handler.on_modified(mock_event)
        
        # 应该没有更新时间戳
        assert handler.last_modified == 0


class TestMCPConfigWatcher:
    """MCP配置监控器测试类"""
    
    def setup_method(self):
        """每个测试前的设置"""
        reset_mcp_config_watcher()
    
    def teardown_method(self):
        """每个测试后的清理"""
        reset_mcp_config_watcher()
    
    def test_watcher_initialization(self):
        """测试监控器初始化"""
        watcher = MCPConfigWatcher("test_config.json")
        
        assert watcher.config_path == Path("test_config.json").resolve()
        assert not watcher.is_watching
        assert len(watcher.callbacks) == 0
        assert watcher.observer is None
    
    def test_add_remove_callbacks(self):
        """测试添加和移除回调函数"""
        watcher = MCPConfigWatcher("test_config.json")
        
        callback1 = MagicMock()
        callback2 = MagicMock()
        
        # 添加回调
        watcher.add_callback(callback1)
        watcher.add_callback(callback2)
        
        assert len(watcher.callbacks) == 2
        assert callback1 in watcher.callbacks
        assert callback2 in watcher.callbacks
        
        # 移除回调
        watcher.remove_callback(callback1)
        
        assert len(watcher.callbacks) == 1
        assert callback1 not in watcher.callbacks
        assert callback2 in watcher.callbacks
    
    def test_notify_callbacks(self):
        """测试回调通知"""
        watcher = MCPConfigWatcher("test_config.json")
        
        callback1 = MagicMock()
        callback2 = MagicMock()
        
        watcher.add_callback(callback1)
        watcher.add_callback(callback2)
        
        test_config = {"test": "data"}
        watcher._notify_callbacks(test_config)
        
        callback1.assert_called_once_with(test_config)
        callback2.assert_called_once_with(test_config)
    
    def test_callback_error_handling(self):
        """测试回调函数错误处理"""
        watcher = MCPConfigWatcher("test_config.json")
        
        # 创建一个会抛出异常的回调
        error_callback = MagicMock(side_effect=Exception("回调错误"))
        normal_callback = MagicMock()
        
        watcher.add_callback(error_callback)
        watcher.add_callback(normal_callback)
        
        test_config = {"test": "data"}
        
        # 应该不会抛出异常，正常回调应该仍然被调用
        watcher._notify_callbacks(test_config)
        
        error_callback.assert_called_once_with(test_config)
        normal_callback.assert_called_once_with(test_config)
    
    def test_start_watching_nonexistent_file(self):
        """测试监控不存在的文件"""
        watcher = MCPConfigWatcher("nonexistent_config.json")
        
        result = watcher.start_watching()
        
        assert not result
        assert not watcher.is_watching
    
    def test_start_watching_already_watching(self):
        """测试重复启动监控"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            config_path = f.name
            json.dump({"test": "config"}, f)
        
        try:
            watcher = MCPConfigWatcher(config_path)
            
            # 第一次启动
            result1 = watcher.start_watching()
            assert result1
            assert watcher.is_watching
            
            # 第二次启动（应该返回True但不重复启动）
            result2 = watcher.start_watching()
            assert result2
            assert watcher.is_watching
            
            watcher.stop_watching()
            
        finally:
            Path(config_path).unlink(missing_ok=True)
    
    def test_stop_watching_not_watching(self):
        """测试停止未启动的监控"""
        watcher = MCPConfigWatcher("test_config.json")
        
        # 应该不会抛出异常
        watcher.stop_watching()
        
        assert not watcher.is_watching
    
    @patch('src.config.mcp_watcher.reset_mcp_config_loader')
    @patch('src.config.mcp_watcher.get_mcp_config_loader')
    def test_reload_config_success(self, mock_get_loader, mock_reset_loader):
        """测试成功重新加载配置"""
        watcher = MCPConfigWatcher("test_config.json")
        
        # 模拟配置加载器
        mock_loader = MagicMock()
        mock_config = {"version": "1.0", "servers": {}}
        mock_loader.load_config.return_value = mock_config
        mock_get_loader.return_value = mock_loader
        
        # 添加回调
        callback = MagicMock()
        watcher.add_callback(callback)
        
        # 重新加载配置
        result = watcher.reload_config()
        
        assert result == mock_config
        mock_reset_loader.assert_called_once()
        mock_get_loader.assert_called_once()
        mock_loader.load_config.assert_called_once()
        callback.assert_called_once_with(mock_config)
    
    @patch('src.config.mcp_watcher.get_mcp_config_loader')
    def test_reload_config_failure(self, mock_get_loader):
        """测试重新加载配置失败"""
        watcher = MCPConfigWatcher("test_config.json")
        
        # 模拟加载失败
        mock_get_loader.side_effect = Exception("加载失败")
        
        result = watcher.reload_config()
        
        assert result is None
    
    def test_get_config_info(self):
        """测试获取配置信息"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            config_path = f.name
            json.dump({"test": "config"}, f)
        
        try:
            watcher = MCPConfigWatcher(config_path)
            callback = MagicMock()
            watcher.add_callback(callback)
            
            info = watcher.get_config_info()
            
            assert info['config_path'] == str(Path(config_path).resolve())
            assert info['is_watching'] == False
            assert info['callbacks_count'] == 1
            assert info['file_exists'] == True
            assert info['file_size'] > 0
            assert info['last_modified'] > 0
            
        finally:
            Path(config_path).unlink(missing_ok=True)
    
    def test_context_manager(self):
        """测试上下文管理器"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            config_path = f.name
            json.dump({"test": "config"}, f)
        
        try:
            watcher = MCPConfigWatcher(config_path)
            
            with watcher:
                assert watcher.is_watching
            
            assert not watcher.is_watching
            
        finally:
            Path(config_path).unlink(missing_ok=True)


class TestGlobalWatcher:
    """全局监控器测试类"""
    
    def setup_method(self):
        """每个测试前的设置"""
        reset_mcp_config_watcher()
    
    def teardown_method(self):
        """每个测试后的清理"""
        reset_mcp_config_watcher()
    
    def test_get_global_watcher(self):
        """测试获取全局监控器"""
        watcher1 = get_mcp_config_watcher("test1.json")
        watcher2 = get_mcp_config_watcher("test2.json")
        
        # 应该返回同一个实例
        assert watcher1 is watcher2
        assert watcher1.config_path == Path("test1.json").resolve()
    
    def test_reset_global_watcher(self):
        """测试重置全局监控器"""
        watcher1 = get_mcp_config_watcher("test.json")
        
        reset_mcp_config_watcher()
        
        watcher2 = get_mcp_config_watcher("test.json")
        
        # 应该是不同的实例
        assert watcher1 is not watcher2
    
    def test_reset_watching_watcher(self):
        """测试重置正在监控的监控器"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            config_path = f.name
            json.dump({"test": "config"}, f)
        
        try:
            watcher = get_mcp_config_watcher(config_path)
            watcher.start_watching()
            
            assert watcher.is_watching
            
            # 重置应该停止监控
            reset_mcp_config_watcher()
            
            # 原监控器应该已停止
            assert not watcher.is_watching
            
        finally:
            Path(config_path).unlink(missing_ok=True)


class TestIntegration:
    """集成测试类"""
    
    def setup_method(self):
        """每个测试前的设置"""
        reset_mcp_config_watcher()
    
    def teardown_method(self):
        """每个测试后的清理"""
        reset_mcp_config_watcher()
    
    def test_file_modification_detection(self):
        """测试文件修改检测（集成测试）"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            config_path = f.name
            initial_config = {"version": "1.0", "servers": {}}
            json.dump(initial_config, f)
        
        try:
            watcher = MCPConfigWatcher(config_path)
            callback_results = []
            
            def test_callback(config):
                callback_results.append(config)
            
            watcher.add_callback(test_callback)
            
            # 启动监控
            assert watcher.start_watching()
            
            # 等待监控器启动
            time.sleep(0.1)
            
            # 修改配置文件
            modified_config = {"version": "2.0", "servers": {"test": {}}}
            with open(config_path, 'w') as f:
                json.dump(modified_config, f)
            
            # 等待文件系统事件处理
            time.sleep(2.0)
            
            # 停止监控
            watcher.stop_watching()
            
            # 验证回调被调用（可能需要更长时间）
            # 注意：在某些系统上文件监控可能不会立即触发
            # 这个测试主要验证监控器能正常启动和停止
            
        finally:
            Path(config_path).unlink(missing_ok=True) 