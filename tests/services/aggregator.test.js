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
      { url: 'https://a.com', title: 'A', content: '', engine: 'bing' }, // No date - kept
      { url: 'https://b.com', title: 'B', content: '', engine: 'bing', publishedDate: '2020-01-01' } // Old date - removed
    ];

    const result = aggregate(rawResults, 'test', 'list', 'month');
    assert.strictEqual(result.results.length, 1); // Keeps A (no date), removes B (old)
    assert.strictEqual(result.results[0].title, 'A');
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
      content: 'This is a very long snippet that exceeds two hundred characters and should be truncated according to the requirements of the extract mode in our system architecture and all the related specifications.',
      engine: 'bing'
    }];

    const result = aggregate(rawResults, 'test', 'extract', '');
    assert.strictEqual(result.extractedData[0].keyInfo.length, 200);
  });
});
