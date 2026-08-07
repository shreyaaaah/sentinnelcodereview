import os
import json
import re
from typing import List, Dict, Any, Optional
from app.ingestion.chunker import CodeChunk
from app.agents.llm_client import LLMClient

SYSTEM_PROMPT_SECURITY = """You are a security-focused code reviewer. Analyze the given code diff for OWASP Top 10 vulnerabilities, hardcoded secrets/credentials, SQL/Command injection risks, XSS, and insecure deserialization. For each finding, output a CVSS 3.1 score and vector string, exact line numbers, and a concrete fix. Do not flag stylistic issues. Return only valid JSON matching the specified schema."""

class SecurityAgent:
    """
    Security Agent focusing on OWASP Top 10 vulnerabilities, hardcoded secrets,
    SQL/Command injection, XSS, and insecure deserialization.
    Outputs structured CVSS 3.1 scores and vector strings.
    """
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY") or os.getenv("OPENAI_API_KEY")
        self.llm_client = LLMClient()

    async def analyze(self, chunk: CodeChunk, rag_context: List[str] = []) -> List[Dict[str, Any]]:
        # 1. Try Live LLM (Claude Sonnet / GPT-4o)
        llm_findings = await self.llm_client.invoke_agent_llm(
            agent_type="security",
            system_prompt=SYSTEM_PROMPT_SECURITY,
            code_chunk=chunk.code,
            file_path=chunk.file_path,
            start_line=chunk.start_line,
            rag_context=rag_context
        )

        if llm_findings is not None:
            return llm_findings

        # 2. Fallback to heuristic scan if no LLM key is set
        return self._heuristic_security_scan(chunk)

    def _heuristic_security_scan(self, chunk: CodeChunk) -> List[Dict[str, Any]]:
        findings = []
        lines = chunk.code.splitlines()

        for idx, line in enumerate(lines, start=chunk.start_line):
            line_str = line.strip()

            # 1. Hardcoded API Keys / Secrets / Tokens
            if re.search(r'(api_key|secret|password|token|private_key|auth_token)\s*[:=]\s*["\'][A-Za-z0-9_\-]{8,}["\']', line_str, re.IGNORECASE) or \
               re.search(r'(sk_live_|ghp_|ak_live_|secret_)[A-Za-z0-9_\-]{10,}', line_str):
                findings.append({
                    "agent": "security",
                    "file_path": chunk.file_path,
                    "line_start": idx,
                    "line_end": idx,
                    "severity": "critical",
                    "cvss_score": 9.8,
                    "cvss_vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
                    "description": "Hardcoded secret or authentication credential exposed in source code.",
                    "suggested_fix": "Extract credential to environment variables (e.g. process.env.API_KEY or os.getenv('API_KEY'))."
                })

            # 2. XSS & Insecure DOM Rendering (React/Next.js)
            if re.search(r'dangerouslySetInnerHTML\s*=|innerHTML\s*=', line_str):
                findings.append({
                    "agent": "security",
                    "file_path": chunk.file_path,
                    "line_start": idx,
                    "line_end": idx,
                    "severity": "high",
                    "cvss_score": 7.5,
                    "cvss_vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N",
                    "description": "Cross-Site Scripting (XSS) vulnerability detected via raw innerHTML injection.",
                    "suggested_fix": "Sanitize HTML using DOMPurify before rendering or use safe JSX interpolation."
                })

            # 3. Wildcard CORS Misconfiguration
            if re.search(r'Access-Control-Allow-Origin.*\*|cors\(\s*\{\s*origin:\s*["\']\*["\']', line_str, re.IGNORECASE):
                findings.append({
                    "agent": "security",
                    "file_path": chunk.file_path,
                    "line_start": idx,
                    "line_end": idx,
                    "severity": "medium",
                    "cvss_score": 6.5,
                    "cvss_vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N",
                    "description": "Wildcard CORS policy allows unrestricted cross-origin requests from untrusted domains.",
                    "suggested_fix": "Restrict CORS origin header to explicit trusted domain origins."
                })

            # 4. SQL / Database Query Injection
            if re.search(r'(SELECT|INSERT|UPDATE|DELETE|find|query).*\+.*(req|params|input|user|var|id)', line_str, re.IGNORECASE) or \
               re.search(r'execute\s*\(\s*f["\'].*SELECT', line_str, re.IGNORECASE):
                findings.append({
                    "agent": "security",
                    "file_path": chunk.file_path,
                    "line_start": idx,
                    "line_end": idx,
                    "severity": "high",
                    "cvss_score": 8.6,
                    "cvss_vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N",
                    "description": "Potential SQL / Query Injection flaw. Dynamic string concatenation allows query tampering.",
                    "suggested_fix": "Use parameterized query placeholders or ORM bind variables."
                })

            # 5. Unsafe Code Execution
            if re.search(r'(eval|exec|os\.system|subprocess\.Popen)\s*\([^)]*\+', line_str):
                findings.append({
                    "agent": "security",
                    "file_path": chunk.file_path,
                    "line_start": idx,
                    "line_end": idx,
                    "severity": "critical",
                    "cvss_score": 9.8,
                    "cvss_vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
                    "description": "Unsafe code evaluation or system execution flaw.",
                    "suggested_fix": "Eliminate eval/exec calls and use safe functional abstractions."
                })

        return findings
