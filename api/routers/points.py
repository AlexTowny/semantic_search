from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services import qdrant, embeddings
from typing import Optional


router = APIRouter()

class PointCreate(BaseModel):
    collection: str
    text: str
    link: str
    name: Optional[str] = None
    description: Optional[str] = None

class DeleteRequest(BaseModel):
    collection: str
    name: str
    payload_key: str = "name"

@router.post("/points/")
async def create_point(point: PointCreate):
    try:


        vectors = embeddings.get_embeddings(point.text)
        points = [
            {
               
                "vector":vec ,
                "payload": {
                    "link": point.link,
                    "name": point.name,
                    "description": point.description
                }
            } for vec in vectors
        ]
        
        qdrant.upsert_points(point.collection, points)
        return {"status": "created"}
    except Exception as e:
        raise HTTPException(400, str(e) )

@router.get("/points/{collection}/{point_id}")
async def get_point_by_id(collection: str, point_id: int):
    point = qdrant.get_point(collection, point_id)
    if not point:
        raise HTTPException(status_code=404, detail="Point not found")
    return point

@router.delete("/points/")
async def delete_point_by_key(request: DeleteRequest):
    try:
        qdrant.delete_points_by_name(request.collection, request.name, request.payload_key)
        return {"status": "deleted"}
    except ValueError as e:  
        raise HTTPException(404, detail=str(e))
    except Exception as e:
        raise HTTPException(500, detail=str(e))


@router.delete("/points/{collection}/{point_id}")
async def delete_point_by_id(collection: str, point_id: int):
    try:
        qdrant.delete_points(collection, [point_id])
        return {"status": "deleted"}
    except ValueError as e:  
        raise HTTPException(404, detail=str(e))
    except Exception as e:
        raise HTTPException(500, detail=str(e))