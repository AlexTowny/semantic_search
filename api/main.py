from fastapi import FastAPI
from routers import collections, points, search

app = FastAPI()
app.include_router(collections.router)
app.include_router(points.router)
app.include_router(search.router)
