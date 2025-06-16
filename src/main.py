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
from typing import Dict, List, Any

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


class ModelConfigError(Exception):
    """模型配置错误"""


class MCPConfigError(Exception):
    """MCP配置错误"""


def initialize_prompt_manager():
    """初始化PromptManager
    
    Returns:
        PromptManager实例，如果失败返回None
    """
    global prompt_manager
    
    try:
        prompt_manager = PromptManager("config/prompts")
        print("✓ 提示词配置加载成功")
        return prompt_manager
    except PromptManagerError as e:
        print(f"⚠️  提示词配置加载失败: {e}")
        print("将使用后备提示词")
        return None
    except Exception as e:
        print(f"⚠️  提示词管理器初始化错误: {e}")
        print("将使用后备提示词")
        return None


def get_prompt(prompt_key: str, variables: Dict[str, Any] = None) -> str:
    """获取提示词，配置缺失时快速失败
    
    Args:
        prompt_key: 提示词键
        variables: 变量替换字典
        
    Returns:
        提示词内容
        
    Raises:
        RuntimeError: 配置文件缺失或提示词不存在时立即失败
    """
    global prompt_manager
    
    if not prompt_manager:
        raise RuntimeError(f"❌ PromptManager未初始化！无法获取提示词: {prompt_key}")
    
    try:
        return prompt_manager.get_prompt(prompt_key, variables)
    except Exception as e:
        # 快速失败：配置问题应该立即暴露，而不是掩盖
        raise RuntimeError(
            f"❌ 提示词配置错误 '{prompt_key}': {str(e)}\n"
            f"请检查配置文件 config/prompts/ 是否存在且格式正确"
        ) from e


def setup_mcp_servers() -> Dict[str, Any]:
    """设置MCP服务器配置
    
    从配置文件动态加载启用的MCP服务器，如果配置文件不存在则使用默认配置
    
    Returns:
        MCP服务器配置字典，符合Qwen-Agent格式
        
    Raises:
        MCPConfigError: MCP配置加载失败（仅在严重错误时）
    """
    # 默认配置作为后备
    default_config = {
        'time': {
            'command': 'uvx',
            'args': ['mcp-server-time', '--local-timezone=Asia/Shanghai']
        },
        'fetch': {
            'command': 'uvx',
            'args': ['mcp-server-fetch']
        },
        'memory': {
            'command': 'npx',
            'args': ['-y', '@modelcontextprotocol/server-memory']
        }
    }
    
    try:
        # 获取MCP配置加载器
        config_loader = get_mcp_config_loader()
        
        # 获取启用的服务器
        enabled_servers = config_loader.get_enabled_servers()
        
        if not enabled_servers:
            print("⚠️  未找到启用的MCP服务器，将使用默认配置")
            return default_config
        
        # 构建Qwen-Agent格式的MCP配置
        mcp_servers = {}
        
        for server_name in enabled_servers:
            server_config = config_loader.get_server_config(server_name)
            if server_config:
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
                timeout = server_config.get('timeout', '默认')
                print(f"✓ 加载MCP服务器: {server_name} (分类: {category}, 超时: {timeout}s)")
        
        print(f"📡 成功加载 {len(mcp_servers)} 个MCP服务器")
        return mcp_servers
        
    except MCPConfigError as e:
        # 配置文件相关错误，使用默认配置
        if "配置文件不存在" in str(e) or "FileNotFoundError" in str(e):
            print("⚠️  MCP配置文件不存在，使用默认配置")
            print(f"📡 加载默认MCP服务器: {list(default_config.keys())}")
            return default_config
        else:
            # 其他配置错误，也使用默认配置但记录警告
            print(f"⚠️  MCP配置加载失败: {e}")
            print("📡 使用默认配置继续运行")
            return default_config
    except Exception as e:
        # 严重错误，使用默认配置
        print(f"⚠️  MCP配置系统错误: {e}")
        print("📡 使用默认配置继续运行")
        return default_config


def create_llm_config() -> Dict:
    """创建LLM配置 - 从.env文件加载"""
    
    try:
        config = get_config()
    except ConfigError as e:
        raise ModelConfigError(f"配置加载失败: {str(e)}")
    
    # 检查是否要使用R1推理模型
    use_r1 = config.get_bool('USE_DEEPSEEK_R1', False)
    
    # 检查DeepSeek API密钥
    try:
        api_key = config.require('DEEPSEEK_API_KEY')
    except ConfigError:
        raise ModelConfigError(
            "❌ 未找到DeepSeek API密钥！\n"
            "请在.env文件中设置: DEEPSEEK_API_KEY=your-api-key"
        )
    
    print("🔍 检测到DeepSeek API密钥")
    
    base_url = 'https://api.deepseek.com/v1'
    
    if use_r1:
        model = 'deepseek-reasoner'  # R1-0528推理模型
        model_name = "DeepSeek R1-0528 推理模型"
    else:
        model = 'deepseek-chat'  # V3-0324 稳定模型
        model_name = "DeepSeek V3 稳定模型"
    
    # 暂时跳过连接测试以简化演示
    print(f"⚡ 使用{model_name}(跳过连接测试)")
    
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
    """创建工具列表
    
    动态构建包含MCP服务器的工具列表，如果MCP配置失败则使用基本工具
    
    Returns:
        工具列表，包含自定义工具和MCP服务器配置（如果可用）
    """
    try:
        # 设置MCP服务器
        mcp_servers = setup_mcp_servers()
        
        # 构建工具列表
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
        
    except MCPConfigError as e:
        # MCP配置失败，使用基本工具列表
        print(f"⚠️  MCP配置失败: {e}")
        print("📦 使用基本工具列表继续运行")
        
        return [
            'custom_save_info', 
            'custom_recall_info', 
            'custom_math_calc',
            'code_interpreter',  # 内置代码解释器工具
        ]
    except Exception as e:
        # 其他错误，也使用基本工具列表
        print(f"⚠️  工具列表创建失败: {e}")
        print("📦 使用基本工具列表继续运行")
        
        return [
            'custom_save_info', 
            'custom_recall_info', 
            'custom_math_calc',
            'code_interpreter',  # 内置代码解释器工具
        ]


