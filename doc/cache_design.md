# Baseline and Cache Design

## Objective
Evaluate Redis caching for department-wise employee statistics and document performance, TTL, cache keys, invalidation, and freshness.

## Selected Read-Heavy Operation
Department-wise employee summary is the primary caching candidate because the same statistics may be requested repeatedly.

## Cache Configuration
- Backend: Redis
- Cache key: `employee:department_summary:v1`
- TTL: 300 seconds (5 minutes)

## Cache Key Convention
- Department summary: `employee:department_summary:v1`
- Employee list: `employee:list:v1`
- Employee details: `employee:detail:<employee_id>:v1`

Employee list cache keys should include relevant filters and pagination parameters if list caching is implemented.

## Invalidation Strategy
Delete the department summary cache after successful employee changes that affect department statistics, such as creation, department transfer, deactivation, or deletion.

Automatic invalidation integration requires code verification.

## Freshness Expectations
The department summary has a five-minute TTL. Explicit invalidation should refresh the summary after relevant changes. TTL provides fallback expiration.

## Initial Performance Measurement
- Database aggregation average: 1.52 ms
- Cached service HIT average: 1.57 ms
- Results matched: True

This initial microbenchmark does not demonstrate a performance improvement. It compares database aggregation time with cached service time, not full API response time. A controlled same-endpoint benchmark is still required.

## Validation
- Redis connectivity: Verified
- Cache HIT and MISS: Verified
- Manual invalidation: Verified
- Data consistency after invalidation: Verified
- Automatic invalidation after employee changes: Pending verification
- TTL expiration: Pending verification
- Full API response-time comparison: Pending
