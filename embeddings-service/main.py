from fastapi import FastAPI
from sentence_transformers import SentenceTransformer
from pydantic import BaseModel
import logging

app = FastAPI()
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

class EmbeddingRequest(BaseModel):
    text: str

def split_text(text: str, max_length: int = 256) -> list[str]:
    words = text.split()
    chunks = []
    current_chunk = []
    current_length = 0
    
    for word in words:
        if current_length + len(word) + 1 > max_length:
            chunks.append(" ".join(current_chunk))
            current_chunk = []
            current_length = 0
        current_chunk.append(word)
        current_length += len(word) + 1
    
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    return chunks

@app.post("/embeddings")
async def get_embeddings(request: EmbeddingRequest):
    try:
        chunks = split_text(request.text)
        embeddings = model.encode(chunks).tolist()
        return {"embeddings": embeddings}
    except Exception as e:
        logging.error(e)
        return {"error": str(e)}
