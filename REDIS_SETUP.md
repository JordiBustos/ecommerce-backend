# Redis Caching Setup Guide

This guide explains how to set up and use Redis caching in the e-commerce backend. Redis is used to cache frequently accessed data like best-selling products, improving response times significantly.

## What is Redis?

Redis is an in-memory data structure store used as a database, cache, and message broker. In this project, we use it to cache expensive database queries.

## Features

- ⚡ **Fast Response Times**: Cache hits return data in milliseconds instead of querying the database
- 🔄 **Automatic Expiration**: Cached data expires after a configurable TTL (Time To Live)
- 🛡️ **Graceful Fallback**: Application works perfectly even if Redis is not available
- 🧹 **Manual Cache Clearing**: Admin endpoint to force cache refresh
- 📊 **Logging**: Detailed logs for cache hits, misses, and errors

## Current Implementation

### Best-Selling Products Endpoint

The `/api/v1/best-selling/` endpoint uses Redis caching:

**Without Cache:**

1. Query joins Product and OrderItem tables
2. Groups by product ID
3. Sums quantities and sorts
4. Returns results
   ⏱️ ~50-200ms depending on data size

**With Cache:**

1. Check Redis for cached product IDs
2. If found (cache HIT), fetch products by IDs
3. If not found (cache MISS), run query and cache results
   ⏱️ ~5-15ms on cache hit

**Cache Strategy:**

- Cache key: `best_selling:limit:{N}` (e.g., `best_selling:limit:12`)
- TTL: 5 minutes (configurable via `CACHE_TTL`)
- Stores only product IDs (lightweight)
- Maintains product order from original query

## Installation

### 1. Install Redis

**Ubuntu/Debian:**

```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis
sudo systemctl enable redis
```

**macOS (using Homebrew):**

```bash
brew install redis
brew services start redis
```

**Docker (recommended for development):**

```bash
docker run -d \
  --name redis \
  -p 6379:6379 \
  redis:7-alpine
```

**Windows:**

- Download from https://github.com/microsoftarchive/redis/releases
- Or use Docker Desktop with the command above

### 2. Verify Redis is Running

```bash
redis-cli ping
# Should return: PONG
```

### 3. Configure Application

Add to your `.env` file:

```env
# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=
CACHE_TTL=300  # 5 minutes in seconds
```

## Graceful Degradation

**The application works perfectly without Redis!**

If Redis is not available:

1. Connection attempt times out (2 seconds)
2. Warning is logged: `Redis not available: [error]. Falling back to database-only queries.`
3. All requests query the database directly
4. No errors or exceptions are thrown
5. Application continues to function normally

This makes Redis truly optional for development and testing.

### Security

If exposing Redis to the internet:

```env
REDIS_PASSWORD=your-strong-password-here
```

And configure Redis:

```bash
# In redis.conf
requirepass your-strong-password-here
```
