import os
import sys
from pathlib import Path

# Add project root (parent of src/) to path
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from services.searxng import searxng_service
from config.settings import API_PORT, SEARXNG_URL

@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"WebSearch Backend starting...")
    print(f"SearXNG URL: {SEARXNG_URL}")
    yield
    print("WebSearch Backend shutting down...")

app = FastAPI(title="WebSearch Backend", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

from routes.search import router as search_router
from middleware.error_handler import error_handler
from fastapi import HTTPException

app.include_router(search_router)
app.add_exception_handler(Exception, error_handler)
app.add_exception_handler(HTTPException, error_handler)

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
