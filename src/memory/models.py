"""Data models for memory management and Mem0 integration."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class MemoryType(str, Enum):
    """Types of memory entries."""
    FACT = "fact"
    CONVERSATION = "conversation"
    PREFERENCE = "preference"
    CONTEXT = "context"
    TOOL_RESULT = "tool_result"


class MemorySource(str, Enum):
    """Sources of memory entries."""
    USER_INPUT = "user_input"
    AGENT_RESPONSE = "agent_response"
    TOOL_EXECUTION = "tool_execution"
    SYSTEM = "system"
    EXTERNAL = "external"


class MemoryMetadata(BaseModel):
    """Metadata for memory entries."""
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    agent_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source: MemorySource = MemorySource.USER_INPUT
    category: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    importance: int = Field(default=5, ge=1, le=10)
    custom_fields: Dict[str, Any] = Field(default_factory=dict)


class Memory(BaseModel):
    """A memory entry in the system."""
    id: Optional[str] = None
    content: str = Field(..., min_length=1)
    memory_type: MemoryType = MemoryType.FACT
    metadata: MemoryMetadata = Field(default_factory=MemoryMetadata)
    embedding: Optional[List[float]] = None
    score: Optional[float] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    version: int = Field(default=1, ge=1)
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {datetime: lambda v: v.isoformat()}


class SearchQuery(BaseModel):
    """Query parameters for memory search."""
    text: str = Field(..., min_length=1)
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    memory_type: Optional[MemoryType] = None
    limit: int = Field(default=10, ge=1, le=100)
    threshold: float = Field(default=0.7, ge=0.0, le=1.0)
    tags: List[str] = Field(default_factory=list)
    date_range: Optional[Dict[str, datetime]] = None
    filters: Dict[str, Any] = Field(default_factory=dict)


class SearchResult(BaseModel):
    """Result from memory search."""
    memories: List[Memory]
    total_count: int = Field(ge=0)
    query: SearchQuery
    execution_time_ms: float = Field(ge=0)
    
    @property
    def has_results(self) -> bool:
        """Check if search returned any results."""
        return len(self.memories) > 0
    
    @property
    def average_score(self) -> float:
        """Calculate average relevance score."""
        if not self.memories:
            return 0.0
        scores = [m.score for m in self.memories if m.score is not None]
        return sum(scores) / len(scores) if scores else 0.0


class MemoryOperation(BaseModel):
    """Represents a memory operation result."""
    success: bool
    operation: str
    memory_id: Optional[str] = None
    message: Optional[str] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class MemoryStats(BaseModel):
    """Memory usage statistics."""
    total_memories: int = Field(ge=0)
    memories_by_type: Dict[MemoryType, int] = Field(default_factory=dict)
    memories_by_source: Dict[MemorySource, int] = Field(default_factory=dict)
    average_importance: float = Field(ge=0.0, le=10.0)
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {datetime: lambda v: v.isoformat()} 