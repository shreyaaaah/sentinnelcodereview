from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class RepositoryBase(BaseModel):
    full_name: str
    github_repo_id: Optional[int] = None

class RepositoryCreate(RepositoryBase):
    pass

class RepositoryResponse(RepositoryBase):
    id: int
    installed_at: datetime

    class Config:
        from_attributes = True

class FindingBase(BaseModel):
    agent: str
    file_path: str
    line_start: int = 1
    line_end: int = 1
    severity: str # low, medium, high, critical
    cvss_score: Optional[float] = None
    cvss_vector: Optional[str] = None
    complexity_estimate: Optional[str] = None
    description: str
    suggested_fix: Optional[str] = None

class FindingCreate(FindingBase):
    pr_id: int

class FindingResponse(FindingBase):
    id: int
    pr_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class PullRequestBase(BaseModel):
    pr_number: int
    title: str
    author: str
    status: str = "open"

class PullRequestCreate(PullRequestBase):
    repo_id: int

class PullRequestResponse(PullRequestBase):
    id: int
    repo_id: int
    created_at: datetime
    overall_risk_score: float
    findings: List[FindingResponse] = []

    class Config:
        from_attributes = True

class FileRiskHistoryBase(BaseModel):
    file_path: str
    churn_count: int
    bugfix_commit_count: int
    last_incident_date: Optional[datetime] = None
    bug_proneness_score: float

class FileRiskHistoryResponse(FileRiskHistoryBase):
    id: int
    repo_id: int
    updated_at: datetime

    class Config:
        from_attributes = True

class HeatmapCell(BaseModel):
    file_path: str
    time_bucket: str # e.g. "2026-W30"
    bug_proneness_score: float
    churn_count: int
    bugfix_count: int
    last_incident: Optional[str] = None

class HeatmapResponse(BaseModel):
    repo_id: int
    repo_name: str
    files: List[str]
    time_buckets: List[str]
    cells: List[HeatmapCell]

class TrendDataPoint(BaseModel):
    week: str
    low: int = 0
    medium: int = 0
    high: int = 0
    critical: int = 0
    avg_risk_score: float = 0.0

class QualityTrendsResponse(BaseModel):
    repo_id: int
    repo_name: str
    trends: List[TrendDataPoint]
    avg_time_to_merge_hours: float
    risk_vs_merge_time: List[Dict[str, Any]]

class DemoPRRequest(BaseModel):
    repo_name: str = "sentinel-demo/payment-gateway"
    pr_number: int = 101
    title: str = "Add payment retry logic and fast hashing"
    author: str = "dev-alice"
    diff_text: Optional[str] = None

class CodeScanRequest(BaseModel):
    code_text: str
    filename: Optional[str] = "payment_processor.py"
    language: Optional[str] = "python"
    repo_name: Optional[str] = "sentinel-demo/payment-gateway"

class GitHubRepoScanRequest(BaseModel):
    repo_url: str
    pr_number: Optional[int] = None


