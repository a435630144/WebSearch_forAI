# WebSearch Backend Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 创建 Python + FastAPI 后端，集成 SearXNG 子进程，为 AI 提供联网搜索能力

**Architecture:** FastAPI 应用 + SearXNG 子进程管理，模块化服务设计，内存缓存

**Tech Stack:** Python 3.10+, FastAPI, uvicorn, httpx, lxml, cachetools, python-dotenv

---

## 文件结构

```
WebSearch_forAI/
├── src/
│   ├── __init__.py
│   ├── main.py              # FastAPI 入口，启动时管理 SearXNG 子进程
│   ├── routes/
│   │   ├── __init__.py
│   │   └── search.py       # /api/search 路由
│   ├── services/
│   │   ├── __init__.py
│   │   ├── searxng.py      # SearXNG 子进程管理 + API 调用
│   │   ├── cache.py       # 内存缓存服务
│   │   ├── parser.py      # HTML 清洗、结构化
│   │   └── aggregator.py  # 整理模式逻辑
│   ├── middleware/
│   │   ├── __init__.py
│   │   └── error_handler.py
│   └── utils/
│       ├── __init__.py
│       └── detect_mode.py  # auto 模式判断
├── config/
│   ├── __init__.py
│   └── settings.py        # 配置管理
├── .env.example
├── requirements.txt
└── README.md
```

---

## Task 1: 项目初始化

**Files:**
- Create: `requirements.txt`
- Create: `.env.example`
- Create: `src/__init__.py`
- Create: `src/routes/__init__.py`
- Create: `src/services/__init__.py`
- Create: `src/middleware/__init__.py`
- Create: `src/utils/__init__.py`
- Create: `config/__init__.py`

- [ ] **Step 1: 创建 requirements.txt**

```txt
fastapi==0.111.0
uvicorn==0.30.0
httpx==0.27.0
lxml==5.2.2
cachetools==5.4.0
python-dotenv==1.0.1
```

- [ ] **Step 2: 创建 .env.example**

```env
SEARXNG_PORT=4000
API_PORT=4001
CACHE_TTL=300
REQUEST_TIMEOUT=10000
SEARXNG_DATA_DIR=./searxng_data
```

- [ ] **Step 3: 创建 config/settings.py**

```python
from dotenv import load_dotenv
import os

load_dotenv()

SEARXNG_PORT = int(os.getenv("SEARXNG_PORT", "4000"))
API_PORT = int(os.getenv("API_PORT", "4001"))
CACHE_TTL = int(os.getenv("CACHE_TTL", "300"))
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "10000"))
SEARXNG_DATA_DIR = os.getenv("SEARXNG_DATA_DIR", "./searxng_data")
SEARXNG_URL = f"http://127.0.0.1:{SEARXNG_PORT}"
```

- [ ] **Step 4: 安装依赖**

Run: `cd "D:\OneDrive\自学编程\claude code\WebSearch_forAI" && pip install -r requirements.txt`

- [ ] **Step 5: 提交**

```bash
git add requirements.txt .env.example src/__init__.py src/routes/__init__.py src/services/__init__.py src/middleware/__init__.py src/utils/__init__.py config/__init__.py config/settings.py
git commit -m "feat: project scaffold with Python/FastAPI base structure"
```

---

## Task 2: SearXNG Service（子进程管理）

**Files:**
- Create: `src/services/searxng.py`

- [ ] **Step 1: 创建 SearXNG 服务**

