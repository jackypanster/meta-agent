"""Agent集成测试

测试Qwen-Agent核心集成功能，包括LLM、工具和内存的协同工作。
"""

import pytest
import asyncio
import os
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any, List

from src.agent import (
    QwenAgentMVP, 
    ConversationSession,
    AgentFactory,
    SimpleAgentFactory,
    create_agent,
    create_session,
    quick_chat
)
from src.config import ConfigManager, ConfigLoader


class TestAgentIntegration:
    """Agent集成测试类"""
    
    @pytest.fixture
    def mock_config_manager(self):
        """模拟配置管理器"""
        config_manager = MagicMock(spec=ConfigManager)
        config_manager.deepseek = MagicMock()
        config_manager.deepseek.api_key = "test-key"
        config_manager.deepseek.model = "deepseek-reasoner"
        config_manager.deepseek.base_url = "https://api.deepseek.com"
        config_manager.mcp = MagicMock()
        config_manager.mcp.server_url = "https://mcp.context7.com/sse"
        config_manager.mem0 = MagicMock()
        config_manager.mem0.api_key = "test-mem0-key"
        
        async def mock_initialize():
            pass
        config_manager.initialize = AsyncMock(side_effect=mock_initialize)
        
        return config_manager
    
    @pytest.fixture
    def mock_agent_components(self):
        """模拟Agent组件"""
        # 模拟LLM适配器
        mock_llm = AsyncMock()
        mock_llm.chat.return_value = [{"role": "assistant", "content": "测试响应"}]
        
        # 模拟工具管理器
        mock_tool_manager = AsyncMock()
        mock_tool_manager.get_tools = MagicMock(return_value=[])
        mock_tool_manager.initialize = AsyncMock()
        mock_tool_manager.close = AsyncMock()
        
        # 模拟内存管理器
        mock_memory = AsyncMock()
        mock_memory.initialize = AsyncMock()
        mock_memory.search_memories = AsyncMock(return_value=[])
        mock_memory.add_memory = AsyncMock()
        mock_memory.close = AsyncMock()
        
        # 模拟Qwen-Agent
        mock_qwen_agent = MagicMock()
        mock_qwen_agent.run.return_value = [{"role": "assistant", "content": "Agent响应"}]
        
        return {
            "llm": mock_llm,
            "tool_manager": mock_tool_manager, 
            "memory": mock_memory,
            "qwen_agent": mock_qwen_agent
        }
    
    @patch('src.agent.core_agent.Agent')
    @patch('src.agent.core_agent.MCPToolManager')
    @patch('src.agent.core_agent.MemoryManager')
    @patch('src.agent.core_agent.DeepSeekLLMAdapter')
    async def test_agent_initialization(
        self, 
        mock_llm_adapter, 
        mock_memory_manager, 
        mock_tool_manager,
        mock_agent_class,
        mock_config_manager,
        mock_agent_components
    ):
        """测试Agent初始化"""
        # 设置模拟
        mock_llm_adapter.return_value = mock_agent_components["llm"]
        mock_memory_manager.return_value = mock_agent_components["memory"]
        mock_tool_manager.return_value = mock_agent_components["tool_manager"]
        mock_agent_class.return_value = mock_agent_components["qwen_agent"]
        
        # 创建Agent
        agent = QwenAgentMVP(mock_config_manager)
        await agent.initialize()
        
        # 验证初始化
        assert agent._initialized
        mock_agent_components["memory"].initialize.assert_called_once()
        mock_agent_components["tool_manager"].initialize.assert_called_once()
        mock_agent_class.assert_called_once()
    
    @patch('src.agent.core_agent.Agent')
    @patch('src.agent.core_agent.MCPToolManager')
    @patch('src.agent.core_agent.MemoryManager')
    @patch('src.agent.core_agent.DeepSeekLLMAdapter')
    async def test_message_processing_flow(
        self,
        mock_llm_adapter,
        mock_memory_manager,
        mock_tool_manager,
        mock_agent_class,
        mock_config_manager,
        mock_agent_components
    ):
        """测试消息处理流程"""
        # 设置模拟
        mock_llm_adapter.return_value = mock_agent_components["llm"]
        mock_memory_manager.return_value = mock_agent_components["memory"]
        mock_tool_manager.return_value = mock_agent_components["tool_manager"]
        mock_agent_class.return_value = mock_agent_components["qwen_agent"]
        
        # 模拟记忆搜索结果
        mock_agent_components["memory"].search_memories.return_value = [
            {"text": "历史对话1"},
            {"text": "历史对话2"}
        ]
        
        # 创建Agent并处理消息
        agent = QwenAgentMVP(mock_config_manager)
        await agent.initialize()
        
        response = await agent.process_message("测试消息", "session_1")
        
        # 验证流程
        assert response == "Agent响应"
        mock_agent_components["memory"].search_memories.assert_called_once()
        mock_agent_components["memory"].add_memory.assert_called_once()
        mock_agent_components["qwen_agent"].run.assert_called_once()
        
        # 验证对话历史
        assert len(agent.conversation_history) == 2
        assert agent.conversation_history[0]["role"] == "user"
        assert agent.conversation_history[1]["role"] == "assistant"
    
    @patch('src.agent.core_agent.Agent')
    @patch('src.agent.core_agent.MCPToolManager')
    @patch('src.agent.core_agent.MemoryManager') 
    @patch('src.agent.core_agent.DeepSeekLLMAdapter')
    async def test_tool_integration(
        self,
        mock_llm_adapter,
        mock_memory_manager,
        mock_tool_manager,
        mock_agent_class,
        mock_config_manager,
        mock_agent_components
    ):
        """测试工具集成"""
        # 设置模拟工具
        mock_tool = MagicMock()
        mock_tool.name = "test_tool"
        mock_tool.description = "测试工具"
        mock_agent_components["tool_manager"].get_tools.return_value = [mock_tool]
        
        # 设置模拟
        mock_llm_adapter.return_value = mock_agent_components["llm"]
        mock_memory_manager.return_value = mock_agent_components["memory"]
        mock_tool_manager.return_value = mock_agent_components["tool_manager"]
        mock_agent_class.return_value = mock_agent_components["qwen_agent"]
        
        # 创建Agent
        agent = QwenAgentMVP(mock_config_manager)
        await agent.initialize()
        
        # 验证工具发现
        tools = await agent.get_available_tools()
        assert "test_tool" in tools
    
    @patch('src.agent.core_agent.Agent')
    @patch('src.agent.core_agent.MCPToolManager')
    @patch('src.agent.core_agent.MemoryManager')
    @patch('src.agent.core_agent.DeepSeekLLMAdapter')
    async def test_memory_integration(
        self,
        mock_llm_adapter,
        mock_memory_manager,
        mock_tool_manager,
        mock_agent_class,
        mock_config_manager,
        mock_agent_components
    ):
        """测试内存集成"""
        # 设置模拟
        mock_llm_adapter.return_value = mock_agent_components["llm"]
        mock_memory_manager.return_value = mock_agent_components["memory"]
        mock_tool_manager.return_value = mock_agent_components["tool_manager"]
        mock_agent_class.return_value = mock_agent_components["qwen_agent"]
        
        # 模拟记忆
        test_memories = [
            {"text": "用户喜欢Python编程", "metadata": {"type": "preference"}},
            {"text": "之前讨论过机器学习", "metadata": {"type": "topic"}}
        ]
        mock_agent_components["memory"].search_memories.return_value = test_memories
        
        # 创建Agent并处理消息
        agent = QwenAgentMVP(mock_config_manager)
        await agent.initialize()
        
        response = await agent.process_message("继续讨论编程", "session_1")
        
        # 验证记忆搜索和存储
        mock_agent_components["memory"].search_memories.assert_called_once()
        mock_agent_components["memory"].add_memory.assert_called_once()
        
        # 验证消息上下文包含记忆
        call_args = mock_agent_components["qwen_agent"].run.call_args[1]["messages"]
        assert len(call_args) == 2  # 系统消息(包含记忆) + 用户消息
        assert "相关历史信息" in call_args[0]["content"]
    
    @patch('src.agent.core_agent.Agent')
    @patch('src.agent.core_agent.MCPToolManager')
    @patch('src.agent.core_agent.MemoryManager')
    @patch('src.agent.core_agent.DeepSeekLLMAdapter')
    async def test_multi_turn_conversation(
        self,
        mock_llm_adapter,
        mock_memory_manager, 
        mock_tool_manager,
        mock_agent_class,
        mock_config_manager,
        mock_agent_components
    ):
        """测试多轮对话"""
        # 设置模拟
        mock_llm_adapter.return_value = mock_agent_components["llm"]
        mock_memory_manager.return_value = mock_agent_components["memory"]
        mock_tool_manager.return_value = mock_agent_components["tool_manager"]
        mock_agent_class.return_value = mock_agent_components["qwen_agent"]
        
        # 创建Agent
        agent = QwenAgentMVP(mock_config_manager)
        await agent.initialize()
        
        # 多轮对话
        responses = []
        for i, message in enumerate(["第一条消息", "第二条消息", "第三条消息"]):
            mock_agent_components["qwen_agent"].run.return_value = [
                {"role": "assistant", "content": f"响应{i+1}"}
            ]
            response = await agent.process_message(message, "session_1")
            responses.append(response)
        
        # 验证对话历史
        assert len(agent.conversation_history) == 6  # 3轮 * 2消息/轮
        assert len(responses) == 3
        assert all(f"响应{i+1}" in responses[i] for i in range(3))
    
    async def test_conversation_session(self, mock_config_manager):
        """测试对话会话功能"""
        with patch('src.agent.core_agent.QwenAgentMVP') as mock_agent_class:
            # 设置模拟Agent
            mock_agent = AsyncMock()
            mock_agent.process_message = AsyncMock(return_value="会话响应")
            mock_agent_class.return_value = mock_agent
            
            # 创建会话
            session = ConversationSession(mock_agent, "test_session")
            
            # 发送消息
            response = await session.send_message("测试消息")
            
            # 验证
            assert response == "会话响应"
            assert len(session.history) == 2
            mock_agent.process_message.assert_called_once_with("测试消息", "test_session")


