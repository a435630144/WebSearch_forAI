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
