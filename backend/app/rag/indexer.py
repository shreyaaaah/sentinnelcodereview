import os
import math
import re
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.models import ReviewEmbedding

class RAGIndexer:
    """
    Indexes repository style guides, CONTRIBUTING.md files, and past PR review comments
    for similarity retrieval during agent reviews.
    """
    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def index_content(self, pr_id: int, content: str) -> ReviewEmbedding:
        # Simple vector generation (dimension 1536)
        vector = self._generate_simple_embedding(content)
        embedding_obj = ReviewEmbedding(
            pr_id=pr_id,
            content=content,
            embedding=vector
        )
        self.db.add(embedding_obj)
        await self.db.commit()
        await self.db.refresh(embedding_obj)
        return embedding_obj

    def _generate_simple_embedding(self, text: str) -> List[float]:
        # Generates a normalized 1536-dimensional pseudo-embedding vector from text features
        words = re.findall(r'\w+', text.lower())
        vec = [0.0] * 1536
        for w in words:
            h = hash(w) % 1536
            vec[h] += 1.0
        
        norm = math.sqrt(sum(x * x for x in vec)) or 1.0
        return [x / norm for x in vec]
