---
name: Redis
description: "Use Redis effectively for caching, queues, and data structures with proper expiration and persistence."
---

## Expiration (Memory Leaks)

- Keys without TTL live forever—set expiry on every cache key: `SET key value EX 3600`
- Can't add TTL after SET without another command—use `SETEX` or `SET ... EX`
- `EXPIRE` resets on key update by default—`SET` removes TTL; use `SET ... KEEPTTL` (Redis 6+)
- Lazy expiration: expired keys removed on access—may consume memory until touched
- `SCAN` with large database: expired keys still show until cleanup cycle runs

## Data Structures I Underuse

- Sorted sets for rate limiting: `ZADD limits:{user} {now} {request_id}` + `ZREMRANGEBYSCORE` for sliding window
- HyperLogLog for unique counts: `PFADD visitors {ip}` uses 12KB for billions of uniques
- Streams for queues: `XADD`, `XREAD`, `XACK`—better than LIST for reliable queues
- Hashes for objects: `HSET user:1 name "Alice" email "a@b.com"`—more memory efficient than JSON string

## Atomicity Traps

- `GET` then `SET` is not atomic—another client can modify between; use `INCR`, `SETNX`, or Lua
- `SETNX` for locks: `SET lock:resource {token} NX EX 30`—NX = only if not exists
- `WATCH`/`MULTI`/`EXEC` for optimistic locking—transaction aborts if watched key changed
- Lua scripts are atomic—use for complex operations: `EVAL "script" keys args`

## Pub/Sub Limitations

- Messages not persisted—subscribers miss messages sent while disconnected
- At-most-once delivery—no acknowledgment, no retry
- Use Streams for reliable messaging—`XREAD BLOCK` + `XACK` pattern
- Pub/Sub across cluster: message goes to all nodes—works but adds overhead

## Persistence Configuration

- RDB (snapshots): fast recovery, but data loss between snapshots—default every 5min
- AOF (append log): less data loss, slower recovery—`appendfsync everysec` is good balance
- Both off = pure cache—acceptable if data can be regenerated
- `BGSAVE` for manual snapshot—doesn't block but forks process, needs memory headroom

## Memory Management (Critical)

- `maxmemory` must be set—without it, Redis uses all RAM, then swap = disaster
- Eviction policies: `allkeys-lru` for cache, `volatile-lru` for mixed, `noeviction` for persistent data
- `INFO memory` shows usage—monitor `used_memory` vs `maxmemory`
- Large keys hurt eviction—one 1GB key evicts poorly; prefer many small keys

## Clustering

- Hash slots: keys distributed by hash—same slot required for multi-key operations
- Hash tags: `{user:1}:profile` and `{user:1}:sessions` go to same slot—use for related keys
- No cross-slot `MGET`/`MSET`—error unless all keys in same slot
- `MOVED` redirect: client must follow—use cluster-aware client library

## Common Patterns

- Cache-aside: check Redis, miss → fetch DB → write Redis—standard caching
- Write-through: write DB + Redis together—keeps cache fresh
- Rate limiter: `INCR requests:{ip}:{minute}` with `EXPIRE`—simple fixed window
- Distributed lock: `SET ... NX EX` + unique token—verify token on release

## Connection Management

- Connection pooling: reuse connections—creating is expensive
- Pipeline commands: send batch without waiting—reduces round trips
- `QUIT` on shutdown—graceful disconnect
- Sentinel or Cluster for HA—single Redis is SPOF

## Common Mistakes

- No TTL on cache keys—memory grows until OOM
- Using as primary database without persistence—data loss on restart
- Blocking operations in single-threaded Redis—`KEYS *` blocks everything; use `SCAN`
- Storing large blobs—Redis is RAM; 100MB values are expensive
- Ignoring `maxmemory`—production Redis without limit will crash host
