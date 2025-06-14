"""Agent工厂

提供简洁的Agent创建和配置管理接口。
"""

import asyncio
import logging
from typing import Optional, Dict, Any
from pathlib import Path

from .core_agent import QwenAgentMVP, ConversationSession
from ..config import ConfigManager, ConfigLoader


logger = logging.getLogger(__name__)


class AgentFactory:
    """Agent工厂类
    
    提供简洁的Agent创建接口，管理配置和实例生命周期。
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """初始化工厂
        
        Args:
            config_path: 配置文件路径，None时使用默认配置
        """
        self.config_path = config_path
        self.config_manager: Optional[ConfigManager] = None
        self._agent_instances: Dict[str, QwenAgentMVP] = {}
    
    async def initialize(self) -> None:
        """初始化工厂和配置管理器"""
        try:
            # 加载配置
            if self.config_path:
                config_loader = ConfigLoader(self.config_path)
            else:
                config_loader = ConfigLoader()
            
            self.config_manager = ConfigManager(config_loader)
            await self.config_manager.initialize()
            
            logger.info("Agent工厂初始化完成")
            
        except Exception as e:
            logger.error(f"Agent工厂初始化失败: {e}")
            raise
    
    async def create_agent(
        self, 
        agent_id: Optional[str] = None,
        custom_config: Optional[Dict[str, Any]] = None
    ) -> QwenAgentMVP:
        """创建新的Agent实例
        
        Args:
            agent_id: Agent实例ID，用于管理多个实例
            custom_config: 自定义配置覆盖
            
        Returns:
            Agent实例
        """
        if not self.config_manager:
            await self.initialize()
        
        try:
            # 生成唯一ID
            if not agent_id:
                agent_id = f"agent_{len(self._agent_instances) + 1}"
            
            # 应用自定义配置
            config_manager = self.config_manager
            if custom_config:
                # 创建配置副本并应用覆盖
                config_manager = self._create_config_override(custom_config)
            
            # 创建Agent实例
            agent = QwenAgentMVP(config_manager)
            await agent.initialize()
            
            # 存储实例
            self._agent_instances[agent_id] = agent
            
            logger.info(f"Agent实例 '{agent_id}' 创建成功")
            return agent
            
        except Exception as e:
            logger.error(f"创建Agent实例失败: {e}")
            raise
    
    def get_agent(self, agent_id: str) -> Optional[QwenAgentMVP]:
        """获取Agent实例
        
        Args:
            agent_id: Agent实例ID
            
        Returns:
            Agent实例或None
        """
        return self._agent_instances.get(agent_id)
    
    async def create_session(
        self, 
        session_id: str,
        agent_id: Optional[str] = None
    ) -> ConversationSession:
        """创建对话会话
        
        Args:
            session_id: 会话ID
            agent_id: 使用的Agent实例ID，None时使用默认实例
            
        Returns:
            对话会话实例
        """
        # 获取或创建Agent实例
        if agent_id and agent_id in self._agent_instances:
            agent = self._agent_instances[agent_id]
        else:
            # 创建默认Agent
            if not self._agent_instances:
                agent = await self.create_agent("default")
            else:
                agent = list(self._agent_instances.values())[0]
        
        # 创建会话
        session = ConversationSession(agent, session_id)
        logger.info(f"创建会话 '{session_id}'")
        
        return session
    
    async def close_agent(self, agent_id: str) -> None:
        """关闭特定Agent实例
        
        Args:
            agent_id: Agent实例ID
        """
        if agent_id in self._agent_instances:
            agent = self._agent_instances[agent_id]
            await agent.close()
            del self._agent_instances[agent_id]
            logger.info(f"Agent实例 '{agent_id}' 已关闭")
    
    async def close_all_agents(self) -> None:
        """关闭所有Agent实例"""
        for agent_id in list(self._agent_instances.keys()):
            await self.close_agent(agent_id)
        logger.info("所有Agent实例已关闭")
    
    def list_agents(self) -> Dict[str, Dict[str, Any]]:
        """列出所有Agent实例信息
        
        Returns:
            Agent实例信息字典
        """
        result = {}
        for agent_id, agent in self._agent_instances.items():
            result[agent_id] = {
                "initialized": agent._initialized,
                "config_path": str(self.config_path) if self.config_path else "default"
            }
        return result
    
    def _create_config_override(
        self, 
        custom_config: Dict[str, Any]
    ) -> ConfigManager:
        """创建带有自定义配置覆盖的配置管理器
        
        Args:
            custom_config: 自定义配置
            
        Returns:
            新的配置管理器实例
        """
        # 这里可以实现配置覆盖逻辑
        # 目前返回原配置管理器，后续可扩展
        return self.config_manager


class SimpleAgentFactory:
    """简化的Agent工厂
    
    提供最简单的Agent创建接口，适用于快速原型开发。
    """
    
    @staticmethod
    async def create_default_agent() -> QwenAgentMVP:
        """创建默认配置的Agent
        
        Returns:
            Agent实例
        """
        try:
            # 使用默认配置
            config_loader = ConfigLoader()
            config_manager = ConfigManager(config_loader)
            await config_manager.initialize()
            
            # 创建Agent
            agent = QwenAgentMVP(config_manager)
            await agent.initialize()
            
            logger.info("默认Agent创建成功")
            return agent
            
        except Exception as e:
            logger.error(f"创建默认Agent失败: {e}")
            raise
    
    @staticmethod
    async def create_simple_session(session_id: str) -> ConversationSession:
        """创建简单对话会话
        
        Args:
            session_id: 会话ID
            
        Returns:
            对话会话实例
        """
        agent = await SimpleAgentFactory.create_default_agent()
        return ConversationSession(agent, session_id)


# 便捷函数
async def create_agent(config_path: Optional[str] = None) -> QwenAgentMVP:
    """便捷函数：创建Agent实例
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        Agent实例
    """
    factory = AgentFactory(config_path)
    return await factory.create_agent()


async def create_session(
    session_id: str, 
    config_path: Optional[str] = None
) -> ConversationSession:
    """便捷函数：创建对话会话
    
    Args:
        session_id: 会话ID
        config_path: 配置文件路径
        
    Returns:
        对话会话实例
    """
    factory = AgentFactory(config_path)
    agent = await factory.create_agent()
    return ConversationSession(agent, session_id)


async def quick_chat(message: str, session_id: str = "default") -> str:
    """便捷函数：快速对话
    
    Args:
        message: 用户消息
        session_id: 会话ID
        
    Returns:
        Agent响应
    """
    session = await SimpleAgentFactory.create_simple_session(session_id)
    response = await session.send_message(message)
    await session.agent.close()
    return response 