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