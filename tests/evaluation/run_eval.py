import asyncio
import json
import logging
import sys
import uuid
from pathlib import Path
from typing import Any

# Setup path to include src
root_dir = Path(__file__).resolve().parent.parent.parent
src_path = root_dir / "src"
sys.path.insert(0, str(src_path))

from advence_rag.infrastructure.ai.agent_service import OrchestratorAgentService
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from advence_rag.utils.log_config import setup_logging
from advence_rag.config import get_settings
import os

# Setup logging
setup_logging(level="WARNING")
logger = logging.getLogger("evaluator")

# Ensure API Key is available to ADK
settings = get_settings()
if settings.google_api_key:
    os.environ["GOOGLE_API_KEY"] = settings.google_api_key

class RAGEvaluator:
    def __init__(self, golden_dataset_path: str):
        with open(golden_dataset_path, "r") as f:
            self.dataset = json.load(f)
        
        self.session_service = InMemorySessionService()
        self.agent_service = OrchestratorAgentService(session_service=self.session_service)
    
    async def evaluate_case(self, case: dict[str, Any]) -> dict[str, Any]:
        print(f"Evaluating Case: {case['id']} - '{case['query']}'")
        
        # Mapping English keywords to Chinese for bilingual verification
        bilingual_map = {
            "which file": ["哪一個檔案", "什麼檔案", "哪件文件", "指的是哪"],
            "provide more details": ["提供更多細節", "詳細資訊", "具體內容", "或者是關於", "想了解更多", "具體資訊"],
            "clarify": ["釐清", "澄清", "具體是指", "指的是什麼", "指的是哪", "具體是指", "更多關於"],
            "what would you like to know": ["想了解什麼", "想知道什麼", "指的是什麼", "了解更多關於什麼"],
            "programming language": ["程式語言", "編程語言"],
            "readability": ["可讀性", "易讀性"],
            "web search": ["網路搜尋", "Google 搜尋", "外部資料", "進行網頁搜尋"],
            "pizza": ["披薩", "比薩"]
        }
        
        # Reset session for clean state
        session_id = f"eval-{case['id']}-{uuid.uuid4().hex[:6]}"
        
        messages = [{"role": "user", "content": case["query"]}]
        
        # Simple retry for 500 errors
        max_retries = 2
        for attempt in range(max_retries + 1):
            try:
                result = await self.agent_service.chat(messages, stream=False, session_id=session_id)
                answer = result["answer"].lower()
                
                # Bilingual keyword matching
                matches = []
                for kw in case["must_contain_in_response"]:
                    kw_lower = kw.lower()
                    found = False
                    # Check English
                    if kw_lower in answer:
                        found = True
                    # Check Chinese synonyms
                    elif kw_lower in bilingual_map:
                        for synonym in bilingual_map[kw_lower]:
                            if synonym in answer:
                                found = True
                                break
                    
                    if found:
                        matches.append(kw)
                
                success = len(matches) == len(case["must_contain_in_response"])
                score = len(matches) / len(case["must_contain_in_response"]) if case["must_contain_in_response"] else 1.0
                
                return {
                    "id": case["id"],
                    "query": case["query"],
                    "expected_category": case["expected_category"],
                    "actual_answer": result["answer"],
                    "matches": matches,
                    "score": score,
                    "passed": success,
                }
            except Exception as e:
                if attempt < max_retries and ("500" in str(e) or "INTERNAL" in str(e)):
                    print(f"   ⚠️ Transient error, retrying... ({attempt+1}/{max_retries})")
                    await asyncio.sleep(2)
                    continue
                
                logger.error(f"Error evaluating {case['id']}: {e}")
                return {
                    "id": case["id"],
                    "query": case["query"],
                    "error": str(e),
                    "score": 0.0,
                    "passed": False,
                }

    async def run_evaluation(self) -> dict[str, Any]:
        results = []
        for case in self.dataset:
            res = await self.evaluate_case(case)
            results.append(res)
        
        total_score = sum(r["score"] for r in results)
        avg_score = total_score / len(results) if results else 0.0
        pass_rate = sum(1 for r in results if r["passed"]) / len(results) if results else 0.0
        
        summary = {
            "average_score": avg_score,
            "pass_rate": pass_rate,
            "total_cases": len(results),
            "results": results,
        }
        
        return summary

async def main():
    dataset_path = root_dir / "tests/evaluation/golden_dataset.json"
    evaluator = RAGEvaluator(str(dataset_path))
    
    print("\n" + "="*50)
    print("RUNNING RAG EVALUATION")
    print("="*50 + "\n")
    
    summary = await evaluator.run_evaluation()
    
    print("\n" + "="*50)
    print("EVALUATION SUMMARY")
    print(f"Average Score: {summary['average_score']:.2%}")
    print(f"Pass Rate:     {summary['pass_rate']:.2%}")
    print(f"Total Cases:   {summary['total_cases']}")
    print("="*50 + "\n")
    
    # Save results
    output_path = root_dir / "tests/evaluation/eval_results.json"
    with open(output_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"Results saved to {output_path}")

if __name__ == "__main__":
    asyncio.run(main())
