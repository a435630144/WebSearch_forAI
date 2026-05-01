# Node.js Express Refactor: WebSearch_forAI

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor the Python FastAPI backend into Node.js Express to improve performance and developer ecosystem familiarity.

**Architecture:**
- **API Layer**: Express.js for routing, middleware, and request handling.
- **Service Layer**: Standalone modules for SearXNG communication, caching, parsing, and aggregation.
- **Utility Layer**: Pure functions for date processing, mode detection, and key generation.
- **Configuration**: Environment-driven via `dotenv`.

**Tech Stack:**
- **Runtime**: Node.js 18+
- **Framework**: Express.js
- **HTTP Client**: `axios`
- **HTML Parsing**: `cheerio`
- **Caching**: `node-cache`
- **Environment Variables**: `dotenv`
- **CORS**: `cors`

---

## File Structure

```
WebSearch_forAI/
├── src/
│   ├── index.js                  # Application entry point
│   ├── config/
│   │   └── index.js              # Environment variable loader
│   ├── routes/
│   │   ├── index.js              # Route registration
│   │   └── search.js             # POST /api/search handler
│   ├── services/
│   │   ├── searxng.js            # SearXNG HTTP client
│   │   ├── aggregator.js         # Time filtering and mode detection
│   │   └── cache.js              # TTL Cache logic
│   ├── utils/
│   │   ├── parser.js             # HTML cleaning and URL dedup
│   │   └── detect_mode.js       # Mode detection keywords
│   └── middleware/
│       └── error_handler.js      # Global error handler
├── .env.example
├── package.json
├── README.md
└── SPEC.md
```

---

## Task 1: Project Setup and Configuration

**Files:**
- Create: `package.json`
- Create: `.env.example`
- Create: `src/config/index.js`

- [ ] **Step 1: Create package.json**

```json
{
  "name": "websearch-forai",
  "version": "1.0.0",
  "description": "SearXNG integration proxy for AI",
  "main": "src/index.js",
  "scripts": {
    "start": "node src/index.js",
    "dev": "node src/index.js"
  },
  "dependencies": {
    "axios": "^1.6.0",
    "cheerio": "^1.0.0-rc.12",
    "cors": "^2.8.5",
    "dotenv": "^16.3.1",
    "express": "^4.18.2",
    "node-cache": "^5.1.2"
  }
}
```

- [ ] **Step 2: Install dependencies**

Run: `npm install`

- [ ] **Step 3: Create .env.example**

```env
SEARXNG_HOST=192.168.3.64
SEARXNG_PORT=8080
API_PORT=4001
CACHE_TTL=300
REQUEST_TIMEOUT=30000
```

- [ ] **Step 4: Create src/config/index.js**

```javascript
require('dotenv').config();

const SEARXNG_HOST = process.env.SEARXNG_HOST || '127.0.0.1';
const SEARXNG_PORT = process.env.SEARXNG_PORT || '8080';
const API_PORT = process.env.API_PORT || '4001';
const CACHE_TTL = process.env.CACHE_TTL || '300';
const REQUEST_TIMEOUT = process.env.REQUEST_TIMEOUT || '10000';

const SEARXNG_URL = `http://${SEARXNG_HOST}:${SEARXNG_PORT}`;

module.exports = {
  SEARXNG_HOST,
  SEARXNG_PORT,
  API_PORT,
  CACHE_TTL,
  REQUEST_TIMEOUT,
  SEARXNG_URL
};
```

- [ ] **Step 5: Commit**

```bash
git add package.json .env.example src/config/index.js
git commit -m "feat: init Node.js project and config"
```

---

## Task 2: Cache Service

**Files:**
- Create: `src/services/cache.js`
- Create: `tests/services/cache.test.js`

- [ ] **Step 1: Create tests/services/cache.test.js**

```javascript
const assert = require('assert');
const CacheService = require('../../src/services/cache');

// Mock config
const mockConfig = { CACHE_TTL: 5 }; // 5 seconds for testing

