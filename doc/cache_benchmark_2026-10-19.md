# Cache Design and Baseline Measurement — 19 October 2026

## 1. Objective
Measure department summary performance with Redis caching and verify cache invalidation.

## 2. Cache Strategy
- Cache key: `employee:department_summary:v1`
- Cache TTL: 300 seconds (5 minutes)
- Cached data: Department-wise employee counts
- Cache miss: Fetch summary from the database and cache the result
- Cache hit: Return cached data without executing the summary database query

## 3. Benchmark Results

| Run | Cache status | Latency | Database queries |
|---|---|---:|---:|
| 1 | MISS | 3.05 ms | 1 |
| 2 | HIT | 0.87 ms | 0 |
| 3 | HIT | 0.62 ms | 0 |
| 4 | HIT | 0.75 ms | 0 |
| 5 | HIT | 1.15 ms | 0 |

- First-run latency: 3.05 ms
- Average cache-hit latency: 0.85 ms
- Database queries on cache hits: 0
- Cache-hit latency was approximately 72% lower than the first-run latency in this sample.

*Note: These are local measurements from one test session, not a production performance guarantee.*

## 4. Department Summary Observed

| Department | Employee count |
|---|---:|
| Backend | 14 |
| Frontend | 1 |
| IT | 16 |
| Unassigned (`None`) | 8 |
| **Total** | **39** |

## 5. Cache Invalidation Test

1. Confirmed the summary was cached.
2. Called `invalidate_department_employee_summary()`.
3. Confirmed the cache key was removed.
4. Requested the summary again.
5. Observed a cache MISS and successful cache rebuild.

**Result:** Cache invalidation and rebuilding passed.

## 6. Invalidation Matrix

| Event | Expected behaviour | Status |
|---|---|---|
| Cache miss | Query database and populate cache | Tested — passed |
| Cache hit | Return cached summary; no summary DB query | Tested — passed |
| Explicit invalidation | Remove cached summary | Tested — passed |
| Rebuild after invalidation | Query DB and repopulate cache | Tested — passed |
| TTL expiry after 300 seconds | Cache miss and refresh | Pending |
| Employee create/update/delete | Invalidate summary where applicable | Pending verification |
| Redis unavailable | Return database result without unhandled cache error | Pending verification |

## 7. Conclusion
Redis caching reduced the measured department-summary latency from 3.05 ms on the initial run to an average of 0.85 ms across four cache-hit runs. Cache hits required zero database queries for the measured summary operation. Invalidation and cache rebuilding passed. TTL expiry, write-event invalidation, and Redis outage fallback still require verification.