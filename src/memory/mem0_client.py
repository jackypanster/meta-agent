"""Mem0 client wrapper for memory management operations."""

import asyncio
import logging
import os
from typing import Dict, Optional, Any, List
from datetime import datetime
from mem0 import AsyncMemoryClient
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
        self._client: Optional[AsyncMemoryClient] = None
        
    async def __aenter__(self):
        await self.connect()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()
        
    async def connect(self) -> None:
        try:
            # 确保MEM0_API_KEY环境变量已设置
            if not os.environ.get("MEM0_API_KEY"):
                # 尝试从配置中获取API密钥
                mem0_config = getattr(self._config, 'mem0', None)
                if mem0_config and hasattr(mem0_config, 'api_key'):
                    os.environ["MEM0_API_KEY"] = mem0_config.api_key
                else:
                    raise ValueError("MEM0_API_KEY not found in environment variables or configuration")
            
            # 创建AsyncMemoryClient
            self._client = AsyncMemoryClient()
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
            
    async def add_memory(self, text: str, metadata: Optional[Dict[str, Any]] = None,
                        user_id: Optional[str] = None) -> MemoryOperation:
        """添加记忆
        
        Args:
            text: 记忆内容
            metadata: 元数据
            user_id: 用户ID
            
        Returns:
            记忆操作结果
        """
        self._ensure_connected()
        start_time = datetime.utcnow()
        try:
            # 构建消息格式（按照mem0官方文档）
            messages = [{"role": "user", "content": text}]
            
            # 调用add方法
            if user_id:
                result = await self._client.add(messages, user_id=user_id)
            else:
                result = await self._client.add(messages)
            
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            # 提取结果信息
            memory_id = None
            if isinstance(result, dict):
                memory_id = result.get("id")
            elif isinstance(result, list) and len(result) > 0:
                memory_id = result[0].get("id") if isinstance(result[0], dict) else str(result[0])
            
            logger.info(f"Added memory {memory_id} in {execution_time:.2f}ms")
            return MemoryOperation(
                success=True, 
                operation="add_memory",
                memory_id=memory_id,
                message="Memory added successfully",
                metadata={"execution_time_ms": execution_time}
            )
        except Exception as e:
            logger.error(f"Failed to add memory: {e}")
            return MemoryOperation(success=False, operation="add_memory", error=str(e))
            
    async def search_memories(self, query: str, user_id: Optional[str] = None, 
                             limit: int = 5) -> List[Dict[str, Any]]:
        """搜索记忆
        
        Args:
            query: 搜索查询
            user_id: 用户ID
            limit: 返回结果数量限制
            
        Returns:
            搜索结果列表
        """
        self._ensure_connected()
        start_time = datetime.utcnow()
        try:
            # 调用search方法
            if user_id:
                results = await self._client.search(query, user_id=user_id)
            else:
                results = await self._client.search(query)
            
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            # 处理结果
            memories = []
            if results:
                for result in results[:limit]:  # 应用限制
                    if isinstance(result, dict):
                        memories.append(result)
                    
            logger.info(f"Found {len(memories)} memories in {execution_time:.2f}ms")
            return memories
            
        except Exception as e:
            logger.error(f"Memory search failed: {e}")
            return []
            
    def _convert_to_memory(self, mem0_result: Dict[str, Any]) -> Optional[Memory]:
        """将mem0结果转换为内部Memory对象
        
        Args:
            mem0_result: mem0返回的结果
            
        Returns:
            转换后的Memory对象
        """
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
                id=mem0_result.get("id"),
                content=mem0_result.get("text", mem0_result.get("memory", "")),
                memory_type=MemoryType.FACT,
                metadata=metadata,
                score=mem0_result.get("score")
            )
        except Exception as e:
            logger.warning(f"Failed to convert mem0 result: {e}")
            return None 