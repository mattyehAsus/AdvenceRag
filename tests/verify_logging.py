import sys
from pathlib import Path
import logging

# Setup path
src_path = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(src_path))

from advence_rag.utils.log_config import setup_logging

def verify_logging():
    print("--- Verifying Structured Logging ---")
    
    # Setup logger
    logger = setup_logging()
    
    print("1. Emitting Log with Extra Context...")
    # This should print JSON to stdout
    logger.info("Test Event", extra={
        "trace_id": "test-trace-123",
        "agent_name": "test_agent",
        "action": "testing_logging"
    })
    
    print("\n✅ Logging verification complete (Check stdout for JSON format)")

if __name__ == "__main__":
    verify_logging()
