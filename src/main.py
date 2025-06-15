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
from typing import Dict

# Qwen-Agent imports
from qwen_agent.agents import Assistant
from qwen_agent.utils.output_beautify import typewriter_print

# 导入工具类 - 使用绝对导入
from src.tools.qwen_tools.memory_tools import get_memory_store

# 导入配置管理
from src.config.settings import get_config, ConfigError

# 导入UI帮助函数
from src.ui import show_welcome, show_help, show_memory, clear_screen


class APIConnectionError(Exception):
    """API连接错误"""


class ModelConfigError(Exception):
    """模型配置错误"""





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


def main():
    """主函数 - 专注于程序流程控制"""
    try:
        # 1. 显示欢迎界面
        show_welcome()
        
        # 2. 创建Agent (with enhanced error handling)
        print("\n🔧 正在初始化AI模型...")
        
        try:
            llm_cfg = create_llm_config()
        except ModelConfigError as e:
            print(f"\n❌ 模型配置失败:\n{str(e)}")
            return
        except Exception as e:
            print(f"\n❌ 初始化失败: {str(e)}")
            print("请检查网络连接和环境配置")
            return
        
        # 系统提示 - 针对推理模型优化，简化指令
        system_message = '''你是一个友好的AI助手，具有强大的推理能力。

核心功能：
1. 智能对话和问题解答
2. 记住用户信息 - 当用户介绍个人信息时使用custom_save_info工具
3. 回忆信息 - 当用户询问之前信息时使用custom_recall_info工具  
4. 数学计算 - 使用custom_math_calc工具
5. 代码执行 - 使用code_interpreter工具执行Python代码、数据分析、绘图等
6. MCP服务集成 - 通过官方Qwen-Agent MCP支持访问外部服务

MCP服务说明：
- time服务器: 获取当前时间信息（亚洲/上海时区）
- fetch服务器: 可以抓取网页内容，获取实时信息
- memory服务器: 提供外部内存存储功能

使用场景：
- 当用户询问"现在几点"、"当前时间"时，系统会自动使用time服务
- 当用户要求"抓取网页"、"获取网页内容"、"访问网站"时，系统会自动使用fetch服务
- 当用户需要"外部存储"、"持久化数据"时，系统会自动使用memory服务
- 当用户需要"执行代码"、"数据分析"、"绘图"、"计算"时，系统会自动使用code_interpreter
- MCP工具会根据需要自动调用，无需手动指定

行为准则：
- 自然友好的交流
- 根据用户需求智能选择合适的工具
- 保持对话流畅，适度使用工具
- 利用MCP服务和代码执行提供实时、准确的信息和分析'''

        # 创建Agent (with error handling) - 参考官方Qwen3示例
        try:
            # 使用官方Qwen-Agent MCP集成方式，参考官方示例
            tools = [
                'custom_save_info', 
                'custom_recall_info', 
                'custom_math_calc',
                {
                    'mcpServers': {  # 官方MCP配置格式
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
                },
                'code_interpreter',  # 内置代码解释器工具
            ]
            agent = Assistant(
                llm=llm_cfg,
                system_message=system_message,
                function_list=tools,
                name='DeepSeek增强版AI助手',
                description='基于DeepSeek模型的智能助手，支持记忆、计算、MCP服务和代码执行功能'
            )
            print("✓ AI助手初始化成功！")
        except Exception as e:
            print(f"❌ Agent创建失败: {str(e)}")
            print("可能的原因: API配置错误或模型服务不可用")
            return
        
        # 3. 对话循环 (with enhanced error handling)
        messages = []
        memory_store = get_memory_store()
        config = get_config()
        use_r1 = config.get_bool('USE_DEEPSEEK_R1', False)
        model_display = "DeepSeek-R1推理模型" if use_r1 else "DeepSeek-V3稳定模型"
        print(f"\n✨ 开始对话吧！(使用{model_display})\n")
        
        while True:
            # 获取用户输入
            try:
                user_input = input("您: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n\n👋 再见！")
                break
            
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
            print("\n🤖 助手: ", end='', flush=True)
            
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
                print(f"\n❌ 网络连接错误: {str(e)}")
                print("请检查网络连接，稍后重试")
            except APIConnectionError as e:
                print(f"\n❌ API调用失败: {str(e)}")
                print("请检查API服务状态和配置")
            except Exception as e:
                error_msg = str(e)
                # 特别处理DeepSeek R1模型的reasoning_content错误
                if 'reasoning_content' in error_msg:
                    print("\n❌ DeepSeek R1模型格式错误")
                    print("正在清理消息历史并重试...")
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
                    print(f"\n❌ 处理出错: {error_msg}")
                    print("请检查输入并重试")
    
    except KeyboardInterrupt:
        print("\n\n👋 程序被用户中断，再见！")
    except Exception as e:
        print(f"\n❌ 程序异常退出: {str(e)}")
        print("\n请检查:")
        print("1. 网络连接是否正常")
        print("2. API密钥是否正确设置")
        print("3. 依赖是否正确安装")
        print("4. DeepSeek API服务是否可用")


if __name__ == "__main__":
    main() 