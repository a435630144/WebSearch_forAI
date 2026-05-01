const errorHandler = (err, req, res, next) => {
  console.error(`Error: ${err.message}`);

  if (err.code === 'INVALID_PARAMS') {
    return res.status(400).json({
      success: false,
      error: { code: 'INVALID_PARAMS', message: err.message }
    });
  }

  if (err.code === 'REQUEST_TIMEOUT') {
    return res.status(504).json({
      success: false,
      error: { code: 'REQUEST_TIMEOUT', message: `Search service timeout: ${err.message}` }
    });
  }

  res.status(500).json({
    success: false,
    error: { code: 'INTERNAL_ERROR', message: err.message || 'Internal error' }
  });
};

module.exports = errorHandler;