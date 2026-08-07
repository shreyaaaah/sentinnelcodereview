import pytest
import asyncio
from app.ingestion.diff_parser import parse_unified_diff
from app.ingestion.chunker import SemanticChunker, CodeChunk
from app.git_mining.blame_analyzer import GitBlameAnalyzer
from app.agents.security_agent import SecurityAgent
from app.agents.orchestrator import ReviewOrchestrator

SAMPLE_DIFF = """diff --git a/backend/app/auth.py b/backend/app/auth.py
index 1111111..2222222 100644
--- a/backend/app/auth.py
+++ b/backend/app/auth.py
@@ -10,6 +10,10 @@ def authenticate_user(username, password):
     secret = "sk_live_1234567890abcdef"
     sql = f"SELECT * FROM users WHERE name = '{username}'"
     db.execute(sql)
+    for item in user_roles:
+        db.execute(f"SELECT * FROM roles WHERE id = {item.id}")
+    eval(password)
+    return True
"""

def test_diff_parser():
    file_diffs = parse_unified_diff(SAMPLE_DIFF)
    assert len(file_diffs) == 1
    fd = file_diffs[0]
    assert fd.filename == "backend/app/auth.py"
    ranges = fd.get_changed_line_ranges()
    assert len(ranges) > 0

def test_semantic_chunker_token_reduction():
    file_diffs = parse_unified_diff(SAMPLE_DIFF)
    chunker = SemanticChunker()
    chunks = chunker.chunk_file_diff(file_diffs[0])
    
    full_files = {"backend/app/auth.py": "def large_file():\n" + ("    pass\n" * 500)}
    stats = chunker.calculate_reduction_stats(full_files, chunks)
    
    assert stats["reduction_percentage"] >= 90.0

def test_risk_agent_scoring():
    analyzer = GitBlameAnalyzer(".")
    score = analyzer.compute_bug_proneness_score(churn_count=30, bugfix_count=6, last_incident_date=None)
    assert score >= 75.0

def test_security_agent_recall():
    async def _test():
        agent = SecurityAgent()
        chunk = CodeChunk(
            file_path="auth.py",
            name="authenticate_user",
            chunk_type="function",
            code="secret = 'sk_live_1234567890abcdef'\nsql = 'SELECT * FROM users WHERE name = ' + user_input\neval(user_input)",
            start_line=10,
            end_line=13
        )
        findings = await agent.analyze(chunk)
        agents_found = [f["agent"] for f in findings]
        assert "security" in agents_found
        assert any(f["severity"] in ["high", "critical"] for f in findings)
    asyncio.run(_test())

def test_orchestrator_pipeline():
    async def _test():
        orchestrator = ReviewOrchestrator(repo_path=".")
        result = await orchestrator.run_pipeline(SAMPLE_DIFF)
        
        assert "overall_risk_score" in result
        assert "findings" in result
        assert result["overall_risk_score"] > 0
    asyncio.run(_test())
