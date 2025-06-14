"""MCP工具集成测试

测试SSE解析、MCP客户端连接、工具发现和工具调用功能。
"""

import asyncio
import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.tools.models import (
    SSEEvent, MCPRequest, MCPResponse, MCPError, ToolDefinition, 
    ToolParameter, ToolCall, ToolResult, MCPClientStatus
)
from src.tools.sse_parser import SSEParser, SSEParseError
from src.tools.mcp_client import MCPClient, MCPConnectionError
from src.tools.tool_manager import ToolManager, ToolExecutionError
from src.config import ConfigManager


@pytest.fixture
def config_manager():
    """配置管理器fixture"""
    config = MagicMock(spec=ConfigManager)
    # 模拟MCP配置
    mcp_config = MagicMock()
    mcp_config.server_url = "https://mcp.context7.com/sse"
    config.mcp = mcp_config
    return config


@pytest.fixture
def mock_session():
    """模拟HTTP会话"""
    session = AsyncMock()
    
    # 模拟成功响应
    mock_response = AsyncMock()
    mock_response.status = 200
    
    # 模拟SSE流
    async def mock_content():
        yield b'data: {"jsonrpc": "2.0", "id": "1", "result": {"tools": []}}\n\n'
    
    mock_response.content = mock_content()
    
    # 确保上下文管理器返回正确的响应
    async_context_manager = AsyncMock()
    async_context_manager.__aenter__.return_value = mock_response
    async_context_manager.__aexit__.return_value = None
    session.post.return_value = async_context_manager
    
    return session


class TestSSEParser:
    """SSE解析器测试"""
    
    def test_parse_simple_event(self):
        parser = SSEParser()
        
        # 测试数据事件
        event = parser.parse_line("data: hello world")
        assert event is None
        
        # 空行结束事件
        event = parser.parse_line("")
        assert event is not None
        assert event.data == "hello world"
    
    def test_parse_complex_event(self):
        parser = SSEParser()
        
        parser.parse_line("event: message")
        parser.parse_line("id: 123")
        parser.parse_line("data: test data")
        parser.parse_line("retry: 5000")
        
        event = parser.parse_line("")
        assert event.event == "message"
        assert event.id == "123"
        assert event.data == "test data"
        assert event.retry == 5000
    
    def test_parse_multiline_data(self):
        parser = SSEParser()
        
        parser.parse_line("data: line 1")
        parser.parse_line("data: line 2")
        
        event = parser.parse_line("")
        assert event.data == "line 1\nline 2"
    
    def test_parse_json_data(self):
        parser = SSEParser()
        test_data = {"message": "hello", "value": 123}
        
        parser.parse_line(f"data: {json.dumps(test_data)}")
        event = parser.parse_line("")
        
        parsed_data = event.parse_data()
        assert parsed_data == test_data
    
    @pytest.mark.asyncio
    async def test_parse_stream(self):
        parser = SSEParser()
        
        async def mock_stream():
            yield "data: first event\n\n"
            yield "event: test\ndata: second event\n\n"
        
        events = []
        async for event in parser.parse_stream(mock_stream()):
            events.append(event)
        
        assert len(events) == 2
        assert events[0].data == "first event"
        assert events[1].event == "test"
        assert events[1].data == "second event"
    
    def test_parse_mcp_response(self):
        parser = SSEParser()
        response_data = {
            "jsonrpc": "2.0",
            "id": "123",
            "result": {"status": "ok"}
        }
        
        parser.parse_line(f"data: {json.dumps(response_data)}")
        event = parser.parse_line("")
        
        mcp_response = parser.parse_mcp_response(event)
        assert mcp_response is not None
        assert mcp_response.id == "123"
        assert mcp_response.result == {"status": "ok"}
        assert mcp_response.is_success
    
    def test_create_sse_data(self):
        data = {"message": "test", "id": 123}
        sse_data = SSEParser.create_sse_data(data, "test-event")
        
        expected = "event: test-event\ndata: {\"message\": \"test\", \"id\": 123}\n"
        assert sse_data == expected


