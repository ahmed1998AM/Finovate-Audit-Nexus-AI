"""
Finovate Audit Nexus AI - Event Bus System
Internal pub/sub event bus for service communication
"""

import asyncio
import inspect
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


class EventPriority(Enum):
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3


@dataclass
class Event:
    event_type: str
    data: Dict[str, Any] = field(default_factory=dict)
    source: str = "system"
    priority: EventPriority = EventPriority.NORMAL
    timestamp: datetime = field(default_factory=datetime.now)
    event_id: str = ""


class EventBus:
    def __init__(self, max_handlers_per_event: int = 50):
        self._handlers: Dict[str, List[Callable]] = {}
        self._once_handlers: Dict[str, List[Callable]] = {}
        self._history: List[Event] = []
        self._max_history: int = 1000
        self._max_handlers = max_handlers_per_event
        self._lock = asyncio.Lock()

    def on(self, event_type: str, handler: Callable):
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        if len(self._handlers[event_type]) >= self._max_handlers:
            logger.warning(f"Max handlers ({self._max_handlers}) reached for event: {event_type}")
            return
        self._handlers[event_type].append(handler)
        logger.debug(f"Handler registered for event: {event_type}")

    def once(self, event_type: str, handler: Callable):
        if event_type not in self._once_handlers:
            self._once_handlers[event_type] = []
        self._once_handlers[event_type].append(handler)

    def off(self, event_type: str, handler: Optional[Callable] = None):
        if handler is None:
            self._handlers.pop(event_type, None)
            self._once_handlers.pop(event_type, None)
            return
        handlers = self._handlers.get(event_type, [])
        if handler in handlers:
            handlers.remove(handler)
        once_handlers = self._once_handlers.get(event_type, [])
        if handler in once_handlers:
            once_handlers.remove(handler)

    async def emit(self, event_type: str, data: Optional[Dict[str, Any]] = None, source: str = "system", priority: EventPriority = EventPriority.NORMAL):
        event = Event(
            event_type=event_type,
            data=data or {},
            source=source,
            priority=priority,
            timestamp=datetime.now(),
            event_id=f"{event_type}_{datetime.now().timestamp()}"
        )
        self._history.append(event)
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history:]

        async with self._lock:
            once_handlers = self._once_handlers.pop(event_type, [])
            handlers = self._handlers.get(event_type, [])

        all_handlers = handlers + once_handlers
        if not all_handlers:
            logger.debug(f"No handlers for event: {event_type}")
            return

        for handler in all_handlers:
            try:
                if inspect.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
            except Exception as e:
                logger.error(f"Handler failed for event {event_type}: {e}")

    def history(self, event_type: Optional[str] = None, limit: int = 100) -> List[Event]:
        filtered = [e for e in self._history if event_type is None or e.event_type == event_type]
        return filtered[-limit:]

    def clear_history(self):
        self._history.clear()


_event_bus_instance: Optional[EventBus] = None


def get_event_bus() -> EventBus:
    global _event_bus_instance
    if _event_bus_instance is None:
        _event_bus_instance = EventBus()
    return _event_bus_instance
