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
    } else {
      published = null;
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