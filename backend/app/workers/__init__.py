#!/usr/bin/env python3
"""
NFM-X Workers Module
====================

Provides background worker functionality for async processing.
Handles tasks like embedding generation, memory indexing, and cleanup.

Urdu: Background workers ke liye module
"""

from typing import Dict, Any, List, Optional, Callable, Awaitable
import asyncio
import threading
from queue import Queue
from concurrent.futures import ThreadPoolExecutor
import time
from dataclasses import dataclass, field
from enum import Enum


class WorkerStatus(Enum):
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"


class TaskPriority(Enum):
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class WorkerTask:
    task_id: str
    function: Callable
    args: tuple = ()
    kwargs: Dict[str, Any] = field(default_factory=dict)
    priority: TaskPriority = TaskPriority.NORMAL
    retry_count: int = 0
    max_retries: int = 3
    created_at: float = field(default_factory=time.time)
    completed: bool = False
    result: Any = None
    error: Optional[Exception] = None


class WorkerPool:
    def __init__(self, num_workers: int = 4, queue_size: int = 100):
        self.num_workers = num_workers
        self.task_queue = Queue(maxsize=queue_size)
        self.workers: List = []
        self.status = WorkerStatus.IDLE
        self.executor = ThreadPoolExecutor(max_workers=num_workers)
        self._running = False
    
    def start(self):
        if self._running:
            return
        self._running = True
        self.status = WorkerStatus.RUNNING
        for i in range(self.num_workers):
            worker = WorkerThread(f"worker-{i}", self.task_queue)
            self.workers.append(worker)
            worker.start()
    
    def stop(self, wait: bool = True):
        self._running = False
        self.status = WorkerStatus.STOPPED
        for worker in self.workers:
            worker.stop()
        if wait:
            for worker in self.workers:
                worker.join()
        self.executor.shutdown(wait=wait)
    
    def submit_task(self, task: WorkerTask) -> bool:
        try:
            self.task_queue.put(task)
            return True
        except Exception:
            return False
    
    def submit(self, function: Callable, *args, **kwargs) -> Optional[WorkerTask]:
        import uuid
        task = WorkerTask(
            task_id=str(uuid.uuid4()), function=function, args=args, kwargs=kwargs
        )
        if self.submit_task(task):
            return task
        return None
    
    def get_status(self) -> Dict[str, Any]:
        return {
            'status': self.status.value, 'num_workers': self.num_workers,
            'active_workers': sum(1 for w in self.workers if hasattr(w, 'is_alive') and w.is_alive()),
            'queue_size': self.task_queue.qsize(), 'running': self._running
        }


class WorkerThread(threading.Thread):
    def __init__(self, name: str, task_queue: Queue):
        super().__init__(name=name, daemon=True)
        self.task_queue = task_queue
        self._stop_event = threading.Event()
        self.status = WorkerStatus.IDLE
    
    def run(self):
        self.status = WorkerStatus.RUNNING
        while not self._stop_event.is_set():
            try:
                task = self.task_queue.get(timeout=1.0)
                if task is None:
                    break
                self.status = WorkerStatus.RUNNING
                try:
                    task.result = task.function(*task.args, **task.kwargs)
                    task.completed = True
                    task.error = None
                except Exception as e:
                    task.error = e
                    task.completed = False
                    task.retry_count += 1
                    if task.retry_count < task.max_retries:
                        self.task_queue.put(task)
                self.task_queue.task_done()
            except Exception:
                self.status = WorkerStatus.IDLE
                continue
        self.status = WorkerStatus.STOPPED
    
    def stop(self):
        self._stop_event.set()


class AsyncWorkerPool:
    def __init__(self, num_workers: int = 4):
        self.num_workers = num_workers
        self.task_queue = asyncio.Queue(maxsize=100)
        self.workers: List = []
        self._running = False
    
    async def start(self):
        if self._running:
            return
        self._running = True
        for i in range(self.num_workers):
            worker = asyncio.create_task(self._worker_coroutine(f"async-worker-{i}"))
            self.workers.append(worker)
    
    async def stop(self):
        self._running = False
        for worker in self.workers:
            worker.cancel()
        await asyncio.gather(*self.workers, return_exceptions=True)
        self.workers = []
    
    async def _worker_coroutine(self, name: str):
        while self._running:
            try:
                task = await asyncio.wait_for(self.task_queue.get(), timeout=1.0)
                if task is None:
                    break
                try:
                    if asyncio.iscoroutinefunction(task.function):
                        task.result = await task.function(*task.args, **task.kwargs)
                    else:
                        task.result = task.function(*task.args, **task.kwargs)
                    task.completed = True
                    task.error = None
                except Exception as e:
                    task.error = e
                    task.completed = False
                    task.retry_count += 1
                    if task.retry_count < task.max_retries:
                        await self.task_queue.put(task)
                self.task_queue.task_done()
            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                break
    
    async def submit_task(self, task: WorkerTask) -> bool:
        try:
            await self.task_queue.put(task)
            return True
        except Exception:
            return False
    
    async def submit(self, function: Callable, *args, **kwargs) -> Optional[WorkerTask]:
        import uuid
        task = WorkerTask(
            task_id=str(uuid.uuid4()), function=function, args=args, kwargs=kwargs
        )
        if await self.submit_task(task):
            return task
        return None


worker_pool = WorkerPool(num_workers=4)
async_worker_pool = AsyncWorkerPool(num_workers=4)


# Urdu: NFM-X workers module - Background processing ke liye