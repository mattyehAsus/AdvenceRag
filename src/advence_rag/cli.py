"""CLI entry point for Advence RAG."""

import argparse
import sys
from pathlib import Path

# 確保 src 目錄在 sys.path 中，以支援絕對導入
_src_path = Path(__file__).resolve().parent.parent
if str(_src_path) not in sys.path:
    sys.path.insert(0, str(_src_path))

from advence_rag.config import get_settings
from advence_rag.utils import setup_logging


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Advence RAG - Multi-Agent RAG System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # ingest command
    ingest_parser = subparsers.add_parser(
        "ingest",
        help="Ingest documents into the knowledge base",
    )
    ingest_parser.add_argument(
        "path",
        help="File or directory path to ingest",
    )
    ingest_parser.add_argument(
        "--parser",
        choices=["auto", "pymupdf", "docling", "unstructured"],
        default="auto",
        help="Parser to use (default: auto)",
    )
    ingest_parser.add_argument(
        "--recursive", "-r",
        action="store_true",
        help="Recursively process directories",
    )
    
    # serve command
    serve_parser = subparsers.add_parser(
        "serve",
        help="Start the ADK development server",
    )
    serve_parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to run the server on (default: 8000)",
    )
    
    # scheduler command
    scheduler_parser = subparsers.add_parser(
        "scheduler",
        help="Start the background scheduler",
    )
    scheduler_parser.add_argument(
        "--watch",
        help="Directory to watch for new documents",
    )
    scheduler_parser.add_argument(
        "--interval",
        type=int,
        default=5,
        help="Scan interval in minutes (default: 5)",
    )
    
    args = parser.parse_args()
    
    # Setup logging
    settings = get_settings()
    logger = setup_logging(settings.log_level)
    
    if args.command == "ingest":
        import asyncio
        from pathlib import Path
        from advence_rag.parsers import ParserType
        from advence_rag.workflows.optimization import optimization_pipeline
        
        async def run_ingest():
            parser_type = ParserType(args.parser)
            path = Path(args.path)
            
            if path.is_file():
                result = await optimization_pipeline.process_document(path, parser_type)
            elif path.is_dir():
                result = await optimization_pipeline.process_directory(path, args.recursive)
            else:
                logger.error(f"Path not found: {args.path}")
                sys.exit(1)
            
            print(f"Result: {result}")
        
        asyncio.run(run_ingest())
        
    elif args.command == "serve":
        import subprocess
        logger.info(f"Starting ADK server on port {args.port}...")
        subprocess.run([
            "adk", "web", "src/advence_rag",
            "--port", str(args.port),
        ])
        
    elif args.command == "scheduler":
        import asyncio
        from advence_rag.workflows.optimization import optimization_pipeline
        
        async def run_scheduler():
            logger.info("Starting background scheduler...")
            optimization_pipeline.start_scheduler(args.watch, interval=args.interval)
            
            # Keep running
            try:
                while True:
                    await asyncio.sleep(60)
            except asyncio.CancelledError:
                optimization_pipeline.stop_scheduler()
                logger.info("Scheduler stopped")
        
        try:
            asyncio.run(run_scheduler())
        except KeyboardInterrupt:
            pass
            
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
