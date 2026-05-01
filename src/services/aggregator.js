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