describe('CacheService', () => {
  let cache;

  before(() => {
    cache = new CacheService(mockConfig);
  });

  it('should generate a consistent key for same inputs', () => {
    const key1 = cache.generateKey('test', 10, 'auto', [], 'month');
    const key2 = cache.generateKey('test', 10, 'auto', [], 'month');
    assert.strictEqual(key1, key2);
  });

  it('should generate different keys for different queries', () => {
    const key1 = cache.generateKey('query1', 10, 'auto', [], 'month');
    const key2 = cache.generateKey('query2', 10, 'auto', [], 'month');
    assert.notStrictEqual(key1, key2);
  });

  it('should store and retrieve a value', () => {
    const key = 'test:123';
    cache.set(key, { foo: 'bar' });
    const value = cache.get(key);
    assert.deepStrictEqual(value, { foo: 'bar' });
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `npm test -- --grep "CacheService"`
Expected: FAIL with "Cannot find module"

- [ ] **Step 3: Write minimal implementation (src/services/cache.js)**

```javascript
const NodeCache = require('node-cache');
const crypto = require('crypto');

class CacheService {
  constructor(config) {
    // TTL is in seconds for node-cache
    this.cache = new NodeCache({ stdTTL: config.CACHE_TTL });
  }

  get(key) {
    return this.cache.get(key);
  }

  set(key, value) {
    this.cache.set(key, value);
  }

  generateKey(query, numResults, mode, engines, timeRange = "") {
    const data = `${query}|${numResults}|${mode}|${engines.join(',')}|${timeRange}`;
    const hashVal = crypto.createHash('md5').update(data).digest('hex');
    return `search:${hashVal}`;
  }
}

module.exports = CacheService;
```

- [ ] **Step 4: Run test to verify it passes**

Run: `npm test -- --grep "CacheService"`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/services/cache.js tests/services/cache.test.js
git commit -m "feat: implement TTL cache service with MD5 key generation"
```

---

## Task 3: Detect Mode Utility

**Files:**
- Create: `src/utils/detect_mode.js`
- Create: `tests/utils/detect_mode.test.js`

- [ ] **Step 1: Create tests/utils/detect_mode.test.js**

```javascript
const assert = require('assert');
const detectMode = require('../../src/utils/detect_mode');

describe('detectMode', () => {
  it('should return "list" for query with "什么"', () => {
    assert.strictEqual(detectMode('最新AI大模型有什么'), 'list');
  });
  it('should return "list" for query with "who"', () => {
    assert.strictEqual(detectMode('who is the president'), 'list');
  });
  it('should return "extract" for query with "为什么"', () => {
    assert.strictEqual(detectMode('为什么会下雨'), 'extract');
  });
  it('should return "extract" for query with "analyze"', () => {
    assert.strictEqual(detectMode('analyze the market trends'), 'extract');
  });
  it('should default to "list"', () => {
    assert.strictEqual(detectMode('hello world'), 'list');
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `npm test -- --grep "detectMode"`
Expected: FAIL with "Cannot find module"

- [ ] **Step 3: Write minimal implementation (src/utils/detect_mode.js)**

```javascript
const DETECT_LIST_PATTERNS = ["谁", "什么", "哪个", "多少", "何时", "哪里", "who", "what", "which", "how many", "when", "where"];
const DETECT_EXTRACT_PATTERNS = ["为什么", "怎么", "如何", "评价", "分析", "比较", "解释", "why", "how", "explain", "analyze", "compare", "evaluate"];

function detectMode(query) {
  const q = query.toLowerCase();
  if (DETECT_EXTRACT_PATTERNS.some(p => q.includes(p))) return "extract";
  if (DETECT_LIST_PATTERNS.some(p => q.includes(p))) return "list";
  return "list";
}

module.exports = detectMode;
```

- [ ] **Step 4: Run test to verify it passes**

Run: `npm test -- --grep "detectMode"`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/utils/detect_mode.js tests/utils/detect_mode.test.js
git commit -m "feat: implement mode detection utility"
```

---

## Task 4: Parser Utility

**Files:**
- Create: `src/utils/parser.js`
- Create: `tests/utils/parser.test.js`

- [ ] **Step 1: Create tests/utils/parser.test.js**

```javascript
const assert = require('assert');
const parseResults = require('../../src/utils/parser');

describe('parseResults', () => {
  it('should clean HTML from content', () => {
    const input = [{
      url: 'https://example.com',
      title: 'Test',
      content: '<p>Hello <b>World</b></p>',
      engine: 'google'
    }];
    const result = parseResults(input);
    assert.strictEqual(result[0].snippet, 'Hello World');
  });

  it('should deduplicate by URL', () => {
    const input = [
      { url: 'https://example.com', title: 'Test 1', content: '', engine: 'google' },
      { url: 'https://example.com', title: 'Test 2', content: '', engine: 'google' }
    ];
    const result = parseResults(input);
    assert.strictEqual(result.length, 1);
  });

  it('should keep results without publishedDate', () => {
    const input = [{ url: 'https://example.com', title: 'Test', content: '', engine: 'google' }];
    const result = parseResults(input);
    assert.strictEqual(result.length, 1);
    assert.strictEqual(result[0].publishedDate, null);
  });

  it('should normalize ISO date strings', () => {
    const input = [{
      url: 'https://example.com',
      title: 'Test',
      content: '',
      engine: 'google',
      publishedDate: '2026-05-01T12:00:00Z'
    }];
    const result = parseResults(input);
    assert.strictEqual(result[0].publishedDate, '2026-05-01');
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `npm test -- --grep "parseResults"`
Expected: FAIL with "Cannot find module"

- [ ] **Step 3: Write minimal implementation (src/utils/parser.js)**

```javascript
const cheerio = require('cheerio');

function parseResults(rawResults) {
  const seenUrls = new Set();
  const parsed = [];

  rawResults.forEach(item => {
    let content = item.content || '';
    if (content) {
      const $ = cheerio.load(content);
      content = $.text().trim();
    }

    const url = item.url || '';
    if (!url || seenUrls.has(url)) return;
    seenUrls.add(url);

    let published = item.publishedDate || item.pubdate;
    if (published) {
      try {
        // Handle ISO format and Z suffix
        const date = new Date(published.replace('Z', '+00:00'));
        if (!isNaN(date)) {
          published = date.toISOString().split('T')[0];
        } else {
          published = null;
        }
      } catch (e) {
        published = null;
      }
    }

    parsed.push({
      title: item.title || 'Untitled',
      url: url,
      snippet: content.slice(0, 500),
      engine: item.engine || 'unknown',
      publishedDate: published
    });
  });

  return parsed;
}

module.exports = parseResults;
```

- [ ] **Step 4: Run test to verify it passes**

Run: `npm test -- --grep "parseResults"`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/utils/parser.js tests/utils/parser.test.js
git commit -m "feat: implement HTML cleaning and URL dedup parser"
```

---

## Task 5: Aggregator Service

**Files:**
- Create: `src/services/aggregator.js`
- Create: `tests/services/aggregator.test.js`

- [ ] **Step 1: Create tests/services/aggregator.test.js**

```javascript
const assert = require('assert');
const aggregate = require('../../src/services/aggregator');

describe('aggregate', () => {
  it('should filter out results older than 1 month', () => {
    const now = new Date();
    const lastMonth = new Date(now.setMonth(now.getMonth() - 1)).toISOString().split('T')[0];
    const twoMonthsAgo = new Date(now.setMonth(now.getMonth() - 2)).toISOString().split('T')[0];

    const rawResults = [
      { url: 'https://a.com', title: 'A', content: '', engine: 'bing', publishedDate: lastMonth },
      { url: 'https://b.com', title: 'B', content: '', engine: 'bing', publishedDate: twoMonthsAgo }
    ];

    const result = aggregate(rawResults, 'test', 'list', 'month');
    assert.strictEqual(result.results.length, 1);
    assert.strictEqual(result.results[0].title, 'A');
  });

  it('should keep results without publishedDate when filtering', () => {
    const rawResults = [
      { url: 'https://a.com', title: 'A', content: '', engine: 'bing' }, // No date
      { url: 'https://b.com', title: 'B', content: '', engine: 'bing', publishedDate: '2020-01-01' }
    ];

    const result = aggregate(rawResults, 'test', 'list', 'month');
    assert.strictEqual(result.results.length, 2); // Keeps A (no date), removes B (old)
  });

  it('should detect mode if auto', () => {
    const rawResults = [{ url: 'https://a.com', title: 'A', content: '', engine: 'bing' }];
    const result = aggregate(rawResults, '为什么会下雨', 'auto', '');
    assert.strictEqual(result.mode, 'extract');
  });

  it('should truncate snippet for extract mode', () => {
    const rawResults = [{
      url: 'https://a.com',
      title: 'A',
      content: 'This is a very long snippet that exceeds two hundred characters and should be truncated according to the requirements of the extract mode in our system architecture.',
      engine: 'bing'
    }];

    const result = aggregate(rawResults, 'test', 'extract', '');
    assert.strictEqual(result.extractedData[0].keyInfo.length, 200);
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `npm test -- --grep "aggregate"`
Expected: FAIL with "Cannot find module"

- [ ] **Step 3: Write minimal implementation (src/services/aggregator.js)**

```javascript
const parseResults = require('../utils/parser');
const detectMode = require('../utils/detect_mode');

function aggregate(rawResults, query, mode, timeRange = "") {
  let parsed = parseResults(rawResults);

  // Hard filter by time_range
  if (timeRange) {
    const now = new Date();
    let threshold = new Date();

    if (timeRange === 'day') threshold.setDate(now.getDate() - 1);
    else if (timeRange === 'week') threshold.setDate(now.getDate() - 7);
    else if (timeRange === 'month') threshold.setDate(now.getDate() - 31);
    else if (timeRange === 'year') threshold.setDate(now.getDate() - 366);

    const thresholdStr = threshold.toISOString().split('T')[0];
    parsed = parsed.filter(r => {
      if (!r.publishedDate) return true; // Keep if no date
      return r.publishedDate >= thresholdStr;
    });
  }

  if (mode === 'auto') {
    mode = detectMode(query);
  }

  const results = parsed.map(r => ({
    title: r.title,
    url: r.url,
    snippet: r.snippet,
    engine: r.engine,
    publishedDate: r.publishedDate
  }));

  let extractedData = null;
  if (mode === 'extract') {
    extractedData = parsed.map(r => ({
      title: r.title,
      url: r.url,
      keyInfo: r.snippet.slice(0, 200)
    }));
  }

  return {
    mode: mode,
    results: results,
    extractedData: extractedData
  };
}

module.exports = aggregate;
```

- [ ] **Step 4: Run test to verify it passes**

Run: `npm test -- --grep "aggregate"`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/services/aggregator.js tests/services/aggregator.test.js
git commit -m "feat: implement time filtering and mode selection aggregator"
```

---

## Task 6: SearXNG Service

**Files:**
- Create: `src/services/searxng.js`
- Create: `tests/services/searxng.test.js`

- [ ] **Step 1: Create tests/services/searxng.test.js**

```javascript
const assert = require('assert');
const nock = require('nock'); // Use nock for HTTP mocking
const axios = require('axios');
const SearXNGService = require('../../src/services/searxng');

// Mock config
const mockConfig = {
  SEARXNG_URL: 'http://localhost:8080',
  REQUEST_TIMEOUT: 5000
};

describe('SearXNGService', () => {
  let service;

  before(() => {
    service = new SearXNGService(mockConfig);
    nock.disableNetConnect();
    nock.enableNetConnect('localhost');
  });

  after(() => {
    nock.enableNetConnect();
  });

  it('should call search endpoint with correct params', async () => {
    const scope = nock('http://localhost:8080')
      .get('/search')
      .query({ q: 'test', format: 'json' })
      .reply(200, { results: [{ url: 'http://test.com', title: 'Test' }] });

    const results = await service.search('test', 10, [], '');
    assert.strictEqual(results.length, 1);
    scope.done();
  });

  it('should check health by fetching root', async () => {
    const scope = nock('http://localhost:8080')
      .get('/')
      .reply(200, 'OK');

    const health = await service.isHealthy();
    assert.strictEqual(health, true);
    scope.done();
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `npm test -- --grep "SearXNGService"`
Expected: FAIL with "Cannot find module" or "nock not found"

- [ ] **Step 3: Write minimal implementation (src/services/searxng.js)**

```javascript
const axios = require('axios');

class SearXNGService {
  constructor(config) {
    this.SEARXNG_URL = config.SEARXNG_URL;
    this.REQUEST_TIMEOUT = config.REQUEST_TIMEOUT;
  }

  async search(query, numResults = 10, engines = [], timeRange = "") {
    const params = {
      q: query,
      format: 'json',
      categories: 'general'
    };

    if (engines.length > 0) {
      params.engines = engines.join(',');
    }

    if (timeRange) {
      params.time_range = timeRange;
    }

    try {
      const response = await axios.get(`${this.SEARXNG_URL}/search`, {
        params: params,
        timeout: this.REQUEST_TIMEOUT
      });

      const data = response.data;
      return (data.results || []).slice(0, numResults);
    } catch (error) {
      console.error(`SearXNG search error: ${error.message}`);
      return [];
    }
  }

  async isHealthy() {
    try {
      // Try health endpoint first if available, otherwise fallback to root
      await axios.get(`${this.SEARXNG_URL}/health`, { timeout: 2000 });
      return true;
    } catch (e) {
      try {
        await axios.get(this.SEARXNG_URL, { timeout: 2000 });
        return true;
      } catch (e2) {
        return false;
      }
    }
  }
}

module.exports = SearXNGService;
```

- [ ] **Step 4: Install nock for testing**

Run: `npm install nock --save-dev`

- [ ] **Step 5: Run test to verify it passes**

Run: `npm test -- --grep "SearXNGService"`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add src/services/searxng.js tests/services/searxng.test.js
git commit -m "feat: implement SearXNG HTTP client service"
```

---

## Task 7: Error Handler Middleware

**Files:**
- Create: `src/middleware/error_handler.js`

- [ ] **Step 1: Write src/middleware/error_handler.js**

```javascript
const errorHandler = (err, req, res, next) => {
  console.error(`Error: ${err.message}`);

  if (err.code === 'INVALID_PARAMS') {
    return res.status(400).json({
      success: false,
      error: { code: 'INVALID_PARAMS', message: err.message }
    });
  }

  if (err.code === 'REQUEST_TIMEOUT') {
    return res.status(504).json({
      success: false,
      error: { code: 'REQUEST_TIMEOUT', message: `Search service timeout: ${err.message}` }
    });
  }

  res.status(500).json({
    success: false,
    error: { code: 'INTERNAL_ERROR', message: err.message || 'Internal error' }
  });
};

module.exports = errorHandler;
```

- [ ] **Step 2: Commit**

```bash
git add src/middleware/error_handler.js
git commit -m "feat: implement global error handler middleware"
```

---

## Task 8: Search Route

**Files:**
- Create: `src/routes/search.js`

- [ ] **Step 1: Write src/routes/search.js**

```javascript
const express = require('express');
const router = express.Router();

// Mock inject for now - will be injected in index.js
let searxngService;
let cacheService;
let aggregateService;

function setDependencies(svc, cache, agg) {
  searxngService = svc;
  cacheService = cache;
  aggregateService = agg;
}

router.post('/search', async (req, res, next) => {
  try {
    const { query, num_results, mode, engines, time_range } = req.body;

    // Validation
    if (!query || typeof query !== 'string') {
      return next({ code: 'INVALID_PARAMS', message: 'query parameter is required and must be a string' });
    }

    const numResults = num_results || 10;
    if (numResults < 1 || numResults > 50) {
      return next({ code: 'INVALID_PARAMS', message: 'num_results must be between 1 and 50' });
    }

    const validModes = ['auto', 'list', 'extract'];
    const currentMode = mode || 'auto';
    if (!validModes.includes(currentMode)) {
      return next({ code: 'INVALID_PARAMS', message: 'mode must be auto, list, or extract' });
    }

    const validTimeRanges = ['', 'day', 'week', 'month', 'year'];
    const currentTimeRange = time_range || '';
    if (!validTimeRanges.includes(currentTimeRange)) {
      return next({ code: 'INVALID_PARAMS', message: 'time_range must be day, week, month, year or empty' });
    }

    const engineList = engines || [];

    // Cache check
    const cacheKey = cacheService.generateKey(query, numResults, currentMode, engineList, currentTimeRange);
    const cached = cacheService.get(cacheKey);
    if (cached) {
      cached.meta.cached = true;
      return res.json({ success: true, data: cached });
    }

    // Call SearXNG
    const start = Date.now();
    const rawResults = await searxngService.search(query, numResults, engineList, currentTimeRange);

    // Aggregate
    const result = aggregateService(rawResults, query, currentMode, currentTimeRange);

    const response = {
      query: query,
      mode: result.mode,
      results: result.results,
      extractedData: result.extractedData,
      meta: {
        total: result.results.length,
        cached: false,
        responseTime: Date.now() - start
      }
    };

    cacheService.set(cacheKey, response);

    res.json({ success: true, data: response });
  } catch (error) {
    next({ code: 'REQUEST_TIMEOUT', message: error.message });
  }
});

module.exports = { router, setDependencies };
```

- [ ] **Step 2: Commit**

```bash
git add src/routes/search.js
git commit -m "feat: implement POST /api/search endpoint with validation and caching"
```

---

## Task 9: Application Entry Point

**Files:**
- Create: `src/index.js`

- [ ] **Step 1: Write src/index.js**

```javascript
const express = require('express');
const cors = require('cors');
const config = require('./config');
const errorHandler = require('./middleware/error_handler');
const { router: searchRouter, setDependencies } = require('./routes/search');

// Initialize services
const SearXNGService = require('./services/searxng');
const CacheService = require('./services/cache');
const aggregate = require('./services/aggregator');

const searxngService = new SearXNGService(config);
const cacheService = new CacheService(config);

// Inject dependencies into search route
setDependencies(searxngService, cacheService, aggregate);

const app = express();

// Middleware
app.use(cors());
app.use(express.json());

// Routes
app.use('/api', searchRouter);

// Health check
app.get('/health', async (req, res) => {
  const searxngOk = await searxngService.isHealthy();
  res.json({
    status: 'ok',
    searxng: searxngOk ? 'running' : 'stopped'
  });
});

// Error handler
app.use(errorHandler);

const PORT = config.API_PORT;
app.listen(PORT, () => {
  console.log(`WebSearch Backend starting...`);
  console.log(`SearXNG URL: ${config.SEARXNG_URL}`);
  console.log(`Server running on port ${PORT}`);
});
```

- [ ] **Step 2: Commit**

```bash
git add src/index.js
git commit -m "feat: wire up Express application entry point"
```

---

## Task 10: Update Documentation

**Files:**
- Modify: `README.md`
- Modify: `SPEC.md`

- [ ] **Step 1: Update README.md**

... (Update dependencies list and environment variables to reflect Node.js implementation)

- [ ] **Step 2: Update SPEC.md**

... (Update tech stack table to show Node.js/Express instead of Python/FastAPI)

- [ ] **Step 3: Commit**

```bash
git add README.md SPEC.md
git commit -m "docs: update documentation for Node.js refactor"
```

---

## Execution Checklist

- [ ] Task 1: Project Setup
- [ ] Task 2: Cache Service
- [ ] Task 3: Detect Mode Utility
- [ ] Task 4: Parser Utility
- [ ] Task 5: Aggregator Service
- [ ] Task 6: SearXNG Service
- [ ] Task 7: Error Handler Middleware
- [ ] Task 8: Search Route
- [ ] Task 9: Application Entry Point
- [ ] Task 10: Update Documentation

**Plan complete and saved to `docs/superpowers/plans/2026-05-01-nodejs-express-refactor.md`. Two execution options:**

**1. Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints

**Which approach?**