```python
import subprocess
import time
import httpx
import os
import signal
from threading import Thread
from config.settings import SEARXNG_PORT, SEARXNG_URL, REQUEST_TIMEOUT, SEARXNG_DATA_DIR

class SearXNGService:
    def __init__(self):
        self.process = None
        self.running = False

    def start(self, searxng_dir: str) -> bool:
        """启动 SearXNG 子进程"""
        if self.running:
            return True

        os.makedirs(SEARXNG_DATA_DIR, exist_ok=True)

        env = os.environ.copy()
        env.update({
            "SEARXNG_PORT": str(SEARXNG_PORT),
            "SEARXNG_BIND": f"127.0.0.1:{SEARXNG_PORT}",
            "SEARXNG_SECRET": "changeme-" + str(os.getpid()),
            "SEARXNG_INSTANCE_TYPE": "public",
            "SEARXNG_DATA_DIR": SEARXNG_DATA_DIR,
        })

        self.process = subprocess.Popen(
            ["python", "-m", "searxng", "webapp"],
            cwd=searxng_dir,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        if not self._wait_for_ready(timeout=60):
            self.stop()
            return False

        self.running = True
        return True

    def _wait_for_ready(self, timeout: int = 60) -> bool:
        """等待 SearXNG 就绪"""
        start = time.time()
        while time.time() - start < timeout:
            try:
                resp = httpx.get(f"{SEARXNG_URL}/health", timeout=2)
                if resp.status_code == 200:
                    return True
            except httpx.RequestError:
                pass
            time.sleep(1)
        return False

    def stop(self):
        """停止 SearXNG 子进程"""
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
            self.process = None
        self.running = False

    def search(self, query: str, num_results: int = 10, engines: list = None) -> list:
        """调用 SearXNG 搜索"""
        params = {
            "q": query,
            "format": "json",
            "categories": "general",
        }
        if engines:
            params["engines"] = ",".join(engines)

        resp = httpx.get(
            f"{SEARXNG_URL}/search",
            params=params,
            timeout=REQUEST_TIMEOUT / 1000
        )
        resp.raise_for_status()
        data = resp.json()
        return data.get("results", [])[:num_results]

    def is_healthy(self) -> bool:
        """检查 SearXNG 健康状态"""
        try:
            resp = httpx.get(f"{SEARXNG_URL}/health", timeout=2)
            return resp.status_code == 200
        except httpx.RequestError:
            return False

searxng_service = SearXNGService()
```

- [ ] **Step 2: 提交**

```bash
git add src/services/searxng.py
git commit -m "feat: add SearXNG service with subprocess management"
```

---

## Task 3: Cache Service

**Files:**
- Create: `src/services/cache.py`

- [ ] **Step 1: 创建缓存服务**

```python
from cachetools import TTLCache
from config.settings import CACHE_TTL

cache = TTLCache(maxsize=1000, ttl=CACHE_TTL)

def get(key: str):
    return cache.get(key)

def set(key: str, value):
    cache[key] = value

def generate_key(query: str, num_results: int, mode: str, engines: list) -> str:
    data = f"{query}|{num_results}|{mode}|{','.join(engines or [])}"
    hash_val = hash(data)
    return f"search:{abs(hash_val)}"
```

- [ ] **Step 2: 提交**

```bash
git add src/services/cache.py
git commit -m "feat: add cache service with TTL"
```

---

## Task 4: Parser Service

**Files:**
- Create: `src/services/parser.py`

- [ ] **Step 1: 创建解析服务**

```python
from lxml import html

def parse_results(raw_results: list) -> list:
    seen_urls = set()
    parsed = []

    for item in raw_results:
        content = item.get("content", "")
        if content:
            tree = html.fromstring(content)
            content = tree.text_content().strip()

        url = item.get("url", "")
        if not url or url in seen_urls:
            continue
        seen_urls.add(url)

        published = item.get("publishedDate")
        if published:
            try:
                from datetime import datetime
                published = datetime.fromisoformat(published.replace("Z", "+00:00"))
                published = published.strftime("%Y-%m-%d")
            except (ValueError, AttributeError):
                published = None

        parsed.append({
            "title": item.get("title", "Untitled"),
            "url": url,
            "snippet": content[:500] if content else "",
            "engine": item.get("engine", "unknown"),
            "publishedDate": published
        })

    return parsed
```

- [ ] **Step 2: 提交**

```bash
git add src/services/parser.py
git commit -m "feat: add parser service with HTML cleaning and dedup"
```

---

## Task 5: detect_mode Utility

