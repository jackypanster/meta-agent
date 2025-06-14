"""MCP协议数据模型

定义Model Context Protocol (MCP) JSON-RPC 2.0协议的数据结构。
"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field


class MCPRequest(BaseModel):
    """MCP JSON-RPC请求"""
    
    jsonrpc: str = Field("2.0", description="JSON-RPC版本")
    method: str = Field(..., description="方法名")
    params: Optional[Dict[str, Any]] = Field(None, description="参数")
    id: Union[str, int] = Field(..., description="请求ID")


class MCPError(BaseModel):
    """MCP错误信息"""
    
    code: int = Field(..., description="错误代码")
    message: str = Field(..., description="错误消息")
    data: Optional[Any] = Field(None, description="附加错误数据")


class MCPResponse(BaseModel):
    """MCP JSON-RPC响应"""
    
    jsonrpc: str = Field("2.0", description="JSON-RPC版本")
    id: Union[str, int] = Field(..., description="请求ID")
    result: Optional[Any] = Field(None, description="成功结果")
    error: Optional[MCPError] = Field(None, description="错误信息")
    
    @property
    def is_success(self) -> bool:
        """是否成功响应"""
        return self.error is None


class ToolParameter(BaseModel):
    """工具参数定义"""
    
    type: str = Field(..., description="参数类型")
    description: Optional[str] = Field(None, description="参数描述")
    required: bool = Field(False, description="是否必需")
    default: Optional[Any] = Field(None, description="默认值")


class ToolDefinition(BaseModel):
    """工具定义"""
    
    name: str = Field(..., description="工具名称")
    description: str = Field(..., description="工具描述")
    parameters: Dict[str, ToolParameter] = Field(..., description="参数定义")
    
    def to_schema(self) -> Dict[str, Any]:
        """转换为JSON Schema格式"""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    name: {"type": param.type, "description": param.description}
                    for name, param in self.parameters.items()
                },
                "required": [name for name, param in self.parameters.items() if param.required]
            }
        }


class ToolCall(BaseModel):
    """工具调用"""
    
    name: str = Field(..., description="工具名称")
    arguments: Dict[str, Any] = Field(..., description="调用参数")
    call_id: Optional[str] = Field(None, description="调用ID")


class ToolResult(BaseModel):
    """工具调用结果"""
    
    call_id: Optional[str] = Field(None, description="调用ID")
    result: Optional[Any] = Field(None, description="成功结果")
    error: Optional[str] = Field(None, description="错误信息")
    
    @property
    def is_success(self) -> bool:
        """是否成功"""
        return self.error is None


class SSEEvent(BaseModel):
    """Server-Sent Event事件"""
    
    event: Optional[str] = Field(None, description="事件类型")
    data: Optional[str] = Field(None, description="事件数据")
    id: Optional[str] = Field(None, description="事件ID")
    retry: Optional[int] = Field(None, description="重试间隔")
    
    def parse_data(self) -> Optional[Dict[str, Any]]:
        """解析JSON数据"""
        if self.data:
            try:
                import json
                return json.loads(self.data)
            except json.JSONDecodeError:
                return None
        return None


class MCPClientStatus(BaseModel):
    """MCP客户端状态"""
    
    connected: bool = Field(False, description="是否已连接")
    server_url: str = Field(..., description="服务器URL")
    available_tools: List[str] = Field(default_factory=list, description="可用工具列表")
    last_error: Optional[str] = Field(None, description="最后错误")
    connection_time: Optional[float] = Field(None, description="连接时间戳") 