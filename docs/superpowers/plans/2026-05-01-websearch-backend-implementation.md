# WebSearch Backend Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为 AI 联网搜索功能创建 Express 后端，调用 SearXNG API 并返回清洗后的结构化结果

**Architecture:** 单一 Express 应用，内存缓存，模块化服务设计。SearXNG 由用户自部署，本项目仅做代理层。

**Tech Stack:** Node.js, Express.js, node-cache, axios, cheerio, dotenv

---

## 文件结构

```
WebSearch_forAI/
├── src/
│   ├── index.js              # Express 入口
│   ├── routes/
│   │   └── search.js         # /api/search 路由
│   ├── services/
│   │   ├── searxng.js        # SearXNG API 调用
│   │   ├── cache.js         # 内存缓存服务
│   │   ├── parser.js        # HTML 清洗、结构化
│   │   └── aggregator.js    # 整理模式逻辑
│   ├── middleware/
│   │   └── errorHandler.js  # 统一错误处理
│   └── utils/
│       └── detectMode.js     # auto 模式判断
├── .env.example
├── package.json
└── README.md
```

---

## Task 1: 项目初始化

**Files:**
- Create: `package.json`
- Create: `.env.example`
- Create: `src/index.js`

- [ ] **Step 1: 创建 package.json**

```json
{
  "name": "websearch-backend",
  "version": "1.0.0",
  "description": "SearXNG 代理层，为 AI 提供联网搜索能力",
  "main": "src/index.js",
  "scripts": {
    "start": "node src/index.js",
    "dev": "node --watch src/index.js"
  },
  "dependencies": {
    "axios": "^1.7.0",
    "cheerio": "^1.0.0",
    "dotenv": "^16.4.0",
    "express": "^4.19.0",
    "node-cache": "^5.1.2"
  }
}
```

- [ ] **Step 2: 创建 .env.example**

```env
SEARXNG_URL=http://localhost:4000
CACHE_TTL=300
REQUEST_TIMEOUT=10000
PORT=3002
```

- [ ] **Step 3: 创建 Express 入口 src/index.js**

```javascript
require('dotenv').config();
const express = require('express');
const searchRouter = require('./routes/search');
const errorHandler = require('./middleware/errorHandler');

const app = express();
const PORT = process.env.PORT || 3002;

app.use(express.json());

app.use('/api/search', searchRouter);

app.get('/health', (req, res) => {
  res.json({ status: 'ok' });
});

app.use(errorHandler);

app.listen(PORT, () => {
  console.log(`WebSearch Backend running on port ${PORT}`);
});
```

- [ ] **Step 4: 安装依赖**

Run: `cd "D:\OneDrive\自学编程\claude code\WebSearch_forAI" && npm install`

- [ ] **Step 5: 提交**

```bash
git add package.json .env.example src/index.js
git commit -m "feat: project scaffold with Express entry point"
```

---

## Task 2: Error Handler Middleware

**Files:**
- Create: `src/middleware/errorHandler.js`

- [ ] **Step 1: 创建统一错误处理中间件**

```javascript
const errorHandler = (err, req, res, next) => {
  console.error('Error:', err.message);

  if (err.code === 'SEARXNG_UNAVAILABLE') {
    return res.status(503).json({
      success: false,
      error: {
        code: 'SEARXNG_UNAVAILABLE',
        message: '搜索引擎服务不可用'
      }
    });
  }

  if (err.code === 'REQUEST_TIMEOUT') {
    return res.status(504).json({
      success: false,
      error: {
        code: 'REQUEST_TIMEOUT',
        message: '请求超时'
      }
    });
  }

  if (err.code === 'INVALID_PARAMS') {
    return res.status(400).json({
      success: false,
      error: {
        code: 'INVALID_PARAMS',
        message: err.message || '参数缺失或格式错误'
      }
    });
  }

  res.status(500).json({
    success: false,
    error: {
      code: 'INTERNAL_ERROR',
      message: '内部错误'
    }
  });
};

module.exports = errorHandler;
```

- [ ] **Step 2: 提交**

```bash
git add src/middleware/errorHandler.js
git commit -m "feat: add unified error handler middleware"
```

---

## Task 3: Cache Service

**Files:**
- Create: `src/services/cache.js`

- [ ] **Step 1: 创建内存缓存服务**

