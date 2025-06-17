"""
应用程序核心模块

主要的对话循环和Agent管理逻辑
"""

import time
from typing import Dict, List, Any, NoReturn

from qwen_agent.agents import Assistant
from qwen_agent.utils.output_beautify import typewriter_print

from src.config.settings import get_config
from src.config.prompt_manager import PromptManager, PromptManagerError
from src.tools.qwen_tools.memory_tools import get_memory_store
from src.llm_config import create_llm_config, get_model_display_name
from src.agent_setup import create_tools_list
from src.ui import show_welcome, show_help, show_memory, clear_screen


# 全局PromptManager实例
prompt_manager = None


def initialize_prompt_manager() -> PromptManager:
    """初始化PromptManager - 失败时立即抛出异常
    
    Returns:
        PromptManager实例
        
    Raises:
        PromptManagerError: 提示词配置加载失败时立即抛出
    """
    global prompt_manager
    
    prompt_manager = PromptManager("config/prompts")
    print("✓ 提示词配置加载成功")
    return prompt_manager


def get_prompt(prompt_key: str, variables: Dict[str, Any] = None) -> str:
    """获取提示词，配置缺失时快速失败
    
    Args:
        prompt_key: 提示词键
        variables: 变量替换字典
        
    Returns:
        提示词内容
        
    Raises:
        PromptManagerError: 提示词不存在或配置错误时立即失败
    """
    global prompt_manager
    
    if not prompt_manager:
        raise PromptManagerError(f"PromptManager未初始化！无法获取提示词: {prompt_key}")
    
    return prompt_manager.get_prompt(prompt_key, variables)


def create_agent() -> Assistant:
    """创建并配置Agent
    
    Returns:
        配置好的Assistant实例
        
    Raises:
        各种配置错误: 配置失败时立即抛出
    """
    # 创建LLM配置
    ai_loading_msg = get_prompt("ai_loading")
    print(f"\n{ai_loading_msg}")
    
    llm_cfg = create_llm_config()
    
    # 设置工具
    mcp_loading_msg = get_prompt("mcp_loading")
    print(f"\n{mcp_loading_msg}")
    
    tools = create_tools_list()
    
    # 获取系统提示词
    system_message = get_prompt("system_base")
    
    # 获取Agent配置
    agent_name = get_prompt("agent_name")
    agent_description = get_prompt("agent_description")
    
    # 创建Agent
    agent = Assistant(
        llm=llm_cfg,
        system_message=system_message,
        function_list=tools,
        name=agent_name,
        description=agent_description
    )
    
    ai_success_msg = get_prompt("ai_success")
    print(ai_success_msg)
    
    return agent


def run_conversation_loop(agent: Assistant) -> NoReturn:
    """运行主要的对话循环
    
    Args:
        agent: 配置好的Assistant实例
        
    Raises:
        任何异常都会立即传播导致程序崩溃
    """
    messages = []
    memory_store = get_memory_store()
    model_display = get_model_display_name()
    
    conversation_start_msg = get_prompt(
        "conversation_start",
        {"model_display": model_display}
    )
    print(f"\n{conversation_start_msg}\n")
    
    while True:
        # 获取用户输入 - 只处理用户中断
        user_input = input("您: ").strip()
        
        # 处理特殊命令
        if user_input.lower() in ['quit', 'exit', 'q', '退出']:
            goodbye_msg = get_prompt("goodbye_message")
            print(goodbye_msg)
            break
        elif user_input.lower() in ['help', 'h', '帮助']:
            show_help()
            continue
        elif user_input.lower() in ['clear', 'cls', '清屏']:
            clear_screen()
            continue
        elif user_input.lower() in ['memory', 'mem', '记忆']:
            show_memory()
            continue
        elif not user_input:
            continue
        
        # 添加用户消息到历史
        messages.append({'role': 'user', 'content': user_input})
        
        # 显示AI回复
        ai_response_prefix = get_prompt("ai_response_prefix")
        print(f"\n{ai_response_prefix}", end='', flush=True)
        
        # 调用Agent并流式显示
        # 注意: 任何来自 agent.run() 的异常都没有被捕获，
        # 这是为了确保当前交互轮次的 fail-fast 行为。
        response_text = ""
        response_messages = agent.run(messages=messages)
        
        for response in response_messages:
            response_text = typewriter_print(response, response_text)
        
        # 清理并添加响应到历史 - 特别处理R1模型的reasoning_content
        clean_messages = []
        for msg in response_messages:
            if isinstance(msg, dict):
                # 创建清理后的消息副本，移除reasoning_content
                clean_msg = {k: v for k, v in msg.items() if k != 'reasoning_content'}
                clean_messages.append(clean_msg)
            else:
                clean_messages.append(msg)
        
        messages.extend(clean_messages)
        
        # 保存对话到简单历史记录
        memory_store['history'].append({
            'user': user_input,
            'assistant': response_text,
            'timestamp': time.time()
        })
        
        # 保持历史记录不超过50条
        if len(memory_store['history']) > 50:
            memory_store['history'] = memory_store['history'][-50:]
        
        print()  # 换行