class TestAgentFactory:
    """Agent工厂测试类"""
    
    @pytest.fixture
    async def mock_components(self):
        """模拟组件"""
        with patch('src.agent.factory.ConfigLoader') as mock_loader, \
             patch('src.agent.factory.ConfigManager') as mock_manager, \
             patch('src.agent.factory.QwenAgentMVP') as mock_agent:
            
            # 模拟配置
            mock_config_manager = AsyncMock()
            mock_config_manager.initialize = AsyncMock()
            mock_manager.return_value = mock_config_manager
            
            # 模拟Agent
            mock_agent_instance = AsyncMock()
            mock_agent_instance.initialize = AsyncMock()
            mock_agent_instance._initialized = True
            mock_agent.return_value = mock_agent_instance
            
            yield {
                "config_manager": mock_config_manager,
                "agent": mock_agent_instance,
                "agent_class": mock_agent,
                "manager_class": mock_manager
            }
    
    async def test_factory_initialization(self, mock_components):
        """测试工厂初始化"""
        factory = AgentFactory()
        await factory.initialize()
        
        assert factory.config_manager is not None
        mock_components["config_manager"].initialize.assert_called_once()
    
    async def test_create_agent(self, mock_components):
        """测试创建Agent"""
        factory = AgentFactory()
        agent = await factory.create_agent("test_agent")
        
        assert agent is not None
        assert "test_agent" in factory._agent_instances
        mock_components["agent"].initialize.assert_called_once()
    
    async def test_create_session(self, mock_components):
        """测试创建会话"""
        factory = AgentFactory()
        session = await factory.create_session("test_session")
        
        assert session is not None
        assert session.session_id == "test_session"
        assert session.agent is not None
    
    async def test_agent_lifecycle(self, mock_components):
        """测试Agent生命周期管理"""
        factory = AgentFactory()
        
        # 创建多个Agent
        agent1 = await factory.create_agent("agent1")
        agent2 = await factory.create_agent("agent2")
        
        # 验证列表
        agents = factory.list_agents()
        assert len(agents) == 2
        assert "agent1" in agents
        assert "agent2" in agents
        
        # 关闭单个Agent
        await factory.close_agent("agent1")
        agents = factory.list_agents()
        assert len(agents) == 1
        assert "agent1" not in agents
        
        # 关闭所有Agent
        await factory.close_all_agents()
        agents = factory.list_agents()
        assert len(agents) == 0


