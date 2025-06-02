from fastapi import APIRouter, HTTPException
from services import qdrant, embeddings
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

class SearchQuery(BaseModel):
    collection: str 
    query: str
    limit: int = 10
    negative: Optional[str] = None  
    distinct: bool

@router.post("/search/")
async def search(query: SearchQuery):
    try:
        vector = embeddings.get_embeddings(query.query)[0]

        if query.negative is None:
            results = qdrant.search_points(
                collection=query.collection, 
                vector=vector, 
                distinct=query.distinct,
                limit=query.limit
                )
        else:
            negative_vector = embeddings.get_embeddings(query.negative)[0]
            results = qdrant.recommend_points(
                query.collection,
                positive_vector=[vector],
                negative_vector=[negative_vector],
                distinct=query.distinct,
                limit=query.limit
            )
        
        return results
    except Exception as e:
        raise HTTPException(400, str(e))

