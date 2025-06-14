"""Tests for memory management functionality."""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime
from typing import Dict, Any, List

from src.memory.models import (
    Memory, MemoryMetadata, SearchQuery, SearchResult,
    MemoryOperation, MemoryType, MemorySource
)
from src.memory.mem0_client import Mem0Client
from src.memory.manager import MemoryManager
from src.memory.service import MemoryService
from src.config import ConfigManager


class TestMemoryModels:
    """Test memory data models."""
    
    def test_memory_type_enum(self):
        """Test MemoryType enum values."""
        assert MemoryType.FACT == "fact"
        assert MemoryType.CONVERSATION == "conversation"
        assert MemoryType.PREFERENCE == "preference"
        assert MemoryType.CONTEXT == "context"
        assert MemoryType.TOOL_RESULT == "tool_result"
        
    def test_memory_source_enum(self):
        """Test MemorySource enum values."""
        assert MemorySource.USER_INPUT == "user_input"
        assert MemorySource.AGENT_RESPONSE == "agent_response"
        assert MemorySource.TOOL_EXECUTION == "tool_execution"
        assert MemorySource.SYSTEM == "system"
        assert MemorySource.EXTERNAL == "external"
        
    def test_memory_metadata_defaults(self):
        """Test MemoryMetadata default values."""
        metadata = MemoryMetadata()
        assert metadata.source == MemorySource.USER_INPUT
        assert metadata.confidence == 1.0
        assert metadata.importance == 5
        assert metadata.tags == []
        assert metadata.custom_fields == {}
        assert isinstance(metadata.timestamp, datetime)
        
    def test_memory_creation(self):
        """Test Memory model creation."""
        metadata = MemoryMetadata(user_id="test_user", session_id="test_session")
        memory = Memory(
            content="Test fact about the user",
            memory_type=MemoryType.FACT,
            metadata=metadata
        )
        assert memory.content == "Test fact about the user"
        assert memory.memory_type == MemoryType.FACT
        assert memory.metadata.user_id == "test_user"
        assert memory.metadata.session_id == "test_session"
        
    def test_search_query_validation(self):
        """Test SearchQuery validation."""
        query = SearchQuery(text="test query", limit=5, threshold=0.8)
        assert query.text == "test query"
        assert query.limit == 5
        assert query.threshold == 0.8
        
    def test_search_result_properties(self):
        """Test SearchResult convenience properties."""
        memories = [
            Memory(content="Test 1", score=0.9),
            Memory(content="Test 2", score=0.8)
        ]
        query = SearchQuery(text="test")
        result = SearchResult(
            memories=memories,
            total_count=2,
            query=query,
            execution_time_ms=100.0
        )
        
        assert result.has_results is True
        # Use approximate comparison for float precision
        assert abs(result.average_score - 0.85) < 0.001
        
        empty_result = SearchResult(
            memories=[], total_count=0, query=query, execution_time_ms=50.0
        )
        assert empty_result.has_results is False
        assert empty_result.average_score == 0.0


class TestMem0Client:
    """Test Mem0Client functionality."""
    
    @pytest.fixture
    def mock_config(self):
        """Mock configuration manager."""
        config = Mock(spec=ConfigManager)
        # Create proper mock structure
        mem0_mock = MagicMock()
        mem0_mock.api_key = "test_api_key"
        config.mem0 = mem0_mock
        return config
        
    @pytest.fixture
    def mem0_client(self, mock_config):
        """Create Mem0Client with mocked config."""
        return Mem0Client(mock_config)
        
    @pytest.mark.asyncio
    async def test_client_connection(self, mem0_client, mock_config):
        """Test client connection setup."""
        with patch('src.memory.mem0_client.Mem0Memory') as mock_mem0:
            mock_instance = Mock()
            mock_mem0.return_value = mock_instance
            
            await mem0_client.connect()
            
            mock_mem0.assert_called_once_with(api_key="test_api_key")
            assert mem0_client._client == mock_instance
            
    @pytest.mark.asyncio
    async def test_add_memory_success(self, mem0_client):
        """Test successful memory addition."""
        mock_client = AsyncMock()
        mem0_client._client = mock_client
        
        # Mock successful API response
        mock_client.add = Mock(return_value={"id": "memory_123"})
        
        with patch('asyncio.to_thread') as mock_to_thread:
            mock_to_thread.return_value = {"id": "memory_123"}
            
            metadata = MemoryMetadata(user_id="test_user")
            result = await mem0_client.add_memory("Test content", metadata, "test_user")
            
            assert result.success is True
            assert result.memory_id == "memory_123"
            assert result.operation == "add_memory"
            
    @pytest.mark.asyncio
    async def test_search_memories_success(self, mem0_client):
        """Test successful memory search."""
        mock_client = AsyncMock()
        mem0_client._client = mock_client
        
        # Mock search results
        mock_results = [
            {"id": "mem1", "content": "Result 1", "score": 0.9},
            {"id": "mem2", "content": "Result 2", "score": 0.8}
        ]
        
        with patch('asyncio.to_thread') as mock_to_thread:
            mock_to_thread.return_value = mock_results
            
            query = SearchQuery(text="test query", limit=10)
            result = await mem0_client.search_memories(query)
            
            assert len(result.memories) == 2
            assert result.total_count == 2
            assert result.memories[0].content == "Result 1"
            assert result.memories[0].score == 0.9


