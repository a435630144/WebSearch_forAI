# WebSearch_forAI

SearXNG 集成代理层，为 AI 提供联网搜索能力（Node.js Express 版本）。

## 快速开始

```bash
npm install

# 配置 SearXNG 服务器地址
cp .env.example .env
# 编辑 .env 文件，设置 SEARXNG_HOST 和 SEARXNG_PORT

npm start
```

## API

### 健康检查

```bash
GET /health
```

返回：
```json
{
  "status": "ok",
  "searxng": "running"
}
```

### 搜索

```bash
POST /api/search
Content-Type: application/json
```

**请求参数：**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| **query** | string | **是** | - | 搜索关键词 |
| num_results | int | 否 | 10 | 返回结果数量 (1-50) |
| mode | string | 否 | "auto" | 模式：auto/list/extract |
| engines | array | 否 | [] | 指定引擎列表，例如 `["baidu", "bing"]` |
| time_range | string | 否 | "" | 时间范围：`""` (不限), `day`, `week`, `month`, `year` |

**请求示例：**

```json
{
  "query": "最新AI大模型有哪些",
  "num_results": 10,
  "mode": "auto",
  "engines": ["baidu", "bing"]
}
```

**返回格式：**

```json
{
  "success": true,
  "data": {
    "query": "最新AI大模型有哪些",
    "mode": "list",
    "results": [
      {
        "title": "文章标题",
        "url": "https://example.com/article",
        "snippet": "文章摘要内容...",
        "engine": "baidu",
        "publishedDate": "2026-01-01"
      }
    ],
    "extractedData": null,
    "meta": {
      "total": 10,
      "cached": false,
      "responseTime": 1523
    }
  }
}
```

**mode 参数说明：**

- `auto`：智能模式，自动判断返回格式
- `list`：列表模式，返回搜索结果列表（默认）
- `extract`：提取模式，额外提取结构化数据

**错误响应：**

```json
{
  "success": false,
  "error": {
    "code": "REQUEST_TIMEOUT",
    "message": "搜索服务响应超时或出错: timed out"
  }
}
```

## 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| SEARXNG_HOST | 192.168.3.64 | SearXNG 服务器 IP 地址 |
| SEARXNG_PORT | 8080 | SearXNG 端口 |
| API_PORT | 4001 | 本 API 服务端口 |
| CACHE_TTL | 300 | 内存缓存有效期（秒） |
| REQUEST_TIMEOUT | 30000 | 搜索请求超时时间（毫秒） |

## 技术栈

- **Runtime**: Node.js 18+
- **Framework**: Express.js
- **HTTP Client**: axios
- **HTML Parsing**: cheerio
- **Caching**: node-cache
- **Environment Variables**: dotenv
- **CORS**: cors
