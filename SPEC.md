# WebSearch_forAI 设计文档

**日期**: 2026-05-02（更新）
**项目**: WebSearch_forAI
**用途**: SearXNG 集成代理层，为 AI 提供联网搜索能力

---

## 1. 概述

### 项目定位
- **名称**: `WebSearch_forAI`
- **技术栈**: Node.js + Express.js
- **部署环境**: 局域网 NAS (Docker)
- **SearXNG**: 远程 Docker 部署，访问地址: http://192.168.3.64:8080

### 核心功能
1. **搜索转发** - 调用远程 SearXNG 实例
2. **结果清洗** - HTML 清洗、去重、字段标准化
3. **缓存** - 内存缓存（node-cache），减少重复调用
4. **时间过滤** - 后端硬过滤，支持 day/week/month/year 时间范围
5. **灵活整理** - 支持 auto / list / extract 三种模式

---

## 2. 技术栈

| 组件 | 技术选型 | 说明 |
|------|----------|------|
| 运行时 | Node.js 18+ | |
| 框架 | Express.js | 高性能 Web 框架 |
| HTTP 客户端 | axios | 异步 HTTP 调用 |
| HTML 解析 | cheerio | 高性能解析 |
| 缓存 | node-cache | 内存缓存 (TTL) |
| 环境变量 | dotenv | 配置管理 |
| 跨域 | cors | 跨域资源共享 |

---

## 3. 端口分配

| 服务 | 地址 |
|------|------|
| SearXNG 远程服务 | http://192.168.3.64:8080 |
| Express 主服务 | localhost:4001 |

---

## 4. API 设计

### 4.1 搜索接口

**`POST /api/search`**

```json
// 请求体
{
  "query": "最新的AI模型有哪些",
  "num_results": 10,
  "mode": "auto",
  "engines": ["baidu", "bing"],
  "time_range": "month"
}
```

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| query | string | 是 | - | 搜索关键词 |
| num_results | int | 否 | 10 | 返回结果数量 (1-50) |
| mode | string | 否 | "auto" | 整理模式: auto / list / extract |
| engines | string[] | 否 | [] | 指定搜索来源 |
| time_range | string | 否 | "" | 时间范围: 空/day/week/month/year |

```json
// 响应
{
  "success": true,
  "data": {
    "query": "最新的AI模型有哪些",
    "mode": "list",
    "results": [
      {
        "title": "GPT-5 发布",
        "url": "https://example.com/gpt5",
        "snippet": "OpenAI 宣布推出 GPT-5...",
        "engine": "baidu",
        "publishedDate": "2026-04-28"
      }
    ],
    "extractedData": null,
    "meta": {
      "total": 10,
      "cached": false,
      "responseTime": 1234
    }
  }
}
```

### 4.2 健康检查

**`GET /health`**

```json
{
  "status": "ok",
  "searxng": "running"
}
```

### 4.3 错误响应

```json
{
  "success": false,
  "error": {
    "code": "INVALID_PARAMS",
    "message": "query parameter is required and must be a string"
  }
}
```

---

## 5. 整理模式

| 模式 | 说明 | 适用场景 |
|------|------|----------|
| auto | 根据 query 复杂度自动选择 | 默认，推荐 |
| list | 清洗去重后的结果列表，保留完整 snippet | 事实查询、多结果对比 |
| extract | 进一步提炼关键信息、结构化输出 | 节省 token、需要提取实体 |

**auto 模式判断逻辑**:
- 包含"谁"、"什么"、"哪个"、"多少"、"何时"、"哪里"（中文）或 "who", "what", "which", "when", "where"（英文）→ list 模式
- 包含"为什么"、"怎么"、"如何"、"评价"、"分析"、"比较"、"解释"（中文）或 "why", "how", "analyze", "compare", "evaluate"（英文）→ extract 模式
- 默认 → list 模式

---

## 6. 项目结构

项目根目录：`D:\OneDrive\自学编程\claude code\WebSearch_forAI`

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
│   │   ├── cache.js          # TTL 缓存服务 (MD5 key)
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

---

## 7. 启动流程

```
应用启动
  │
  ├─► 加载 .env 环境变量
  ├─► 初始化 SearXNGService (配置 URL 和超时)
  ├─► 初始化 CacheService (配置 TTL)
  │
  ├─► 注册路由和中间件
  │     - cors 中间件
  │     - JSON 解析中间件
  │     - /api/search 路由
  │     - /health 健康检查
  │     - 全局错误处理中间件
  │
  └─► 启动 Express 服务（端口 4001）
```

---

## 8. 数据流

```
请求 POST /api/search
  │
  ├─► 参数验证
  │     - query 非空字符串
  │     - num_results 1-50
  │     - mode in [auto, list, extract]
  │     - time_range in [day, week, month, year, ""]
  │
  ├─► 缓存检查（key = MD5(query|num_results|mode|engines|time_range)）
  │     └─► 命中 ──► 返回缓存结果 (cached: true)
  │
  ├─► 调用 http://192.168.3.64:8080/search
  │     └─► 超时/失败 ──► 返回 504 错误
  │
  ├─► 解析清洗（parser.js）
  │     - HTML 转文本 (cheerio)
  │     - 去重（URL 去重）
  │     - 字段标准化 (title, url, snippet, engine, publishedDate)
  │
  ├─► 时间过滤（aggregator.js）
  │     - 根据 time_range 计算截止日期
  │     - 剔除 publishedDate 早于阈值的项目
  │     - 保留无日期的结果（无法确认是否过期）
  │
  ├─► 模式处理（aggregator.js）
  │     - auto: 调用 detect_mode 判断
  │     - list: 保持原 snippet
  │     - extract: 额外构建 extractedData[]
  │
  ├─► 存入缓存 (TTL 300s)
  │
  └─► 返回标准化响应
```

---

## 9. 环境变量

```env
# SearXNG 服务器地址
SEARXNG_HOST=192.168.3.64

# SearXNG 端口
SEARXNG_PORT=8080

# API 服务端口
API_PORT=4001

# 缓存 TTL（秒）
CACHE_TTL=300

# 请求超时（毫秒）
REQUEST_TIMEOUT=30000
```

---

## 10. 错误处理

| 错误码 | HTTP 状态 | 说明 |
|--------|-----------|------|
| INVALID_PARAMS | 400 | 参数缺失或格式错误 |
| REQUEST_TIMEOUT | 504 | 请求超时或连接失败 |
| INTERNAL_ERROR | 500 | 内部错误 |

---

## 11. 缓存策略

- **存储**: MD5 哈希作为 key，格式: `search:{hash}`
- **Key 生成**: `query|num_results|mode|engines.join|time_range`
- **TTL**: 默认 300 秒（可配置）
- **命中处理**: 返回缓存数据，`meta.cached = true`

---

## 12. 时间过滤逻辑

当 `time_range` 不为空时，后端进行二次硬过滤：

| time_range | 过滤逻辑 |
|------------|----------|
| day | 保留 publishedDate >= 今天-1天 |
| week | 保留 publishedDate >= 今天-7天 |
| month | 保留 publishedDate >= 今天-31天 |
| year | 保留 publishedDate >= 今天-366天 |
| "" | 不过滤 |

**注意**: 对于 `publishedDate` 为 `null` 的结果（引擎未提供日期），会被保留，因为无法确认其是否过期。

---

## 13. 后续扩展（暂不实现）

- [ ] 限流中间件
- [ ] 持久化缓存（Redis）
- [ ] 多 SearXNG 实例负载均衡
- [ ] 搜索历史记录
- [ ] SearXNG 配置 UI