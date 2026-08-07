import math
import re
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.models import ReviewEmbedding

class RAGRetriever:
    """
    Retrieves relevant style guides, architecture notes, and past PR review comments
    using cosine similarity search over stored embeddings.
    """
    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def retrieve_context(self, query_text: str, limit: int = 3) -> List[str]:
        stmt = select(ReviewEmbedding)
        result = await self.db.execute(stmt)
        all_embeddings = result.scalars().all()

        if not all_embeddings:
            return [
                "Repository Style Guide: Follow PEP8 / Standard guidelines. Ensure parameterized SQL queries to prevent injection.",
                "Performance Guideline: Avoid N+1 database queries in loop iterations. Use join fetches."
            ]

        query_vec = self._generate_query_vector(query_text)

        scored = []
        for emb in all_embeddings:
            if not emb.embedding:
                continue
            sim = self._cosine_similarity(query_vec, emb.embedding)
            scored.append((sim, emb.content))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in scored[:limit]]

    def _generate_query_vector(self, text: str) -> List[float]:
        words = re.findall(r'\w+', text.lower())
        vec = [0.0] * 1536
        for w in words:
            h = hash(w) % 1536
            vec[h] += 1.0
        norm = math.sqrt(sum(x * x for x in vec)) or 1.0
        return [x / norm for x in vec]

    def _cosine_similarity(self, vec_a: List[float], vec_b: List[float]) -> float:
        if len(vec_a) != len(vec_b):
            return 0.0
        dot = sum(a * b for a, b in zip(vec_a, vec_b))
        return dot
