"""DeepSeek LLM客户端

实现DeepSeek API的专用客户端，支持聊天完成和流式响应。
"""

import json
from typing import List, Optional, AsyncGenerator
from ..config.manager import ConfigManager
from .http_client import AsyncHttpClient, HttpClientError
from .models import Message, ChatResponse, StreamChunk


class DeepSeekClientError(Exception):
    """DeepSeek客户端错误"""
    pass


class DeepSeekClient:
    """DeepSeek LLM API客户端"""
    
    def __init__(self, config_manager: Optional[ConfigManager] = None):
        """初始化DeepSeek客户端"""
        self.config = config_manager or ConfigManager()
        deepseek_config = self.config.deepseek
        
        headers = {
            "Authorization": f"Bearer {deepseek_config.api_key}",
            "Content-Type": "application/json"
        }
        
        self.http_client = AsyncHttpClient(
            base_url=deepseek_config.base_url,
            headers=headers,
            timeout=deepseek_config.timeout,
            max_retries=deepseek_config.max_retries
        )
    
    def _build_payload(self, messages: List[Message], model: Optional[str] = None,
                      temperature: Optional[float] = None, max_tokens: Optional[int] = None,
                      stream: bool = False) -> dict:
        """构建请求payload"""
        if not messages:
            raise DeepSeekClientError("消息列表不能为空")
        
        deepseek_config = self.config.deepseek
        return {
            "model": model or deepseek_config.model_name,
            "messages": [msg.to_dict() for msg in messages],
            "temperature": temperature or deepseek_config.temperature,
            "max_tokens": max_tokens or deepseek_config.max_tokens,
            "stream": stream
        }
    
    async def chat_completion(
        self,
        messages: List[Message],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> ChatResponse:
        """聊天完成API调用"""
        payload = self._build_payload(messages, model, temperature, max_tokens, False)
        
        try:
            response_data = await self.http_client.post("v1/chat/completions", payload)
            return ChatResponse(**response_data)
        except HttpClientError as e:
            raise DeepSeekClientError(f"DeepSeek API调用失败: {str(e)}") from e
    
    async def stream_completion(
        self,
        messages: List[Message],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> AsyncGenerator[StreamChunk, None]:
        """流式聊天完成"""
        payload = self._build_payload(messages, model, temperature, max_tokens, True)
        
        try:
            async for line in self.http_client.stream_post("v1/chat/completions", payload):
                if line.strip() and line.startswith("data: "):
                    data = line[6:]  # 移除 "data: " 前缀
                    if data.strip() == "[DONE]":
                        break
                    try:
                        chunk_data = json.loads(data)
                        yield StreamChunk(**chunk_data)
                    except json.JSONDecodeError:
                        continue
        except HttpClientError as e:
            raise DeepSeekClientError(f"DeepSeek流式API调用失败: {str(e)}") from e 