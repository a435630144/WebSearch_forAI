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