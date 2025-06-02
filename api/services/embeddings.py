import requests
import os

EMBEDDINGS_SERVICE_URL = os.getenv("EMBEDDINGS_SERVICE_URL")

def get_embeddings(text: str) -> list[list[float]]:
    response = requests.post(
        f"{EMBEDDINGS_SERVICE_URL}/embeddings",
        json={"text": text}
    )
    return response.json()["embeddings"]
