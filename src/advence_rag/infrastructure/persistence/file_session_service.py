import json
import os
import aiofiles
import asyncio
from typing import Optional, Any, Dict, List
from datetime import datetime
import asyncio

from google.adk.sessions.base_session_service import BaseSessionService
from google.adk.sessions.session import Session

class FileSessionService(BaseSessionService):
    """A simple file-based session service for persistence without pickling issues."""
    
    def __init__(self, data_dir: str = ".sessions"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
    
    def _get_file_path(self, session_id: str) -> str:
        return os.path.join(self.data_dir, f"{session_id}.json")

    async def create_session(self, app_name: str, user_id: str, session_id: str,
                           session_data: Optional[Dict[str, Any]] = None) -> Session:
        import time
        session = Session(
            id=session_id,
            app_name=app_name,
            user_id=user_id,
            state=session_data or {},
            events=[],
            last_update_time=time.time()
        )
        await self.save_session(session)
        return session

    async def get_session(self, *, app_name: str, user_id: str, session_id: str, config: Optional[Any] = None) -> Optional[Session]:
        path = self._get_file_path(session_id)
        if not await asyncio.to_thread(os.path.exists, path):
            return None
            
        async with aiofiles.open(path, 'r') as f:
            content = await f.read()
            try:
                # Use Pydantic's built-in validation/deserialization
                return Session.model_validate_json(content)
            except Exception:
                return None

    async def save_session(self, session: Session) -> None:
        path = self._get_file_path(session.id)
        # Use Pydantic's built-in serialization
        async with aiofiles.open(path, 'w') as f:
            await f.write(session.model_dump_json(indent=2))

    async def delete_session(self, session_id: str) -> None:
        path = self._get_file_path(session_id)
        if await asyncio.to_thread(os.path.exists, path):
            await asyncio.to_thread(os.remove, path)

    async def list_sessions(self) -> List[Session]:
        sessions = []
        if not await asyncio.to_thread(os.path.exists, self.data_dir):
            return sessions
            
        filenames = await asyncio.to_thread(os.listdir, self.data_dir)
        for filename in filenames:
            if filename.endswith(".json"):
                session_id = filename[:-5]
                session = await self.get_session(session_id)
                if session:
                    sessions.append(session)
        return sessions