class TestMCPClient:
    """MCP客户端测试"""
    
    @pytest.mark.asyncio
    async def test_connect_success(self, config_manager, mock_session):
        with patch('aiohttp.ClientSession', return_value=mock_session):
            client = MCPClient(config_manager)
            
            success = await client.connect()
            assert success
            assert client.status.connected
            assert client.status.last_error is None
    
    @pytest.mark.asyncio
    async def test_connect_failure_no_url(self, config_manager):
        config_manager.mcp.server_url = ""
        client = MCPClient(config_manager)
        
        success = await client.connect()
        assert not success
        assert not client.status.connected
        assert "未配置MCP服务器URL" in client.status.last_error
    
    @pytest.mark.asyncio
    async def test_disconnect(self, config_manager, mock_session):
        with patch('aiohttp.ClientSession', return_value=mock_session):
            client = MCPClient(config_manager)
            await client.connect()
            
            await client.disconnect()
            assert not client.status.connected
            assert len(client.available_tools) == 0
    
    def test_tool_management(self, config_manager):
        """测试工具管理功能"""
        client = MCPClient(config_manager)
        
        # 手动添加工具用于测试
        tool_def = ToolDefinition(
            name="test_tool",
            description="测试工具",
            parameters={
                "param1": ToolParameter(type="string", required=True)
            }
        )
        client.available_tools["test_tool"] = tool_def
        
        # 测试工具获取
        assert "test_tool" in client.available_tools
        tool = client.get_tool("test_tool")
        assert tool.name == "test_tool"
        assert tool.description == "测试工具"
        
        # 测试工具列表
        tools = client.list_tools()
        assert "test_tool" in tools
    
    @pytest.mark.asyncio
    async def test_context_manager(self, config_manager, mock_session):
        with patch('aiohttp.ClientSession', return_value=mock_session):
            async with MCPClient(config_manager) as client:
                assert client.status.connected
            
            assert not client.status.connected


class TestToolManager:
    """工具管理器测试"""
    
    @pytest.fixture
    def mcp_client(self, config_manager):
        client = MagicMock(spec=MCPClient)
        client.get_tool.return_value = ToolDefinition(
            name="test_tool",
            description="测试工具",
            parameters={
                "param1": ToolParameter(type="string", required=True)
            }
        )
        client._get_request_id.return_value = "123"
        client._send_request.return_value = MCPResponse(
            id="123",
            result={"output": "success"}
        )
        return client
    
    @pytest.mark.asyncio
    async def test_execute_tool_success(self, mcp_client):
        manager = ToolManager(mcp_client)
        
        tool_call = ToolCall(
            name="test_tool",
            arguments={"param1": "value1"},
            call_id="call_123"
        )
        
        result = await manager.execute_tool(tool_call)
        
        assert result.is_success
        assert result.result == {"output": "success"}
        assert result.call_id == "call_123"
    
    @pytest.mark.asyncio
    async def test_execute_tool_missing_param(self, mcp_client):
        manager = ToolManager(mcp_client)
        
        tool_call = ToolCall(
            name="test_tool",
            arguments={},  # 缺少必需参数
            call_id="call_123"
        )
        
        result = await manager.execute_tool(tool_call)
        
        assert not result.is_success
        assert "缺少必需参数" in result.error
    
    @pytest.mark.asyncio
    async def test_execute_tool_not_found(self, mcp_client):
        mcp_client.get_tool.return_value = None
        manager = ToolManager(mcp_client)
        
        tool_call = ToolCall(
            name="nonexistent_tool",
            arguments={},
            call_id="call_123"
        )
        
        result = await manager.execute_tool(tool_call)
        
        assert not result.is_success
        assert "工具不存在" in result.error
    
    @pytest.mark.asyncio
    async def test_execute_tools_batch(self, mcp_client):
        manager = ToolManager(mcp_client)
        
        tool_calls = [
            ToolCall(name="test_tool", arguments={"param1": "value1"}, call_id="call_1"),
            ToolCall(name="test_tool", arguments={"param1": "value2"}, call_id="call_2")
        ]
        
        results = await manager.execute_tools_batch(tool_calls)
        
        assert len(results) == 2
        assert all(result.is_success for result in results)
    
    def test_execution_stats(self, mcp_client):
        manager = ToolManager(mcp_client)
        
        # 添加一些执行历史
        manager.execution_history = [
            {"success": True, "duration": 1.0},
            {"success": False, "duration": 2.0},
            {"success": True, "duration": 1.5}
        ]
        
        stats = manager.get_execution_stats()
        
        assert stats["total_calls"] == 3
        assert stats["successful_calls"] == 2
        assert stats["success_rate"] == 2/3
        assert stats["average_duration"] == 1.5 