"""
应用程序核心模块

主要的对话循环和Agent管理逻辑
"""

import time
from typing import Dict, List, Any, NoReturn

from qwen_agent.agents import Assistant
from qwen_agent.utils.output_beautify import typewriter_print

from src.config.settings import get_config
from src.tools.qwen_tools.memory_tools import get_memory_store
from src.llm_config import create_llm_config, get_model_display_name
from src.agent_setup import create_tools_list
from src.ui import show_welcome, show_help, show_memory, clear_screen


def create_agent() -> Assistant:
    """创建并配置Agent
    
    Returns:
        配置好的Assistant实例
        
    Raises:
        各种配置错误: 配置失败时立即抛出
    """
    # 创建LLM配置
    print("\n🔧 正在初始化AI模型...")
    
    llm_cfg = create_llm_config()
    
    # 设置工具
    print("\n📡 正在加载MCP服务器配置...")
    
    tools = create_tools_list()
    
    # 使用空系统提示词，完全依赖qwen-agent框架内置指令
    system_message = ""
    
    # 创建Agent - 使用简单配置
    agent = Assistant(
        llm=llm_cfg,
        system_message=system_message,
        function_list=tools,
        name="AI助手",
        description="基于qwen-agent框架的智能助手"
    )
    
    print("✓ AI助手初始化成功！")
    
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
    
    print(f"\n✨ 开始对话吧！(使用{model_display})\n")
    
    while True:
        # 获取用户输入 - 只处理用户中断
        user_input = input("您: ").strip()
        
        # 处理特殊命令
        if user_input.lower() in ['quit', 'exit', 'q', '退出']:
            print("👋 再见！")
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
        print(f"\n🤖 助手: ", end='', flush=True)
        
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