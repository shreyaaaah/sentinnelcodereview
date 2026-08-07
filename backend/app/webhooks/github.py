from fastapi import APIRouter, Request, Header, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.services.github_client import GitHubAppClient
from app.services.review_pipeline import ReviewPipeline

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])
github_client = GitHubAppClient()

SAMPLE_PR_DIFF = """diff --git a/backend/app/services/payment_processor.py b/backend/app/services/payment_processor.py
index a1b2c3d..e5f6g7h 100644
--- a/backend/app/services/payment_processor.py
+++ b/backend/app/services/payment_processor.py
@@ -40,6 +40,10 @@ def process_user_payment(user_id, amount, card_token):
     api_key = "sk_live_998877665544332211"
     query = "SELECT * FROM accounts WHERE id = " + str(user_id)
     db.execute(query)
+    for item in user_items:
+        db.query("SELECT * FROM inventory WHERE id = " + str(item.id))
+    eval("process_hook(" + card_token + ")")
+    return True
"""

@router.post("/github")
async def handle_github_webhook(
    request: Request,
    x_hub_signature_256: str = Header(None),
    x_github_event: str = Header("pull_request"),
    db: AsyncSession = Depends(get_db)
):
    body_bytes = await request.body()

    if x_hub_signature_256 and not github_client.verify_webhook_signature(body_bytes, x_hub_signature_256):
        raise HTTPException(status_code=401, detail="Invalid GitHub webhook signature")

    payload = await request.json() if body_bytes else {}

    if x_github_event == "pull_request":
        action = payload.get("action", "opened")
        if action in ["opened", "synchronize", "reopened"]:
            pr_data = payload.get("pull_request", {})
            repo_data = payload.get("repository", {})

            repo_name = repo_data.get("full_name", "sentinel-demo/payment-gateway")
            pr_number = pr_data.get("number", 101)
            title = pr_data.get("title", "Update payment processing logic")
            author = pr_data.get("user", {}).get("login", "dev-user")
            diff_url = pr_data.get("diff_url")

            # Execute pipeline
            pipeline = ReviewPipeline(db)
            result = await pipeline.execute_review(
                repo_name=repo_name,
                pr_number=pr_number,
                title=title,
                author=author,
                diff_text=SAMPLE_PR_DIFF
            )

            return {
                "status": "success",
                "action": action,
                "review_summary": result
            }

    return {"status": "ignored", "event": x_github_event}
