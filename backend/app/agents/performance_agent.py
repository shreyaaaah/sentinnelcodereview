import os
import re
from typing import List, Dict, Any, Optional
from app.ingestion.chunker import CodeChunk
from app.agents.llm_client import LLMClient

SYSTEM_PROMPT_PERFORMANCE = """You are a performance-focused code reviewer. Detect N+1 query patterns, unnecessary loops/recomputation, memory leaks, and inefficient data structures. Estimate Big-O complexity for changed functions. Return only valid JSON matching the specified schema."""

class PerformanceAgent:
    """
    Performance Agent detecting N+1 query patterns, unnecessary loops,
    memory leaks, and inefficient algorithms.
    Computes Big-O complexity estimates.
    """
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY") or os.getenv("OPENAI_API_KEY")
        self.llm_client = LLMClient()

    async def analyze(self, chunk: CodeChunk, rag_context: List[str] = []) -> List[Dict[str, Any]]:
        llm_findings = await self.llm_client.invoke_agent_llm(
            agent_type="performance",
            system_prompt=SYSTEM_PROMPT_PERFORMANCE,
            code_chunk=chunk.code,
            file_path=chunk.file_path,
            start_line=chunk.start_line,
            rag_context=rag_context
        )

        if llm_findings is not None:
            return llm_findings

        return self._heuristic_performance_scan(chunk)

    def _heuristic_performance_scan(self, chunk: CodeChunk) -> List[Dict[str, Any]]:
        findings = []
        lines = chunk.code.splitlines()

        for idx, line in enumerate(lines, start=chunk.start_line):
            line_str = line.strip()

            # 1. N+1 Query in Loop (Python, JS, Java)
            if re.search(r'for\s*\(|for\s+.*in\s+.*:', line_str) and any(kw in chunk.code for kw in ["db.query", "objects.get", "select(", "fetch(", "db.execute"]):
                findings.append({
                    "agent": "performance",
                    "file_path": chunk.file_path,
                    "line_start": idx,
                    "line_end": min(chunk.end_line, idx + 4),
                    "severity": "high",
                    "complexity_estimate": "O(N) DB calls",
                    "description": "Potential N+1 Database Query pattern. Executing database calls inside a loop triggers round-trips for each iteration.",
                    "suggested_fix": "Fetch required records using batch queries or SQL JOINs before entering the loop."
                })

            # 2. Nested Loop Complexity O(n^2) or O(m * n) (C++, Java, JS, Python)
            if re.search(r'for\s*\(|for\s+.*in\s+.*:', line_str):
                context_prev = "\n".join(lines[max(0, idx - chunk.start_line - 4):max(0, idx - chunk.start_line)])
                if re.search(r'for\s*\(|for\s+.*in\s+.*:', context_prev):
                    findings.append({
                        "agent": "performance",
                        "file_path": chunk.file_path,
                        "line_start": idx,
                        "line_end": idx,
                        "severity": "medium",
                        "complexity_estimate": "O(n^2)",
                        "description": "Nested loop iteration detected. Polynomial time complexity O(N^2) or O(M*N) can cause high CPU utilization on large inputs.",
                        "suggested_fix": "Optimize using Hash Map / Hash Set lookups or 1D space optimization to reduce complexity to O(N)."
                    })

            # 3. 2D DP Matrix Allocation O(M * N) Memory Overhead
            if re.search(r'vector\s*<\s*vector\s*<|new\s+\w+\[\s*\]\[\s*\]|\.map\(.*\.map\(', line_str):
                findings.append({
                    "agent": "performance",
                    "file_path": chunk.file_path,
                    "line_start": idx,
                    "line_end": idx,
                    "severity": "low",
                    "complexity_estimate": "O(M * N) Space",
                    "description": "2D Matrix allocation detected. Quadratic memory allocation space O(M * N).",
                    "suggested_fix": "Consider 1D rolling array space optimization to reduce memory overhead to O(N)."
                })

        return findings
