"""LLM代理数据模型

定义LLM API交互的消息、响应和函数调用数据结构。
"""

from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field


class Message(BaseModel):
    """聊天消息模型"""
    
    role: Literal["system", "user", "assistant", "function"] = Field(
        ..., description="消息角色"
    )
    content: Optional[str] = Field(None, description="消息内容")
    name: Optional[str] = Field(None, description="函数名")
    function_call: Optional[Dict[str, Any]] = Field(None, description="函数调用")
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为API请求格式"""
        data = {"role": self.role}
        if self.content is not None:
            data["content"] = self.content
        if self.name is not None:
            data["name"] = self.name
        if self.function_call is not None:
            data["function_call"] = self.function_call
        return data


class ChatChoice(BaseModel):
    """聊天选择模型"""
    
    index: int = Field(..., description="选择索引")
    message: Message = Field(..., description="回复消息")
    finish_reason: Optional[str] = Field(None, description="完成原因")


class ChatUsage(BaseModel):
    """Token使用统计"""
    
    prompt_tokens: int = Field(..., description="输入Token数")
    completion_tokens: int = Field(..., description="输出Token数")
    total_tokens: int = Field(..., description="总Token数")


class ChatResponse(BaseModel):
    """聊天响应模型"""
    
    id: str = Field(..., description="响应ID")
    object: str = Field(..., description="对象类型")
    created: int = Field(..., description="创建时间戳")
    model: str = Field(..., description="使用的模型")
    choices: List[ChatChoice] = Field(..., description="响应选择")
    usage: ChatUsage = Field(..., description="Token使用情况")
    
    @property
    def content(self) -> Optional[str]:
        """获取第一个选择的内容"""
        if self.choices:
            return self.choices[0].message.content
        return None


class FunctionDefinition(BaseModel):
    """函数定义模型"""
    
    name: str = Field(..., description="函数名称")
    description: str = Field(..., description="函数描述")
    parameters: Dict[str, Any] = Field(..., description="参数Schema")


class FunctionCall(BaseModel):
    """函数调用模型"""
    
    name: str = Field(..., description="函数名称")
    arguments: str = Field(..., description="参数JSON字符串")


class StreamChunk(BaseModel):
    """流式响应块模型"""
    
    id: str = Field(..., description="响应ID")
    object: str = Field(..., description="对象类型")
    created: int = Field(..., description="创建时间戳")
    model: str = Field(..., description="使用的模型")
    choices: List[Dict[str, Any]] = Field(..., description="响应选择")
    
    @property
    def delta_content(self) -> Optional[str]:
        """获取增量内容"""
        if self.choices and "delta" in self.choices[0]:
            return self.choices[0]["delta"].get("content")
        return None 