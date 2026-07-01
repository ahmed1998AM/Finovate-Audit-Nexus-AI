"""
Finovate Audit Nexus AI - Task Queue
Async background task processing with thread pool and Celery fallback
"""

import asyncio
import logging
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from enum import Enum
from functools import wraps
from typing import Any, Callable, Coroutine, Dict, List, Optional

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Task:
    def __init__(self, task_id: str, name: str, fn: Callable, args: tuple, kwargs: dict):
        self.task_id = task_id
        self.name = name
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.status = TaskStatus.PENDING
        self.result: Any = None
        self.error: Optional[str] = None
        self.created_at = datetime.now()
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None


class TaskQueue:
    def __init__(self, max_workers: int = 4):
        self._executor = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="task")
        self._tasks: Dict[str, Task] = {}
        self._max_history = 1000
        self._loop: Optional[asyncio.AbstractEventLoop] = None

    def _get_loop(self):
        if self._loop is None or self._loop.is_closed():
            try:
                self._loop = asyncio.get_running_loop()
            except RuntimeError:
                self._loop = asyncio.new_event_loop()
        return self._loop

    def submit(self, name: str, fn: Callable, *args, **kwargs) -> str:
        task_id = f"task_{uuid.uuid4().hex[:12]}"
        task = Task(task_id, name, fn, args, kwargs)
        self._tasks[task_id] = task

        def _run():
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.now()
            try:
                result = fn(*args, **kwargs)
                task.result = result
                task.status = TaskStatus.SUCCESS
                logger.info(f"Task completed: {name} ({task_id})")
            except Exception as e:
                task.error = str(e)
                task.status = TaskStatus.FAILED
                logger.error(f"Task failed: {name} ({task_id}): {e}")
            finally:
                task.completed_at = datetime.now()
                self._trim_history()

        self._executor.submit(_run)
        logger.info(f"Task submitted: {name} ({task_id})")
        return task_id

    async def submit_async(self, name: str, coro: Coroutine) -> str:
        task_id = f"task_{uuid.uuid4().hex[:12]}"
        task = Task(task_id, name, coro, (), {})
        self._tasks[task_id] = task

        async def _run():
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.now()
            try:
                result = await coro
                task.result = result
                task.status = TaskStatus.SUCCESS
            except Exception as e:
                task.error = str(e)
                task.status = TaskStatus.FAILED
            finally:
                task.completed_at = datetime.now()
                self._trim_history()

        loop = self._get_loop()
        loop.create_task(_run())
        return task_id

    def get_task(self, task_id: str) -> Optional[Task]:
        return self._tasks.get(task_id)

    def get_status(self, task_id: str) -> Optional[TaskStatus]:
        task = self._tasks.get(task_id)
        return task.status if task else None

    def get_result(self, task_id: str) -> Any:
        task = self._tasks.get(task_id)
        if task and task.status == TaskStatus.SUCCESS:
            return task.result
        return None

    def cancel(self, task_id: str) -> bool:
        task = self._tasks.get(task_id)
        if task and task.status in (TaskStatus.PENDING, TaskStatus.RUNNING):
            task.status = TaskStatus.CANCELLED
            return True
        return False

    def list_tasks(self, status: Optional[TaskStatus] = None, limit: int = 50) -> List[Dict[str, Any]]:
        tasks = list(self._tasks.values())
        if status:
            tasks = [t for t in tasks if t.status == status]
        tasks.sort(key=lambda t: t.created_at, reverse=True)
        return [
            {
                "task_id": t.task_id,
                "name": t.name,
                "status": t.status.value,
                "created_at": t.created_at.isoformat(),
                "started_at": t.started_at.isoformat() if t.started_at else None,
                "completed_at": t.completed_at.isoformat() if t.completed_at else None,
                "error": t.error,
            }
            for t in tasks[:limit]
        ]

    def _trim_history(self):
        if len(self._tasks) > self._max_history:
            completed_ids = [
                tid for tid, t in self._tasks.items()
                if t.status in (TaskStatus.SUCCESS, TaskStatus.FAILED, TaskStatus.CANCELLED)
            ]
            excess = len(self._tasks) - self._max_history
            for tid in sorted(completed_ids)[:excess]:
                del self._tasks[tid]

    def shutdown(self, wait: bool = True):
        self._executor.shutdown(wait=wait)
        logger.info("Task queue shut down")


_task_queue_instance: Optional[TaskQueue] = None


def get_task_queue() -> TaskQueue:
    global _task_queue_instance
    if _task_queue_instance is None:
        _task_queue_instance = TaskQueue()
    return _task_queue_instance


def async_task(name: str = None):
    def decorator(func: Callable) -> Callable:
        task_name = name or func.__name__

        @wraps(func)
        def wrapper(*args, **kwargs) -> str:
            queue = get_task_queue()
            return queue.submit(task_name, func, *args, **kwargs)

        return wrapper
    return decorator
