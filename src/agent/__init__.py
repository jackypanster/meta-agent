"""Agent模块

提供Qwen-Agent集成，包括LLM适配器、工具适配器、核心Agent和工厂类。
"""

from .llm_adapter import DeepSeekLLMAdapter
from .tool_adapter import MCPToolAdapter, MCPToolManager
from .core_agent import QwenAgentMVP, ConversationSession
from .factory import (
    AgentFactory, 
    SimpleAgentFactory, 
    create_agent, 
    create_session, 
    quick_chat
)

# 主要类导出
__all__ = [
    # 适配器
    "DeepSeekLLMAdapter",
    "MCPToolAdapter", 
    "MCPToolManager",
    
    # 核心Agent
    "QwenAgentMVP",
    "ConversationSession",
    
    # 工厂类
    "AgentFactory",
    "SimpleAgentFactory",
    
    # 便捷函数
    "create_agent",
    "create_session", 
    "quick_chat"
]
