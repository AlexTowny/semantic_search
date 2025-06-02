from fastapi import APIRouter, HTTPException
from services import qdrant

router = APIRouter()

@router.post("/collections/")
async def create_collection(name: str):
    try:
        qdrant.create_collection(name)
        return {"status": "created"}
    except Exception as e:
        raise HTTPException(400, str(e))

@router.delete("/collections/{name}")
async def delete_collection(name: str):
    try:
        qdrant.delete_collection(name)
        return {"status": "deleted"}
    except Exception as e:
        raise HTTPException(400, str(e))

@router.get("/collections/")
async def list_collections():
    return qdrant.list_collections()


