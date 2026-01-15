"""Optimization Workflow - 背景處理流程（含排程）。

流程：Ingestion → Parsing → Summarizing → Vectorizing
使用 APScheduler 實現獨立排程。
"""

import logging
import shutil
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Any

from advence_rag.config import get_settings
from advence_rag.parsers import ParserType, detect_best_parser, get_parser

# Remove top-level imports that might cause gRPC/threading conflicts
# from advence_rag.tools.knowledge_base import add_documents
# from advence_rag.tools.summarizer import extract_key_points

settings = get_settings()
logger = logging.getLogger(__name__)


class OptimizationPipeline:
    """背景優化 Pipeline - 文檔處理與向量化。"""
    
    def __init__(self):
        self._scheduler = None
    
    async def process_document(
        self,
        file_path: str | Path,
        parser_type: ParserType = ParserType.AUTO,
    ) -> dict[str, Any]:
        """處理單一文檔：解析 → 摘要 → 向量化。
        
        Args:
            file_path: 文檔路徑
            parser_type: 解析器類型
            
        Returns:
            dict: 處理結果
        """
        path = Path(file_path)
        
        # Local import to avoid initialization issues
        from advence_rag.tools.knowledge_base import add_documents
        
        # 1. 自動偵測最佳解析器 (Metadata access is fine, but detect_best_parser might do IO)
        if parser_type == ParserType.AUTO:
            parser_type = await asyncio.to_thread(detect_best_parser, str(path))
        
        logger.info(f"Processing {path.name} with {parser_type.value} parser")
        
        try:
            # 2. 解析文檔 (Parsing is CPU/IO heavy)
            parser = get_parser(parser_type)
            documents = await asyncio.to_thread(parser.parse, path)
            
            # 3. 為每個文檔生成摘要/關鍵要點
            # TODO: Enable summarization after resolving hanging issues
            processed_docs = []
            for doc in documents:
                doc.metadata["key_points"] = "" 
                processed_docs.append(doc)
            
            # 4. 加入向量資料庫 (Already refactored to async)
            contents = [doc.content for doc in processed_docs]
            metadatas = [doc.metadata for doc in processed_docs]
            ids = [doc.chunk_id for doc in processed_docs]
            
            result = await add_documents(
                documents=contents,
                metadatas=metadatas,
                ids=ids,
            )
            
            return {
                "status": "success",
                "file": str(path),
                "parser": parser_type.value,
                "chunks_processed": len(processed_docs),
                "added_to_db": result.get("added_count", 0),
            }
            
        except Exception as e:
            logger.error(f"Failed to process {path.name}: {e}")
            return {
                "status": "error",
                "file": str(path),
                "error": str(e),
            }
    
    async def process_directory(
        self,
        directory: str | Path,
        recursive: bool = True,
    ) -> dict[str, Any]:
        """處理目錄中的所有文檔。
        
        Args:
            directory: 目錄路徑
            recursive: 是否遞迴處理子目錄
            
        Returns:
            dict: 處理結果統計
        """
        dir_path = Path(directory)
        
        if not await asyncio.to_thread(dir_path.is_dir):
            return {"status": "error", "error": f"Not a directory: {directory}"}
        
        # 支援的副檔名
        supported_exts = {".pdf", ".docx", ".doc", ".pptx", ".html", ".txt", ".md"}
        
        def find_files():
            processed_dir = dir_path / "processed"
            error_dir = dir_path / "error"
            files_to_process = []
            
            if recursive:
                all_files = dir_path.rglob("*")
            else:
                all_files = dir_path.glob("*")
                
            for f in all_files:
                # 排除已處理和錯誤目錄
                if processed_dir in f.parents or f == processed_dir:
                    continue
                if error_dir in f.parents or f == error_dir:
                    continue
                if f.is_file() and f.suffix.lower() in supported_exts:
                    files_to_process.append(f)
            return files_to_process
        
        files = await asyncio.to_thread(find_files)
        
        results = {
            "status": "success",
            "total_files": len(files),
            "processed": 0,
            "failed": 0,
            "details": [],
        }
        
        if files:
            # Prepare directories
            processed_dir = dir_path / "processed"
            error_dir = dir_path / "error"
            for d in [processed_dir, error_dir]:
                if not await asyncio.to_thread(d.exists):
                    await asyncio.to_thread(d.mkdir, parents=True, exist_ok=True)
        
        for file in files:
            result = await self.process_document(file)
            results["details"].append(result)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if result["status"] == "success":
                results["processed"] += 1
                
                # 搬移至已處理目錄
                try:
                    target_path = processed_dir / file.name
                    
                    # 處理檔名衝突
                    if await asyncio.to_thread(target_path.exists):
                        target_path = processed_dir / f"{file.stem}_{timestamp}{file.suffix}"
                    
                    await asyncio.to_thread(shutil.move, str(file), str(target_path))
                    logger.info(f"Moved processed file to: {target_path}")
                except Exception as e:
                    logger.error(f"Failed to move processed file {file}: {e}")
            else:
                results["failed"] += 1
                
                # 搬移至錯誤目錄並產生 Log
                try:
                    error_msg = result.get("error", "Unknown error")
                    target_path = error_dir / file.name
                    log_path = error_dir / f"{file.name}.log"
                    
                    # 處理檔名衝突
                    if await asyncio.to_thread(target_path.exists):
                        target_path = error_dir / f"{file.stem}_{timestamp}{file.suffix}"
                        log_path = error_dir / f"{file.stem}_{timestamp}{file.suffix}.log"
                    
                    # 寫入錯誤日誌
                    def write_log():
                        with open(log_path, "w", encoding="utf-8") as f:
                            f.write(f"Error processing file: {file.name}\n")
                            f.write(f"Time: {datetime.now().isoformat()}\n")
                            f.write("-" * 20 + "\n")
                            f.write(f"Error Message:\n{error_msg}\n")
                    
                    await asyncio.to_thread(write_log)
                    await asyncio.to_thread(shutil.move, str(file), str(target_path))
                    logger.warning(f"Moved FAILED file to: {target_path}. See log: {log_path}")
                except Exception as e:
                    logger.error(f"Failed to handle error archiving for {file}: {e}")
        
        return results
    
    def start_scheduler(self, watch_directory: str | Path | None = None, interval: int = 5):
        """啟動背景排程器。
        
        Args:
            watch_directory: 要監控的目錄（如提供則定期掃描新檔案）
            interval: 掃描間隔（分鐘，預設 5 分鐘）
        """
        if not settings.scheduler_enabled:
            logger.info("Scheduler is disabled in settings")
            return
        
        try:
            from apscheduler.schedulers.asyncio import AsyncIOScheduler
            from apscheduler.triggers.interval import IntervalTrigger
        except ImportError:
            raise ImportError(
                "apscheduler is required for scheduling. "
                "Install with: pip install apscheduler"
            )
        
        self._scheduler = AsyncIOScheduler(timezone=settings.scheduler_timezone)
        
        if watch_directory:
            # 定期掃描目錄
            self._scheduler.add_job(
                func=self.process_directory,
                args=[watch_directory],
                trigger=IntervalTrigger(minutes=interval),
                id="document_ingestion",
                name="Document Ingestion Job",
                replace_existing=True,
                next_run_time=datetime.now(),
            )
            logger.info(f"Scheduled document ingestion for: {watch_directory} every {interval} minutes")
        
        self._scheduler.start()
        logger.info("Background scheduler started")
    
    def stop_scheduler(self):
        """停止背景排程器。"""
        if self._scheduler:
            self._scheduler.shutdown()
            logger.info("Background scheduler stopped")


# 全域 Pipeline 實例
optimization_pipeline = OptimizationPipeline()
