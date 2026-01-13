from typing import List, Dict, Any, Optional
import uuid
import logging
from dataclasses import dataclass, field

from google.adk import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.genai import types

from advence_rag.domain.interfaces import LLMAgentService
from advence_rag.agent import root_agent

# Setup logger
logger = logging.getLogger("advence_rag.agent_service")
logger.setLevel(logging.DEBUG)

# Console handler with formatting
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)


@dataclass
class ToolExecution:
    """記錄單次工具執行的資訊"""
    name: str
    status: str = "pending"  # pending, success, error
    arguments: str = ""
    result_summary: str = ""
    error: str = ""


@dataclass
class ExecutionContext:
    """追蹤整個請求的執行狀態"""
    session_id: str
    tool_executions: List[ToolExecution] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    
    def add_tool_call(self, name: str, arguments: str = "") -> ToolExecution:
        """記錄新的工具呼叫"""
        execution = ToolExecution(name=name, arguments=arguments)
        self.tool_executions.append(execution)
        return execution
    
    def mark_tool_success(self, name: str, result_summary: str = ""):
        """標記工具執行成功"""
        for exec in reversed(self.tool_executions):
            if exec.name == name and exec.status == "pending":
                exec.status = "success"
                exec.result_summary = result_summary
                break
    
    def mark_tool_error(self, name: str, error: str):
        """標記工具執行失敗"""
        for exec in reversed(self.tool_executions):
            if exec.name == name and exec.status == "pending":
                exec.status = "error"
                exec.error = error
                self.errors.append(f"{name}: {error}")
                break
    
    def add_error(self, error: str):
        """記錄一般性錯誤"""
        self.errors.append(error)
    
    def generate_summary(self) -> str:
        """生成執行摘要（附加在回應末尾）"""
        if not self.tool_executions and not self.errors:
            return ""
        
        lines = ["\n\n---", "📊 **執行摘要**"]
        
        # Tool executions
        if self.tool_executions:
            for exec in self.tool_executions:
                if exec.status == "success":
                    icon = "✅"
                    detail = f" ({exec.result_summary})" if exec.result_summary else ""
                elif exec.status == "error":
                    icon = "❌"
                    detail = f" - {exec.error}"
                else:
                    icon = "⏳"
                    detail = ""
                lines.append(f"- {icon} `{exec.name}`{detail}")
        
        # Errors
        if self.errors:
            lines.append("")
            lines.append("⚠️ **錯誤訊息**")
            for error in self.errors:
                lines.append(f"- {error}")
        
        return "\n".join(lines)
    
    def log_summary(self):
        """在 terminal 輸出詳細日誌"""
        logger.info(f"\n{'─'*50}")
        logger.info(f"📊 執行摘要 (Session: {self.session_id[:8]}...)")
        logger.info(f"{'─'*50}")
        
        for exec in self.tool_executions:
            if exec.status == "success":
                logger.info(f"✅ {exec.name}: 成功 {exec.result_summary}")
            elif exec.status == "error":
                logger.error(f"❌ {exec.name}: 失敗 - {exec.error}")
            else:
                logger.warning(f"⏳ {exec.name}: 進行中")
        
        if self.errors:
            logger.warning(f"⚠️ 總錯誤數: {len(self.errors)}")
            for error in self.errors:
                logger.error(f"   └─ {error}")
        
        # 輸出使用者可見的摘要到 log
        summary = self.generate_summary()
        if summary:
            logger.info(f"{'─'*50}")
            logger.info("📋 使用者回應摘要:")
            for line in summary.split('\n'):
                if line.strip():
                    logger.info(f"   {line}")
        
        logger.info(f"{'─'*50}\n")


