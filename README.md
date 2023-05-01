# Fast utils for work with MOEX data
### Fast utils for work with financial data (MOEX). Pet project for update skill in python concurrency.

# Description:
REST API for work with information about stock exchange data:
> - Markets type
> - Indexes
> - Market data
> - Historical data
> - OTC, RPS (Negotiated trades mode), REPO
> - Equities, Bonds, FX and Derivatives info
> - Issuers
> - Listing
> - Investor calendar
> - Stock info
> - Fixings
> - Exchange rates
> - Information Disclosure

This service can use as part of product for trading, analyses or deals control.

## Assumptions:
 - Use Postgres
 - Only Raw SQL (for fast development) 
 - Only API, without front (but there is a swagger)
 - Need multi-processor machine
 - Cache is allowed (Redis or memcache)
 - Without auth or user roles (at first time)
 - Minimum request to external services (as a rule)

# Use instruments:
## asyncio
- [x] coroutines
- [ ] future
- [x] tasks
- [x] loop
- [ ] events
- [x] gather
- [x] create_task
- [x] run_until_complete
- [ ] task done/cancel
- [ ] wait_for
- [ ] task shield
- [x] get_event_loop / get_running_loop
- [ ] call_soon
- [ ] call_later
- [ ] loop debug
- [ ] all_tasks
- [ ] as_completed (+ timeout)
- [ ] wait (return_when options)
- [ ] async generator
- [x] run_in_executor
- [ ] ContextVar
- [ ] run_coroutine_threadsafe
- [ ] call_soon_threadsafe
- [ ] run_forever
- [ ] Lock
- [ ] Semaphore
- [ ] Event
- [ ] Condition (+ wait_for)
- [x] Queue, PriorityQueue, LifoQueue

## Threads, process and concurrent
- [x] ProcessPoolExecutor (map)
- [ ] ThreadPoolExecutor
- [ ] MapReduce on multiprocessor (pattern)
- [ ] Shared multiprocess values, serializers
- [ ] Executor initializer (pool executors)
- [ ] Lock / RLock
- [ ] Circuit breaker pattern
- [ ] Semaphore

## Frameworks and other libs
- [x] aiohttp (sessions, timeouts)
- [x] fastapi
- [x] logging
- [ ] uvloop (linux container)
- [x] asyncpg (pools, execute/many, fetch, transactions, cursor)
- [x] dataclass, enums
- [x] pydantic
- [x] other standard libs and instruments (functools, itertools etc)