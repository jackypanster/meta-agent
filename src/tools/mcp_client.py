"""MCP客户端核心

实现与Context7 MCP服务器的连接和工具发现。
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional
import aiohttp
from src.config import ConfigManager
from .models import MCPRequest, MCPResponse, ToolDefinition, MCPClientStatus
from .sse_parser import SSEParser

logger = logging.getLogger(__name__)


class MCPConnectionError(Exception):
    """MCP连接错误"""
    pass


class MCPClient:
    """MCP客户端"""
    
    def __init__(self, config_manager: ConfigManager):
        self.config = config_manager
        self.session: Optional[aiohttp.ClientSession] = None
        self.parser = SSEParser()
        self.status = MCPClientStatus(server_url=str(self.config.mcp.server_url))
        self.request_id = 0
        self.available_tools: Dict[str, ToolDefinition] = {}
    
    async def connect(self) -> bool:
        try:
            if not self.status.server_url:
                raise MCPConnectionError("未配置MCP服务器URL")
            
            self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30))
            await self._discover_tools()
            
            self.status.connected = True
            self.status.connection_time = time.time()
            self.status.last_error = None
            logger.info(f"已连接到MCP服务器: {self.status.server_url}")
            return True
            
        except Exception as e:
            error_msg = f"连接MCP服务器失败: {e}"
            logger.error(error_msg)
            self.status.last_error = error_msg
            await self.disconnect()
            return False
    
    async def disconnect(self):
        if self.session:
            await self.session.close()
            self.session = None
        self.status.connected = False
        self.available_tools.clear()
    
    async def _discover_tools(self):
        request = MCPRequest(method="tools/list", id=self._get_request_id())
        response = await self._send_request(request)
        
        if response and response.is_success:
            tools_data = response.result.get("tools", [])
            for tool_data in tools_data:
                tool = ToolDefinition(**tool_data)
                self.available_tools[tool.name] = tool
                self.status.available_tools.append(tool.name)
            logger.info(f"发现 {len(self.available_tools)} 个工具")
    
    async def _send_request(self, request: MCPRequest) -> Optional[MCPResponse]:
        if not self.session:
            raise MCPConnectionError("未连接到MCP服务器")
        
        try:
            headers = {"Content-Type": "application/json", "Accept": "text/event-stream"}
            async with self.session.post(f"{self.status.server_url}/mcp", json=request.model_dump(), headers=headers) as response:
                if response.status != 200:
                    logger.error(f"MCP请求失败: {response.status}")
                    return None
                
                async for line in response.content:
                    line_str = line.decode('utf-8').strip()
                    event = self.parser.parse_line(line_str)
                    if event:
                        mcp_response = self.parser.parse_mcp_response(event)
                        if mcp_response and mcp_response.id == request.id:
                            return mcp_response
                            
        except Exception as e:
            logger.error(f"发送MCP请求失败: {e}")
            return None
    
    def _get_request_id(self) -> str:
        self.request_id += 1
        return str(self.request_id)
    
    def get_tool(self, name: str) -> Optional[ToolDefinition]:
        return self.available_tools.get(name)
    
    def list_tools(self) -> List[str]:
        return list(self.available_tools.keys())
    
    def get_status(self) -> MCPClientStatus:
        return self.status
    
    async def __aenter__(self):
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect() 