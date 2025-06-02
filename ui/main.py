from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import httpx
import os
app = FastAPI()


app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

API_BASE_URL = os.getenv("API_BASE_URL")


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{API_BASE_URL}/collections/")
            collections = [item["name"] for item in response.json().get('collections', [])]

        except Exception as e:
            collections = []
    return templates.TemplateResponse("index.html", {"request": request, "collections": collections})

@app.post("/search")
async def search(
    collection: str = Form(...),
    query: str = Form(...),
    negative: str = Form(None),
    distinct: bool = Form(False)
):
    payload = {
        "collection": collection,
        "query": query,
        "negative": negative,
        "distinct": distinct
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{API_BASE_URL}/search/",
                json=payload
            )
            return response.json()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))