require('dotenv').config();

const SEARXNG_HOST = process.env.SEARXNG_HOST || '127.0.0.1';
const SEARXNG_PORT = process.env.SEARXNG_PORT || '8080';
const API_PORT = process.env.API_PORT || '4001';
const CACHE_TTL = process.env.CACHE_TTL || '300';
const REQUEST_TIMEOUT = process.env.REQUEST_TIMEOUT || '10000';

const SEARXNG_URL = `http://${SEARXNG_HOST}:${SEARXNG_PORT}`;

module.exports = {
  SEARXNG_HOST,
  SEARXNG_PORT,
  API_PORT,
  CACHE_TTL,
  REQUEST_TIMEOUT,
  SEARXNG_URL
};
