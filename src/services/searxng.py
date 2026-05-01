import httpx
from config.settings import SEARXNG_URL, REQUEST_TIMEOUT

class SearXNGService:
    def __init__(self):
        self.running = True

    def search(self, query: str, num_results: int = 10, engines: list = None, time_range: str = "") -> list:
        """调用远程 SearXNG 搜索"""
        params = {
            "q": query,
            "format": "json",
            "categories": "general",
        }
        if engines:
            params["engines"] = ",".join(engines)
        if time_range:
            params["time_range"] = time_range

        try:
            with httpx.Client(http1=True, trust_env=False) as client:
                resp = client.get(
                    f"{SEARXNG_URL}/search",
                    params=params,
                    timeout=REQUEST_TIMEOUT / 1000
                )
            resp.raise_for_status()
            data = resp.json()
            results = data.get("results", [])
            print(f"SearXNG returned {len(results)} results")
            return results[:num_results]
        except Exception as e:
            print(f"SearXNG search error: {type(e).__name__}: {e}")
            return []

    def is_healthy(self) -> bool:
        """检查远程 SearXNG 健康状态"""
        try:
            # 尝试访问首页或 health 接口（如果 remote 开启了）
            resp = httpx.get(f"{SEARXNG_URL}/health", timeout=2)
            return resp.status_code == 200
        except httpx.RequestError:
            # 如果 health 接口不可用，尝试访问搜索页确认服务是否存活
            try:
                resp = httpx.get(f"{SEARXNG_URL}", timeout=2)
                return resp.status_code == 200
            except:
                return False

searxng_service = SearXNGService()
