import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.models import Repository, PullRequest, Finding, FileRiskHistory
from app.agents.orchestrator import ReviewOrchestrator
from app.rag.retriever import RAGRetriever
from app.ingestion.diff_parser import parse_unified_diff

class ReviewPipeline:
    """
    Core pipeline orchestrating database persistence, RAG context retrieval,
    agent execution, and result saving.
    """
    def __init__(self, db: AsyncSession):
        self.db = db

    async def execute_review(
        self,
        repo_name: str,
        pr_number: int,
        title: str,
        author: str,
        diff_text: str,
        github_repo_id: Optional[int] = None
    ) -> Dict[str, Any]:
        # 1. Fetch or create repository record
        stmt = select(Repository).where(Repository.full_name == repo_name)
        res = await self.db.execute(stmt)
        repo = res.scalars().first()

        if not repo:
            repo = Repository(
                full_name=repo_name,
                github_repo_id=github_repo_id or hash(repo_name) % 1000000
            )
            self.db.add(repo)
            await self.db.commit()
            await self.db.refresh(repo)

        # 2. Fetch or create PullRequest record
        stmt_pr = select(PullRequest).where(
            PullRequest.repo_id == repo.id,
            PullRequest.pr_number == pr_number
        )
        res_pr = await self.db.execute(stmt_pr)
        pr = res_pr.scalars().first()

        if not pr:
            pr = PullRequest(
                repo_id=repo.id,
                pr_number=pr_number,
                title=title,
                author=author,
                status="open"
            )
            self.db.add(pr)
            await self.db.commit()
            await self.db.refresh(pr)

        # 3. Retrieve RAG context
        retriever = RAGRetriever(self.db)
        rag_context = await retriever.retrieve_context(diff_text)

        # 4. Execute Multi-Agent Orchestrator
        orchestrator = ReviewOrchestrator(repo_path=".")
        review_result = await orchestrator.run_pipeline(diff_text, rag_context)

        overall_score = review_result["overall_risk_score"]
        findings_data = review_result["findings"]
        risk_findings_data = review_result["risk_findings"]

        # Update PR overall risk score
        pr.overall_risk_score = overall_score

        # 5. Persist Findings
        for f in findings_data:
            finding_obj = Finding(
                pr_id=pr.id,
                agent=f.get("agent", "static"),
                file_path=f["file_path"],
                line_start=f.get("line_start", 1),
                line_end=f.get("line_end", 1),
                severity=f.get("severity", "low"),
                cvss_score=f.get("cvss_score"),
                cvss_vector=f.get("cvss_vector"),
                complexity_estimate=f.get("complexity_estimate"),
                description=f["description"],
                suggested_fix=f.get("suggested_fix")
            )
            self.db.add(finding_obj)

        # 6. Update File Risk History
        for r in risk_findings_data:
            stmt_risk = select(FileRiskHistory).where(
                FileRiskHistory.repo_id == repo.id,
                FileRiskHistory.file_path == r["file_path"]
            )
            res_risk = await self.db.execute(stmt_risk)
            frh = res_risk.scalars().first()

            if not frh:
                frh = FileRiskHistory(
                    repo_id=repo.id,
                    file_path=r["file_path"],
                    churn_count=r["churn_count"],
                    bugfix_commit_count=r["bugfix_count"],
                    bug_proneness_score=r["bug_proneness_score"]
                )
                self.db.add(frh)
            else:
                frh.churn_count = r["churn_count"]
                frh.bugfix_commit_count = r["bugfix_count"]
                frh.bug_proneness_score = r["bug_proneness_score"]

        await self.db.commit()
        await self.db.refresh(pr)

        try:
            file_diffs = parse_unified_diff(diff_text)
            parsed_files = [fd.filename for fd in file_diffs if fd.filename]
        except Exception:
            parsed_files = []

        scanned_files = list(set(f.get("file_path") for f in (findings_data + risk_findings_data)))
        primary_file = parsed_files[0] if parsed_files else (scanned_files[0] if scanned_files else "repository_source.py")

        return {
            "pr_id": pr.id,
            "repo_id": repo.id,
            "pr_number": pr_number,
            "scanned_file_path": primary_file,
            "scanned_files": scanned_files,
            "diff_text": diff_text,
            "overall_risk_score": overall_score,
            "findings_count": len(findings_data),
            "findings": findings_data,
            "risk_findings": risk_findings_data
        }
