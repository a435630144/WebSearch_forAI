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