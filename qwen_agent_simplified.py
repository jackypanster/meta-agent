#!/usr/bin/env python3
"""
Qwen-Agent MVP - 简化版本

基于官方Qwen-Agent文档，创建一个更简洁的实现：
1. 使用官方Assistant类
2. 注册MCP工具作为自定义工具
3. 集成内存管理
4. 保持简单的CLI界面
"""

import os
import json
import asyncio
from typing import List, Dict, Any
from dotenv import load_dotenv

# Qwen-Agent imports
from qwen_agent.agents import Assistant
from qwen_agent.tools.base import BaseTool, register_tool
from qwen_agent.utils.output_beautify import typewriter_print

# 项目内部模块
from src.config.manager import ConfigManager
from src.memory.manager import MemoryManager

# 加载环境变量
load_dotenv()


@register_tool('memory_search')
class MemorySearchTool(BaseTool):
    """内存搜索工具 - 集成mem0功能"""
    description = '在对话记忆中搜索相关信息，可以查找用户之前提到的信息'
    parameters = [{
        'name': 'query',
        'type': 'string',
        'description': '要搜索的内容，例如用户名、兴趣爱好等',
        'required': True
    }]
    
    def __init__(self):
        super().__init__()
        self.memory_manager = None
    
    def set_memory_manager(self, memory_manager):
        """设置内存管理器实例"""
        self.memory_manager = memory_manager
    
    def call(self, params: str, **kwargs) -> str:
        """执行内存搜索"""
        try:
            if not self.memory_manager:
                return json.dumps({'error': '内存管理器未初始化'})
            
            query_data = json.loads(params)
            query = query_data['query']
            
            # 同步调用异步方法
            import asyncio
            try:
                loop = asyncio.get_event_loop()
                memories = loop.run_until_complete(
                    self.memory_manager.search_memories(query, session_id="cli_session", limit=3)
                )
            except RuntimeError:
                # 如果没有事件循环，创建一个新的
                memories = asyncio.run(
                    self.memory_manager.search_memories(query, session_id="cli_session", limit=3)
                )
            
            if memories:
                return json.dumps({
                    'found_memories': memories,
                    'count': len(memories)
                }, ensure_ascii=False)
            else:
                return json.dumps({'message': '未找到相关记忆'})
                
        except Exception as e:
            return json.dumps({'error': f'搜索失败: {str(e)}'})


@register_tool('save_memory')
class SaveMemoryTool(BaseTool):
    """保存记忆工具"""
    description = '保存重要信息到记忆中，如用户的名字、偏好等'
    parameters = [{
        'name': 'content',
        'type': 'string',
        'description': '要保存的重要信息内容',
        'required': True
    }]
    
    def __init__(self):
        super().__init__()
        self.memory_manager = None
    
    def set_memory_manager(self, memory_manager):
        """设置内存管理器实例"""
        self.memory_manager = memory_manager
    
    def call(self, params: str, **kwargs) -> str:
        """保存记忆"""
        try:
            if not self.memory_manager:
                return json.dumps({'error': '内存管理器未初始化'})
            
            content_data = json.loads(params)
            content = content_data['content']
            
            # 同步调用异步方法
            import asyncio
            try:
                loop = asyncio.get_event_loop()
                loop.run_until_complete(
                    self.memory_manager.store_fact(content, session_id="cli_session")
                )
            except RuntimeError:
                asyncio.run(
                    self.memory_manager.store_fact(content, session_id="cli_session")
                )
            
            return json.dumps({'message': '信息已保存到记忆中'})
                
        except Exception as e:
            return json.dumps({'error': f'保存失败: {str(e)}'})


