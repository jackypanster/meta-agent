#!/usr/bin/env python3
"""
Qwen-Agent MVP - 简洁直观实现

基于官方Qwen-Agent框架的最简洁实现：
- 直接使用Assistant类
- 模块化工具系统
- 简单的内存管理
- 直观的CLI界面
- 使用最新DeepSeek-R1-0528推理模型
"""

import time
import requests
from typing import Dict, List, Any, NoReturn

# Qwen-Agent imports
from qwen_agent.agents import Assistant
from qwen_agent.utils.output_beautify import typewriter_print

# 导入工具类 - 使用绝对导入
from src.tools.qwen_tools.memory_tools import get_memory_store

# 导入配置管理
from src.config.settings import get_config, ConfigError
from src.config.mcp_config import get_mcp_config_loader
from src.config.prompt_manager import PromptManager, PromptManagerError

# 导入UI帮助函数
from src.ui import show_welcome, show_help, show_memory, clear_screen

# 全局PromptManager实例
prompt_manager = None


class APIConnectionError(Exception):
    """API连接错误"""
    pass


class ModelConfigError(Exception):
    """模型配置错误"""
    pass


class MCPConfigError(Exception):
    """MCP配置错误"""
    pass


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


def setup_mcp_servers() -> Dict[str, Any]:
    """
    Loads and formats enabled MCP server configurations for use as agent tools.
    
    Dynamically retrieves enabled MCP servers from configuration, extracting only the fields required by the agent (command, args, and optionally env) and returning them in the format expected by Qwen-Agent. Raises MCPConfigError if no servers are enabled or if a server's configuration is missing.
    
    Returns:
        A dictionary mapping server names to their Qwen-Agent-compatible configuration.
    
    Raises:
        MCPConfigError: If no enabled servers are found or a server configuration is missing.
    """
    # 获取MCP配置加载器
    config_loader = get_mcp_config_loader()
    
    # 获取启用的服务器
    enabled_servers = config_loader.get_enabled_servers()
    
    if not enabled_servers:
        raise MCPConfigError("❌ 未找到任何启用的MCP服务器")
    
    # 构建Qwen-Agent格式的MCP配置
    mcp_servers = {}
    
    # This function intentionally only uses a subset of the MCP server
    # configuration (command, args, env) for the agent's tool setup.
    # Other fields in mcp_servers.json might be for the server
    # processes themselves or other administrative purposes.
    for server_name in enabled_servers:
        server_config = config_loader.get_server_config(server_name)
        if not server_config:
            raise MCPConfigError(f"❌ 服务器 '{server_name}' 配置不存在")
        
        # 转换为Qwen-Agent期望的格式
        qwen_config = {
            'command': server_config['command'],
            'args': server_config['args']
        }
        
        # 添加环境变量（如果有）
        if 'env' in server_config:
            qwen_config['env'] = server_config['env']
        
        mcp_servers[server_name] = qwen_config
        
        # 显示加载的服务器信息
        category = server_config.get('category', '未分类')
        print(f"✓ 加载MCP服务器: {server_name} (分类: {category})")
    
    print(f"📡 成功加载 {len(mcp_servers)} 个MCP服务器")
    return mcp_servers


def create_llm_config() -> Dict[str, Any]:
    """创建LLM配置 - 失败时立即抛出异常
    
    Returns:
        LLM配置字典
        
    Raises:
        ConfigError: 配置加载或API密钥验证失败时立即抛出
    """
    
    config = get_config()
    
    # 检查是否要使用R1推理模型
    use_r1 = config.get_bool('USE_DEEPSEEK_R1')
    
    # 检查DeepSeek API密钥 - 失败时立即抛出异常
    api_key = config.require('DEEPSEEK_API_KEY')
    
    print("🔍 检测到DeepSeek API密钥")
    
    base_url = 'https://api.deepseek.com/v1'
    
    if use_r1:
        model = 'deepseek-reasoner'  # R1-0528推理模型
        model_name = "DeepSeek R1-0528 推理模型"
    else:
        model = 'deepseek-chat'  # V3-0324 稳定模型
        model_name = "DeepSeek V3 稳定模型"
    
    # 不进行连接测试 - 任何连接问题都在实际调用时立即暴露
    print(f"⚡ 使用{model_name}")
    
    return {
        'model': model,
        'model_server': base_url,
        'api_key': api_key,
        'generate_cfg': {
            'top_p': 0.8,
            'max_tokens': 2000,
            'temperature': 0.7
        }
    }


