import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, UniqueConstraint, JSON
from sqlalchemy.orm import relationship
from app.db.database import Base

class Repository(Base):
    __tablename__ = "repositories"

    id = Column(Integer, primary_key=True, index=True)
    github_repo_id = Column(Integer, unique=True, nullable=True, index=True)
    full_name = Column(String, unique=True, index=True)
    installed_at = Column(DateTime, default=datetime.datetime.utcnow)

    pull_requests = relationship("PullRequest", back_populates="repository", cascade="all, delete-orphan")
    file_risks = relationship("FileRiskHistory", back_populates="repository", cascade="all, delete-orphan")

class PullRequest(Base):
    __tablename__ = "pull_requests"

    id = Column(Integer, primary_key=True, index=True)
    repo_id = Column(Integer, ForeignKey("repositories.id"), nullable=False)
    pr_number = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    status = Column(String, default="open") # open / merged / closed
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    overall_risk_score = Column(Float, default=0.0) # 0-100 score
    created_at_db = Column(DateTime, default=datetime.datetime.utcnow)

    repository = relationship("Repository", back_populates="pull_requests")
    findings = relationship("Finding", back_populates="pull_request", cascade="all, delete-orphan")
    embeddings = relationship("ReviewEmbedding", back_populates="pull_request", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint('repo_id', 'pr_number', name='_repo_pr_uc'),
    )

class Finding(Base):
    __tablename__ = "findings"

    id = Column(Integer, primary_key=True, index=True)
    pr_id = Column(Integer, ForeignKey("pull_requests.id"), nullable=False)
    agent = Column(String, nullable=False) # security / performance / style / risk
    file_path = Column(String, nullable=False)
    line_start = Column(Integer, default=1)
    line_end = Column(Integer, default=1)
    severity = Column(String, default="low") # low / medium / high / critical
    cvss_score = Column(Float, nullable=True) # security only
    cvss_vector = Column(String, nullable=True) # security only e.g. CVSS:3.1/...
    complexity_estimate = Column(String, nullable=True) # perf only e.g. "O(n^2)"
    description = Column(Text, nullable=False)
    suggested_fix = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    pull_request = relationship("PullRequest", back_populates="findings")

class FileRiskHistory(Base):
    __tablename__ = "file_risk_history"

    id = Column(Integer, primary_key=True, index=True)
    repo_id = Column(Integer, ForeignKey("repositories.id"), nullable=False)
    file_path = Column(String, nullable=False)
    churn_count = Column(Integer, default=0) # number of commits touching file
    bugfix_commit_count = Column(Integer, default=0) # bugfix commit count matching regex
    last_incident_date = Column(DateTime, nullable=True)
    bug_proneness_score = Column(Float, default=0.0) # 0-100 composite score
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    repository = relationship("Repository", back_populates="file_risks")

    __table_args__ = (
        UniqueConstraint('repo_id', 'file_path', name='_repo_file_uc'),
    )

class ReviewEmbedding(Base):
    __tablename__ = "review_embeddings"

    id = Column(Integer, primary_key=True, index=True)
    pr_id = Column(Integer, ForeignKey("pull_requests.id"), nullable=False)
    content = Column(Text, nullable=False)
    embedding = Column(JSON, nullable=True) # Vector stored as JSON float array for compatibility

    pull_request = relationship("PullRequest", back_populates="embeddings")
