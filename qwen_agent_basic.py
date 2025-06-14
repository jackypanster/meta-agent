#!/usr/bin/env python3
"""
Qwen-Agent 基础版本

专注于验证Qwen-Agent核心功能：
1. 使用官方Assistant类
2. 简单的自定义工具
3. 对话循环
"""

import os
import json
from dotenv import load_dotenv

# Qwen-Agent imports
from qwen_agent.agents import Assistant
from qwen_agent.tools.base import BaseTool, register_tool
from qwen_agent.utils.output_beautify import typewriter_print

# 加载环境变量
load_dotenv()


@register_tool('simple_math')
class SimpleMath(BaseTool):
    """简单数学工具"""
    description = '执行基本数学运算：加法、减法、乘法、除法'
    parameters = [{
        'name': 'expression',
        'type': 'string',
        'description': '数学表达式，如 "2 + 3" 或 "10 * 5"',
        'required': True
    }]

    def call(self, params: str, **kwargs) -> str:
        try:
            data = json.loads(params)
            expression = data['expression']
            
            # 安全计算
            allowed_chars = set('0123456789+-*/.() ')
            if not all(c in allowed_chars for c in expression):
                return json.dumps({'error': '只支持基本数学运算'})
            
            result = eval(expression)
            return json.dumps({
                'expression': expression,
                'result': result
            }, ensure_ascii=False)
        except Exception as e:
            return json.dumps({'error': f'计算错误: {str(e)}'})


@register_tool('echo_tool')
class EchoTool(BaseTool):
    """回声工具 - 用于测试"""
    description = '回显输入的文本，用于测试工具调用功能'
    parameters = [{
        'name': 'message',
        'type': 'string',
        'description': '要回显的消息',
        'required': True
    }]

    def call(self, params: str, **kwargs) -> str:
        try:
            data = json.loads(params)
            message = data['message']
            return json.dumps({
                'original': message,
                'echo': f"回声: {message}",
                'timestamp': '2024-01-01 12:00:00'
            }, ensure_ascii=False)
        except Exception as e:
            return json.dumps({'error': f'回声失败: {str(e)}'})


def create_llm_config():
    """创建LLM配置"""
    deepseek_key = os.getenv('DEEPSEEK_API_KEY')
    if deepseek_key:
        print("✓ 使用DeepSeek API")
        return {
            'model': 'deepseek-chat',
            'model_server': 'https://api.deepseek.com/v1',
            'api_key': deepseek_key,
            'generate_cfg': {
                'top_p': 0.8,
                'max_tokens': 1500,
                'temperature': 0.7
            }
        }
    
    openrouter_key = os.getenv('OPENROUTER_API_KEY')
    if openrouter_key:
        print("✓ 使用OpenRouter API")
        return {
            'model': 'deepseek/deepseek-chat',
            'model_server': 'https://openrouter.ai/api/v1',
            'api_key': openrouter_key,
            'generate_cfg': {
                'top_p': 0.8,
                'max_tokens': 1500,
                'temperature': 0.7
            }
        }
    
    raise ValueError("未找到可用的API密钥")


def main():
    """主函数"""
    print("🤖 Qwen-Agent 基础版本")
    print("=" * 50)
    
    try:
        # 配置LLM
        llm_cfg = create_llm_config()
        
        # 系统提示
        system_instruction = '''你是一个友好的AI助手。你可以：

1. 使用simple_math工具进行数学计算
2. 使用echo_tool工具测试回声功能
3. 回答各种问题和进行日常对话

请根据用户需求选择合适的工具，并提供准确、友好的回答。'''

        # 创建Agent
        tools = ['simple_math', 'echo_tool']
        print(f"正在创建Agent，可用工具: {tools}")
        
        bot = Assistant(
            llm=llm_cfg,
            system_message=system_instruction,
            function_list=tools
        )
        print("✓ Agent创建成功！")
        
        # 对话循环
        messages = []
        print("\n开始对话 (输入'quit'退出):")
        print("💡 试试这些:")
        print("- 计算 15 + 25 * 2")
        print("- 回声测试: 你好世界")
        print("- 你好，介绍一下你自己")
        
        while True:
            user_input = input('\n用户: ').strip()
            
            if user_input.lower() in ['quit', 'exit', '退出', 'q']:
                print("再见！")
                break
            
            if not user_input:
                continue
            
            # 添加用户消息
            messages.append({'role': 'user', 'content': user_input})
            
            print('\nAssistant: ', end='', flush=True)
            response_text = ""
            
            try:
                # 调用Agent并流式显示
                for response in bot.run(messages=messages):
                    response_text = typewriter_print(response, response_text)
                
                # 添加响应到历史
                messages.extend(response)
                
            except Exception as e:
                print(f"错误: {str(e)}")
                print("请检查网络连接和API配置")
    
    except Exception as e:
        print(f"初始化失败: {str(e)}")
        print("\n请检查:")
        print("1. 网络连接")
        print("2. API密钥配置")
        print("3. 依赖安装")


if __name__ == "__main__":
    main() 