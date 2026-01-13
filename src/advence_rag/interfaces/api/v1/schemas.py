from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union

# OpenAI compatible schemas
class ChatMessage(BaseModel):
    role: str
    content: str
    name: Optional[str] = None

class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[ChatMessage]
    temperature: Optional[float] = 1.0
    top_p: Optional[float] = 1.0
    n: Optional[int] = 1
    stream: Optional[bool] = False
    stop: Optional[Union[str, List[str]]] = None
    max_tokens: Optional[int] = None
    presence_penalty: Optional[float] = 0.0
    frequency_penalty: Optional[float] = 0.0
    user: Optional[str] = None

class ChatCompletionChoice(BaseModel):
    index: int
    message: Optional[ChatMessage] = None
    delta: Optional[ChatMessage] = None
    finish_reason: Optional[str] = "stop"

class ChatCompletionUsage(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0

class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[ChatCompletionChoice]
    usage: ChatCompletionUsage = Field(default_factory=ChatCompletionUsage)

# Model list schemas
class ModelObject(BaseModel):
    id: str
    object: str = "model"
    created: int = 1677610602
    owned_by: str = "advence-rag"

class ModelListResponse(BaseModel):
    object: str = "list"
    data: List[ModelObject]

# Custom Ingest schemas
class IngestResponse(BaseModel):
    status: str
    added_count: int = 0
    error: Optional[str] = None
