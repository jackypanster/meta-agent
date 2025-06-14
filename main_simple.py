#!/usr/bin/env python3
"""
Qwen-Agent MVP - 简洁直观实现

基于官方Qwen-Agent框架的最简洁实现：
- 直接使用Assistant类
- 用@register_tool注册工具
- 简单的内存管理
- 直观的CLI界面
"""

import os
import json
import time
from typing import Dict, List
from dotenv import load_dotenv

# Qwen-Agent imports
from qwen_agent.agents import Assistant
from qwen_agent.tools.base import BaseTool, register_tool
from qwen_agent.utils.output_beautify import typewriter_print

# 加载环境变量
load_dotenv()

# 简单的内存存储 - 直接用字典，不搞复杂的
MEMORY_STORE = {
    'facts': [],      # 用户事实信息
    'preferences': [], # 用户偏好
    'history': []     # 对话历史
}


@register_tool('save_info')
class SaveInfoTool(BaseTool):
    """保存用户信息工具"""
    description = '保存用户提到的重要信息，如姓名、兴趣爱好、工作等'
    parameters = [{
        'name': 'info',
        'type': 'string', 
        'description': '要保存的信息内容',
        'required': True
    }, {
        'name': 'type',
        'type': 'string',
        'description': '信息类型：fact(事实) 或 preference(偏好)',
        'required': False
    }]

    def call(self, params: str, **kwargs) -> str:
        try:
            data = json.loads(params)
            info = data['info']
            info_type = data.get('type', 'fact')
            
            # 简单保存到内存
            entry = {
                'content': info,
                'timestamp': time.time(),
                'time_str': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            if info_type == 'preference':
                MEMORY_STORE['preferences'].append(entry)
            else:
                MEMORY_STORE['facts'].append(entry)
            
            return json.dumps({
                'status': 'saved',
                'message': f'已保存{info_type}: {info}'
            }, ensure_ascii=False)
            
        except Exception as e:
            return json.dumps({'error': f'保存失败: {str(e)}'})


@register_tool('recall_info') 
class RecallInfoTool(BaseTool):
    """回忆用户信息工具"""
    description = '搜索之前保存的用户信息'
    parameters = [{
        'name': 'query',
        'type': 'string',
        'description': '要搜索的关键词，如"姓名"、"爱好"等',
        'required': True
    }]

    def call(self, params: str, **kwargs) -> str:
        try:
            data = json.loads(params)
            query = data['query'].lower()
            
            # 简单的关键词搜索
            results = []
            
            for fact in MEMORY_STORE['facts']:
                if query in fact['content'].lower():
                    results.append(fact)
                    
            for pref in MEMORY_STORE['preferences']:
                if query in pref['content'].lower():
                    results.append(pref)
            
            if results:
                return json.dumps({
                    'found': True,
                    'count': len(results),
                    'results': results[-3:]  # 最近3条
                }, ensure_ascii=False)
            else:
                return json.dumps({
                    'found': False,
                    'message': '没有找到相关信息'
                })
                
        except Exception as e:
            return json.dumps({'error': f'搜索失败: {str(e)}'})


@register_tool('calculate')
class CalculatorTool(BaseTool):
    """计算器工具"""
    description = '执行数学计算'
    parameters = [{
        'name': 'expression',
        'type': 'string',
        'description': '数学表达式，如 "2 + 3" 或 "sin(3.14/2)"',
        'required': True
    }]

    def call(self, params: str, **kwargs) -> str:
        try:
            data = json.loads(params)
            expression = data['expression']
            
            # 安全计算 - 只允许数学运算
            import math
            allowed_names = {
                k: v for k, v in math.__dict__.items() if not k.startswith("__")
            }
            allowed_names.update({"abs": abs, "round": round})
            
            result = eval(expression, {"__builtins__": {}}, allowed_names)
            
            return json.dumps({
                'expression': expression,
                'result': result
            }, ensure_ascii=False)
            
        except Exception as e:
            return json.dumps({'error': f'计算错误: {str(e)}'})


def create_llm_config() -> Dict:
    """创建LLM配置 - 简单直接"""
    # 优先使用DeepSeek
    if api_key := os.getenv('DEEPSEEK_API_KEY'):
        print("✓ 使用DeepSeek API")
        return {
            'model': 'deepseek-chat',
            'model_server': 'https://api.deepseek.com/v1',
            'api_key': api_key,
            'generate_cfg': {
                'top_p': 0.8,
                'max_tokens': 2000,
                'temperature': 0.7
            }
        }
    
    # 备选OpenRouter
    if api_key := os.getenv('OPENROUTER_API_KEY'):
        print("✓ 使用OpenRouter API")
        return {
            'model': 'deepseek/deepseek-chat', 
            'model_server': 'https://openrouter.ai/api/v1',
            'api_key': api_key,
            'generate_cfg': {
                'top_p': 0.8,
                'max_tokens': 2000,
                'temperature': 0.7
            }
        }
    
    raise ValueError("需要设置DEEPSEEK_API_KEY或OPENROUTER_API_KEY环境变量")


def show_welcome():
    """显示欢迎信息"""
    print("🤖 Qwen-Agent MVP - 简洁版")
    print("=" * 50)
    print("这是一个基于Qwen-Agent的AI助手，具有：")
    print("• 💬 智能对话")
    print("• 🧠 记忆功能 - 记住您的信息")
    print("• 🧮 计算功能")
    print("• 📝 信息保存和回忆")
    print("\n💡 试试这些命令:")
    print("- 你好，我叫张三，喜欢编程")
    print("- 我的名字是什么？")
    print("- 计算 15 * 8 + 32")
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


def show_memory():
    """显示保存的记忆"""
    print("\n🧠 已保存的信息:")
    
    if MEMORY_STORE['facts']:
        print("\n📋 事实信息:")
        for i, fact in enumerate(MEMORY_STORE['facts'][-5:], 1):
            print(f"  {i}. {fact['content']} ({fact['time_str']})")
    
    if MEMORY_STORE['preferences']:
        print("\n❤️ 偏好信息:")
        for i, pref in enumerate(MEMORY_STORE['preferences'][-5:], 1):
            print(f"  {i}. {pref['content']} ({pref['time_str']})")
    
    if not MEMORY_STORE['facts'] and not MEMORY_STORE['preferences']:
        print("  还没有保存任何信息")


def main():
    """主函数 - 保持简单"""
    try:
        # 1. 显示欢迎界面
        show_welcome()
        
        # 2. 创建Agent
        print("\n🔧 正在初始化...")
        llm_cfg = create_llm_config()
        
        # 系统提示 - 简洁明了
        system_message = '''你是一个友好的AI助手。功能包括：

1. 💾 **主动记忆**: 当用户提到个人信息时，使用save_info工具保存
2. 🔍 **信息回忆**: 当用户询问之前的信息时，使用recall_info工具搜索
3. 🧮 **数学计算**: 使用calculate工具进行计算
4. 💬 **日常对话**: 友好、自然的交流

重要提示：
- 用户首次介绍姓名、爱好、工作等信息时，主动保存
- 当用户问"我是谁"、"我的爱好"等问题时，先搜索记忆
- 保持对话自然流畅，不要过度使用工具'''

        # 创建Agent
        tools = ['save_info', 'recall_info', 'calculate']
        agent = Assistant(
            llm=llm_cfg,
            system_message=system_message,
            function_list=tools
        )
        print("✓ Agent初始化成功！")
        
        # 3. 对话循环
        messages = []
        print("\n✨ 开始对话吧！\n")
        
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
                os.system('clear' if os.name != 'nt' else 'cls')
                show_welcome()
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
                for response in agent.run(messages=messages):
                    response_text = typewriter_print(response, response_text)
                
                # 添加响应到历史
                messages.extend(response)
                
                # 保存对话到简单历史记录
                MEMORY_STORE['history'].append({
                    'user': user_input,
                    'assistant': response_text,
                    'timestamp': time.time()
                })
                
                # 保持历史记录不超过50条
                if len(MEMORY_STORE['history']) > 50:
                    MEMORY_STORE['history'] = MEMORY_STORE['history'][-50:]
                
                print()  # 换行
                
            except Exception as e:
                print(f"\n❌ 出错了: {str(e)}")
                print("请检查网络连接和API配置")
    
    except Exception as e:
        print(f"\n❌ 初始化失败: {str(e)}")
        print("\n请检查:")
        print("1. 网络连接是否正常")
        print("2. API密钥是否正确设置")
        print("3. 依赖是否正确安装")


if __name__ == "__main__":
    main() 