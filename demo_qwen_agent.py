#!/usr/bin/env python3
"""
基于Qwen-Agent官方文档的最小demo

根据官方文档: https://github.com/QwenLM/Qwen-Agent
测试基本的Qwen-Agent功能，包括：
1. 自定义工具注册
2. LLM配置
3. Agent创建和对话
"""

import os
import pprint
import urllib.parse
import json5
from qwen_agent.agents import Assistant
from qwen_agent.tools.base import BaseTool, register_tool
from qwen_agent.utils.output_beautify import typewriter_print
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# Step 1: 添加自定义工具
@register_tool('simple_calculator')
class SimpleCalculator(BaseTool):
    """简单计算器工具 - 用于替代官方例子中需要额外资源的图像生成工具"""
    description = '简单计算器，可以执行基本的数学运算：加法、减法、乘法、除法'
    parameters = [{
        'name': 'expression',
        'type': 'string',
        'description': '要计算的数学表达式，例如: "2 + 3" 或 "10 * 5"',
        'required': True
    }]

    def call(self, params: str, **kwargs) -> str:
        """执行计算"""
        try:
            expression = json5.loads(params)['expression']
            # 安全的数学表达式计算（仅支持基本运算）
            allowed_chars = set('0123456789+-*/.() ')
            if not all(c in allowed_chars for c in expression):
                return json5.dumps({'error': '只支持基本数学运算：+、-、*、/、()和数字'})
            
            result = eval(expression)
            return json5.dumps({
                'expression': expression,
                'result': result
            }, ensure_ascii=False)
        except Exception as e:
            return json5.dumps({'error': f'计算错误: {str(e)}'})


@register_tool('weather_info')
class WeatherInfo(BaseTool):
    """模拟天气信息工具"""
    description = '获取指定城市的天气信息（模拟数据）'
    parameters = [{
        'name': 'city',
        'type': 'string',
        'description': '城市名称，例如: "北京" 或 "Shanghai"',
        'required': True
    }]

    def call(self, params: str, **kwargs) -> str:
        """返回模拟天气数据"""
        try:
            city = json5.loads(params)['city']
            # 模拟天气数据
            weather_data = {
                'city': city,
                'temperature': '22°C',
                'condition': '晴朗',
                'humidity': '65%',
                'wind': '微风',
                'note': '这是模拟数据，用于演示工具调用功能'
            }
            return json5.dumps(weather_data, ensure_ascii=False)
        except Exception as e:
            return json5.dumps({'error': f'获取天气信息失败: {str(e)}'})


def create_llm_config():
    """创建LLM配置"""
    # 优先使用DeepSeek，因为我们有API key
    deepseek_key = os.getenv('DEEPSEEK_API_KEY')
    if deepseek_key:
        print("✓ 使用DeepSeek API")
        return {
            'model': 'deepseek-chat',
            'model_server': 'https://api.deepseek.com/v1',
            'api_key': deepseek_key,
            'generate_cfg': {
                'top_p': 0.8,
                'max_tokens': 1000
            }
        }
    
    # 备选：OpenRouter
    openrouter_key = os.getenv('OPENROUTER_API_KEY')
    if openrouter_key:
        print("✓ 使用OpenRouter API")
        return {
            'model': 'deepseek/deepseek-chat',
            'model_server': 'https://openrouter.ai/api/v1',
            'api_key': openrouter_key,
            'generate_cfg': {
                'top_p': 0.8,
                'max_tokens': 1000
            }
        }
    
    raise ValueError("未找到可用的API密钥。请在.env文件中设置DEEPSEEK_API_KEY或OPENROUTER_API_KEY")


def main():
    """主函数"""
    print("🤖 Qwen-Agent 最小Demo")
    print("=" * 50)
    
    try:
        # Step 2: 配置LLM
        llm_cfg = create_llm_config()
        
        # Step 3: 创建Agent
        system_instruction = '''你是一个有用的AI助手。你可以：
1. 使用计算器进行数学运算
2. 查询天气信息（模拟数据）
3. 回答各种问题

请根据用户的需求选择合适的工具，并提供友好、准确的回答。'''
        
        tools = ['simple_calculator', 'weather_info']
        
        print(f"正在创建Agent，可用工具: {tools}")
        bot = Assistant(
            llm=llm_cfg,
            system_message=system_instruction,
            function_list=tools
        )
        print("✓ Agent创建成功！")
        
        # Step 4: 运行对话循环
        messages = []
        print("\n开始对话（输入'quit'退出）:")
        print("示例问题:")
        print("- 帮我计算 15 * 8 + 32")
        print("- 北京今天天气怎么样？")
        print("- 你好，请介绍一下你自己")
        
        while True:
            user_input = input('\n用户: ').strip()
            
            if user_input.lower() in ['quit', 'exit', '退出', 'q']:
                print("再见！")
                break
            
            if not user_input:
                continue
            
            # 添加用户消息到历史
            messages.append({'role': 'user', 'content': user_input})
            
            print('\nAssistant: ', end='', flush=True)
            response = []
            response_plain_text = ''
            
            try:
                # 调用Agent
                for response in bot.run(messages=messages):
                    # 流式输出
                    response_plain_text = typewriter_print(response, response_plain_text)
                
                # 添加Assistant响应到历史
                messages.extend(response)
                
            except Exception as e:
                print(f"错误: {str(e)}")
                print("请检查网络连接和API配置")
    
    except Exception as e:
        print(f"初始化失败: {str(e)}")
        print("\n请检查:")
        print("1. 网络连接是否正常")
        print("2. .env文件中的API密钥是否正确")
        print("3. 依赖是否正确安装")


if __name__ == "__main__":
    main() 