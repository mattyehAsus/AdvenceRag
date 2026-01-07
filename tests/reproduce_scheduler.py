import sys
import time
import logging
from pathlib import Path

# Setup path
src_path = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(src_path))

from advence_rag.workflows.optimization import optimization_pipeline

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    print("Testing scheduler job registration...")
    
    test_dir = Path("./test_data")
    if not test_dir.exists():
        test_dir.mkdir()
        (test_dir / "sample.txt").write_text("Hello World")

    # Start scheduler
    optimization_pipeline.start_scheduler(watch_directory=str(test_dir))
    scheduler = optimization_pipeline._scheduler
    
    if not scheduler:
        print("Error: Scheduler not initialized")
        sys.exit(1)

    jobs = scheduler.get_jobs()
    print(f"Jobs found: {len(jobs)}")
    
    if len(jobs) == 0:
        print("Error: No jobs found")
        sys.exit(1)

    for job in jobs:
        print(f"Job: {job.name}, Next run: {job.next_run_time}")
        # Reschedule to run sooner to verify execution
        print("Rescheduling job to run every 2 seconds...")
        job.reschedule(trigger='interval', seconds=2)
        
    print("Waiting for job execution (8 seconds)...")
    # We can't easily see the output of the job unless we hook into logging or the job functionality
    # But seeing no error and process staying alive is a good sign.
    # The optimization pipeline logs to "advence_rag.optimization"
    
    time.sleep(8)
    
    optimization_pipeline.stop_scheduler()
    print("Test complete.")

if __name__ == "__main__":
    main()
