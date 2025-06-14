"""Mem0 client wrapper for memory management operations."""

import asyncio
import logging
from typing import Dict, Optional, Any
from datetime import datetime
from mem0 import Memory as Mem0Memory
from src.config import ConfigManager
from .models import (
    Memory, MemoryMetadata, SearchQuery, SearchResult, 
    MemoryOperation, MemoryType, MemorySource
)

logger = logging.getLogger(__name__)


class Mem0Client:
    """Wrapper for Mem0 memory management service."""
    
    def __init__(self, config_manager: Optional[ConfigManager] = None):
        self._config = config_manager or ConfigManager()
        self._client: Optional[Mem0Memory] = None
        
    async def __aenter__(self):
        await self.connect()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()
        
    async def connect(self) -> None:
        try:
            api_key = self._config.mem0.api_key
            if not api_key:
                raise ValueError("MEM0_API_KEY not found in configuration")
            self._client = Mem0Memory(api_key=api_key)
            logger.info("Connected to Mem0 service")
        except Exception as e:
            logger.error(f"Failed to connect to Mem0: {e}")
            raise
            
    async def disconnect(self) -> None:
        self._client = None
        logger.info("Disconnected from Mem0 service")
        
    def _ensure_connected(self) -> None:
        if not self._client:
            raise RuntimeError("Mem0 client not connected. Call connect() first.")
            
    async def add_memory(self, content: str, metadata: Optional[MemoryMetadata] = None,
                        user_id: Optional[str] = None) -> MemoryOperation:
        self._ensure_connected()
        start_time = datetime.utcnow()
        try:
            memory_data = {"content": content}
            if user_id:
                memory_data["user_id"] = user_id
            if metadata:
                memory_data["metadata"] = {
                    "source": metadata.source.value, "category": metadata.category,
                    "tags": metadata.tags, "confidence": metadata.confidence,
                    "importance": metadata.importance, **metadata.custom_fields
                }
            result = await asyncio.to_thread(self._client.add, memory_data)
            memory_id = result.get("id") if isinstance(result, dict) else str(result)
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            logger.info(f"Added memory {memory_id} in {execution_time:.2f}ms")
            return MemoryOperation(
                success=True, operation="add_memory", memory_id=memory_id,
                message="Memory added successfully",
                metadata={"execution_time_ms": execution_time}
            )
        except Exception as e:
            logger.error(f"Failed to add memory: {e}")
            return MemoryOperation(success=False, operation="add_memory", error=str(e))
            
    async def search_memories(self, query: SearchQuery) -> SearchResult:
        self._ensure_connected()
        start_time = datetime.utcnow()
        try:
            search_params = {"query": query.text, "limit": query.limit}
            if query.user_id:
                search_params["user_id"] = query.user_id
            results = await asyncio.to_thread(self._client.search, **search_params)
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            memories = []
            if results:
                for result in results:
                    memory = self._convert_to_memory(result)
                    if memory:
                        memories.append(memory)
            logger.info(f"Found {len(memories)} memories in {execution_time:.2f}ms")
            return SearchResult(
                memories=memories, total_count=len(memories), 
                query=query, execution_time_ms=execution_time
            )
        except Exception as e:
            logger.error(f"Memory search failed: {e}")
            return SearchResult(memories=[], total_count=0, query=query, execution_time_ms=0)
            
    def _convert_to_memory(self, mem0_result: Dict[str, Any]) -> Optional[Memory]:
        try:
            metadata = MemoryMetadata()
            if "metadata" in mem0_result:
                meta = mem0_result["metadata"]
                metadata.source = MemorySource(meta.get("source", "external"))
                metadata.category = meta.get("category")
                metadata.tags = meta.get("tags", [])
                metadata.confidence = meta.get("confidence", 1.0)
                metadata.importance = meta.get("importance", 5)
            return Memory(
                id=mem0_result.get("id"), content=mem0_result.get("content", ""),
                memory_type=MemoryType.FACT, metadata=metadata,
                score=mem0_result.get("score")
            )
        except Exception as e:
            logger.warning(f"Failed to convert mem0 result: {e}")
            return None 