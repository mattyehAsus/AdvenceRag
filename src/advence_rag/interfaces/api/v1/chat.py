import time
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from google.adk.sessions.in_memory_session_service import InMemorySessionService

from advence_rag.domain.interfaces import LLMAgentService
from advence_rag.infrastructure.ai.agent_service import OrchestratorAgentService
from advence_rag.infrastructure.utils.streaming import StreamWrapper  # 引用包裝器
from advence_rag.interfaces.api.v1.schemas import (
    ChatCompletionChoice,
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatMessage,
    ModelListResponse,
    ModelObject,
)

router = APIRouter()


# Global singleton instance
_agent_service: LLMAgentService | None = None


def get_agent_service() -> LLMAgentService:
    global _agent_service
    if _agent_service is None:
        session_service = InMemorySessionService()
        _agent_service = OrchestratorAgentService(session_service=session_service)
    return _agent_service


# 心跳間隔（秒）- 較短以防止 Open WebUI 超時
HEARTBEAT_INTERVAL = 2

# Dependency 注入類型別名
AgentDep = Annotated[LLMAgentService, Depends(get_agent_service)]


@router.post("/chat/completions", response_model=ChatCompletionResponse)
async def chat_completions(request: ChatCompletionRequest, agent_service: AgentDep):
    try:
        messages = [m.model_dump() for m in request.messages]

        if request.stream:

            async def event_generator():
                resp_id = f"chatcmpl-{uuid.uuid4()}"
                created = int(time.time())

                # 1. 向 Service 請求原始資料 (AsyncGenerator or Dict)
                result_gen = await agent_service.chat(messages, stream=True)

                # 使用包裝器處理 Queue/Event 邏輯
                streamer = StreamWrapper(result_gen, heartbeat_interval=HEARTBEAT_INTERVAL)

                async for chunk in streamer.iterate():
                    # 處理心跳
                    if chunk == ":ping":
                        yield f": ping {int(time.time())}\n\n"
                        continue

                    # 格式化 OpenAI Chunk
                    data = ChatCompletionResponse(
                        id=resp_id,
                        created=created,
                        model=request.model,
                        choices=[
                            ChatCompletionChoice(
                                index=0,
                                delta=ChatMessage(role="assistant", content=chunk),
                                finish_reason=None,
                            )
                        ],
                    )
                    yield f"data: {data.model_dump_json()}\n\n"

                # 傳送結束標記
                final_data = ChatCompletionResponse(
                    id=resp_id,
                    created=created,
                    model=request.model,
                    choices=[
                        ChatCompletionChoice(
                            index=0,
                            delta=ChatMessage(role="assistant", content=""),
                            finish_reason="stop",
                        )
                    ],
                )
                yield f"data: {final_data.model_dump_json()}\n\n"
                yield "data: [DONE]\n\n"

            return StreamingResponse(event_generator(), media_type="text/event-stream")

        # Non-streaming
        result = await agent_service.chat(messages, stream=False)
        # 2. 非串流處理
        return ChatCompletionResponse(
            id=f"chatcmpl-{uuid.uuid4()}",
            created=int(time.time()),
            model=request.model,
            choices=[
                ChatCompletionChoice(
                    index=0,
                    message=ChatMessage(role="assistant", content=result["answer"]),
                    finish_reason="stop",
                )
            ],
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


# @router.post("/chat/completions2", response_model=ChatCompletionResponse)
# async def chat_completions2(request: ChatCompletionRequest, agent_service: AgentDep):
#     """OpenAI-compatible chat completions endpoint."""
#     try:
#         # Adapt Pydantic messages to list of dicts for the service
#         messages = [m.model_dump() for m in request.messages]

#         if request.stream:

#             async def event_generator():
#                 resp_id = f"chatcmpl-{uuid.uuid4()}"
#                 created = int(time.time())

#                 # Execute agent workflow with streaming
#                 token_gen = await agent_service.chat(messages, stream=True)

#                 # 包裝 generator 以支援心跳
#                 token_queue = asyncio.Queue()
#                 stream_done = asyncio.Event()

#                 async def consume_tokens():
#                     """消費 token 並放入 queue"""
#                     print(f"DEBUG: Starting consume_tokens task for {resp_id}")  # DEBUG LOG
#                     try:
#                         async for token in token_gen:
#                             await token_queue.put(token)
#                         print(f"DEBUG: consume_tokens finished normally for {resp_id}")  # DEBUG LOG
#                     except Exception as e:
#                         print(f"DEBUG: consume_tokens error for {resp_id}: {e}")  # DEBUG LOG
#                         await token_queue.put(f"[Error: {e}]")
#                     finally:
#                         stream_done.set()
#                         print(f"DEBUG: stream_done set for {resp_id}")  # DEBUG LOG

#                 # 啟動 token 消費任務
#                 consumer_task = asyncio.create_task(consume_tokens())

#                 try:
#                     while not stream_done.is_set() or not token_queue.empty():
#                         try:
#                             # 嘗試在心跳間隔內獲取 token
#                             token = await asyncio.wait_for(
#                                 token_queue.get(), timeout=HEARTBEAT_INTERVAL
#                             )

#                             if not token:
#                                 continue

#                             data = ChatCompletionResponse(
#                                 id=resp_id,
#                                 created=created,
#                                 model=request.model,
#                                 choices=[
#                                     ChatCompletionChoice(
#                                         index=0,
#                                         delta=ChatMessage(role="assistant", content=token),
#                                         finish_reason=None,
#                                     )
#                                 ],
#                             )
#                             yield f"data: {data.model_dump_json()}\n\n"

#                         except TimeoutError:
#                             # 超時時發送 SSE 註解心跳（不會顯示在 client）
#                             if not stream_done.is_set():
#                                 yield f": ping {int(time.time())}\n\n"

#                 finally:
#                     # 確保消費任務完成
#                     if not consumer_task.done():
#                         consumer_task.cancel()
#                         try:
#                             await consumer_task
#                         except asyncio.CancelledError:
#                             pass

#                 # End of stream
#                 final_data = ChatCompletionResponse(
#                     id=resp_id,
#                     created=created,
#                     model=request.model,
#                     choices=[
#                         ChatCompletionChoice(
#                             index=0,
#                             delta=ChatMessage(role="assistant", content=""),
#                             finish_reason="stop",
#                         )
#                     ],
#                 )
#                 yield f"data: {final_data.model_dump_json()}\n\n"
#                 yield "data: [DONE]\n\n"

#             return StreamingResponse(event_generator(), media_type="text/event-stream")

#         # Non-streaming
#         result = await agent_service.chat(messages, stream=False)

#         # Build OpenAI compatible response
#         return ChatCompletionResponse(
#             id=f"chatcmpl-{uuid.uuid4()}",
#             created=int(time.time()),
#             model=request.model,
#             choices=[
#                 ChatCompletionChoice(
#                     index=0,
#                     message=ChatMessage(role="assistant", content=result["answer"]),
#                     finish_reason="stop",
#                 )
#             ],
#         )
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


@router.get("/models", response_model=ModelListResponse)
async def list_models():
    """List available models for Open WebUI selection."""
    return ModelListResponse(data=[ModelObject(id="advence-rag-agent")])
