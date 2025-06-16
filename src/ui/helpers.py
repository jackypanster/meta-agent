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
    """初始化UI提示词管理器 - 失败时立即抛出异常"""
    global ui_prompt_manager
    
    ui_prompt_manager = PromptManager("config/prompts")
    return ui_prompt_manager


def get_prompt(prompt_key: str, variables: dict = None) -> str:
    """获取UI提示词，配置缺失时快速失败"""
    global ui_prompt_manager
    
    # 懒加载提示词管理器
    if ui_prompt_manager is None:
        initialize_ui_prompts()
    
    return ui_prompt_manager.get_prompt(prompt_key, variables)


def show_welcome():
    """显示欢迎信息"""
    config = get_config()
    use_r1 = config.get_bool('USE_DEEPSEEK_R1', False)
    model_info = "DeepSeek-R1 推理模型" if use_r1 else "DeepSeek-V3 稳定模型"
    
    # 获取欢迎信息组件
    welcome_title = get_prompt("welcome_title")
    welcome_subtitle = get_prompt("welcome_subtitle", {"model_info": model_info})
    features_list = get_prompt("features_list")
    
    r1_tip = get_prompt("r1_tip")
    example_commands = get_prompt("example_commands")
    
    print(welcome_title)
    print("=" * 50)
    print(welcome_subtitle)
    print(features_list)
    if not use_r1:
        print(f"\n{r1_tip}")
    print(f"\n{example_commands}")


def show_help():
    """显示帮助信息"""
    help_commands = get_prompt("help_commands")
    
    ai_features = get_prompt("ai_features")
    
    mcp_examples = get_prompt("mcp_examples")
    
    print(f"\n{help_commands}")
    print(f"\n{ai_features}")
    print(f"\n{mcp_examples}")


def show_memory():
    """显示保存的记忆"""
    memory_store = get_memory_store()
    
    memory_title = get_prompt("memory_title")
    facts_header = get_prompt("memory_facts_header")
    preferences_header = get_prompt("memory_preferences_header")
    no_memory_msg = get_prompt("no_memory_message")
    
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