**Files:**
- Create: `src/utils/detect_mode.py`

- [ ] **Step 1: 创建模式检测工具**

```python
DETECT_LIST_PATTERNS = ["谁", "什么", "哪个", "多少", "何时", "哪里", "who", "what", "which", "how many", "when", "where"]
DETECT_EXTRACT_PATTERNS = ["为什么", "怎么", "如何", "评价", "分析", "比较", "解释", "why", "how", "explain", "analyze", "compare", "evaluate"]

def detect(query: str) -> str:
    q = query.lower()
    if any(p in q for p in DETECT_EXTRACT_PATTERNS):
        return "extract"
    if any(p in q for p in DETECT_LIST_PATTERNS):
        return "list"
    return "list"
```

- [ ] **Step 2: 提交**

```bash
git add src/utils/detect_mode.py
git commit -m "feat: add mode detection utility"
```

---

## Task 6: Aggregator Service

**Files:**
- Create: `src/services/aggregator.py`

- [ ] **Step 1: 创建聚合服务**

```python
from utils.detect_mode import detect
from services.parser import parse_results

def aggregate(raw_results: list, query: str, mode: str) -> dict:
    parsed = parse_results(raw_results)

    if mode == "auto":
        mode = detect(query)

    results = [{
        "title": r["title"],
        "url": r["url"],
        "snippet": r["snippet"],
        "engine": r["engine"],
        "publishedDate": r["publishedDate"]
    } for r in parsed]

    extracted_data = None
    if mode == "extract":
        extracted_data = [{
            "title": r["title"],
            "url": r["url"],
            "keyInfo": r["snippet"][:200]
        } for r in parsed]

    return {
        "mode": mode,
        "results": results,
        "extractedData": extracted_data
    }
```

- [ ] **Step 2: 提交**

```bash
git add src/services/aggregator.py
git commit -m "feat: add aggregator service with mode handling"
```

---

## Task 7: Error Handler Middleware

**Files:**
- Create: `src/middleware/error_handler.py`

- [ ] **Step 1: 创建错误处理中间件**

```python
from fastapi import Request
from fastapi.responses import JSONResponse

async def error_handler(request: Request, exc: Exception) -> JSONResponse:
    print(f"Error: {exc}")

    if hasattr(exc, "code"):
        code = exc.code
    else:
        code = "INTERNAL_ERROR"

    status_map = {
        "INVALID_PARAMS": 400,
        "SEARXNG_UNAVAILABLE": 503,
        "REQUEST_TIMEOUT": 504,
        "INTERNAL_ERROR": 500,
    }
    status = status_map.get(code, 500)

    msg_map = {
        "INVALID_PARAMS": "参数缺失或格式错误",
        "SEARXNG_UNAVAILABLE": "搜索引擎服务不可用",
        "REQUEST_TIMEOUT": "请求超时",
        "INTERNAL_ERROR": "内部错误",
    }

    return JSONResponse(
        status_code=status,
        content={
            "success": False,
            "error": {
                "code": code,
                "message": str(exc) if str(exc) else msg_map.get(code, "未知错误")
            }
        }
    )
```

- [ ] **Step 2: 提交**

```bash
git add src/middleware/error_handler.py
git commit -m "feat: add error handler middleware"
```

---

## Task 8: Search Route

**Files:**
- Create: `src/routes/search.py`

- [ ] **Step 1: 创建搜索路由**

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.searxng import searxng_service
from services.cache import get, set, generate_key
from services.aggregator import aggregate

router = APIRouter(prefix="/api", tags=["search"])

class SearchRequest(BaseModel):
    query: str
    num_results: int = 10
    mode: str = "auto"
    engines: list = []

    class Config:
        json_schema_extra = {
            "example": {
                "query": "最新的AI模型有哪些",
                "num_results": 10,
                "mode": "auto",
                "engines": []
            }
        }

