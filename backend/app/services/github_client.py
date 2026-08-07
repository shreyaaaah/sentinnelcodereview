import os
import hmac
import hashlib
import httpx
from typing import Dict, Any, List, Optional

class GitHubAppClient:
    """
    Client for GitHub REST & GraphQL API integrations using GitHub App installation tokens.
    Handles posting line-anchored inline PR comments, GitHub Check Runs, and PR summary markdown comments.
    """
    def __init__(self, app_id: Optional[str] = None, private_key: Optional[str] = None, webhook_secret: Optional[str] = None):
        self.app_id = app_id or os.getenv("GITHUB_APP_ID")
        self.private_key = private_key or os.getenv("GITHUB_APP_PRIVATE_KEY")
        self.webhook_secret = webhook_secret or os.getenv("GITHUB_WEBHOOK_SECRET")

    def verify_webhook_signature(self, payload_body: bytes, signature_header: str) -> bool:
        if not self.webhook_secret or not signature_header:
            return True # Allow testing when secret isn't set
        
        if not signature_header.startswith("sha256="):
            return False

        expected_hash = hmac.new(
            self.webhook_secret.encode('utf-8'),
            payload_body,
            hashlib.sha256
        ).hexdigest()

        incoming_hash = signature_header.split("sha256=")[1]
        return hmac.compare_digest(expected_hash, incoming_hash)

    async def post_inline_comment(self, repo_full_name: str, pr_number: int, commit_id: str, file_path: str, line: int, body: str, token: str):
        url = f"https://api.github.com/repos/{repo_full_name}/pulls/{pr_number}/comments"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        payload = {
            "body": body,
            "commit_id": commit_id,
            "path": file_path,
            "line": line,
            "side": "RIGHT"
        }
        async with httpx.AsyncClient() as client:
            await client.post(url, headers=headers, json=payload)

    async def create_check_run(self, repo_full_name: str, head_sha: str, name: str, status: str, conclusion: Optional[str], output: Dict[str, Any], token: str):
        url = f"https://api.github.com/repos/{repo_full_name}/check-runs"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        payload = {
            "name": name,
            "head_sha": head_sha,
            "status": status,
            "conclusion": conclusion,
            "output": output
        }
        async with httpx.AsyncClient() as client:
            await client.post(url, headers=headers, json=payload)

    async def post_pr_summary_comment(self, repo_full_name: str, pr_number: int, overall_score: float, findings: List[Dict[str, Any]], risk_findings: List[Dict[str, Any]], token: str):
        url = f"https://api.github.com/repos/{repo_full_name}/issues/{pr_number}/comments"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        status_emoji = "🚨" if overall_score >= 70 else "⚠️" if overall_score >= 40 else "✅"

        markdown_body = f"""### {status_emoji} SentinelReview AI Triage & Review Summary

**Overall PR Risk Score:** `{overall_score}/100`

#### 📊 Risk Agent Breakdown
| File | Bug-Proneness Score | Historical Churn | Bugfix Commits | Recommendation |
|---|---|---|---|---|
"""
        for r in risk_findings:
            markdown_body += f"| `{r['file_path']}` | **{r['bug_proneness_score']}** | {r['churn_count']} | {r['bugfix_count']} | {r['suggested_fix']} |\n"

        markdown_body += f"\n#### 🔍 Static Findings ({len(findings)} issues detected)\n"
        for f in findings:
            markdown_body += f"- **[{f['severity'].upper()}]** `{f['file_path']}:L{f['line_start']}` ({f['agent']}): {f['description']}\n"

        markdown_body += "\n---\n*Powered by SentinelReview Multi-Agent Triage Engine*"

        async with httpx.AsyncClient() as client:
            await client.post(url, headers=headers, json={"body": markdown_body})
