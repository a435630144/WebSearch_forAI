# WebSearch Backend 设计文档

**日期**: 2026-05-01（更新）
**项目**: WebSearch_forAI
**用途**: SearXNG 集成代理层，为 AI 提供联网搜索能力

---

## 1. 概述

### 项目定位
- **名称**: `WebSearch_forAI`
- **技术栈**: Python + FastAPI
- **部署环境**: 局域网 NAS (Docker)
- **SearXNG**: 远程 Docker 部署，访问地址: http://192.168.3.64:8080

### 核心功能
1. **搜索转发** - 调用远程 SearXNG 实例
2. **结果清洗** - HTML 清洗、去重、字段标准化
3. **缓存** - 内存缓存，减少重复调用
4. **灵活整理** - 支持 auto / list / extract 三种模式

---

## 2. 技术栈

| 组件 | 技术选型 | 说明 |
|------|----------|------|
| 运行时 | Python 3.10+ | |
| 框架 | FastAPI | 异步、高性能 |
| ASGI 服务器 | uvicorn | 生产级 ASGI |
| HTTP 客户端 | httpx | 异步 HTTP 调用 |
| HTML 解析 | lxml | 高性能解析 |
| 缓存 | cachetools | 内存缓存 |
| 环境变量 | python-dotenv | 配置管理 |

---

## 3. 端口分配

| 服务 | 地址 |
|------|------|
| SearXNG 远程服务 | http://192.168.3.64:8080 |
| FastAPI 主服务 | localhost:4001 |

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
  "engines": ["google", "bing"]
}
```

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| query | string | 是 | - | 搜索关键词 |
| num_results | int | 否 | 10 | 返回结果数量 |
| mode | string | 否 | "auto" | 整理模式: auto / list / extract |
| engines | string[] | 否 | 全部 | 指定搜索来源 |

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
        "engine": "google",
        "publishedDate": "2026-04-28"
      }
    ],
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
    "code": "SEARXNG_UNAVAILABLE",
    "message": "搜索引擎服务不可用"
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
- 包含"谁"、"什么"、"多少"、"何时"等词 → list 模式
- 开放式问题（如"评价"、"分析"、"为什么"）→ extract 模式

---

## 6. 项目结构

项目根目录：`D:\OneDrive\自学编程\claude code\WebSearch_forAI`

```
WebSearch_forAI/
├── src/
│   ├── __init__.py
│   ├── main.py              # FastAPI 入口，应用启动时自动启动 SearXNG
│   ├── routes/
│   │   ├── __init__.py
│   │   └── search.py        # /api/search 路由
│   ├── services/
│   │   ├── __init__.py
│   │   ├── searxng.py       # SearXNG 子进程管理 + API 调用
│   │   ├── cache.py         # 内存缓存服务
│   │   ├── parser.py        # HTML 清洗、结构化
│   │   └── aggregator.py   # 整理模式逻辑
│   ├── middleware/
│   │   ├── __init__.py
│   │   └── error_handler.py # 统一错误处理
│   └── utils/
│       ├── __init__.py
│       └── detect_mode.py   # auto 模式判断
├── searxng/                  # SearXNG 源码（git submodule 或 copy）
├── config/
│   └── settings.py          # 配置管理
├── .env.example
├── requirements.txt
├── README.md
└── SPEC.md
```

---

## 7. 启动流程

```
应用启动
  │
  ├─► 检查 SearXNG 目录存在
  ├─► 启动 SearXNG 子进程（端口 4000）
  │     - 设置 SEARXNG_DATA_DIR
  │     - 限制只监听 localhost
  │     - 禁用公开访问
  │
  ├─► 等待 SearXNG 就绪（健康检查轮询）
  │     - 超时 60 秒
  │     - 失败则终止应用
  │
  └─► 启动 FastAPI（端口 4001）
```

---

## 8. 数据流

```
请求 POST /api/search
  │
  ├─► 缓存检查（key = query hash）
  │     └─► 命中 ──► 返回缓存结果
  │
  ├─► 调用 localhost:4000 (SearXNG)
  │     └─► 超时/失败 ──► 返回 503 错误
  │
  ├─► 清洗解析（parser.py）
  │     - HTML 转文本
  │     - 去重（URL 去重）
  │     - 字段标准化
  │
  ├─► 模式处理（aggregator.py）
  │     - auto: 调用 detect_mode 判断
  │     - list: 保持原 snippet
  │     - extract: 进一步提炼关键信息
  │
  ├─► 存入缓存
  │
  └─► 返回标准化响应
```

---

## 9. 环境变量

```env
# SearXNG 子进程端口
SEARXNG_PORT=4000

# API 服务端口
API_PORT=4001

# 缓存 TTL（秒）
CACHE_TTL=300

# 请求超时（毫秒）
REQUEST_TIMEOUT=10000

# SearXNG 工作目录
SEARXNG_DATA_DIR=./searxng_data
```

---

## 10. 错误处理

| 错误码 | HTTP 状态 | 说明 |
|--------|-----------|------|
| INVALID_PARAMS | 400 | 参数缺失或格式错误 |
| SEARXNG_UNAVAILABLE | 503 | SearXNG 不可用 |
| REQUEST_TIMEOUT | 504 | 请求超时 |
| INTERNAL_ERROR | 500 | 内部错误 |

---

## 11. SearXNG 配置要求

为集成场景，SearXNG 需要以下配置：
- `SEARXNG_BIND` = "127.0.0.1:4000"
- `SEARXNG_SECRET_KEY` = 随机生成
- `SEARXNG_INSTANCE_TYPE` = "public"
- 禁用公开 UI（只通过 API 使用）

---

## 12. 后续扩展（暂不实现）

- [ ] 限流中间件
- [ ] 持久化缓存（Redis）
- [ ] 多 SearXNG 实例负载均衡
- [ ] 搜索历史记录
- [ ] SearXNG 配置 UI