"""Qwen-Agent核心集成

集成DeepSeek LLM、MCP工具和mem0内存的完整对话代理。
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional, Union
import json

from qwen_agent import Agent

from .llm_adapter import DeepSeekLLMAdapter
from .tool_adapter import MCPToolManager
from ..memory.manager import MemoryManager
from ..config import ConfigManager


logger = logging.getLogger(__name__)


class QwenAgentMVP:
    """Qwen-Agent MVP核心类
    
    集成LLM、工具和内存的完整对话代理。
    """
    
    def __init__(self, config_manager: ConfigManager):
        """初始化Agent
        
        Args:
            config_manager: 配置管理器实例
        """
        self.config_manager = config_manager
        
        # 初始化组件
        self.llm_adapter = DeepSeekLLMAdapter(config_manager)
        self.tool_manager = MCPToolManager(config_manager)
        self.memory_manager = MemoryManager(config_manager)
        
        # Qwen-Agent实例
        self.agent: Optional[Agent] = None
        self._initialized = False
        
        # 对话历史
        self.conversation_history: List[Dict[str, Any]] = []
    
    async def initialize(self) -> None:
        """初始化所有组件和Agent"""
        if self._initialized:
            return
        
        try:
            logger.info("开始初始化Qwen-Agent MVP...")
            
            # 初始化内存管理器
            await self.memory_manager.initialize()
            logger.info("内存管理器初始化完成")
            
            # 初始化工具管理器
            await self.tool_manager.initialize()
            logger.info(f"工具管理器初始化完成，发现 {len(self.tool_manager.get_tools())} 个工具")
            
            # 构建系统消息
            system_message = self._build_system_message()
            
            # 初始化Qwen-Agent
            self.agent = Agent(
                function_list=self.tool_manager.get_tools(),
                llm=self.llm_adapter,
                system_message=system_message,
                name="QwenAgentMVP",
                description="一个集成了DeepSeek LLM、MCP工具和mem0内存的智能助手"
            )
            
            self._initialized = True
            logger.info("Qwen-Agent MVP初始化完成")
            
        except Exception as e:
            logger.error(f"初始化失败: {e}")
            raise
    
    def _build_system_message(self) -> str:
        """构建系统消息"""
        available_tools = [tool.name for tool in self.tool_manager.get_tools()]
        
        system_message = f"""你是一个智能助手，具有以下能力：

1. 使用DeepSeek LLM进行对话
2. 调用多种工具完成任务：{', '.join(available_tools) if available_tools else '暂无可用工具'}
3. 记忆和检索对话历史中的重要信息

