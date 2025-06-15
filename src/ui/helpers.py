"""
UI帮助函数模块

包含所有用户界面显示相关的帮助函数：
- show_welcome() - 显示欢迎信息
- show_help() - 显示帮助信息  
- show_memory() - 显示保存的记忆
"""

import os

from src.config.settings import get_config

# 直接从memory_tools导入，避免加载整个工具包
from src.tools.qwen_tools.memory_tools import get_memory_store


def show_welcome():
    """显示欢迎信息"""
    config = get_config()
    use_r1 = config.get_bool('USE_DEEPSEEK_R1', False)
    model_info = "DeepSeek-R1 推理模型" if use_r1 else "DeepSeek-V3 稳定模型"
    
    print("🤖 Qwen-Agent MVP - DeepSeek 增强版")
    print("=" * 50)
    print(f"基于 {model_info} 的AI助手：")
    print("• 💬 智能对话")
    print("• 🧠 记忆功能 - 记住您的信息")
    print("• 🧮 计算功能")
    print("• 📝 信息保存和回忆")
    print("• 🐍 代码执行 - Python代码、数据分析、绘图")
    print("• 🔗 MCP服务集成 - 时间、网页抓取、外部内存")
    if not use_r1:
        print("\n💡 提示: 设置环境变量 USE_DEEPSEEK_R1=true 可使用R1推理模型")
    print("\n💡 试试这些命令:")
    print("- 你好，我叫张三，喜欢编程")
    print("- 我的名字是什么？")
    print("- 现在几点了？")
    print("- 计算 15 * 8 + 32")
    print("- 用Python画一个正弦波图")
    print("- 抓取网页 https://www.ruanyifeng.com/blog/")
    print("- help (显示帮助)")
    print("- quit (退出)")


def show_help():
    """显示帮助信息"""
    print("\n📋 可用命令:")
    print("• quit/exit/q - 退出程序")
    print("• help/h - 显示此帮助")
    print("• clear/cls - 清屏")
    print("• memory - 显示保存的信息")
    print("\n🤖 AI助手功能:")
    print("• 自动记住您提到的个人信息")
    print("• 可以回忆之前的对话内容") 
    print("• 执行数学计算")
    print("• 日常对话和问答")
    print("• 基于DeepSeek-R1-0528的增强推理能力")
    print("• Python代码执行 - 数据分析、绘图、计算")
    print("• MCP服务集成 - 时间查询、网页抓取、外部内存")
    print("\n🔗 MCP功能示例:")
    print("• '现在几点了？' - 获取当前时间")
    print("• '抓取网页内容' - 获取网页信息")
    print("• '用Python画图' - 执行代码并生成图表")
    print("• '分析数据' - 数据处理和分析")


def show_memory():
    """显示保存的记忆"""
    memory_store = get_memory_store()
    print("\n🧠 已保存的信息:")
    
    if memory_store['facts']:
        print("\n📋 事实信息:")
        for i, fact in enumerate(memory_store['facts'][-5:], 1):
            print(f"  {i}. {fact['content']} ({fact['time_str']})")
    
    if memory_store['preferences']:
        print("\n❤️ 偏好信息:")
        for i, pref in enumerate(memory_store['preferences'][-5:], 1):
            print(f"  {i}. {pref['content']} ({pref['time_str']})")
    
    if not memory_store['facts'] and not memory_store['preferences']:
        print("  还没有保存任何信息")


def clear_screen():
    """清屏并重新显示欢迎信息"""
    os.system('clear' if os.name != 'nt' else 'cls')
    show_welcome() 