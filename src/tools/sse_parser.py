"""SSE事件解析器

实现Server-Sent Events协议的事件解析和处理。
"""

import json
import logging
from typing import AsyncGenerator, Optional, Dict, Any
from .models import SSEEvent, MCPResponse

logger = logging.getLogger(__name__)


class SSEParseError(Exception):
    """SSE解析错误"""
    pass


class SSEParser:
    """Server-Sent Events解析器"""
    
    def __init__(self):
        """初始化解析器"""
        self.current_event = SSEEvent()
        self.buffer = ""
    
    def parse_line(self, line: str) -> Optional[SSEEvent]:
        """解析单行SSE数据"""
        line = line.strip()
        
        # 空行表示事件结束
        if not line:
            if self._has_data():
                event = self.current_event
                self.current_event = SSEEvent()
                return event
            return None
        
        # 注释行跳过
        if line.startswith(':'):
            return None
        
        # 解析字段
        if ':' in line:
            field, value = line.split(':', 1)
            value = value.lstrip()
        else:
            field, value = line, ""
        
        # 处理不同字段
        if field == "data":
            self.current_event.data = value if self.current_event.data is None else self.current_event.data + "\n" + value
        elif field == "event":
            self.current_event.event = value
        elif field == "id":
            self.current_event.id = value
        elif field == "retry":
            try:
                self.current_event.retry = int(value)
            except ValueError:
                logger.warning(f"无效的retry值: {value}")
        
        return None
    
    def _has_data(self) -> bool:
        """检查当前事件是否有数据"""
        return (self.current_event.data is not None or 
                self.current_event.event is not None or
                self.current_event.id is not None)
    
    async def parse_stream(self, stream: AsyncGenerator[str, None]) -> AsyncGenerator[SSEEvent, None]:
        """解析SSE事件流"""
        async for chunk in stream:
            lines = chunk.split('\n')
            
            # 处理缓冲区
            if self.buffer:
                lines[0] = self.buffer + lines[0]
                self.buffer = ""
            
            # 最后一行可能不完整，保存到缓冲区
            if lines and not chunk.endswith('\n'):
                self.buffer = lines[-1]
                lines = lines[:-1]
            
            # 解析每一行
            for line in lines:
                event = self.parse_line(line)
                if event:
                    yield event
        
        # 处理流结束时的剩余事件
        if self._has_data():
            yield self.current_event
    
    def parse_mcp_response(self, event: SSEEvent) -> Optional[MCPResponse]:
        """从SSE事件解析MCP响应"""
        data = event.parse_data()
        if not data:
            return None
        
        try:
            return MCPResponse(**data)
        except Exception as e:
            logger.error(f"MCP响应解析失败: {e}")
            return None
    
    @staticmethod
    def create_sse_data(data: Dict[str, Any], event_type: Optional[str] = None) -> str:
        """创建SSE数据格式"""
        lines = []
        if event_type:
            lines.append(f"event: {event_type}")
        lines.append(f"data: {json.dumps(data, ensure_ascii=False)}")
        lines.append("")  # 空行结束事件
        return "\n".join(lines)
    
    def reset(self):
        """重置解析器状态"""
        self.current_event = SSEEvent()
        self.buffer = "" 