class OrchestratorAgentService(LLMAgentService):
    """Infrastructure implementation of LLMAgentService using the ADK Orchestrator."""
    
    def __init__(self):
        self.session_service = InMemorySessionService()
        self.app_name = "advence_rag"

    async def chat(self, messages: List[Dict[str, str]], stream: bool = False, session_id: Optional[str] = None) -> Any:
        # OpenAI message format: [{"role": "user", "content": "..."}]
        
        if not messages:
            return {"answer": "No messages provided.", "citations": []}

        # Setup Runner
        runner = Runner(
            agent=root_agent,
            app_name=self.app_name,
            session_service=self.session_service
        )

        user_id = "default_user"
        session_id = session_id or str(uuid.uuid4())
        
        # 建立執行上下文
        ctx = ExecutionContext(session_id=session_id)
        
        await self.session_service.create_session(
            app_name=self.app_name,
            user_id=user_id,
            session_id=session_id
        )

        # Build conversation context
        context_parts = []
        for msg in messages[:-1]:
            role_label = "User" if msg["role"] == "user" else "Assistant" if msg["role"] == "assistant" else "System"
            context_parts.append(f"{role_label}: {msg['content']}")
        
        last_msg = messages[-1]
        if context_parts:
            context_str = "\n".join(context_parts)
            full_content = f"[Conversation History]\n{context_str}\n\n[Current Message]\n{last_msg['content']}"
        else:
            full_content = last_msg["content"]
        
        new_message = types.Content(
            role="user",
            parts=[types.Part(text=full_content)]
        )
        
        logger.info(f"\n{'='*60}")
        logger.info(f"📨 New Chat Request (session: {session_id[:8]}...)")
        logger.info(f"{'='*60}")
        logger.info(f"📝 User Message: {last_msg['content'][:200]}{'...' if len(last_msg['content']) > 200 else ''}")
        if context_parts:
            logger.debug(f"📜 History: {len(context_parts)} previous messages")

        try:
            gen = runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=new_message
            )
            
            if stream:
                async def stream_generator():
                    collected_answer = []  # 收集回答用於 log
                    last_author = None  # 追蹤 agent 切換
                    has_yielded_content = False  # 是否已輸出過內容
                    event_count = 0 
                    
                    logger.info("🚀 Starting stream_generator")
                    try:
                        async for event in gen:
                            event_count += 1
                            # 處理事件並記錄
                            self._process_event(event, ctx)
                            
                            # 檢測 agent 切換並發送進度通知
                            if hasattr(event, 'author') and event.author != last_author:
                                agent_name = event.author
                                last_author = agent_name
                                logger.debug(f"Stream: Author changed to {agent_name}")
                                
                                # 根據 agent 名稱產生友善的狀態訊息
                                status_map = {
                                    'orchestrator_agent': '🎯 協調處理中...\n',
                                    'guard_agent': '🛡️ 安全檢查中...\n',
                                    'search_agent': '🔍 搜尋資料中...\n',
                                    'planner_agent': '📋 規劃查詢策略...\n',
                                    'reviewer_agent': '📝 審核結果中...\n',
                                    'writer_agent': '✍️ 生成回答中...\n',
                                }
                                
                                # 只在尚未輸出實際內容時顯示進度
                                if not has_yielded_content and agent_name in status_map:
                                    logger.debug(f"Stream: Yielding status for {agent_name}")
                                    yield status_map[agent_name]
                            
                            # 產生文字輸出
                            text_to_yield = None
                            if hasattr(event, "message") and event.message and event.message.parts:
                                for part in event.message.parts:
                                    if part.text:
                                        text_to_yield = part.text
                            elif hasattr(event, "text") and event.text:
                                text_to_yield = event.text
                            elif hasattr(event, "content") and event.content:
                                if hasattr(event.content, "parts") and event.content.parts:
                                    for part in event.content.parts:
                                        if hasattr(part, "text") and part.text:
                                            text_to_yield = part.text
                            
                            if text_to_yield:
                                has_yielded_content = True
                                collected_answer.append(text_to_yield)
                                yield text_to_yield

                        logger.info(f"🏁 Stream loop finished. Total events: {event_count}, Has content: {has_yielded_content}")

                        # Safety: If no content was yielded, provide feedback
                        if not has_yielded_content and not ctx.errors:
                             msg = "⚠️ 系統未生成任何回答 (System produced no output)."
                             logger.warning(f"Root agent completed but yielded no text. Sending fallback: {msg}")
                             ctx.add_error("No content generated by agent.")
                             yield msg

                        # 串流結束時輸出摘要
                        ctx.log_summary()
                        
                        # 輸出最終回答到 log
                        full_answer = "".join(collected_answer)
                        if full_answer:
                            logger.info(f"{'─'*50}")
                            logger.info("📤 最終回答 (串流):")
                            logger.info(f"{'─'*50}")
                            answer_preview = full_answer[:1000]
                            for line in answer_preview.split('\n'):
                                logger.info(f"   {line}")
                            if len(full_answer) > 1000:
                                logger.info(f"   ... (truncated, total {len(full_answer)} chars)")
                            logger.info(f"{'─'*50}\n")
                        
                        summary = ctx.generate_summary()
                        if summary:
                            yield summary
                            
                    except Exception as e:
                        error_msg = str(e)
                        ctx.add_error(error_msg)
                        logger.error(f"❌ Stream Error: {error_msg}", exc_info=True)
                        ctx.log_summary()
                        
                        if "503" in error_msg or "Overloaded" in error_msg or "overloaded" in error_msg:
                            yield "\n\n---\n⚠️ **系統忙碌中 (Model Overloaded)**\n\n目前 AI 模型負載過高，暫時無法回應。請稍後重試。\n(Google Gemini API Error: 503 Service Unavailable)"
                        else:
                            yield f"\n\n---\n⚠️ **錯誤**: {error_msg}"
                    finally:
                        logger.info(f"Stream generator closing execution (Session: {session_id[:8]})")
                        await runner.close()
                        
                return stream_generator()

            # Non-streaming
            answer = ""
            async for event in gen:
                # 處理事件並記錄
                self._process_event(event, ctx)
                
                # 收集文字輸出
                if hasattr(event, "message") and event.message and event.message.parts:
                    for part in event.message.parts:
                        if part.text:
                            answer += part.text
                elif hasattr(event, "text") and event.text:
                    answer += event.text
                elif hasattr(event, "content") and event.content:
                    if hasattr(event.content, "parts") and event.content.parts:
                        for part in event.content.parts:
                            if hasattr(part, "text") and part.text:
                                answer += part.text
                elif hasattr(event, "payload") and isinstance(event.payload, dict):
                    text = event.payload.get("text") or event.payload.get("content")
                    if isinstance(text, str):
                        answer += text

            # 輸出日誌摘要
            ctx.log_summary()
            
            # 輸出最終回答到 log
            logger.info(f"{'─'*50}")
            logger.info("📤 最終回答:")
            logger.info(f"{'─'*50}")
            # 限制長度避免 log 太長
            answer_preview = answer.strip()[:1000] if answer else "Agent produced no text response."
            for line in answer_preview.split('\n'):
                logger.info(f"   {line}")
            if len(answer.strip()) > 1000:
                logger.info(f"   ... (truncated, total {len(answer)} chars)")
            logger.info(f"{'─'*50}\n")
            
            # 附加執行摘要到回應
            summary = ctx.generate_summary()
            final_answer = (answer.strip() or "Agent produced no text response.") + summary

            return {
                "answer": final_answer,
                "citations": [],
                "tool_executions": [
                    {"name": e.name, "status": e.status, "error": e.error}
                    for e in ctx.tool_executions
                ]
            }
        except Exception as e:
            ctx.add_error(str(e))
            ctx.log_summary()
            if not stream:
                await runner.close()
            raise
        finally:
            if not stream:
                await runner.close()
    
    def _process_event(self, event, ctx: ExecutionContext):
        """處理 ADK 事件並記錄到執行上下文"""
        event_type = type(event).__name__
        
        # 記錄事件
        if hasattr(event, 'author'):
            logger.debug(f"🔄 Event: {event_type} | Author: {event.author}")
        
        # 處理工具呼叫
        if hasattr(event, 'actions') and event.actions:
            # Tool calls (請求)
            if hasattr(event.actions, 'tool_calls') and event.actions.tool_calls:
                for tc in event.actions.tool_calls:
                    tool_name = tc.function.name if hasattr(tc, 'function') else str(tc)
                    args = str(tc.function.arguments)[:100] if hasattr(tc, 'function') else ""
                    ctx.add_tool_call(tool_name, args)
                    logger.info(f"🔧 Tool Call: {tool_name}({args[:50]}...)")
        
        # 處理工具結果
        if hasattr(event, 'content') and event.content:
            if hasattr(event.content, 'parts') and event.content.parts:
                for part in event.content.parts:
                    if hasattr(part, 'function_response'):
                        response = part.function_response
                        tool_name = response.name if hasattr(response, 'name') else "unknown"
                        
                        # 檢查結果
                        result = response.response if hasattr(response, 'response') else {}
                        if isinstance(result, dict):
                            status = result.get('status', 'unknown')
                            if status == 'error':
                                error_msg = result.get('error', 'Unknown error')
                                ctx.mark_tool_error(tool_name, error_msg)
                                logger.error(f"❌ Tool Error: {tool_name} - {error_msg}")
                            else:
                                summary = ""
                                if 'total_found' in result:
                                    summary = f"找到 {result['total_found']} 筆"
                                elif 'count' in result:
                                    summary = f"{result['count']} 筆結果"
                                elif 'added_count' in result:
                                    summary = f"新增 {result['added_count']} 筆"
                                ctx.mark_tool_success(tool_name, summary)
                                logger.info(f"✅ Tool Success: {tool_name} {summary}")