请根据用户的需求，合理使用这些能力为用户提供帮助。在需要时主动调用工具，并利用记忆功能提供更个性化的服务。
"""
        return system_message
    
    async def process_message(
        self, 
        user_input: str, 
        session_id: Optional[str] = None
    ) -> str:
        """处理用户消息
        
        Args:
            user_input: 用户输入
            session_id: 会话ID，用于区分不同对话
            
        Returns:
            Agent响应
        """
        if not self._initialized:
            await self.initialize()
        
        try:
            logger.info(f"处理用户消息: {user_input[:100]}...")
            
            # 搜索相关记忆
            relevant_memories = await self._search_relevant_memories(
                user_input, session_id
            )
            
            # 构建消息上下文
            messages = self._build_message_context(user_input, relevant_memories)
            
            # 调用Agent处理
            response = await self._call_agent(messages)
            
            # 存储对话到记忆
            await self._store_conversation_memory(
                user_input, response, session_id
            )
            
            # 更新对话历史
            self.conversation_history.extend([
                {"role": "user", "content": user_input},
                {"role": "assistant", "content": response}
            ])
            
            logger.info(f"生成响应: {response[:100]}...")
            return response
            
        except Exception as e:
            logger.error(f"处理消息失败: {e}")
            return f"抱歉，处理您的消息时发生错误：{str(e)}"
    
    async def _search_relevant_memories(
        self, 
        user_input: str, 
        session_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """搜索相关记忆
        
        Args:
            user_input: 用户输入
            session_id: 会话ID
            
        Returns:
            相关记忆列表
        """
        try:
            # 构建搜索查询
            search_query = user_input
            if session_id:
                search_query = f"[{session_id}] {user_input}"
            
            # 搜索记忆
            memories = await self.memory_manager.search_memories(
                query=search_query,
                limit=5
            )
            
            logger.debug(f"找到 {len(memories)} 条相关记忆")
            return memories
            
        except Exception as e:
            logger.warning(f"搜索记忆失败: {e}")
            return []
    
    def _build_message_context(
        self,
        user_input: str,
        relevant_memories: List[Dict[str, Any]]
    ) -> List[Dict[str, str]]:
        """构建消息上下文
        
        Args:
            user_input: 用户输入
            relevant_memories: 相关记忆
            
        Returns:
            格式化的消息列表
        """
        messages = []
        
        # 添加记忆上下文
        if relevant_memories:
            memory_context = "相关历史信息：\n"
            for i, memory in enumerate(relevant_memories, 1):
                memory_text = memory.get('text', memory.get('memory', ''))
                memory_context += f"{i}. {memory_text}\n"
            
            messages.append({
                "role": "system",
                "content": memory_context
            })
        
        # 添加用户消息
        messages.append({
            "role": "user", 
            "content": user_input
        })
        
        return messages
    
    async def _call_agent(self, messages: List[Dict[str, str]]) -> str:
        """调用Agent处理消息
        
        Args:
            messages: 消息列表
            
        Returns:
            Agent响应
        """
        try:
            # 调用Agent
            response = self.agent.run(messages=messages)
            
            # 提取响应内容
            if response and isinstance(response, list) and len(response) > 0:
                last_message = response[-1]
                if isinstance(last_message, dict):
                    return last_message.get('content', '抱歉，我无法生成响应。')
                else:
                    return str(last_message)
            
            return "抱歉，我无法生成响应。"
            
        except Exception as e:
            logger.error(f"Agent调用失败: {e}")
            raise
    
    async def _store_conversation_memory(
        self,
        user_input: str,
        agent_response: str,
        session_id: Optional[str] = None
    ) -> None:
        """存储对话到记忆
        
        Args:
            user_input: 用户输入
            agent_response: Agent响应
            session_id: 会话ID
        """
        try:
            # 构建对话记录
            conversation_text = f"用户: {user_input}\n助手: {agent_response}"
            
            # 添加会话ID前缀
            if session_id:
                conversation_text = f"[{session_id}] {conversation_text}"
            
            # 存储到记忆
            await self.memory_manager.add_memory(
                text=conversation_text,
                metadata={
                    "type": "conversation",
                    "session_id": session_id,
                    "user_input": user_input,
                    "agent_response": agent_response
                }
            )
            
            logger.debug("对话已存储到记忆")
            
        except Exception as e:
            logger.warning(f"存储对话记忆失败: {e}")
    
    async def get_conversation_history(self) -> List[Dict[str, Any]]:
        """获取对话历史
        
        Returns:
            对话历史列表
        """
        return self.conversation_history.copy()
    
    async def clear_conversation_history(self) -> None:
        """清空对话历史"""
        self.conversation_history.clear()
        logger.info("对话历史已清空")
    
    async def get_available_tools(self) -> List[str]:
        """获取可用工具列表
        
        Returns:
            工具名称列表
        """
        if not self._initialized:
            await self.initialize()
        
        return [tool.name for tool in self.tool_manager.get_tools()]
    
    async def close(self) -> None:
        """关闭Agent和所有连接"""
        try:
            if hasattr(self.llm_adapter, 'close'):
                await self.llm_adapter.close()
            
            if hasattr(self.tool_manager, 'close'):
                await self.tool_manager.close()
            
            if hasattr(self.memory_manager, 'close'):
                await self.memory_manager.close()
            
            self._initialized = False
            logger.info("Qwen-Agent MVP已关闭")
            
        except Exception as e:
            logger.error(f"关闭Agent失败: {e}")


class ConversationSession:
    """对话会话管理器"""
    
    def __init__(self, agent: QwenAgentMVP, session_id: str):
        """初始化会话
        
        Args:
            agent: Agent实例
            session_id: 会话ID
        """
        self.agent = agent
        self.session_id = session_id
        self.history: List[Dict[str, str]] = []
    
    async def send_message(self, message: str) -> str:
        """发送消息
        
        Args:
            message: 用户消息
            
        Returns:
            Agent响应
        """
        response = await self.agent.process_message(message, self.session_id)
        
        # 更新会话历史
        self.history.extend([
            {"role": "user", "content": message},
            {"role": "assistant", "content": response}
        ])
        
        return response
    
    def get_history(self) -> List[Dict[str, str]]:
        """获取会话历史"""
        return self.history.copy()
    
    def clear_history(self) -> None:
        """清空会话历史"""
        self.history.clear() 