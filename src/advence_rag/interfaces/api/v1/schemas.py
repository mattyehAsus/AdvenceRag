from pydantic import BaseModel, Field


# OpenAI compatible schemas
class ChatMessage(BaseModel):
    role: str
    content: str
    name: str | None = None


class ChatCompletionRequest(BaseModel):
    model: str
    messages: list[ChatMessage]
    temperature: float | None = 1.0
    top_p: float | None = 1.0
    n: int | None = 1
    stream: bool | None = False
    stop: str | list[str] | None = None
    max_tokens: int | None = None
    presence_penalty: float | None = 0.0
    frequency_penalty: float | None = 0.0
    user: str | None = None


class ChatCompletionChoice(BaseModel):
    index: int
    message: ChatMessage | None = None
    delta: ChatMessage | None = None
    finish_reason: str | None = "stop"


class ChatCompletionUsage(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: list[ChatCompletionChoice]
    usage: ChatCompletionUsage = Field(default_factory=ChatCompletionUsage)


# Model list schemas
class ModelObject(BaseModel):
    id: str
    object: str = "model"
    created: int = 1677610602
    owned_by: str = "advence-rag"


class ModelListResponse(BaseModel):
    object: str = "list"
    data: list[ModelObject]


# Custom Ingest schemas
class IngestResponse(BaseModel):
    status: str
    added_count: int = 0
    error: str | None = None
