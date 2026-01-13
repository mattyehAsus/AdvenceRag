import asyncio
import logging
import sys
from pathlib import Path

from dotenv import load_dotenv

# Setup path
src_path = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(src_path))

# Load env before other imports might consume env vars
load_dotenv()

from google.adk import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.genai import types
from advence_rag.agents.orchestrator import orchestrator_agent
from advence_rag.config import get_settings

# Configure logging to see agent transitions
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("verify_clarification")

async def test_ambiguous_query():
    print("\n\n--- Testing Ambiguous Query: 'Where is it?' ---")
    
    session_service = InMemorySessionService()
    runner = Runner(
        agent=orchestrator_agent,
        session_service=session_service,
        app_name="advence_rag"
    )
    session_id = "test-session-clarification"
    await session_service.create_session(app_name="advence_rag", user_id="test-user", session_id=session_id)
    
    # 1. Ambiguous Query
    start_msg = types.Content(
        role="user",
        parts=[types.Part(text="Where is it?")]
    )
    
    print(f"User: {start_msg.parts[0].text}")
    
    async for event in runner.run_async(session_id=session_id, user_id="test-user", new_message=start_msg):
        if hasattr(event, 'author'):
            print(f"🔄 Agent switched to: {event.author}")
        
        if hasattr(event, 'message') and event.message.parts:
            print(f"🤖 Answer: {event.message.parts[0].text}")

async def test_greeting():
    print("\n\n--- Testing Greeting: 'Hi' (Loop Check) ---")
    
    session_service = InMemorySessionService()
    runner = Runner(
        agent=orchestrator_agent,
        session_service=session_service,
        app_name="advence_rag"
    )
    session_id = "test-session-greeting"
    await session_service.create_session(app_name="advence_rag", user_id="test-user", session_id=session_id)
    
    # 2. Greeting
    start_msg = types.Content(
        role="user",
        parts=[types.Part(text="Hi")]
    )
    
    print(f"User: {start_msg.parts[0].text}")
    
    count = 0
    async for event in runner.run_async(session_id=session_id, user_id="test-user", new_message=start_msg):
        if hasattr(event, 'author'):
            print(f"🔄 Agent switched to: {event.author}")
            count += 1
            if count > 5:
                print("❌ Loop detected! Too many agent switches.")
                break
        
        if hasattr(event, 'message') and event.message.parts:
            print(f"🤖 Answer: {event.message.parts[0].text}")

async def main():
    await test_ambiguous_query()
    await test_greeting()

if __name__ == "__main__":
    asyncio.run(main())
