from dotenv import load_dotenv
import os

load_dotenv()

SEARXNG_PORT = int(os.getenv("SEARXNG_PORT", "4000"))
API_PORT = int(os.getenv("API_PORT", "4001"))
CACHE_TTL = int(os.getenv("CACHE_TTL", "300"))
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "10000"))
SEARXNG_DATA_DIR = os.getenv("SEARXNG_DATA_DIR", "./searxng_data")
SEARXNG_URL = f"http://127.0.0.1:{SEARXNG_PORT}"