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
- [ ] coroutines
- [ ] future
- [ ] tasks
- [ ] loop
- [ ] events
- [ ] gather
- [ ] create_task
- [ ] get_event_loop
- [ ] run_until_complete
- [ ] task done/cancel
- [ ] wait_for
- [ ] task shield
- [ ] get_event_loop / get_running_loop
- [ ] call_soon
- [ ] call_later
- [ ] loop debug
- [ ] all_tasks
- [ ] as_completed (+ timeout)
- [ ] wait (return_when options)
- [ ] async generator
- [ ] run_in_executor
- [ ] ContextVar
- [ ] run_coroutine_threadsafe
- [ ] call_soon_threadsafe
- [ ] run_forever
- [ ] Lock
- [ ] Semaphore
- [ ] Event
- [ ] Condition (+ wait_for)
- [ ] Queue, PriorityQueue, LifoQueue

## Threads, process and concurrent
- [ ] threading
- [ ] multiprocessing (apply_async)
- [ ] ProcessPoolExecutor (map)
- [ ] ThreadPoolExecutor
- [ ] MapReduce on multiprocessor (pattern)
- [ ] Shared multiprocess values, serializers
- [ ] Executor initializer (pool executors)
- [ ] Lock / RLock
- [ ] Circuit breaker pattern
- [ ] Semaphore

## Frameworks and other libs
- [ ] aiohttp (sessions, timeouts)
- [ ] fastapi
- [ ] logging
- [ ] uvloop (linux container)
- [ ] asyncpg (pools, execute/many, fetch, transactions, cursor)
- [ ] contextlib.suppress
- [ ] dataclass, enums
- [ ] pydantic
- [ ] other standard libs and instruments (functools, itertools etc)