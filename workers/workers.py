"""
WORKERS FOR MULTIPROCESS CALCULATIONS.
It's a bad pattern for high-loaded system because use additional resource for frequent creation of processes.
Use this only in small project.

FIX FOR FUTURE: create calculation workers in new containers and use cache and queue. Redis, for example.
"""
import asyncio

from dataclasses import dataclass
from db import pool_for_process
from config import QUEUE_PROCESS, settings
from concurrent.futures import ProcessPoolExecutor
from functools import partial


@dataclass
class TaskModel:
    task: partial
    need_db: bool = False
    pool_attribute_name: str = "pool"


async def run_task_with_db(task: TaskModel):
    async with pool_for_process() as pool:
        await task.task(**{task.pool_attribute_name: pool})


def run_task_in_new_process(task: TaskModel):
    if not asyncio.iscoroutinefunction(task.task):
        return task.task()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        if task.need_db:
            loop.run_until_complete(run_task_with_db(task))
        else:
            loop.run_until_complete(task.task())
    finally:
        loop.close()


async def process_workers():
    loop = asyncio.get_running_loop()
    with ProcessPoolExecutor(max_workers=settings.MAX_PROCESS) as executor:
        print("ProcessPool Running")
        while True:
            partial_task: TaskModel = await QUEUE_PROCESS.get()
            loop.run_in_executor(executor, partial(run_task_in_new_process, partial_task))