def main():
    """主函数 - 专注于程序流程控制"""
    try:
        # 1. 初始化提示词管理器
        initialize_prompt_manager()
        
        # 2. 显示欢迎界面
        show_welcome()
        
        # 3. 创建Agent (with enhanced error handling)
        ai_loading_msg = get_prompt("ai_loading")
        print(f"\n{ai_loading_msg}")
        
        try:
            llm_cfg = create_llm_config()
        except ModelConfigError as e:
            model_config_error = get_prompt("model_config_error", {"error_details": str(e)})
            print(f"\n{model_config_error}")
            return
        except Exception as e:
            init_error = get_prompt(
                "initialization_error",
                {"error_details": str(e)},
            )
            print(f"\n{init_error}")
            return
        
        # 4. 设置MCP服务器和工具
        mcp_loading_msg = get_prompt("mcp_loading")
        print(f"\n{mcp_loading_msg}")
        
        tools = create_tools_list()
        
        # 获取系统提示词 - 从配置文件加载
        system_message = get_prompt("system_base")

        # 创建Agent (with error handling) - 参考官方Qwen3示例
        try:
            # 获取Agent配置
            agent_name = get_prompt("agent_name")
            agent_description = get_prompt(
                "agent_description")
            
            agent = Assistant(
                llm=llm_cfg,
                system_message=system_message,
                function_list=tools,
                name=agent_name,
                description=agent_description
            )
            
            ai_success_msg = get_prompt("ai_success")
            print(ai_success_msg)
        except Exception as e:
            agent_creation_error = get_prompt(
                "agent_creation_error",
                {"error_details": str(e)},
            )
            print(agent_creation_error)
            return
        
        # 5. 对话循环 (with enhanced error handling)
        messages = []
        memory_store = get_memory_store()
        config = get_config()
        use_r1 = config.get_bool('USE_DEEPSEEK_R1', False)
        model_display = "DeepSeek-R1推理模型" if use_r1 else "DeepSeek-V3稳定模型"
        
        conversation_start_msg = get_prompt(
            "conversation_start",
            {"model_display": model_display}
        )
        print(f"\n{conversation_start_msg}\n")
        
        while True:
            # 获取用户输入
            try:
                user_input = input("您: ").strip()
            except (EOFError, KeyboardInterrupt):
                goodbye_msg = get_prompt("goodbye_message")
                print(f"\n\n{goodbye_msg}")
                break
            
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
            
            try:
                # 调用Agent并流式显示
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
                
            except requests.exceptions.RequestException as e:
                network_error_msg = get_prompt(
                    "network_error",
                    {"error_details": str(e)},
                )
                print(f"\n{network_error_msg}")
            except APIConnectionError as e:
                api_error_msg = get_prompt(
                    "api_error",
                    {"error_details": str(e)},
                )
                print(f"\n{api_error_msg}")
            except Exception as e:
                error_msg = str(e)
                # 特别处理DeepSeek R1模型的reasoning_content错误
                if 'reasoning_content' in error_msg:
                    deepseek_r1_error_msg = get_prompt(
                        "deepseek_r1_error")
                    print(f"\n{deepseek_r1_error_msg}")
                    # 清理messages中可能的reasoning_content
                    cleaned_messages = []
                    for msg in messages:
                        if isinstance(msg, dict) and 'reasoning_content' in msg:
                            clean_msg = {k: v for k, v in msg.items() if k != 'reasoning_content'}
                            cleaned_messages.append(clean_msg)
                        else:
                            cleaned_messages.append(msg)
                    messages = cleaned_messages
                    continue
                else:
                    generic_error_msg = get_prompt(
                        "generic_error",
                        {"error_message": error_msg})
                    print(f"\n{generic_error_msg}")
    
    except KeyboardInterrupt:
        interrupt_msg = get_prompt(
            "interrupt_message")
        print(f"\n\n{interrupt_msg}")
    except Exception as e:
        program_exit_error_msg = get_prompt(
            "program_exit_error",
            {"error_details": str(e)},
        )
        print(f"\n{program_exit_error_msg}")


if __name__ == "__main__":
    main() 