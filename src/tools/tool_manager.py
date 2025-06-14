"""工具调用管理器

管理MCP工具的调用、结果处理和错误重试。
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any
from .models import MCPRequest, MCPResponse, ToolCall, ToolResult, ToolDefinition
from .mcp_client import MCPClient

logger = logging.getLogger(__name__)


class ToolExecutionError(Exception):
    """工具执行错误"""
    pass


class ToolManager:
    """工具调用管理器"""
    
    def __init__(self, mcp_client: MCPClient, max_retries: int = 3, timeout: int = 30):
        self.client = mcp_client
        self.max_retries = max_retries
        self.timeout = timeout
        self.execution_history: List[Dict[str, Any]] = []
    
    async def execute_tool(self, tool_call: ToolCall) -> ToolResult:
        start_time = time.time()
        
        try:
            # 验证工具存在
            tool_def = self.client.get_tool(tool_call.name)
            if not tool_def:
                raise ToolExecutionError(f"工具不存在: {tool_call.name}")
            
            # 验证参数
            self._validate_arguments(tool_def, tool_call.arguments)
            
            # 执行工具
            result = await self._execute_with_retry(tool_call)
            self._record_execution(tool_call, result, time.time() - start_time)
            return result
            
        except Exception as e:
            error_result = ToolResult(call_id=tool_call.call_id, error=str(e))
            self._record_execution(tool_call, error_result, time.time() - start_time)
            return error_result
    
    async def execute_tools_batch(self, tool_calls: List[ToolCall]) -> List[ToolResult]:
        tasks = [asyncio.create_task(self.execute_tool(call)) for call in tool_calls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理异常结果
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append(ToolResult(call_id=tool_calls[i].call_id, error=str(result)))
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def _execute_with_retry(self, tool_call: ToolCall) -> ToolResult:
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                response = await asyncio.wait_for(
                    self._send_tool_request(tool_call),
                    timeout=self.timeout
                )
                
                if response and response.is_success:
                    return ToolResult(call_id=tool_call.call_id, result=response.result)
                else:
                    error_msg = response.error.message if response and response.error else "未知错误"
                    last_error = ToolExecutionError(f"工具执行失败: {error_msg}")
                    
            except asyncio.TimeoutError:
                last_error = ToolExecutionError(f"工具执行超时 (>{self.timeout}s)")
            except Exception as e:
                last_error = ToolExecutionError(f"工具执行异常: {e}")
            
            if attempt < self.max_retries - 1:
                await asyncio.sleep(2 ** attempt)
        
        raise last_error or ToolExecutionError("工具执行失败")
    
    async def _send_tool_request(self, tool_call: ToolCall) -> Optional[MCPResponse]:
        request = MCPRequest(
            method="tools/call",
            params={"name": tool_call.name, "arguments": tool_call.arguments},
            id=self.client._get_request_id()
        )
        return await self.client._send_request(request)
    
    def _validate_arguments(self, tool_def: ToolDefinition, arguments: Dict[str, Any]):
        for param_name, param in tool_def.parameters.items():
            if param.required and param_name not in arguments:
                raise ToolExecutionError(f"缺少必需参数: {param_name}")
    
    def _record_execution(self, tool_call: ToolCall, result: ToolResult, duration: float):
        self.execution_history.append({"tool_name": tool_call.name, "call_id": tool_call.call_id, 
                                       "success": result.is_success, "duration": duration, "timestamp": time.time()})
        if len(self.execution_history) > 1000:
            self.execution_history = self.execution_history[-500:]
    
    def get_execution_stats(self) -> Dict[str, Any]:
        if not self.execution_history:
            return {}
        total_calls = len(self.execution_history)
        successful_calls = sum(1 for call in self.execution_history if call["success"])
        
        return {"total_calls": total_calls, "successful_calls": successful_calls, 
                "success_rate": successful_calls / total_calls if total_calls > 0 else 0,
                "average_duration": sum(call["duration"] for call in self.execution_history) / total_calls} 