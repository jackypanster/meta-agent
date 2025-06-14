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
            await self.deepseek_client.connect()
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
            Qwen-Agent格式的响应
        """
        return [{
            'role': 'assistant',
            'content': response.content
        }]
    
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
            # 运行异步聊天方法
            return asyncio.run(self._async_chat(messages, functions, **kwargs))
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
            if functions:
                # 有函数调用的情况
                response = await self.deepseek_client.chat_completion_with_functions(
                    messages=deepseek_messages,
                    functions=functions,
                    **kwargs
                )
            else:
                # 普通聊天
                response = await self.deepseek_client.chat_completion(
                    messages=deepseek_messages,
                    **kwargs
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