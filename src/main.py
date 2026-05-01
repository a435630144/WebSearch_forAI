import os
import sys
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from services.searxng import searxng_service
from config.settings import API_PORT

@asynccontextmanager
async def lifespan(app: FastAPI):
    searxng_dir = os.path.join(os.path.dirname(__file__), "..", "searxng")
    if not os.path.exists(searxng_dir):
        raise RuntimeError("searxng directory not found")

    print("Starting SearXNG...")
    if not searxng_service.start(searxng_dir):
        raise RuntimeError("Failed to start SearXNG")
    print("SearXNG started successfully")

    yield

    print("Stopping SearXNG...")
    searxng_service.stop()

app = FastAPI(title="WebSearch Backend", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

from routes.search import router as search_router
app.include_router(search_router)

@app.get("/health")
async def health():
    searxng_ok = searxng_service.is_healthy()
    return {
        "status": "ok",
        "searxng": "running" if searxng_ok else "stopped"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=API_PORT)
