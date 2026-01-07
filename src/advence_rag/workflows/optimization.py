"""Optimization Workflow - 背景處理流程（含排程）。

流程：Ingestion → Parsing → Summarizing → Vectorizing
使用 APScheduler 實現獨立排程。
"""

import logging
from pathlib import Path
from typing import Any

from advence_rag.config import get_settings
from advence_rag.parsers import ParserType, detect_best_parser, get_parser

# Remove top-level imports that might cause gRPC/threading conflicts
# from advence_rag.tools.knowledge_base import add_documents
# from advence_rag.tools.summarizer import extract_key_points

settings = get_settings()
logger = logging.getLogger("advence_rag.optimization")


class OptimizationPipeline:
    """背景優化 Pipeline - 文檔處理與向量化。"""
    
    def __init__(self):
        self._scheduler = None
    
    def process_document(
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
        
        # 1. 自動偵測最佳解析器
        if parser_type == ParserType.AUTO:
            parser_type = detect_best_parser(str(path))
        
        logger.info(f"Processing {path.name} with {parser_type.value} parser")
        
        try:
            # 2. 解析文檔
            parser = get_parser(parser_type)
            documents = parser.parse(path)
            
            # 3. 為每個文檔生成摘要/關鍵要點
            # TODO: Enable summarization after resolving hanging issues
            # from advence_rag.tools.summarizer import extract_key_points
            
            processed_docs = []
            for doc in documents:
                # key_points = extract_key_points(doc.content, max_points=5)
                # doc.metadata["key_points"] = key_points.get("key_points", [])
                
                # Placeholder for key points - convert to string for Chroma
                doc.metadata["key_points"] = ""  # str(key_points.get("key_points", []))
                processed_docs.append(doc)
            
            # 4. 加入向量資料庫
            contents = [doc.content for doc in processed_docs]
            metadatas = [doc.metadata for doc in processed_docs]
            ids = [doc.chunk_id for doc in processed_docs]
            
            result = add_documents(
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
    
    def process_directory(
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
        
        if not dir_path.is_dir():
            return {"status": "error", "error": f"Not a directory: {directory}"}
        
        # 支援的副檔名
        supported_exts = {".pdf", ".docx", ".doc", ".pptx", ".html", ".txt", ".md"}
        
        if recursive:
            files = [f for f in dir_path.rglob("*") if f.suffix.lower() in supported_exts]
        else:
            files = [f for f in dir_path.glob("*") if f.suffix.lower() in supported_exts]
        
        results = {
            "status": "success",
            "total_files": len(files),
            "processed": 0,
            "failed": 0,
            "details": [],
        }
        
        for file in files:
            result = self.process_document(file)
            results["details"].append(result)
            
            if result["status"] == "success":
                results["processed"] += 1
            else:
                results["failed"] += 1
        
        return results
    
    def start_scheduler(self, watch_directory: str | Path | None = None):
        """啟動背景排程器。
        
        Args:
            watch_directory: 要監控的目錄（如提供則定期掃描新檔案）
        """
        if not settings.scheduler_enabled:
            logger.info("Scheduler is disabled in settings")
            return
        
        try:
            from apscheduler.schedulers.background import BackgroundScheduler
            from apscheduler.triggers.interval import IntervalTrigger
        except ImportError:
            raise ImportError(
                "apscheduler is required for scheduling. "
                "Install with: pip install apscheduler"
            )
        
        self._scheduler = BackgroundScheduler(timezone=settings.scheduler_timezone)
        
        if watch_directory:
            # 每 5 分鐘掃描一次目錄
            self._scheduler.add_job(
                func=lambda: self.process_directory(watch_directory),
                trigger=IntervalTrigger(minutes=5),
                id="document_ingestion",
                name="Document Ingestion Job",
                replace_existing=True,
            )
            logger.info(f"Scheduled document ingestion for: {watch_directory}")
        
        self._scheduler.start()
        logger.info("Background scheduler started")
    
    def stop_scheduler(self):
        """停止背景排程器。"""
        if self._scheduler:
            self._scheduler.shutdown()
            logger.info("Background scheduler stopped")


# 全域 Pipeline 實例
optimization_pipeline = OptimizationPipeline()
