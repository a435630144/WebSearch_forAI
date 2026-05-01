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
    time_range: str = ""  # "", "day", "week", "month", "year"

    class Config:
        json_schema_extra = {
            "example": {
                "query": "最新的AI模型有哪些",
                "num_results": 10,
                "mode": "auto",
                "engines": [],
                "time_range": "month"
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

    if req.time_range not in ("", "day", "week", "month", "year"):
        raise HTTPException(status_code=400, detail="time_range 需为 day/week/month/year 或空")

    cache_key = generate_key(req.query, req.num_results, req.mode, req.engines, req.time_range)
    cached = get(cache_key)
    if cached:
        cached["meta"]["cached"] = True
        return {"success": True, "data": cached}

    import time
    start = time.time()

    try:
        raw_results = searxng_service.search(req.query, req.num_results, req.engines, req.time_range)
    except Exception as e:
        raise HTTPException(status_code=504, detail=f"搜索服务响应超时或出错: {str(e)}")

    response_time = int((time.time() - start) * 1000)

    result = aggregate(raw_results, req.query, req.mode, req.time_range)

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