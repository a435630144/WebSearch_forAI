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