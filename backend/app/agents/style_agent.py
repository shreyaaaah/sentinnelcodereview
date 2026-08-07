import os
import re
from typing import List, Dict, Any, Optional
from app.ingestion.chunker import CodeChunk
from app.agents.llm_client import LLMClient

SYSTEM_PROMPT_STYLE = """You are a style-focused code reviewer. Analyze code for naming conventions, docstring/comment coverage, function length, dead code, and adherence to project style guides. Severity must be capped at medium. Return only valid JSON matching the specified schema."""

class StyleAgent:
    """
    Style Agent evaluating naming conventions, docstrings, function length,
    and style guide compliance. Severity is capped at 'medium'.
    """
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY") or os.getenv("OPENAI_API_KEY")
        self.llm_client = LLMClient()

    async def analyze(self, chunk: CodeChunk, rag_context: List[str] = []) -> List[Dict[str, Any]]:
        llm_findings = await self.llm_client.invoke_agent_llm(
            agent_type="style",
            system_prompt=SYSTEM_PROMPT_STYLE,
            code_chunk=chunk.code,
            file_path=chunk.file_path,
            start_line=chunk.start_line,
            rag_context=rag_context
        )

        if llm_findings is not None:
            # Enforce max medium severity rule for style issues
            for f in llm_findings:
                if f.get("severity") == "critical" or f.get("severity") == "high":
                    f["severity"] = "medium"
            return llm_findings

        return self._heuristic_style_scan(chunk)

    def _heuristic_style_scan(self, chunk: CodeChunk) -> List[Dict[str, Any]]:
        findings = []
        lines = chunk.code.splitlines()

        # Check function length
        if len(lines) > 50:
            findings.append({
                "agent": "style",
                "file_path": chunk.file_path,
                "line_start": chunk.start_line,
                "line_end": chunk.end_line,
                "severity": "medium",
                "description": f"Function '{chunk.name}' is excessively long ({len(lines)} lines). Long functions are harder to maintain and test.",
                "suggested_fix": "Refactor logic into smaller, single-responsibility helper functions."
            })

        for idx, line in enumerate(lines, start=chunk.start_line):
            line_str = line.strip()

            # Non-standard function or variable naming
            if re.search(r'def\s+[A-Z][a-zA-Z0-9]+', line_str): # CamelCase python function
                findings.append({
                    "agent": "style",
                    "file_path": chunk.file_path,
                    "line_start": idx,
                    "line_end": idx,
                    "severity": "low",
                    "description": "CamelCase function naming violates PEP 8 conventions. Python functions should use snake_case.",
                    "suggested_fix": "Rename function using snake_case (e.g., process_data instead of ProcessData)."
                })

            # Missing docstrings on public function
            if re.search(r'def\s+[a-z_][a-z0-9_]*\s*\(', line_str) and not line_str.startswith("def _"):
                next_line = lines[idx - chunk.start_line + 1].strip() if (idx - chunk.start_line + 1) < len(lines) else ""
                if not (next_line.startswith('"""') or next_line.startswith("'''")):
                    findings.append({
                        "agent": "style",
                        "file_path": chunk.file_path,
                        "line_start": idx,
                        "line_end": idx,
                        "severity": "low",
                        "description": "Public function is missing a docstring explaining parameters and return types.",
                        "suggested_fix": "Add a descriptive docstring adhering to standard format."
                    })

        return findings