```javascript
const NodeCache = require('node-cache');

const cache = new NodeCache({
  stdTTL: process.env.CACHE_TTL ? parseInt(process.env.CACHE_TTL) : 300,
  checkperiod: 60
});

const get = (key) => {
  return cache.get(key);
};

const set = (key, value) => {
  return cache.set(key, value);
};

const generateKey = (query, numResults, mode, engines) => {
  const data = JSON.stringify({ query, numResults, mode, engines });
  let hash = 0;
  for (let i = 0; i < data.length; i++) {
    const char = data.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash;
  }
  return `search:${Math.abs(hash)}`;
};

module.exports = {
  cache,
  get,
  set,
  generateKey
};
```

- [ ] **Step 2: 提交**

```bash
git add src/services/cache.js
git commit -m "feat: add in-memory cache service"
```

---

## Task 4: SearXNG Service

**Files:**
- Create: `src/services/searxng.js`

- [ ] **Step 1: 创建 SearXNG 调用服务**

```javascript
const axios = require('axios');

const SEARXNG_URL = process.env.SEARXNG_URL || 'http://localhost:4000';
const REQUEST_TIMEOUT = process.env.REQUEST_TIMEOUT ? parseInt(process.env.REQUEST_TIMEOUT) : 10000;

const search = async (query, numResults = 10, engines = []) => {
  const params = {
    q: query,
    format: 'json',
    categories: 'general',
   engines: engines.length > 0 ? engines.join(',') : undefined
  };

  try {
    const response = await axios.get(`${SEARXNG_URL}/search`, {
      params,
      timeout: REQUEST_TIMEOUT
    });

    if (!response.data || !response.data.results) {
      throw Object.assign(new Error('Invalid SearXNG response'), { code: 'SEARXNG_UNAVAILABLE' });
    }

    return response.data.results.slice(0, numResults);
  } catch (error) {
    if (error.code === 'ECONNABORTED' || error.code === 'ETIMEDOUT') {
      throw Object.assign(new Error('SearXNG request timeout'), { code: 'REQUEST_TIMEOUT' });
    }
    if (!error.code) {
      error.code = 'SEARXNG_UNAVAILABLE';
    }
    throw error;
  }
};

const checkHealth = async () => {
  try {
    await axios.get(`${SEARXNG_URL}/health`, { timeout: 3000 });
    return true;
  } catch {
    return false;
  }
};

module.exports = {
  search,
  checkHealth
};
```

- [ ] **Step 2: 提交**

```bash
git add src/services/searxng.js
git commit -m "feat: add SearXNG service with timeout handling"
```

---

## Task 5: Parser Service

**Files:**
- Create: `src/services/parser.js`

- [ ] **Step 1: 创建解析服务**

```javascript
const cheerio = require('cheerio');

const parseResults = (rawResults) => {
  const seenUrls = new Set();
  const parsed = [];

  for (const item of rawResults) {
    let content = item.content || '';

    if (item.html) {
      const $ = cheerio.load(item.html);
      content = $.text().trim();
    } else if (typeof content === 'string' && content.includes('<')) {
      const $ = cheerio.load(content);
      content = $.text().trim();
    }

    const url = item.url || item.parsedUrl?.URL || '';
    if (!url || seenUrls.has(url)) continue;
    seenUrls.add(url);

    let publishedDate = null;
    if (item.publishedDate) {
      publishedDate = new Date(item.publishedDate).toISOString().split('T')[0];
    }

    parsed.push({
      title: item.title || 'Untitled',
      url,
      snippet: content.substring(0, 500),
      engine: item.engine || 'unknown',
      publishedDate
    });
  }

  return parsed;
};

module.exports = {
  parseResults
};
```

- [ ] **Step 2: 提交**

```bash
git add src/services/parser.js
git commit -m "feat: add HTML parser and deduplication"
```

---

## Task 6: detectMode Utility

**Files:**
- Create: `src/utils/detectMode.js`

- [ ] **Step 1: 创建模式检测工具**

```javascript
const DETECT_LIST_PATTERNS = [
  '谁', '什么', '哪个', '多少', '何时', '哪里',
  'who', 'what', 'which', 'how many', 'when', 'where'
];

const DETECT_EXTRACT_PATTERNS = [
  '为什么', '怎么', '如何', '评价', '分析', '比较', '解释',
  'why', 'how', 'explain', 'analyze', 'compare', 'evaluate'
];

const detect = (query) => {
  const lowerQuery = query.toLowerCase();

  if (DETECT_EXTRACT_PATTERNS.some(p => lowerQuery.includes(p))) {
    return 'extract';
  }

  if (DETECT_LIST_PATTERNS.some(p => lowerQuery.includes(p))) {
    return 'list';
  }

  return 'list';
};

module.exports = {
  detect
};
```

- [ ] **Step 2: 提交**

