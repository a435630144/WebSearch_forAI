from dotenv import load_dotenv
import os

load_dotenv()

SEARXNG_HOST = os.getenv("SEARXNG_HOST", "127.0.0.1")
SEARXNG_PORT = int(os.getenv("SEARXNG_PORT", "8080"))
API_PORT = int(os.getenv("API_PORT", "4001"))
CACHE_TTL = int(os.getenv("CACHE_TTL", "300"))
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "10000"))
SEARXNG_URL = f"http://{SEARXNG_HOST}:{SEARXNG_PORT}"