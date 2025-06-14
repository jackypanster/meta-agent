"""Core memory management functionality."""

import logging
from typing import List, Optional, Dict, Any
from src.config import ConfigManager
from .mem0_client import Mem0Client
from .models import (
    Memory, MemoryMetadata, SearchQuery, SearchResult,
    MemoryOperation, MemoryType, MemorySource
)

logger = logging.getLogger(__name__)


class MemoryManager:
    """High-level memory management interface."""
    
    def __init__(self, config_manager: Optional[ConfigManager] = None,
                 mem0_client: Optional[Mem0Client] = None):
        self._config = config_manager or ConfigManager()
        self._client = mem0_client or Mem0Client(self._config)
        self._session_context: Dict[str, Any] = {}
        
    async def __aenter__(self):
        await self._client.connect()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._client.disconnect()
        
    async def store_fact(self, content: str, user_id: Optional[str] = None,
                        session_id: Optional[str] = None, 
                        category: Optional[str] = None,
                        tags: List[str] = None,
                        importance: int = 5) -> MemoryOperation:
        metadata = MemoryMetadata(
            user_id=user_id, session_id=session_id, 
            source=MemorySource.USER_INPUT, category=category,
            tags=tags or [], importance=importance
        )
        return await self._client.add_memory(content, metadata, user_id)
        
    async def store_conversation(self, content: str, user_id: Optional[str] = None,
                               session_id: Optional[str] = None,
                               source: MemorySource = MemorySource.USER_INPUT) -> MemoryOperation:
        metadata = MemoryMetadata(
            user_id=user_id, session_id=session_id,
            source=source, tags=["conversation"]
        )
        return await self._client.add_memory(content, metadata, user_id)
        
    async def store_preference(self, content: str, user_id: Optional[str] = None,
                             category: str = "user_preference") -> MemoryOperation:
        metadata = MemoryMetadata(
            user_id=user_id, source=MemorySource.USER_INPUT,
            category=category, tags=["preference"], importance=8
        )
        return await self._client.add_memory(content, metadata, user_id)
        
    async def store_tool_result(self, tool_name: str, result: str,
                              user_id: Optional[str] = None,
                              session_id: Optional[str] = None) -> MemoryOperation:
        content = f"Tool '{tool_name}' result: {result}"
        metadata = MemoryMetadata(
            user_id=user_id, session_id=session_id,
            source=MemorySource.TOOL_EXECUTION, category="tool_result",
            tags=["tool", tool_name], importance=6
        )
        return await self._client.add_memory(content, metadata, user_id)
        
    async def search_memories(self, query_text: str, user_id: Optional[str] = None,
                            session_id: Optional[str] = None,
                            memory_type: Optional[MemoryType] = None,
                            limit: int = 10,
                            threshold: float = 0.7) -> SearchResult:
        query = SearchQuery(
            text=query_text, user_id=user_id, session_id=session_id,
            memory_type=memory_type, limit=limit, threshold=threshold
        )
        return await self._client.search_memories(query)
        
    async def search_by_category(self, category: str, user_id: Optional[str] = None,
                               limit: int = 10) -> SearchResult:
        query = SearchQuery(
            text=f"category:{category}", user_id=user_id, limit=limit,
            filters={"category": category}
        )
        return await self._client.search_memories(query)
        
    async def get_user_preferences(self, user_id: str, limit: int = 20) -> SearchResult:
        return await self.search_by_category("user_preference", user_id, limit)
        
    async def get_conversation_history(self, user_id: Optional[str] = None,
                                     session_id: Optional[str] = None,
                                     limit: int = 50) -> SearchResult:
        query = SearchQuery(
            text="conversation", user_id=user_id, session_id=session_id,
            memory_type=MemoryType.CONVERSATION, limit=limit, tags=["conversation"]
        )
        return await self._client.search_memories(query)
        
    async def extract_facts_from_text(self, text: str, user_id: Optional[str] = None,
                                    session_id: Optional[str] = None) -> List[MemoryOperation]:
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        operations = []
        for sentence in sentences:
            if len(sentence) > 10:
                op = await self.store_fact(
                    sentence, user_id=user_id, session_id=session_id,
                    category="extracted_fact", tags=["auto_extracted"]
                )
                operations.append(op)
        return operations
        
    def set_session_context(self, user_id: Optional[str] = None,
                          session_id: Optional[str] = None, **context) -> None:
        self._session_context.update({
            "user_id": user_id, "session_id": session_id, **context
        })
        
    def get_session_context(self) -> Dict[str, Any]:
        return self._session_context.copy() 