class TestConvenienceFunctions:
    """便捷函数测试类"""
    
    @patch('src.agent.factory.AgentFactory')
    async def test_create_agent_function(self, mock_factory_class):
        """测试create_agent便捷函数"""
        # 设置模拟
        mock_factory = AsyncMock()
        mock_agent = AsyncMock()
        mock_factory.create_agent = AsyncMock(return_value=mock_agent)
        mock_factory_class.return_value = mock_factory
        
        # 调用函数
        agent = await create_agent()
        
        # 验证
        assert agent is mock_agent
        mock_factory.create_agent.assert_called_once()
    
    @patch('src.agent.factory.AgentFactory')
    async def test_create_session_function(self, mock_factory_class):
        """测试create_session便捷函数"""
        # 设置模拟
        mock_factory = AsyncMock()
        mock_agent = AsyncMock()
        mock_session = MagicMock()
        mock_session.agent = mock_agent
        
        mock_factory.create_agent = AsyncMock(return_value=mock_agent)
        mock_factory_class.return_value = mock_factory
        
        # 调用函数
        with patch('src.agent.factory.ConversationSession', return_value=mock_session):
            session = await create_session("test_session")
        
        # 验证
        assert session is mock_session
        mock_factory.create_agent.assert_called_once()
    
    @patch('src.agent.factory.SimpleAgentFactory')
    async def test_quick_chat_function(self, mock_simple_factory):
        """测试quick_chat便捷函数"""
        # 设置模拟
        mock_session = AsyncMock()
        mock_session.send_message = AsyncMock(return_value="快速响应")
        mock_session.agent = AsyncMock()
        mock_session.agent.close = AsyncMock()
        
        mock_simple_factory.create_simple_session = AsyncMock(return_value=mock_session)
        
        # 调用函数
        response = await quick_chat("测试消息")
        
        # 验证
        assert response == "快速响应"
        mock_session.send_message.assert_called_once_with("测试消息")
        mock_session.agent.close.assert_called_once()


