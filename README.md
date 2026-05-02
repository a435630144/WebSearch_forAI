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

服务启动后访问：
- API 地址: `http://localhost:4001`
- 健康检查: `GET http://localhost:4001/health`
- 搜索接口: `POST http://localhost:4001/api/search`

## 技术栈

- **Runtime**: Node.js 18+
- **Framework**: Express.js
- **HTTP Client**: axios
- **HTML Parsing**: cheerio
- **Caching**: node-cache
- **Environment Variables**: dotenv
- **CORS**: cors

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
  "engines": ["baidu", "bing"],
  "time_range": "month"
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

- `auto`：智能模式，根据 query 关键词自动判断返回格式
- `list`：列表模式，返回搜索结果列表（默认）
- `extract`：提取模式，额外提取结构化数据（truncate snippet to 200 chars）

**auto 模式判断规则：**

| 模式 | 关键词示例 |
|------|------------|
| list | 谁、什么、哪个、多少、何时、哪里 (中文) / who、what、which、when、where (英文) |
| extract | 为什么、怎么、如何、评价、分析、比较、解释 (中文) / why、how、analyze、compare、evaluate (英文) |

**错误响应：**

```json
{
  "success": false,
  "error": {
    "code": "INVALID_PARAMS",
    "message": "query parameter is required and must be a string"
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

## 项目结构

```
WebSearch_forAI/
├── src/
│   ├── index.js              # Express 应用入口
│   ├── config/
│   │   └── index.js          # 环境变量加载
│   ├── routes/
│   │   └── search.js         # POST /api/search 路由
│   ├── services/
│   │   ├── searxng.js        # SearXNG HTTP 客户端
│   │   ├── cache.js          # TTL 缓存服务
│   │   └── aggregator.js     # 时间过滤 + 模式选择
│   ├── middleware/
│   │   └── error_handler.js  # 全局错误处理
│   └── utils/
│       ├── parser.js          # HTML 清洗、URL 去重
│       └── detect_mode.js     # auto 模式判断
├── tests/                    # 单元测试
├── .env.example
├── package.json
├── README.md
└── SPEC.md
```

## 测试

```bash
npm test
```

运行单元测试验证核心功能。