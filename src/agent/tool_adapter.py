"""MCP工具适配器

将MCP工具适配为Qwen-Agent框架兼容的Tool接口。
"""

import asyncio
import json
from typing import Dict, Any, Union, List, Optional
import logging

from qwen_agent.tools.base import BaseTool

from ..tools.mcp_client import MCPClient
from ..tools.models import ToolDefinition as MCPTool, ToolCall as ToolCallRequest
from ..config import ConfigManager


logger = logging.getLogger(__name__)


class MCPToolAdapter(BaseTool):
    """MCP工具适配器
    
    将MCP工具包装为Qwen-Agent兼容的BaseTool。
    """
    
    def __init__(
        self, 
        mcp_tool: MCPTool, 
        mcp_client: MCPClient,
        config_manager: ConfigManager
    ):
        """初始化适配器
        
        Args:
            mcp_tool: MCP工具信息
            mcp_client: MCP客户端
            config_manager: 配置管理器
        """
        self.mcp_tool = mcp_tool
        self.mcp_client = mcp_client
        self.config_manager = config_manager
        
        # 构建工具配置
        cfg = {
            'name': mcp_tool.name,
            'description': mcp_tool.description or f"MCP tool: {mcp_tool.name}",
            'parameters': self._convert_parameters(mcp_tool.input_schema)
        }
        
        super().__init__(cfg)
    
    def _convert_parameters(self, input_schema: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """转换MCP输入模式为Qwen-Agent参数格式
        
        Args:
            input_schema: MCP工具的输入模式
            
        Returns:
            Qwen-Agent格式的参数定义
        """
        if not input_schema:
            return {
                "type": "object",
                "properties": {},
                "required": []
            }
        
        # 如果已经是正确格式，直接返回
        if isinstance(input_schema, dict) and "type" in input_schema:
            return input_schema
        
        # 否则包装为object类型
        return {
            "type": "object", 
            "properties": input_schema or {},
            "required": []
        }
    
    @property
    def name(self) -> str:
        """工具名称"""
        return self.mcp_tool.name
    
    @property
    def description(self) -> str:
        """工具描述"""
        return self.mcp_tool.description or f"MCP tool: {self.mcp_tool.name}"
    
    @property
    def parameters(self) -> Dict[str, Any]:
        """工具参数定义"""
        return self._convert_parameters(self.mcp_tool.input_schema)
    
    def call(self, params: Union[str, dict], **kwargs) -> Union[str, dict]:
        """调用工具（Qwen-Agent标准接口）
        
        Args:
            params: 工具参数
            **kwargs: 其他参数
            
        Returns:
            工具执行结果
        """
        try:
            # 运行异步调用方法
            return asyncio.run(self._async_call(params, **kwargs))
        except Exception as e:
            logger.error(f"MCP工具调用失败 [{self.name}]: {e}")
            return {
                "error": f"工具调用失败: {str(e)}",
                "tool_name": self.name
            }
    
    async def _async_call(self, params: Union[str, dict], **kwargs) -> Union[str, dict]:
        """异步工具调用实现
        
        Args:
            params: 工具参数
            **kwargs: 其他参数
            
        Returns:
            工具执行结果
        """
        # 解析参数
        if isinstance(params, str):
            try:
                tool_params = json.loads(params)
            except json.JSONDecodeError:
                # 如果不是JSON，尝试作为简单字符串参数处理
                tool_params = {"input": params}
        elif isinstance(params, dict):
            tool_params = params
        else:
            tool_params = {"input": str(params)}
        
        try:
            # 创建工具调用请求
            request = ToolCallRequest(
                name=self.mcp_tool.name,
                arguments=tool_params
            )
            
            # 执行MCP工具调用 (暂时模拟，实际需要实现)
            # TODO: 实现真正的工具调用
            result = {"content": f"工具 {self.mcp_tool.name} 调用成功", "is_error": False}
            
            # 处理结果
            if result.get("is_error", False):
                return {
                    "error": result.get("content", "工具调用失败"),
                    "tool_name": self.name
                }
            
            # 返回成功结果
            content = result.get("content", "")
            if isinstance(content, (dict, list)):
                return content
            else:
                return {"result": content}
                
        except Exception as e:
            logger.error(f"MCP工具执行异常 [{self.name}]: {e}")
            raise


class MCPToolManager:
    """MCP工具管理器
    
    管理MCP工具的发现、适配和调用。
    """
    
    def __init__(self, config_manager: ConfigManager):
        """初始化工具管理器
        
        Args:
            config_manager: 配置管理器
        """
        self.config_manager = config_manager
        self.mcp_client = MCPClient(config_manager)
        self.tools: Dict[str, MCPToolAdapter] = {}
        self._initialized = False
    
    async def initialize(self) -> None:
        """初始化MCP连接并发现工具"""
        if self._initialized:
            return
        
        try:
            # 连接MCP服务器
            await self.mcp_client.connect()
            
            # 获取可用工具
            tool_names = self.mcp_client.list_tools()
            
            # 创建工具适配器
            for tool_name in tool_names:
                tool_info = self.mcp_client.get_tool(tool_name)
                if not tool_info:
                    continue
                adapter = MCPToolAdapter(
                    mcp_tool=tool_info,
                    mcp_client=self.mcp_client,
                    config_manager=self.config_manager
                )
                self.tools[tool_info.name] = adapter
                logger.info(f"已适配MCP工具: {tool_info.name}")
            
            self._initialized = True
            logger.info(f"MCP工具管理器初始化完成，共适配 {len(self.tools)} 个工具")
            
        except Exception as e:
            logger.error(f"MCP工具管理器初始化失败: {e}")
            raise
    
    def get_tools(self) -> List[MCPToolAdapter]:
        """获取所有可用的工具适配器
        
        Returns:
            工具适配器列表
        """
        return list(self.tools.values())
    
    def get_tool(self, name: str) -> Optional[MCPToolAdapter]:
        """根据名称获取工具适配器
        
        Args:
            name: 工具名称
            
        Returns:
            工具适配器或None
        """
        return self.tools.get(name)
    
    async def close(self) -> None:
        """关闭MCP连接"""
        if self._initialized:
            await self.mcp_client.close()
            self.tools.clear()
            self._initialized = False
            logger.info("MCP工具管理器已关闭") 