"""DeepSeek客户端测试

测试DeepSeek LLM API客户端的各项功能。
"""

import pytest
import json
from unittest.mock import AsyncMock, Mock, patch
from src.agent.models import Message, ChatResponse
from src.agent.deepseek_client import DeepSeekClient, DeepSeekClientError
from src.agent.http_client import HttpClientError


class TestDeepSeekClient:
    """测试DeepSeek客户端"""
    
    @pytest.fixture
    def mock_config(self):
        """模拟配置管理器"""
        config = Mock()
        config.deepseek.api_key = "test-key"
        config.deepseek.base_url = "https://api.deepseek.com"
        config.deepseek.model = "deepseek-reasoner"
        config.deepseek.temperature = 0.7
        config.deepseek.max_tokens = 2000
        config.deepseek.timeout = 30.0
        config.deepseek.max_retries = 3
        return config
    
    @pytest.fixture
    def client(self, mock_config):
        """创建DeepSeek客户端"""
        return DeepSeekClient(mock_config)
    
    def test_client_initialization(self, client, mock_config):
        """测试客户端初始化"""
        assert client.config == mock_config
        assert client.http_client is not None
    
    @pytest.mark.asyncio
    async def test_chat_completion_success(self, client):
        """测试聊天完成成功"""
        # 模拟HTTP响应
        mock_response = {
            "id": "test-id",
            "object": "chat.completion",
            "created": 1234567890,
            "model": "deepseek-reasoner",
            "choices": [{
                "index": 0,
                "message": {"role": "assistant", "content": "Hello!"},
                "finish_reason": "stop"
            }],
            "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15}
        }
        
        with patch.object(client.http_client, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response
            
            messages = [Message(role="user", content="Hi")]
            response = await client.chat_completion(messages)
            
            assert isinstance(response, ChatResponse)
            assert response.content == "Hello!"
            assert response.model == "deepseek-reasoner"
    
    @pytest.mark.asyncio
    async def test_chat_completion_with_custom_params(self, client):
        """测试自定义参数的聊天完成"""
        mock_response = {
            "id": "test-id",
            "object": "chat.completion",
            "created": 1234567890,
            "model": "custom-model",
            "choices": [{
                "index": 0,
                "message": {"role": "assistant", "content": "Custom response"},
                "finish_reason": "stop"
            }],
            "usage": {"prompt_tokens": 15, "completion_tokens": 10, "total_tokens": 25}
        }
        
        with patch.object(client.http_client, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response
            
            messages = [Message(role="user", content="Test")]
            response = await client.chat_completion(
                messages,
                model="custom-model",
                temperature=0.9,
                max_tokens=1000
            )
            
            # 验证调用参数
            call_args = mock_post.call_args
            payload = call_args[0][1]  # 第二个参数是payload
            
            assert payload["model"] == "custom-model"
            assert payload["temperature"] == 0.9
            assert payload["max_tokens"] == 1000
            assert payload["stream"] is False
    
    @pytest.mark.asyncio
    async def test_chat_completion_empty_messages(self, client):
        """测试空消息列表错误"""
        with pytest.raises(DeepSeekClientError) as exc_info:
            await client.chat_completion([])
        
        assert "消息列表不能为空" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_chat_completion_http_error(self, client):
        """测试HTTP错误处理"""
        with patch.object(client.http_client, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.side_effect = HttpClientError("API错误")
            
            messages = [Message(role="user", content="Test")]
            
            with pytest.raises(DeepSeekClientError) as exc_info:
                await client.chat_completion(messages)
            
            assert "DeepSeek API调用失败" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_stream_completion_success(self, client):
        """测试流式完成成功"""
        # 模拟流式响应
        stream_lines = [
            "data: " + json.dumps({
                "id": "test-id",
                "object": "chat.completion.chunk",
                "created": 1234567890,
                "model": "deepseek-reasoner",
                "choices": [{"delta": {"content": "Hello"}}]
            }),
            "data: " + json.dumps({
                "id": "test-id",
                "object": "chat.completion.chunk",
                "created": 1234567890,
                "model": "deepseek-reasoner",
                "choices": [{"delta": {"content": " world!"}}]
            }),
            "data: [DONE]"
        ]
        
        async def mock_stream():
            for line in stream_lines:
                yield line
        
        with patch.object(client.http_client, 'stream_post', return_value=mock_stream()):
            messages = [Message(role="user", content="Hi")]
            chunks = []
            
            async for chunk in client.stream_completion(messages):
                chunks.append(chunk)
            
            assert len(chunks) == 2
            assert chunks[0].delta_content == "Hello"
            assert chunks[1].delta_content == " world!" 