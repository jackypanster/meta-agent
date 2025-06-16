"""
MCP配置文件监控器

提供配置文件的实时监控和热重载功能，支持：
- 文件系统监控
- 线程安全的配置重载
- 错误处理和恢复
- 回调通知机制
"""

import os
import time
import threading
import logging
from typing import Dict, Any, Callable, Optional, List
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent

from .mcp_config import get_mcp_config_loader, reset_mcp_config_loader, MCPConfigError

logger = logging.getLogger(__name__)


class MCPConfigChangeHandler(FileSystemEventHandler):
    """MCP配置文件变化处理器"""
    
    def __init__(self, config_path: str, callback: Callable[[Dict[str, Any]], None]):
        self.config_path = Path(config_path).resolve()
        self.callback = callback
        self.last_modified = 0
        self.debounce_delay = 1.0  # 防抖延迟（秒）
        
    def on_modified(self, event):
        """文件修改事件处理"""
        if event.is_directory:
            return
            
        # 检查是否是我们关心的配置文件
        event_path = Path(event.src_path).resolve()
        if event_path != self.config_path:
            return
        
        # 防抖处理 - 避免重复触发
        current_time = time.time()
        if current_time - self.last_modified < self.debounce_delay:
            return
        
        self.last_modified = current_time
        
        logger.info(f"检测到配置文件变化: {event_path}")
        
        # 延迟一点时间确保文件写入完成
        threading.Timer(0.5, self._handle_config_change).start()
    
    def _handle_config_change(self):
        """处理配置文件变化 - 失败时立即抛出异常"""
        # 重置配置加载器以强制重新加载
        reset_mcp_config_loader()
        
        # 加载新配置 - 任何错误都会立即抛出
        config_loader = get_mcp_config_loader()
        new_config = config_loader.load_config()
        
        logger.info("配置文件重新加载成功")
        
        # 调用回调函数通知配置变化
        if self.callback:
            self.callback(new_config)


class MCPConfigWatcher:
    """MCP配置文件监控器"""
    
    def __init__(self, config_path: str = "config/mcp_servers.json"):
        self.config_path = Path(config_path).resolve()
        self.observer: Optional[Observer] = None
        self.event_handler: Optional[MCPConfigChangeHandler] = None
        self.callbacks: List[Callable[[Dict[str, Any]], None]] = []
        self.is_watching = False
        self._lock = threading.RLock()
        
        logger.debug(f"初始化MCP配置监控器: {self.config_path}")
    
    def add_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """添加配置变化回调函数
        
        Args:
            callback: 配置变化时调用的函数，接收新配置作为参数
        """
        with self._lock:
            self.callbacks.append(callback)
            logger.debug(f"添加配置变化回调，当前回调数量: {len(self.callbacks)}")
    
    def remove_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """移除配置变化回调函数
        
        Args:
            callback: 要移除的回调函数
        """
        with self._lock:
            if callback in self.callbacks:
                self.callbacks.remove(callback)
                logger.debug(f"移除配置变化回调，当前回调数量: {len(self.callbacks)}")
    
    def _notify_callbacks(self, config: Dict[str, Any]):
        """通知所有回调函数配置已变化 - 回调失败时立即抛出异常
        
        Args:
            config: 新的配置数据
        """
        with self._lock:
            for callback in self.callbacks:
                callback(config)  # 任何回调失败都会立即抛出异常
    
    def start_watching(self) -> None:
        """开始监控配置文件 - 失败时立即抛出异常"""
        with self._lock:
            if self.is_watching:
                raise RuntimeError("❌ 配置监控已经在运行")
            
            # 检查配置文件是否存在
            if not self.config_path.exists():
                raise FileNotFoundError(f"❌ 配置文件不存在: {self.config_path}")
            
            # 创建事件处理器
            self.event_handler = MCPConfigChangeHandler(
                str(self.config_path),
                self._notify_callbacks
            )
            
            # 创建文件系统观察者
            self.observer = Observer()
            self.observer.schedule(
                self.event_handler,
                str(self.config_path.parent),
                recursive=False
            )
            
            # 启动监控
            self.observer.start()
            self.is_watching = True
            
            logger.info(f"开始监控MCP配置文件: {self.config_path}")
    
    def stop_watching(self):
        """停止监控配置文件 - 失败时立即抛出异常"""
        with self._lock:
            if not self.is_watching:
                return
            
            if self.observer:
                self.observer.stop()
                self.observer.join(timeout=5.0)
                self.observer = None
            
            self.event_handler = None
            self.is_watching = False
            
            logger.info("已停止MCP配置文件监控")
    
    def reload_config(self) -> Dict[str, Any]:
        """手动重新加载配置 - 失败时立即抛出异常
        
        Returns:
            新的配置数据
        """
        # 重置配置加载器
        reset_mcp_config_loader()
        
        # 加载新配置 - 任何错误都会立即抛出
        config_loader = get_mcp_config_loader()
        new_config = config_loader.load_config()
        
        logger.info("手动重新加载配置成功")
        
        # 通知回调函数
        self._notify_callbacks(new_config)
        
        return new_config
    
    def get_config_info(self) -> Dict[str, Any]:
        """获取配置监控器信息
        
        Returns:
            监控器状态信息
        """
        with self._lock:
            return {
                'config_path': str(self.config_path),
                'is_watching': self.is_watching,
                'callbacks_count': len(self.callbacks),
                'file_exists': self.config_path.exists(),
                'file_size': self.config_path.stat().st_size if self.config_path.exists() else 0,
                'last_modified': self.config_path.stat().st_mtime if self.config_path.exists() else 0
            }
    
    def __enter__(self):
        """上下文管理器入口"""
        self.start_watching()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.stop_watching()


# 全局配置监控器实例
_global_watcher: Optional[MCPConfigWatcher] = None


def get_mcp_config_watcher(config_path: str = "config/mcp_servers.json") -> MCPConfigWatcher:
    """获取全局MCP配置监控器实例
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        MCPConfigWatcher实例
    """
    global _global_watcher
    
    if _global_watcher is None:
        _global_watcher = MCPConfigWatcher(config_path)
    
    return _global_watcher


def reset_mcp_config_watcher():
    """重置全局配置监控器实例（主要用于测试）"""
    global _global_watcher
    
    if _global_watcher and _global_watcher.is_watching:
        _global_watcher.stop_watching()
    
    _global_watcher = None 