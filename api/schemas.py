"""
OpenAI-compatible API schemas for the LLM orchestrator.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid


class MessageModel(BaseModel):
    role: str = Field(..., description="Message role: 'system', 'user', or 'assistant'")
    content: str = Field(..., description="Message content")


class ChatCompletionRequest(BaseModel):
    model: str = Field(default="local", description="Model name")
    messages: List[MessageModel] = Field(..., description="Chat messages")
    temperature: Optional[float] = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=None)
    top_p: Optional[float] = Field(default=1.0)
    frequency_penalty: Optional[float] = Field(default=0.0)
    presence_penalty: Optional[float] = Field(default=0.0)
    stream: Optional[bool] = Field(default=False)


class Choice(BaseModel):
    index: int
    message: MessageModel
    finish_reason: str = "stop"


class ChatCompletionResponse(BaseModel):
    id: str = Field(default_factory=lambda: f"chatcmpl-{uuid.uuid4().hex[:24]}")
    object: str = "chat.completion"
    created: int = Field(default_factory=lambda: int(datetime.now().timestamp()))
    model: str
    choices: List[Choice]
    usage: Optional[Dict[str, Any]] = None


class QueryRequest(BaseModel):
    prompt: str = Field(..., description="Input prompt")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Optional metadata")


class QueryResponse(BaseModel):
    id: str = Field(default_factory=lambda: f"query-{uuid.uuid4().hex[:24]}")
    result: Dict[str, Any]
    status: str = "success"