@router.post("/search")
async def search(req: SearchRequest):
    if not req.query or not isinstance(req.query, str):
        raise HTTPException(status_code=400, detail="query 参数必填且为字符串")

    if req.num_results < 1 or req.num_results > 50:
        raise HTTPException(status_code=400, detail="num_results 需在 1-50 之间")

    if req.mode not in ("auto", "list", "extract"):
        raise HTTPException(status_code=400, detail="mode 需为 auto/list/extract 之一")

    cache_key = generate_key(req.query, req.num_results, req.mode, req.engines)
    cached = get(cache_key)
    if cached:
        cached["meta"]["cached"] = True
        return {"success": True, "data": cached}

    import time
    start = time.time()

    raw_results = searxng_service.search(req.query, req.num_results, req.engines)
    response_time = int((time.time() - start) * 1000)

    result = aggregate(raw_results, req.query, req.mode)

    response = {
        "query": req.query,
        "mode": result["mode"],
        "results": result["results"],
        "extractedData": result["extractedData"],
        "meta": {
            "total": len(result["results"]),
            "cached": False,
            "responseTime": response_time
        }
    }

    set(cache_key, response)

    return {"success": True, "data": response}
```

- [ ] **Step 2: 提交**

```bash
git add src/routes/search.py
git commit -m "feat: add search route with cache and aggregation"
```

---

## Task 9: Main Entry

**Files:**
- Create: `src/main.py`

- [ ] **Step 1: 创建 FastAPI 主入口**

```python
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
        print("Error: searxng directory not found")
        sys.exit(1)

    print("Starting SearXNG...")
    if not searxng_service.start(searxng_dir):
        print("Error: Failed to start SearXNG")
        sys.exit(1)
    print("SearXNG started successfully")

    yield

    print("Stopping SearXNG...")
    searxng_service.stop()

app = FastAPI(title="WebSearch Backend", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
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
```

- [ ] **Step 2: 提交**

```bash
git add src/main.py
git commit -m "feat: add FastAPI entry with SearXNG lifecycle management"
```

---

## Task 10: README

**Files:**
- Create: `README.md`

- [ ] **Step 1: 创建 README**

```markdown
# WebSearch_forAI

SearXNG 集成代理层，为 AI 提供联网搜索能力。

## 快速开始

```bash
pip install -r requirements.txt

# 克隆 SearXNG 源码
git clone https://github.com/searxng/searxng.git

cp .env.example .env
python src/main.py
```

## API

### 搜索

POST /api/search

```json
{
  "query": "最新的AI模型有哪些",
  "num_results": 10,
  "mode": "auto",
  "engines": []
}
```

### 健康检查

GET /health

## 环境变量

- `SEARXNG_PORT` - SearXNG 端口 (默认: 4000)
- `API_PORT` - API 服务端口 (默认: 4001)
- `CACHE_TTL` - 缓存 TTL 秒 (默认: 300)
- `REQUEST_TIMEOUT` - 请求超时毫秒 (默认: 10000)
- `SEARXNG_DATA_DIR` - SearXNG 数据目录 (默认: ./searxng_data)
```

- [ ] **Step 2: 提交**

```bash
git add README.md
git commit -m "docs: add README"
```

---

## 验证计划

1. 克隆 SearXNG 源码到 `searxng/` 目录
2. 配置 `.env`
3. 启动服务: `python src/main.py`
4. 测试健康检查: `curl http://localhost:4001/health`
5. 测试搜索: `curl -X POST http://localhost:4001/api/search -H "Content-Type: application/json" -d '{"query": "test"}'`

---

## Spec 覆盖检查

| Spec 章节 | 覆盖情况 |
|-----------|----------|
| SearXNG 子进程管理 | Task 2 (searxng.py) |
| 搜索转发 | Task 2 (search 方法) |
| 结果清洗 | Task 4 (parser.py) |
| 内存缓存 | Task 3 (cache.py) |
| auto/list/extract 模式 | Task 5, 6 |
| API 设计 | Task 8 (search.py) |
| 健康检查 | Task 9 (main.py) |
| 错误处理 | Task 7 (error_handler.py) |