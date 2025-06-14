"""DeepSeek LLM适配器

将DeepSeek客户端适配为Qwen-Agent框架兼容的LLM接口。
"""

import asyncio
from typing import List, Dict, Any, Union, Optional
import logging

from qwen_agent.llm import BaseChatModel

from .deepseek_client import DeepSeekClient
from .models import Message, ChatResponse
from ..config import ConfigManager


logger = logging.getLogger(__name__)


class DeepSeekLLMAdapter(BaseChatModel):
    """DeepSeek LLM适配器
    
    将DeepSeek客户端包装为Qwen-Agent兼容的BaseChatModel。
    """
    
    def __init__(self, config_manager: ConfigManager):
        """初始化适配器
        
        Args:
            config_manager: 配置管理器实例
        """
        super().__init__()
        self.config_manager = config_manager
        self.deepseek_client = DeepSeekClient(config_manager)
        self._initialized = False
    
    async def _ensure_initialized(self) -> None:
        """确保客户端已初始化"""
        if not self._initialized:
            # DeepSeekClient在__init__时就已经初始化，无需额外connect
            self._initialized = True
    
    def _convert_messages(self, messages: List[Dict[str, Any]]) -> List[Message]:
        """将Qwen-Agent消息格式转换为DeepSeek格式
        
        Args:
            messages: Qwen-Agent格式的消息列表
            
        Returns:
            DeepSeek格式的消息列表
        """
        converted = []
        for msg in messages:
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            
            # 处理不同的内容类型
            if isinstance(content, str):
                message_content = content
            elif isinstance(content, list):
                # 处理多模态内容（目前简化为文本）
                text_parts = [
                    item.get('text', '') for item in content 
                    if isinstance(item, dict) and item.get('type') == 'text'
                ]
                message_content = ' '.join(text_parts)
            else:
                message_content = str(content)
            
            converted.append(Message(role=role, content=message_content))
        
        return converted
    
    def _convert_response(self, response: ChatResponse) -> List[Dict[str, Any]]:
        """将DeepSeek响应转换为Qwen-Agent格式
        
        Args:
            response: DeepSeek LLM响应
            
        Returns:
            Qwen-Agent格式的响应 - 确保返回消息列表
        """
        # 确保返回的是标准的OpenAI格式消息列表
        message = {
            'role': 'assistant',
            'content': response.content
        }
        return [message]
    
    def chat(
        self, 
        messages: List[Dict[str, Any]], 
        functions: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """聊天接口（Qwen-Agent标准接口）
        
        Args:
            messages: 消息列表
            functions: 可用函数列表
            **kwargs: 其他参数
            
        Returns:
            响应消息列表
        """
        try:
            # 创建一个新的事件循环来处理异步调用
            import threading
            import queue
            
            result_queue = queue.Queue()
            
            def run_in_thread():
                # 在新线程中创建新的事件循环
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                try:
                    result = new_loop.run_until_complete(self._async_chat(messages, functions, **kwargs))
                    result_queue.put(('success', result))
                except Exception as e:
                    result_queue.put(('error', e))
                finally:
                    new_loop.close()
            
            # 在新线程中运行异步代码
            thread = threading.Thread(target=run_in_thread)
            thread.start()
            thread.join()
            
            # 获取结果
            status, result = result_queue.get()
            if status == 'success':
                return result
            else:
                raise result
        except Exception as e:
            logger.error(f"聊天过程中发生错误: {e}")
            return [{'role': 'assistant', 'content': f'抱歉，处理您的请求时发生错误: {str(e)}'}]
    
    async def _async_chat(
        self,
        messages: List[Dict[str, Any]], 
        functions: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """异步聊天实现
        
        Args:
            messages: 消息列表
            functions: 可用函数列表
            **kwargs: 其他参数
            
        Returns:
            响应消息列表
        """
        # 确保客户端已初始化
        await self._ensure_initialized()
        
        # 转换消息格式
        deepseek_messages = self._convert_messages(messages)
        
        try:
            # 调用DeepSeek客户端
            # 注意：当前DeepSeekClient暂不支持函数调用，统一使用普通聊天
            if functions:
                logger.warning("DeepSeek客户端暂不支持函数调用，将忽略functions参数")
            
            # 过滤出DeepSeek支持的参数
            supported_params = {
                'model': kwargs.get('model'),
                'temperature': kwargs.get('temperature'), 
                'max_tokens': kwargs.get('max_tokens')
            }
            # 移除None值
            supported_params = {k: v for k, v in supported_params.items() if v is not None}
            
            response = await self.deepseek_client.chat_completion(
                messages=deepseek_messages,
                **supported_params
            )
            
            # 转换响应格式
            return self._convert_response(response)
            
        except Exception as e:
            logger.error(f"DeepSeek API调用失败: {e}")
            raise
    
    def support_multimodal_input(self) -> bool:
        """是否支持多模态输入"""
        return False  # DeepSeek目前主要支持文本
    
    def support_multimodal_output(self) -> bool:
        """是否支持多模态输出"""
        return False  # DeepSeek目前主要输出文本
    
    def support_audio_input(self) -> bool:
        """是否支持音频输入"""
        return False  # DeepSeek目前不支持音频
    
    async def close(self) -> None:
        """关闭客户端连接"""
        if self._initialized:
            await self.deepseek_client.close()
            self._initialized = False
    
    def _chat_no_stream(
        self,
        messages: List[Dict[str, Any]],
        functions: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """非流式聊天（Qwen-Agent抽象方法实现）"""
        return self.chat(messages, functions, **kwargs)
    
    def _chat_stream(
        self,
        messages: List[Dict[str, Any]],
        functions: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ):
        """流式聊天（Qwen-Agent抽象方法实现）"""
        # 目前返回非流式结果，后续可扩展为真正的流式处理
        response = self.chat(messages, functions, **kwargs)
        # 确保每次yield都是消息列表
        if response:
            yield response
        else:
            yield [{'role': 'assistant', 'content': ''}]
    
    def _chat_with_functions(
        self,
        messages: List[Dict[str, Any]],
        functions: List[Dict[str, Any]],
        **kwargs
    ) -> List[Dict[str, Any]]:
        """带函数调用的聊天（Qwen-Agent抽象方法实现）"""
        return self.chat(messages, functions, **kwargs) 