```bash
git add src/utils/detectMode.js
git commit -m "feat: add mode detection utility for auto mode"
```

---

## Task 7: Aggregator Service

**Files:**
- Create: `src/services/aggregator.js`

- [ ] **Step 1: 创建聚合服务**

```javascript
const { detect } = require('../utils/detectMode');
const { parseResults } = require('./parser');

const aggregate = (rawResults, query, mode) => {
  const parsed = parseResults(rawResults);

  if (mode === 'auto') {
    mode = detect(query);
  }

  let results;
  let extractedData = null;

  if (mode === 'extract') {
    extractedData = parsed.map(r => ({
      title: r.title,
      url: r.url,
      keyInfo: r.snippet.substring(0, 200)
    }));
  }

  results = parsed.map(r => ({
    title: r.title,
    url: r.url,
    snippet: r.snippet,
    engine: r.engine,
    publishedDate: r.publishedDate
  }));

  return {
    mode,
    results,
    extractedData
  };
};

module.exports = {
  aggregate
};
```

- [ ] **Step 2: 提交**

```bash
git add src/services/aggregator.js
git commit -m "feat: add aggregator service with mode handling"
```

---

## Task 8: Search Route

**Files:**
- Create: `src/routes/search.js`

- [ ] **Step 1: 创建搜索路由**

```javascript
const express = require('express');
const router = express.Router();
const { search: searxngSearch } = require('../services/searxng');
const { aggregate } = require('../services/aggregator');
const { get, set, generateKey } = require('../services/cache');

router.post('/', async (req, res, next) => {
  try {
    const { query, num_results = 10, mode = 'auto', engines = [] } = req.body;

    if (!query || typeof query !== 'string') {
      const error = new Error('query 参数必填且为字符串');
      error.code = 'INVALID_PARAMS';
      return next(error);
    }

    if (num_results < 1 || num_results > 50) {
      const error = new Error('num_results 需在 1-50 之间');
      error.code = 'INVALID_PARAMS';
      return next(error);
    }

    const cacheKey = generateKey(query, num_results, mode, engines);
    const cached = get(cacheKey);
    if (cached) {
      return res.json({
        success: true,
        data: {
          ...cached,
          meta: {
            ...cached.meta,
            cached: true
          }
        }
      });
    }

    const startTime = Date.now();
    const rawResults = await searxngSearch(query, num_results, engines);
    const responseTime = Date.now() - startTime;

    const result = aggregate(rawResults, query, mode);

    const response = {
      query,
      mode: result.mode,
      results: result.results,
      extractedData: result.extractedData,
      meta: {
        total: result.results.length,
        cached: false,
        responseTime
      }
    };

    set(cacheKey, response);

    res.json({
      success: true,
      data: response
    });
  } catch (error) {
    next(error);
  }
});

module.exports = router;
```

- [ ] **Step 2: 更新 health 路由检查 SearXNG**

Modify: `src/index.js`

```javascript
const { checkHealth: checkSearxng } = require('./services/searxng');

app.get('/health', async (req, res) => {
  const searxngOk = await checkSearxng();
  res.json({
    status: 'ok',
    searxng: searxngOk ? 'connected' : 'disconnected'
  });
});
```

- [ ] **Step 3: 提交**

```bash
git add src/routes/search.js src/index.js
git commit -m "feat: add search route with cache and aggregation"
```

---

## Task 9: README

**Files:**
- Create: `README.md`

- [ ] **Step 1: 创建 README**

```markdown
# WebSearch Backend

SearXNG 代理层，为 AI 提供联网搜索能力。

## 快速开始

```bash
npm install
cp .env.example .env
# 编辑 .env 中的 SEARXNG_URL
npm start
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

mode 可选: `auto` | `list` | `extract`

### 健康检查

GET /health

## 环境变量

- `SEARXNG_URL` - SearXNG 实例地址 (默认: http://localhost:4000)
- `CACHE_TTL` - 缓存 TTL 秒 (默认: 300)
- `REQUEST_TIMEOUT` - 请求超时毫秒 (默认: 10000)
- `PORT` - 服务端口 (默认: 3002)
```

- [ ] **Step 2: 提交**

```bash
git add README.md
git commit -m "docs: add README"
```

---

## 验证计划

1. 启动 SearXNG 实例（如未运行）
2. 配置 `.env` 中的 `SEARXNG_URL`
3. 启动本服务: `npm start`
4. 测试健康检查: `curl http://localhost:3002/health`
5. 测试搜索: `curl -X POST http://localhost:3002/api/search -H "Content-Type: application/json" -d '{"query": "test"}'`