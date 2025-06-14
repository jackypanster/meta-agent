"""代理模型和HTTP客户端测试

测试消息模型和HTTP客户端的基础功能。
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from src.agent.models import Message, ChatResponse, ChatChoice, ChatUsage, FunctionCall
from src.agent.http_client import AsyncHttpClient, HttpClientError


class TestMessage:
    """测试消息模型"""
    
    def test_create_user_message(self):
        """测试创建用户消息"""
        msg = Message(role="user", content="Hello")
        assert msg.role == "user"
        assert msg.content == "Hello"
        assert msg.name is None
        assert msg.function_call is None
    
    def test_create_assistant_message(self):
        """测试创建助手消息"""
        msg = Message(role="assistant", content="Hi there")
        assert msg.role == "assistant"
        assert msg.content == "Hi there"
    
    def test_create_function_message(self):
        """测试创建函数消息"""
        msg = Message(role="function", name="test_func", content="result")
        assert msg.role == "function"
        assert msg.name == "test_func"
        assert msg.content == "result"
    
    def test_to_dict(self):
        """测试转换为字典"""
        msg = Message(role="assistant", content="Hi there")
        data = msg.to_dict()
        assert data == {"role": "assistant", "content": "Hi there"}
    
    def test_to_dict_with_function_call(self):
        """测试包含函数调用的消息转换"""
        func_call = {"name": "test_func", "arguments": "{}"}
        msg = Message(role="assistant", function_call=func_call)
        data = msg.to_dict()
        assert "function_call" in data
        assert data["function_call"] == func_call


class TestChatResponse:
    """测试聊天响应模型"""
    
    def test_content_property(self):
        """测试内容属性"""
        choice = ChatChoice(
            index=0,
            message=Message(role="assistant", content="Hello!"),
            finish_reason="stop"
        )
        usage = ChatUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15)
        
        response = ChatResponse(
            id="test-id",
            object="chat.completion",
            created=1234567890,
            model="deepseek-reasoner",
            choices=[choice],
            usage=usage
        )
        
        assert response.content == "Hello!"
    
    def test_empty_choices(self):
        """测试空选择列表"""
        usage = ChatUsage(prompt_tokens=10, completion_tokens=0, total_tokens=10)
        response = ChatResponse(
            id="test-id",
            object="chat.completion",
            created=1234567890,
            model="deepseek-reasoner",
            choices=[],
            usage=usage
        )
        
        assert response.content is None


class TestAsyncHttpClient:
    """测试HTTP客户端"""
    
    @pytest.fixture
    def client(self):
        """创建HTTP客户端"""
        return AsyncHttpClient("https://api.test.com", headers={"Auth": "token"})
    
    @pytest.mark.asyncio
    @patch('httpx.AsyncClient')
    async def test_post_success(self, mock_client_class, client):
        """测试POST请求成功"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": "success"}
        
        mock_client = AsyncMock()
        mock_client.request = AsyncMock(return_value=mock_response)
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        result = await client.post("test", {"data": "value"})
        assert result == {"result": "success"}
    
    @pytest.mark.asyncio
    @patch('httpx.AsyncClient')
    async def test_post_http_error(self, mock_client_class, client):
        """测试HTTP错误处理"""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        
        mock_client = AsyncMock()
        mock_client.request = AsyncMock(return_value=mock_response)
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        with pytest.raises(HttpClientError) as exc_info:
            await client.post("test", {"data": "value"})
        
        assert "HTTP错误 400" in str(exc_info.value)
        assert exc_info.value.status_code == 400 