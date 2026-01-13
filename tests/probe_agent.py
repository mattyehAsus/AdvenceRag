import asyncio
from google.adk import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.genai import types
from advence_rag.agent import root_agent

async def main():
    app_name = "advence_rag"
    user_id = "test_user"
    session_id = "test_session"
    
    session_service = InMemorySessionService()
    # Create the session
    session_service.create_session(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id
    )
    
    runner = Runner(
        agent=root_agent, 
        app_name=app_name,
        session_service=session_service
    )
    
    # Simple user message
    user_input = types.Content(
        role="user",
        parts=[types.Part(text="Hello")]
    )
    
    try:
        print("Running agent with Runner...")
        gen = runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=user_input
        )
        
        full_text = ""
        async for event in gen:
            # print(f"Event: {type(event)}")
            # Search for text in the event
            # ADK events usually have a payload that might contain the message
            # For simplicity, let's just log what we find
            event_dict = event.model_dump() if hasattr(event, "model_dump") else str(event)
            # print(f"Event Dict Keys: {event_dict.keys() if isinstance(event_dict, dict) else 'N/A'}")
            
            # Look for model response in events
            # Usually events have a 'type' or similar
            pass
                
        print("Run completed successfully (probed for events).")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await runner.close()

if __name__ == "__main__":
    asyncio.run(main())