class QwenAgentSimplified:
    """简化版Qwen-Agent MVP"""
    
    def __init__(self):
        self.config = None
        self.memory_manager = None
        self.agent = None
        self.memory_tool = None
        self.save_tool = None
        
    async def initialize(self):
        """异步初始化"""
        try:
            # 初始化配置
            self.config = ConfigManager()
            print("✓ 配置加载成功")
            
            # 初始化内存管理
            self.memory_manager = MemoryManager(self.config)
            await self.memory_manager.__aenter__()  # 使用异步上下文管理器
            print("✓ 内存管理器初始化成功")
            
            # 创建并配置工具实例
            self.memory_tool = MemorySearchTool()
            self.memory_tool.set_memory_manager(self.memory_manager)
            
            self.save_tool = SaveMemoryTool()
            self.save_tool.set_memory_manager(self.memory_manager)
            
            # 配置LLM
            llm_cfg = self._create_llm_config()
            print("✓ LLM配置创建成功")
            
            # 系统提示
            system_instruction = '''你是一个有用的AI助手。你具有以下能力：

1. **记忆功能**：
   - 使用memory_search工具搜索之前的对话记忆
   - 使用save_memory工具保存用户的重要信息
   - 当用户提到个人信息时，主动保存到记忆中

2. **对话能力**：
   - 友好、专业的对话
   - 根据上下文和记忆提供个性化回答
   - 支持中英文交流

使用记忆功能的最佳实践：
- 当用户首次介绍自己时，保存其姓名和基本信息
- 当用户提到兴趣爱好、工作等信息时，主动保存
- 在后续对话中，适时搜索和使用记忆信息
- 让对话更有连续性和个性化'''

            # 创建Agent
            tools = ['memory_search', 'save_memory', 'code_interpreter']
            self.agent = Assistant(
                llm=llm_cfg,
                system_message=system_instruction,
                function_list=tools
            )
            print(f"✓ Agent创建成功，可用工具: {tools}")
            
            return True
            
        except Exception as e:
            print(f"✗ 初始化失败: {str(e)}")
            return False
    
    def _create_llm_config(self) -> Dict[str, Any]:
        """创建LLM配置"""
        deepseek_key = os.getenv('DEEPSEEK_API_KEY')
        if deepseek_key:
            return {
                'model': 'deepseek-chat',
                'model_server': 'https://api.deepseek.com/v1',
                'api_key': deepseek_key,
                'generate_cfg': {
                    'top_p': 0.8,
                    'max_tokens': 2000,
                    'temperature': 0.7
                }
            }
        
        openrouter_key = os.getenv('OPENROUTER_API_KEY')
        if openrouter_key:
            return {
                'model': 'deepseek/deepseek-chat',
                'model_server': 'https://openrouter.ai/api/v1',
                'api_key': openrouter_key,
                'generate_cfg': {
                    'top_p': 0.8,
                    'max_tokens': 2000,
                    'temperature': 0.7
                }
            }
        
        raise ValueError("未找到可用的API密钥")
    
    async def chat(self, messages: List[Dict[str, str]]) -> str:
        """处理对话"""
        try:
            response_text = ""
            for response in self.agent.run(messages=messages):
                # 累积响应文本
                if isinstance(response, list) and response:
                    last_msg = response[-1]
                    if isinstance(last_msg, dict) and 'content' in last_msg:
                        response_text = last_msg['content']
            
            return response_text
        except Exception as e:
            return f"对话处理出错: {str(e)}"
    
    async def cleanup(self):
        """清理资源"""
        if self.memory_manager:
            await self.memory_manager.__aexit__(None, None, None)


async def main():
    """主函数"""
    print("🤖 Qwen-Agent MVP - 简化版")
    print("=" * 50)
    
    # 创建并初始化Agent
    agent = QwenAgentSimplified()
    
    if not await agent.initialize():
        print("初始化失败，退出程序")
        return
    
    print("\n✨ 开始对话 (输入'quit'退出)")
    print("💡 建议尝试:")
    print("- 你好，我叫张三")
    print("- 我的名字是什么？")
    print("- 我喜欢编程和阅读")
    print("- 我有什么兴趣爱好？")
    
    messages = []
    
    try:
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
            
            # 获取响应并流式显示
            response_text = ""
            for response in agent.agent.run(messages=messages):
                response_text = typewriter_print(response, response_text)
            
            # 添加Assistant响应到历史
            messages.extend(response)
            
    except KeyboardInterrupt:
        print("\n\n程序被用户中断")
    except Exception as e:
        print(f"\n运行时错误: {str(e)}")
    finally:
        await agent.cleanup()


if __name__ == "__main__":
    asyncio.run(main()) 