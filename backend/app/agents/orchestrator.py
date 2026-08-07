import asyncio
from typing import List, Dict, Any, TypedDict, Optional
from app.ingestion.chunker import CodeChunk, SemanticChunker
from app.ingestion.diff_parser import parse_unified_diff
from app.agents.security_agent import SecurityAgent
from app.agents.performance_agent import PerformanceAgent
from app.agents.style_agent import StyleAgent
from app.agents.risk_agent import RiskAgent

SEVERITY_RANK = {
    "low": 1,
    "medium": 2,
    "high": 3,
    "critical": 4
}

RANK_TO_SEVERITY = {v: k for k, v in SEVERITY_RANK.items()}

class ReviewState(TypedDict):
    repo_path: str
    diff_text: str
    chunks: List[CodeChunk]
    rag_context: List[str]
    security_findings: List[Dict[str, Any]]
    performance_findings: List[Dict[str, Any]]
    style_findings: List[Dict[str, Any]]
    risk_findings: List[Dict[str, Any]]
    merged_findings: List[Dict[str, Any]]
    overall_risk_score: float

class ReviewOrchestrator:
    """
    LangGraph-based state machine orchestrating parallel multi-agent scans,
    finding deduplication, severity escalation based on file risk, and overall PR risk scoring.
    """
    def __init__(self, repo_path: str = "."):
        self.repo_path = repo_path
        self.security_agent = SecurityAgent()
        self.performance_agent = PerformanceAgent()
        self.style_agent = StyleAgent()
        self.risk_agent = RiskAgent(repo_path)

    async def run_pipeline(self, diff_text: str, rag_context: List[str] = []) -> Dict[str, Any]:
        # 1. Ingestion: Parse diff & chunk code
        file_diffs = parse_unified_diff(diff_text)
        chunker = SemanticChunker()
        all_chunks: List[CodeChunk] = []

        for fd in file_diffs:
            all_chunks.extend(chunker.chunk_file_diff(fd))

        changed_files = list(set(fd.filename for fd in file_diffs))

        # 2. Parallel Agent Execution
        sec_tasks = [self.security_agent.analyze(c, rag_context) for c in all_chunks]
        perf_tasks = [self.performance_agent.analyze(c, rag_context) for c in all_chunks]
        style_tasks = [self.style_agent.analyze(c, rag_context) for c in all_chunks]
        risk_tasks = [self.risk_agent.analyze_file_risk(f) for f in changed_files]

        sec_results, perf_results, style_results, risk_results = await asyncio.gather(
            asyncio.gather(*sec_tasks) if sec_tasks else asyncio.sleep(0, result=[]),
            asyncio.gather(*perf_tasks) if perf_tasks else asyncio.sleep(0, result=[]),
            asyncio.gather(*style_tasks) if style_tasks else asyncio.sleep(0, result=[]),
            asyncio.gather(*risk_tasks) if risk_tasks else asyncio.sleep(0, result=[])
        )

        flat_sec = [item for sublist in sec_results for item in sublist] if sec_tasks else []
        flat_perf = [item for sublist in perf_results for item in sublist] if perf_tasks else []
        flat_style = [item for sublist in style_results for item in sublist] if style_tasks else []
        flat_risk = risk_results if risk_tasks else []

        # Map file risk scores
        file_risk_map = {r["file_path"]: r["bug_proneness_score"] for r in flat_risk}

        # 3. Deduplication & Escalation
        all_findings = flat_sec + flat_perf + flat_style
        merged_findings = self._dedupe_and_escalate(all_findings, file_risk_map)

        # 4. Overall Risk Score Calculation
        overall_score = self._compute_overall_pr_risk(merged_findings, flat_risk)

        return {
            "findings": merged_findings,
            "risk_findings": flat_risk,
            "overall_risk_score": round(overall_score, 1),
            "total_chunks_scanned": len(all_chunks),
            "files_scanned": len(changed_files)
        }

    def _dedupe_and_escalate(self, findings: List[Dict[str, Any]], file_risk_map: Dict[str, float]) -> List[Dict[str, Any]]:
        deduped: Dict[str, Dict[str, Any]] = {}

        for f in findings:
            key = f"{f['file_path']}:{f['line_start']}:{f['agent']}"
            
            # Severity escalation based on Risk Agent bug-proneness score
            file_risk = file_risk_map.get(f['file_path'], 0.0)
            orig_sev = f["severity"]
            current_rank = SEVERITY_RANK.get(orig_sev, 1)

            if file_risk >= 75 and current_rank < 3: # Escalate to high/critical on high-risk files
                f["severity"] = "high"
                f["description"] += f" [Escalated from {orig_sev.upper()} due to high historical file risk ({file_risk}/100)]"
            elif file_risk >= 50 and current_rank < 2:
                f["severity"] = "medium"
                f["description"] += f" [Escalated from {orig_sev.upper()} due to moderate historical file risk ({file_risk}/100)]"

            if key not in deduped:
                deduped[key] = f
            else:
                # Keep higher severity finding if duplicated
                if SEVERITY_RANK.get(f["severity"], 1) > SEVERITY_RANK.get(deduped[key]["severity"], 1):
                    deduped[key] = f

        return list(deduped.values())

    def _compute_overall_pr_risk(self, findings: List[Dict[str, Any]], risk_findings: List[Dict[str, Any]]) -> float:
        # Realistic severity weights
        sev_weights = {"low": 4, "medium": 8, "high": 15, "critical": 25}
        finding_score = sum(sev_weights.get(f["severity"], 4) for f in findings)

        max_file_risk = max((r.get("bug_proneness_score", 0.0) for r in risk_findings), default=0.0)

        # Baseline score: 12.0 for clean code
        # Smooth scaling based on findings + historical churn (15% context)
        baseline = 12.0 if not findings else 15.0
        composite = baseline + finding_score + (max_file_risk * 0.15)

        # Cap between 12.0 and 96.0 for realistic scoring
        return min(96.0, max(12.0, round(composite, 1)))
