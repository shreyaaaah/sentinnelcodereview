import asyncio
import datetime
from app.db.database import AsyncSessionLocal, init_db
from app.models.models import Repository, PullRequest, Finding, FileRiskHistory

async def seed_data():
    await init_db()
    async with AsyncSessionLocal() as session:
        # Check if already seeded
        from sqlalchemy import select
        res = await session.execute(select(Repository))
        if res.scalars().first():
            print("Database already contains data. Skipping seed.")
            return

        print("Seeding database with realistic SentinelReview demo data...")

        # 1. Create Repository
        repo = Repository(
            github_repo_id=987654321,
            full_name="sentinel-demo/payment-gateway",
            installed_at=datetime.datetime.utcnow() - datetime.timedelta(days=90)
        )
        session.add(repo)
        await session.commit()
        await session.refresh(repo)

        # 2. Add File Risk History (Risk Agent mining metrics)
        risk_files = [
            ("backend/app/services/payment_processor.py", 38, 7, 88.5, datetime.timedelta(days=5)),
            ("backend/app/auth/jwt_verifier.py", 22, 4, 76.2, datetime.timedelta(days=14)),
            ("backend/app/db/session_manager.py", 15, 2, 54.0, datetime.timedelta(days=40)),
            ("backend/app/api/checkout.py", 29, 5, 81.0, datetime.timedelta(days=8)),
            ("backend/app/utils/helpers.py", 6, 0, 18.2, None),
            ("frontend/app/components/Header.tsx", 4, 0, 12.0, None),
        ]

        now = datetime.datetime.utcnow()

        for path, churn, bugfixes, score, incident_delta in risk_files:
            inc_date = now - incident_delta if incident_delta else None
            frh = FileRiskHistory(
                repo_id=repo.id,
                file_path=path,
                churn_count=churn,
                bugfix_commit_count=bugfixes,
                last_incident_date=inc_date,
                bug_proneness_score=score
            )
            session.add(frh)

        # 3. Create Sample Pull Requests
        prs = [
            (101, "Add payment retry logic and fast hashing", "dev-alice", "open", 79.5),
            (100, "Refactor session timeout middleware", "dev-bob", "merged", 25.0),
            (99, "Fix token expiration edge case", "dev-charlie", "merged", 64.0),
            (98, "Update dependencies and security patches", "dev-alice", "merged", 88.0),
        ]

        pr_objects = []
        for num, title, author, status, risk_score in prs:
            pr = PullRequest(
                repo_id=repo.id,
                pr_number=num,
                title=title,
                author=author,
                status=status,
                overall_risk_score=risk_score,
                created_at=now - datetime.timedelta(days=101 - num)
            )
            session.add(pr)
            pr_objects.append(pr)

        await session.commit()

        # 4. Add Findings for PR 101
        pr101 = pr_objects[0]
        findings_101 = [
            Finding(
                pr_id=pr101.id,
                agent="security",
                file_path="backend/app/services/payment_processor.py",
                line_start=42,
                line_end=42,
                severity="critical",
                cvss_score=9.8,
                cvss_vector="CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
                description="Hardcoded secret credential detected in source code. Exposure of credentials allows authentication bypass. [Escalated from CRITICAL due to high historical file risk (88.5/100)]",
                suggested_fix="Extract secret to an environment variable or secrets vault (e.g., os.getenv('PAYMENT_KEY'))."
            ),
            Finding(
                pr_id=pr101.id,
                agent="security",
                file_path="backend/app/services/payment_processor.py",
                line_start=43,
                line_end=43,
                severity="high",
                cvss_score=8.6,
                cvss_vector="CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N",
                description="Potential SQL Injection vulnerability. Raw string concatenation in query allows unauthorized SQL execution. [Escalated from HIGH due to high historical file risk (88.5/100)]",
                suggested_fix="Use parameterized queries (e.g. cursor.execute('SELECT * FROM accounts WHERE id = %s', (user_id,)))."
            ),
            Finding(
                pr_id=pr101.id,
                agent="performance",
                file_path="backend/app/services/payment_processor.py",
                line_start=45,
                line_end=48,
                severity="high",
                complexity_estimate="O(N) DB calls",
                description="Potential N+1 Database Query pattern inside loop iteration. Triggers individual database queries per item.",
                suggested_fix="Batch fetch required inventory items using SQL IN clause or eager join loading."
            ),
            Finding(
                pr_id=pr101.id,
                agent="style",
                file_path="backend/app/services/payment_processor.py",
                line_start=40,
                line_end=40,
                severity="low",
                description="Public function is missing a docstring explaining parameters and expected return values.",
                suggested_fix="Add standard docstring with parameter and return type annotations."
            ),
            Finding(
                pr_id=pr101.id,
                agent="risk",
                file_path="backend/app/services/payment_processor.py",
                line_start=1,
                line_end=1,
                severity="critical",
                description="Historical Risk Score: 88.5/100. 7 bugfix commits in recent history; touched in 38 commits.",
                suggested_fix="Escalate to mandatory senior reviewer. High bug recurrence area."
            )
        ]

        for f in findings_101:
            session.add(f)

        await session.commit()
        print("Successfully seeded SentinelReview demo dataset!")

if __name__ == "__main__":
    asyncio.run(seed_data())
