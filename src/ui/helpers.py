"""
UI帮助函数模块

包含所有用户界面显示相关的帮助函数：
- show_welcome() - 显示欢迎信息
- show_help() - 显示帮助信息  
- show_memory() - 显示保存的记忆
"""

import os
from typing import Dict, Any, Optional

from src.config.settings import get_config

# 直接从memory_tools导入，避免加载整个工具包
from src.tools.qwen_tools.memory_tools import get_memory_store


def show_welcome() -> None:
    """显示欢迎信息
    
    Raises:
        ConfigError: 配置加载失败时立即抛出
    """
    config = get_config()
    use_r1 = config.get_bool('USE_DEEPSEEK_R1')
    model_info = "DeepSeek-R1 推理模型" if use_r1 else "DeepSeek-V3 稳定模型"
    
    print("🚀 Qwen-Agent MVP")
    print("=" * 50)
    print(f"基于{model_info}的智能助手")
    print()
    print("🎯 核心功能:")
    print("• 智能对话和问题解答")
    print("• MCP服务集成 - 网页抓取、时间查询等")
    print()
    if not use_r1:
        print("💡 提示: 使用 'export USE_DEEPSEEK_R1=true' 启用R1推理模型")
    print()
    print("📝 示例命令:")
    print("- 你好，我叫张三，喜欢编程")
    print("- 抓取网页 https://www.ruanyifeng.com/blog/")
    print("- help (显示帮助)")
    print("- quit (退出)")


def show_help() -> None:
    """显示帮助信息"""
    
    print("\n📋 帮助命令:")
    print("• quit/exit/q - 退出程序")
    print("• help/h - 显示此帮助")
    print("• clear/cls - 清屏")
    print("• memory/mem - 查看记忆信息")
    
    print("\n🤖 AI助手功能:")
    print("• 自动记住您提到的个人信息")
    print("• 回答问题时会回忆相关记忆")
    print("• 可访问实时信息和外部服务")
    
    print("\n🔧 MCP服务示例:")
    print("• 抓取网页 - 'fetch https://example.com'")
    print("• 获取时间 - '现在几点？'")


def show_memory() -> None:
    """显示保存的记忆"""
    memory_store = get_memory_store()
    
    print("\n🧠 记忆信息")
    
    if memory_store['facts']:
        print("\n📝 事实信息:")
        for i, fact in enumerate(memory_store['facts'][-5:], 1):
            print(f"  {i}. {fact['content']} ({fact['time_str']})")
    
    if memory_store['preferences']:
        print("\n❤️ 偏好信息:")
        for i, pref in enumerate(memory_store['preferences'][-5:], 1):
            print(f"  {i}. {pref['content']} ({pref['time_str']})")
    
    if not memory_store['facts'] and not memory_store['preferences']:
        print("  暂无保存的记忆信息")


def clear_screen() -> None:
    """清屏并重新显示欢迎信息
    
    Raises:
        ConfigError: 配置加载失败时立即抛出
    """
    os.system('clear' if os.name != 'nt' else 'cls')
    show_welcome() 