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