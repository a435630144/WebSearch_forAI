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