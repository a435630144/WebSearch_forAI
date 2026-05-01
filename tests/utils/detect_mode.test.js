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