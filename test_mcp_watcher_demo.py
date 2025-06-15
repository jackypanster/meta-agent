#!/usr/bin/env python3
"""
MCP配置监控器演示脚本

展示MCPConfigWatcher的动态配置更新功能
"""

import time
import json
import threading
from pathlib import Path
from src.config.mcp_watcher import get_mcp_config_watcher, reset_mcp_config_watcher


def demo_config_watching():
    """演示配置文件监控功能"""
    print("🔍 MCP配置监控器演示")
    print("=" * 50)
    
    # 确保配置文件存在
    config_file = Path("config/mcp_servers.json")
    if not config_file.exists():
        print("❌ 配置文件不存在，请先运行子任务13.1创建配置文件")
        return
    
    # 重置监控器
    reset_mcp_config_watcher()
    
    # 获取监控器
    watcher = get_mcp_config_watcher()
    
    # 配置变化计数器
    change_count = 0
    
    def on_config_change(config):
        """配置变化回调函数"""
        nonlocal change_count
        change_count += 1
        
        print(f"\n🔄 配置变化 #{change_count}")
        print(f"📅 时间: {time.strftime('%H:%M:%S')}")
        print(f"📊 版本: {config.get('version', 'unknown')}")
        
        servers = config.get('servers', {})
        enabled_servers = [name for name, cfg in servers.items() if cfg.get('enabled', True)]
        print(f"🖥️  启用的服务器: {enabled_servers}")
        print("-" * 30)
    
    # 添加回调函数
    watcher.add_callback(on_config_change)
    
    # 显示初始状态
    print("\n📋 监控器初始状态:")
    info = watcher.get_config_info()
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    # 启动监控
    print(f"\n🚀 启动配置文件监控: {config_file}")
    if watcher.start_watching():
        print("✅ 监控启动成功")
    else:
        print("❌ 监控启动失败")
        return
    
    print("\n📝 现在可以修改配置文件来测试热重载功能")
    print("💡 提示: 修改 config/mcp_servers.json 文件")
    print("🔧 例如: 更改版本号、启用/禁用服务器、修改超时设置等")
    print("⏰ 监控将运行30秒...")
    
    try:
        # 运行30秒
        for i in range(30):
            time.sleep(1)
            if i % 5 == 0:
                print(f"⏱️  剩余时间: {30-i}秒")
        
        print(f"\n📊 监控结束，共检测到 {change_count} 次配置变化")
        
    except KeyboardInterrupt:
        print("\n⚠️  用户中断监控")
    
    finally:
        # 停止监控
        watcher.stop_watching()
        print("🛑 监控已停止")


def demo_manual_reload():
    """演示手动重新加载配置"""
    print("\n\n🔄 手动重新加载演示")
    print("=" * 50)
    
    watcher = get_mcp_config_watcher()
    
    print("📥 手动重新加载配置...")
    config = watcher.reload_config()
    
    if config:
        print("✅ 配置重新加载成功")
        print(f"📊 版本: {config.get('version', 'unknown')}")
        
        servers = config.get('servers', {})
        print(f"🖥️  总服务器数: {len(servers)}")
        
        enabled_servers = [name for name, cfg in servers.items() if cfg.get('enabled', True)]
        print(f"✅ 启用的服务器: {enabled_servers}")
        
        disabled_servers = [name for name, cfg in servers.items() if not cfg.get('enabled', True)]
        if disabled_servers:
            print(f"❌ 禁用的服务器: {disabled_servers}")
    else:
        print("❌ 配置重新加载失败")


def demo_callback_management():
    """演示回调函数管理"""
    print("\n\n📞 回调函数管理演示")
    print("=" * 50)
    
    watcher = get_mcp_config_watcher()
    
    def callback1(config):
        print("📞 回调1: 配置已更新")
    
    def callback2(config):
        print("📞 回调2: 检测到变化")
    
    def callback3(config):
        print("📞 回调3: 新配置已加载")
    
    # 添加回调
    print("➕ 添加回调函数...")
    watcher.add_callback(callback1)
    watcher.add_callback(callback2)
    watcher.add_callback(callback3)
    
    info = watcher.get_config_info()
    print(f"📊 当前回调数量: {info['callbacks_count']}")
    
    # 触发回调（通过手动重新加载）
    print("\n🔄 触发回调函数...")
    watcher.reload_config()
    
    # 移除一个回调
    print("\n➖ 移除回调函数...")
    watcher.remove_callback(callback2)
    
    info = watcher.get_config_info()
    print(f"📊 当前回调数量: {info['callbacks_count']}")
    
    # 再次触发回调
    print("\n🔄 再次触发回调函数...")
    watcher.reload_config()


def demo_error_handling():
    """演示错误处理"""
    print("\n\n⚠️  错误处理演示")
    print("=" * 50)
    
    # 测试不存在的配置文件
    print("📁 测试监控不存在的文件...")
    reset_mcp_config_watcher()
    
    from src.config.mcp_watcher import MCPConfigWatcher
    watcher = MCPConfigWatcher("nonexistent_config.json")
    
    result = watcher.start_watching()
    print(f"🔍 监控结果: {'成功' if result else '失败（预期）'}")
    
    # 测试错误回调
    print("\n🐛 测试错误回调处理...")
    watcher = get_mcp_config_watcher()
    
    def error_callback(config):
        raise Exception("模拟回调错误")
    
    def normal_callback(config):
        print("✅ 正常回调执行成功")
    
    watcher.add_callback(error_callback)
    watcher.add_callback(normal_callback)
    
    print("🔄 触发包含错误的回调...")
    watcher.reload_config()


def main():
    """主演示函数"""
    print("🎬 MCP配置监控器功能演示")
    print("=" * 60)
    
    try:
        # 1. 配置文件监控演示
        demo_config_watching()
        
        # 2. 手动重新加载演示
        demo_manual_reload()
        
        # 3. 回调函数管理演示
        demo_callback_management()
        
        # 4. 错误处理演示
        demo_error_handling()
        
        print("\n🎉 演示完成！")
        print("\n💡 主要功能:")
        print("  - ✅ 实时配置文件监控")
        print("  - ✅ 手动配置重新加载")
        print("  - ✅ 回调函数管理")
        print("  - ✅ 错误处理和恢复")
        print("  - ✅ 线程安全操作")
        print("  - ✅ 上下文管理器支持")
        
    except Exception as e:
        print(f"\n❌ 演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 清理
        reset_mcp_config_watcher()
        print("\n🧹 清理完成")


if __name__ == "__main__":
    main() 