def create_tools_list() -> List[Any]:
    """
    Constructs and returns the list of tools available to the conversational agent.
    
    The tool list includes custom tools, dynamically loaded MCP server configurations, and a built-in code interpreter. Raises an exception if MCP server setup fails.
    
    Returns:
        A list containing custom tool identifiers, a dictionary of MCP server configurations, and the code interpreter tool.
    
    Raises:
        MCPConfigError: If MCP server configuration fails.
    """
    # 设置MCP服务器
    mcp_servers = setup_mcp_servers()
    
    # 构建工具列表
    # These tools are explicitly listed to ensure their availability to the agent.
    # Relying on potential auto-discovery mechanisms of the Qwen framework
    # is not currently implemented or confirmed for this project.
    tools = [
        'custom_save_info', 
        'custom_recall_info', 
        'custom_math_calc',
        {
            'mcpServers': mcp_servers  # 使用动态加载的MCP配置
        },
        'code_interpreter',  # 内置代码解释器工具
    ]
    
    return tools


def main() -> NoReturn:
    """
    Runs the main program loop for the conversational AI CLI, handling initialization, user interaction, and conversation management.
    
    Initializes the prompt manager, displays welcome and loading messages, configures the LLM and tools, and creates the conversational agent. Enters an interactive loop to process user input, handle special commands (help, clear, memory, exit), manage conversation history, and stream AI responses. Conversation pairs are stored in a simple memory store, retaining the latest 50 exchanges. Any configuration or runtime errors propagate immediately, causing the program to terminate.
    """
    # 1. 初始化提示词管理器
    initialize_prompt_manager()
    
    # 2. 显示欢迎界面
    show_welcome()
    
    # 3. 创建Agent
    ai_loading_msg = get_prompt("ai_loading")
    print(f"\n{ai_loading_msg}")
    
    llm_cfg = create_llm_config()
    
    # 4. 设置MCP服务器和工具
    mcp_loading_msg = get_prompt("mcp_loading")
    print(f"\n{mcp_loading_msg}")
    
    tools = create_tools_list()
    
    # 获取系统提示词 - 从配置文件加载
    system_message = get_prompt("system_base")

    # 创建Agent - 参考官方Qwen3示例
    # 获取Agent配置
    agent_name = get_prompt("agent_name")
    agent_description = get_prompt("agent_description")
    
    agent = Assistant(
        llm=llm_cfg,
        system_message=system_message,
        function_list=tools,
        name=agent_name,
        description=agent_description
    )
    
    ai_success_msg = get_prompt("ai_success")
    print(ai_success_msg)
    
    # 5. 对话循环 - 任何异常都立即崩溃
    messages = []
    memory_store = get_memory_store()
    config = get_config()
    use_r1 = config.get_bool('USE_DEEPSEEK_R1')
    model_display = "DeepSeek-R1推理模型" if use_r1 else "DeepSeek-V3稳定模型"
    
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
        
        # 调用Agent并流式显示.
        # 注意: 任何来自 agent.run() 的异常 (例如工具执行错误、LLM API错误等)
        # 在这里都没有被捕获，这是为了确保当前交互轮次的 fail-fast 行为。
        # 这种设计符合项目立即暴露问题的原则。
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


if __name__ == "__main__":
    main() 