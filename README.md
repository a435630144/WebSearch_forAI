# WebSearch_forAI

SearXNG 集成代理层，为 AI 提供联网搜索能力。

## 快速开始

```bash
pip install -r requirements.txt

# 配置 SearXNG 服务器地址
cp .env.example .env
# 编辑 .env 文件，设置 SEARXNG_HOST 和 SEARXNG_PORT

python src/main.py
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
| query | string | 是 | - | 搜索关键词 |
| num_results | int | 否 | 10 | 返回结果数量 (1-50) |
| mode | string | 否 | "auto" | 模式：auto/list/extract |
| engines | array | 否 | [] | 指定引擎，留空使用全部 |

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
        "publishedDate": "2026-01-01T12:00:00"
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

**返回字段说明：**

| 字段 | 类型 | 说明 |
|------|------|------|
| success | bool | 请求是否成功 |
| data.query | string | 查询的关键词 |
| data.mode | string | 响应模式 |
| data.results | array | 搜索结果列表 |
| data.results[].title | string | 结果标题 |
| data.results[].url | string | 结果链接 |
| data.results[].snippet | string | 结果摘要 |
| data.results[].engine | string | 来源引擎 |
| data.results[].publishedDate | string | 发布时间 |
| data.extractedData | object | 提取的实体数据（extract 模式） |
| data.meta.total | int | 结果总数 |
| data.meta.cached | bool | 是否来自缓存 |
| data.meta.responseTime | int | 响应时间（毫秒） |

**mode 参数说明：**

- `auto`：智能模式，自动判断返回格式
- `list`：列表模式，返回搜索结果列表（默认）
- `extract`：提取模式，额外提取结构化数据

**错误响应：**

```json
{
  "detail": "错误描述"
}
```

## 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| SEARXNG_HOST | 127.0.0.1 | SearXNG 服务器地址 |
| SEARXNG_PORT | 8080 | SearXNG 端口 |
| API_PORT | 4001 | API 服务端口 |
| CACHE_TTL | 300 | 缓存 TTL（秒） |
| REQUEST_TIMEOUT | 10000 | 请求超时（毫秒） |
| SEARXNG_DATA_DIR | ./searxng_data | SearXNG 数据目录 |

## SearXNG 配置

推荐只启用国内可访问的搜索引擎，修改 `settings.yml`：

```yaml
engines:
  - name: baidu
    engine: baidu
  - name: 360search
    engine: 360search
  - name: bing
    engine: bing
  - name: wikipedia
    engine: wikipedia
```

超时配置建议：

```yaml
outgoing:
  request_timeout: 10.0
```