import asyncio
import json
from app.db.database import AsyncSessionLocal, init_db
from app.services.review_pipeline import ReviewPipeline

SAMPLE_CLI_DIFF = """diff --git a/auth_service.py b/auth_service.py
index a1b2c3d..e5f6g7h 100644
--- a/auth_service.py
+++ b/auth_service.py
@@ -12,6 +12,12 @@ def verify_user_access(token, user_input):
     secret_jwt_key = "super_secret_jwt_key_12345"
     query = f"SELECT * FROM users WHERE username = '{user_input}'"
     db.execute(query)
+    for user in user_list:
+        db.execute(f"SELECT * FROM permissions WHERE user_id = {user.id}")
+    eval(user_input)
+    return True
"""

async def run_cli_demo():
    await init_db()
    async with AsyncSessionLocal() as session:
        pipeline = ReviewPipeline(session)
        print("\n=======================================================")
        print("  SentinelReview — Multi-Agent Code Review CLI Engine")
        print("=======================================================\n")
        print("Running security, performance, style, and git-history risk triage...\n")

        res = await pipeline.execute_review(
            repo_name="sentinel-demo/payment-gateway",
            pr_number=102,
            title="Update auth verification and permissions check",
            author="dev-alice",
            diff_text=SAMPLE_CLI_DIFF
        )

        print("Review Complete!")
        print(f"Overall PR Risk Score: {res['overall_risk_score']}/100")
        print(f"Total Findings Detected: {res['findings_count']}\n")

        print("--- STATIC & RISK FINDINGS ---")
        for idx, f in enumerate(res["findings"], 1):
            print(f"[{idx}] [{f['severity'].upper()}] Agent: {f['agent'].upper()} | File: {f['file_path']}:L{f['line_start']}")
            print(f"    Description: {f['description']}")
            if f.get("cvss_score"):
                print(f"    CVSS 3.1: {f['cvss_score']} ({f.get('cvss_vector', '')})")
            if f.get("complexity_estimate"):
                print(f"    Complexity: {f['complexity_estimate']}")
            if f.get("suggested_fix"):
                print(f"    Suggested Fix: {f['suggested_fix']}")
            print()

if __name__ == "__main__":
    asyncio.run(run_cli_demo())
