"""High-level memory service API for Qwen-Agent."""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from src.config import ConfigManager
from .manager import MemoryManager
from .models import (
    Memory, MemoryOperation, SearchResult, MemoryType, MemorySource
)

logger = logging.getLogger(__name__)


class MemoryService:
    
    def __init__(self, config_manager: Optional[ConfigManager] = None):
        self._config = config_manager or ConfigManager()
        self._manager = MemoryManager(self._config)
        self._active_session: Optional[Dict[str, str]] = None
        
    async def __aenter__(self):
        await self._manager.__aenter__()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._manager.__aexit__(exc_type, exc_val, exc_tb)
        
    def start_session(self, user_id: str, session_id: Optional[str] = None) -> str:
        session_id = session_id or f"session_{int(datetime.utcnow().timestamp())}"
        self._active_session = {"user_id": user_id, "session_id": session_id}
        self._manager.set_session_context(user_id=user_id, session_id=session_id)
        logger.info(f"Started memory session {session_id} for user {user_id}")
        return session_id
        
    def end_session(self) -> None:
        if self._active_session:
            logger.info(f"Ended memory session {self._active_session['session_id']}")
            self._active_session = None
            self._manager.set_session_context()
            
    async def store_user_message(self, message: str, user_id: Optional[str] = None) -> MemoryOperation:
        return await self._manager.store_conversation(
            f"User: {message}", user_id=user_id or self._get_current_user(),
            session_id=self._get_current_session(), source=MemorySource.USER_INPUT
        )
        
    async def store_agent_response(self, response: str, user_id: Optional[str] = None) -> MemoryOperation:
        return await self._manager.store_conversation(
            f"Agent: {response}", user_id=user_id or self._get_current_user(),
            session_id=self._get_current_session(), source=MemorySource.AGENT_RESPONSE
        )
        
    async def store_fact(self, fact: str, category: Optional[str] = None,
                        tags: List[str] = None, importance: int = 5,
                        user_id: Optional[str] = None) -> MemoryOperation:
        return await self._manager.store_fact(
            fact, user_id=user_id or self._get_current_user(),
            session_id=self._get_current_session(),
            category=category, tags=tags, importance=importance
        )
        
    async def store_preference(self, preference: str, user_id: Optional[str] = None) -> MemoryOperation:
        return await self._manager.store_preference(
            preference, user_id=user_id or self._get_current_user()
        )
        
    async def store_tool_result(self, tool_name: str, result: str,
                              user_id: Optional[str] = None) -> MemoryOperation:
        return await self._manager.store_tool_result(
            tool_name, result, user_id=user_id or self._get_current_user(),
            session_id=self._get_current_session()
        )
        
    async def search(self, query: str, limit: int = 10,
                    memory_type: Optional[MemoryType] = None,
                    user_id: Optional[str] = None) -> SearchResult:
        return await self._manager.search_memories(
            query, user_id=user_id or self._get_current_user(),
            session_id=self._get_current_session(),
            memory_type=memory_type, limit=limit
        )
        
    async def get_relevant_context(self, query: str, limit: int = 5) -> List[str]:
        result = await self.search(query, limit=limit)
        return [memory.content for memory in result.memories]
        
    async def get_user_preferences(self, user_id: Optional[str] = None,
                                 limit: int = 20) -> List[str]:
        result = await self._manager.get_user_preferences(
            user_id=user_id or self._get_current_user(), limit=limit
        )
        return [memory.content for memory in result.memories]
        
    async def get_conversation_history(self, limit: int = 50,
                                     user_id: Optional[str] = None,
                                     session_id: Optional[str] = None) -> List[str]:
        result = await self._manager.get_conversation_history(
            user_id=user_id or self._get_current_user(),
            session_id=session_id or self._get_current_session(), limit=limit
        )
        return [memory.content for memory in result.memories]
        
    async def extract_and_store_facts(self, text: str,
                                    user_id: Optional[str] = None) -> List[MemoryOperation]:
        return await self._manager.extract_facts_from_text(
            text, user_id=user_id or self._get_current_user(),
            session_id=self._get_current_session()
        )
        
    def _get_current_user(self) -> Optional[str]:
        return self._active_session.get("user_id") if self._active_session else None
    def _get_current_session(self) -> Optional[str]:
        return self._active_session.get("session_id") if self._active_session else None
        
    @property
    def is_session_active(self) -> bool:
        return self._active_session is not None
    @property
    def current_session_info(self) -> Optional[Dict[str, str]]:
        return self._active_session.copy() if self._active_session else None 