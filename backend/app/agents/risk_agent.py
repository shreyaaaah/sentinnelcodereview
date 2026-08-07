from typing import List, Dict, Any
from app.git_mining.blame_analyzer import GitBlameAnalyzer

class RiskAgent:
    """
    Risk Agent: Mines historical git churn and bugfix commits per file
    to compute a bug-proneness score independently of static code syntax.
    """
    def __init__(self, repo_path: str = "."):
        self.blame_analyzer = GitBlameAnalyzer(repo_path)

    async def analyze_file_risk(self, file_path: str) -> Dict[str, Any]:
        risk_data = self.blame_analyzer.analyze_file_history(file_path)

        score = risk_data["bug_proneness_score"]
        churn = risk_data["churn_count"]
        bugfixes = risk_data["bugfix_commit_count"]

        # Derive severity & recommendation based on score
        if score >= 75:
            severity = "critical"
            rec = "Escalate to mandatory senior reviewer. High bug recurrence area."
        elif score >= 50:
            severity = "high"
            rec = "Recommend thorough manual regression and unit testing."
        elif score >= 25:
            severity = "medium"
            rec = "Standard review recommended."
        else:
            severity = "low"
            rec = "Low risk file — standard review sufficient."

        rationale = f"{bugfixes} bugfix commits in recent history; touched in {churn} commits."

        return {
            "agent": "risk",
            "file_path": file_path,
            "line_start": 1,
            "line_end": 1,
            "bug_proneness_score": score,
            "severity": severity,
            "churn_count": churn,
            "bugfix_count": bugfixes,
            "description": f"Historical Risk Score: {score}/100. {rationale}",
            "suggested_fix": rec
        }