class TestMemoryManager:
    """Test MemoryManager functionality."""
    
    @pytest.fixture
    def mock_mem0_client(self):
        """Mock Mem0Client."""
        client = AsyncMock(spec=Mem0Client)
        client.add_memory = AsyncMock(return_value=MemoryOperation(
            success=True, operation="add_memory", memory_id="test_id"
        ))
        client.search_memories = AsyncMock(return_value=SearchResult(
            memories=[], total_count=0, 
            query=SearchQuery(text="test"), execution_time_ms=100.0
        ))
        return client
        
    @pytest.fixture
    def memory_manager(self, mock_mem0_client):
        """Create MemoryManager with mocked client."""
        manager = MemoryManager()
        manager._client = mock_mem0_client
        return manager
        
    @pytest.mark.asyncio
    async def test_store_fact(self, memory_manager, mock_mem0_client):
        """Test storing a fact."""
        result = await memory_manager.store_fact(
            "User likes coffee", user_id="user123", 
            category="preference", tags=["coffee"], importance=7
        )
        
        assert result.success is True
        mock_mem0_client.add_memory.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_search_memories(self, memory_manager, mock_mem0_client):
        """Test memory search."""
        result = await memory_manager.search_memories(
            "coffee preference", user_id="user123", limit=5
        )
        
        assert isinstance(result, SearchResult)
        mock_mem0_client.search_memories.assert_called_once()


class TestMemoryService:
    """Test MemoryService functionality."""
    
    @pytest.fixture
    def mock_manager(self):
        """Mock MemoryManager."""
        manager = AsyncMock(spec=MemoryManager)
        manager.store_conversation = AsyncMock(return_value=MemoryOperation(
            success=True, operation="store_conversation", memory_id="test_id"
        ))
        manager.search_memories = AsyncMock(return_value=SearchResult(
            memories=[Memory(content="Test memory")], total_count=1,
            query=SearchQuery(text="test"), execution_time_ms=100.0
        ))
        return manager
        
    @pytest.fixture
    def memory_service(self, mock_manager):
        """Create MemoryService with mocked manager."""
        service = MemoryService()
        service._manager = mock_manager
        return service
        
    def test_session_management(self, memory_service):
        """Test session start and end."""
        session_id = memory_service.start_session("user123")
        
        assert memory_service.is_session_active is True
        assert memory_service.current_session_info["user_id"] == "user123"
        assert memory_service.current_session_info["session_id"] == session_id
        
        memory_service.end_session()
        assert memory_service.is_session_active is False
        assert memory_service.current_session_info is None
        
    @pytest.mark.asyncio
    async def test_store_user_message(self, memory_service, mock_manager):
        """Test storing user message."""
        memory_service.start_session("user123")
        
        result = await memory_service.store_user_message("Hello there!")
        
        assert result.success is True
        mock_manager.store_conversation.assert_called_once()
        call_args = mock_manager.store_conversation.call_args[0]
        assert "User: Hello there!" in call_args[0]


if __name__ == "__main__":
    pytest.main([__file__]) 