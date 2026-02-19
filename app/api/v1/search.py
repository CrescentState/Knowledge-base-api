from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.vector import VectorService

router = APIRouter(prefix="/search", tags=["search"])
vector_db = VectorService()


class SearchQuery(BaseModel):
    query: str
    limit: int = 3


@router.post("/")
async def search_knowledge_base(payload: SearchQuery) -> dict[str, Any]:
    """Searches the vector database for relevant document snippets."""
    if not payload.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    results = await vector_db.query(payload.query, n_results=payload.limit)
    return {"results": results}
