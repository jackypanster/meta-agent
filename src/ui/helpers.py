"""
UI帮助函数模块

包含所有用户界面显示相关的帮助函数：
- show_welcome() - 显示欢迎信息
- show_help() - 显示帮助信息  
- show_memory() - 显示保存的记忆
"""

import os

from src.config.settings import get_config
from src.config.prompt_manager import PromptManager, PromptManagerError

# 直接从memory_tools导入，避免加载整个工具包
from src.tools.qwen_tools.memory_tools import get_memory_store

# UI提示词管理器
ui_prompt_manager = None


def initialize_ui_prompts():
    """初始化UI提示词管理器"""
    global ui_prompt_manager
    
    try:
        ui_prompt_manager = PromptManager("config/prompts")
        return ui_prompt_manager
    except PromptManagerError as e:
        # 静默失败，使用后备文本
        return None
    except Exception as e:
        # 静默失败，使用后备文本
        return None


def get_ui_prompt(prompt_key: str, variables: dict = None, fallback: str = "") -> str:
    """获取UI提示词，支持后备机制"""
    global ui_prompt_manager
    
    # 懒加载提示词管理器
    if ui_prompt_manager is None:
        initialize_ui_prompts()
    
    if ui_prompt_manager:
        try:
            return ui_prompt_manager.get_prompt(prompt_key, variables)
        except Exception:
            pass
    
    return fallback


def show_welcome():
    """显示欢迎信息"""
    config = get_config()
    use_r1 = config.get_bool('USE_DEEPSEEK_R1', False)
    model_info = "DeepSeek-R1 推理模型" if use_r1 else "DeepSeek-V3 稳定模型"
    
    # 获取欢迎信息组件
    welcome_title = get_ui_prompt("welcome_title", fallback="🤖 Qwen-Agent MVP - DeepSeek 增强版")
    welcome_subtitle = get_ui_prompt("welcome_subtitle", {"model_info": model_info}, fallback=f"基于 {model_info} 的AI助手：")
    features_list = get_ui_prompt("features_list", fallback="""• 💬 智能对话
• 🧠 记忆功能 - 记住您的信息
• 🧮 计算功能
• 📝 信息保存和回忆
• 🐍 代码执行 - Python代码、数据分析、绘图
• 🔗 MCP服务集成 - 时间、网页抓取、外部内存""")
    
    r1_tip = get_ui_prompt("r1_tip", fallback="💡 提示: 设置环境变量 USE_DEEPSEEK_R1=true 可使用R1推理模型")
    example_commands = get_ui_prompt("example_commands", fallback="""💡 试试这些命令:
- 你好，我叫张三，喜欢编程
- 我的名字是什么？
- 现在几点了？
- 计算 15 * 8 + 32
- 用Python画一个正弦波图
- 抓取网页 https://www.ruanyifeng.com/blog/
- help (显示帮助)
- quit (退出)""")
    
    print(welcome_title)
    print("=" * 50)
    print(welcome_subtitle)
    print(features_list)
    if not use_r1:
        print(f"\n{r1_tip}")
    print(f"\n{example_commands}")


def show_help():
    """显示帮助信息"""
    help_commands = get_ui_prompt("help_commands", fallback="""📋 可用命令:
• quit/exit/q - 退出程序
• help/h - 显示此帮助
• clear/cls - 清屏
• memory - 显示保存的信息""")
    
    ai_features = get_ui_prompt("ai_features", fallback="""🤖 AI助手功能:
• 自动记住您提到的个人信息
• 可以回忆之前的对话内容
• 执行数学计算
• 日常对话和问答
• 基于DeepSeek-R1-0528的增强推理能力
• Python代码执行 - 数据分析、绘图、计算
• MCP服务集成 - 时间查询、网页抓取、外部内存""")
    
    mcp_examples = get_ui_prompt("mcp_examples", fallback="""🔗 MCP功能示例:
• '现在几点了？' - 获取当前时间
• '抓取网页内容' - 获取网页信息
• '用Python画图' - 执行代码并生成图表
• '分析数据' - 数据处理和分析""")
    
    print(f"\n{help_commands}")
    print(f"\n{ai_features}")
    print(f"\n{mcp_examples}")


def show_memory():
    """显示保存的记忆"""
    memory_store = get_memory_store()
    
    memory_title = get_ui_prompt("memory_title", fallback="🧠 已保存的信息:")
    facts_header = get_ui_prompt("memory_facts_header", fallback="📋 事实信息:")
    preferences_header = get_ui_prompt("memory_preferences_header", fallback="❤️ 偏好信息:")
    no_memory_msg = get_ui_prompt("no_memory_message", fallback="还没有保存任何信息")
    
    print(f"\n{memory_title}")
    
    if memory_store['facts']:
        print(f"\n{facts_header}")
        for i, fact in enumerate(memory_store['facts'][-5:], 1):
            print(f"  {i}. {fact['content']} ({fact['time_str']})")
    
    if memory_store['preferences']:
        print(f"\n{preferences_header}")
        for i, pref in enumerate(memory_store['preferences'][-5:], 1):
            print(f"  {i}. {pref['content']} ({pref['time_str']})")
    
    if not memory_store['facts'] and not memory_store['preferences']:
        print(f"  {no_memory_msg}")


def clear_screen():
    """清屏并重新显示欢迎信息"""
    os.system('clear' if os.name != 'nt' else 'cls')
    show_welcome() 