class TestErrorHandling:
    """错误处理测试类"""
    
    @patch('src.agent.core_agent.Agent')
    @patch('src.agent.core_agent.MCPToolManager')
    @patch('src.agent.core_agent.MemoryManager')
    @patch('src.agent.core_agent.DeepSeekLLMAdapter')
    async def test_initialization_error_handling(
        self,
        mock_llm_adapter,
        mock_memory_manager,
        mock_tool_manager,
        mock_agent_class,
        mock_config_manager
    ):
        """测试初始化错误处理"""
        # 模拟初始化失败
        mock_memory_manager.return_value.initialize = AsyncMock(
            side_effect=Exception("内存初始化失败")
        )
        
        agent = QwenAgentMVP(mock_config_manager)
        
        with pytest.raises(Exception, match="内存初始化失败"):
            await agent.initialize()
        
        assert not agent._initialized
    
    @patch('src.agent.core_agent.Agent')
    @patch('src.agent.core_agent.MCPToolManager')
    @patch('src.agent.core_agent.MemoryManager')
    @patch('src.agent.core_agent.DeepSeekLLMAdapter')
    async def test_message_processing_error_handling(
        self,
        mock_llm_adapter,
        mock_memory_manager,
        mock_tool_manager,
        mock_agent_class,
        mock_config_manager
    ):
        """测试消息处理错误处理"""
        # 设置正常模拟
        mock_llm = AsyncMock()
        mock_memory = AsyncMock()
        mock_tool_mgr = AsyncMock()
        mock_qwen_agent = MagicMock()
        
        mock_llm_adapter.return_value = mock_llm
        mock_memory_manager.return_value = mock_memory
        mock_tool_manager.return_value = mock_tool_mgr
        mock_agent_class.return_value = mock_qwen_agent
        
        # 模拟Agent调用失败
        mock_qwen_agent.run.side_effect = Exception("Agent调用失败")
        
        agent = QwenAgentMVP(mock_config_manager)
        await agent.initialize()
        
        response = await agent.process_message("测试消息")
        
        # 验证错误处理
        assert "处理您的消息时发生错误" in response
        assert "Agent调用失败" in response


# 运行所有测试的标记
pytestmark = pytest.mark.asyncio 