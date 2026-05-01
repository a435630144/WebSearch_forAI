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