# Future Implementation: SQLSessionService

為了將對話記憶持久化（不再隨重啟消失），我們需要實作一個 `SQLSessionService` 來取代現有的 `InMemorySessionService`。

這是一個標準的 **Infrastructure** 層實作，建議使用 SQLAlchemy 以支援 SQLite (開發用) 與 PostgreSQL (生產用)。

## 1. 新增依賴
首先需要安裝 SQLAlchemy 相關套件：
```bash
pip install sqlalchemy aiosqlite  # 若使用 SQLite (Async)
# pip install asyncpg             # 若使用 PostgreSQL (Async)
```

## 2. 實作 SQLSessionService
建立新檔案：`src/advence_rag/infrastructure/persistence/sql_session_service.py`

此類別必須符合 ADK `SessionService` 的介面（Duck Typing 或是繼承 Base Class）。

```python
from typing import Optional, List
from datetime import datetime
import json

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, String, Text, DateTime, JSON

# 假設 ADK 提供 Base Class，若無則依據介面實作
# from google.adk.sessions import SessionService 

Base = declarative_base()

# --- DB Schema ---
class SessionModel(Base):
    __tablename__ = "sessions"
    
    session_id = Column(String, primary_key=True)
    user_id = Column(String, index=True)
    app_name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    # 儲存對話歷史 (Messages) 與 Context
    state = Column(JSON, default=dict) 

# --- Service Implementation ---
class SQLSessionService:
    def __init__(self, db_url: str = "sqlite+aiosqlite:///sessions.db"):
        self.engine = create_async_engine(db_url, echo=False)
        self.async_session = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )

    async def init_db(self):
        """初始化資料庫 Tables"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def create_session(self, app_name: str, user_id: str, session_id: str):
        """建立新 Session"""
        async with self.async_session() as session:
            new_session = SessionModel(
                session_id=session_id,
                user_id=user_id,
                app_name=app_name,
                state={"history": []}
            )
            session.add(new_session)
            await session.commit()

    async def get_session(self, session_id: str) -> Optional[dict]:
        """讀取 Session 狀態 (包含對話歷史)"""
        async with self.async_session() as session:
            result = await session.get(SessionModel, session_id)
            if result:
                # ADK 通常預期回傳某種 Session 物件，需視 ADK 介面轉換
                return result.state
            return None

    # ADK 可能需要 save_session 或類似方法來更新對話
    async def save_session_state(self, session_id: str, state: dict):
        async with self.async_session() as session:
            s = await session.get(SessionModel, session_id)
            if s:
                s.state = state
                await session.commit()
```

## 3. 整合至 Chat API
修改 `src/advence_rag/interfaces/api/v1/chat.py` 進行依賴注入。

我們之前已經準備好 Singleton 模式，現在只需要在 `on_startup` 初始化資料庫，並替換 Service 即可。

```python
from contextlib import asynccontextmanager
from advence_rag.infrastructure.persistence.sql_session_service import SQLSessionService

# Global Singleton
sql_session_service = SQLSessionService("sqlite+aiosqlite:///./chat_history.db")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # App 啟動時建立 Table
    await sql_session_service.init_db()
    yield

# 在 chat.py 中替換
@lru_cache()
def get_agent_service() -> LLMAgentService:
    # 注入 SQL implementation
    return OrchestratorAgentService(session_service=sql_session_service)
```

## 下一步
1. 確定 ADK `SessionService` 的具體 Method Signature (查看原始碼或文件)。
2. 實作上述程式碼。
3. 享受可持久化的對話記憶！
