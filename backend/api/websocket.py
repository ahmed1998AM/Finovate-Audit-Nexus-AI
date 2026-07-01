"""
Finovate Audit Nexus AI - WebSocket Manager
Real-time event broadcasting to connected clients
"""

import asyncio
import json
import logging
from typing import Any, Dict, Optional, Set

from fastapi import WebSocket

from backend.core.events import Event, get_event_bus

logger = logging.getLogger(__name__)


class WebSocketManager:
    def __init__(self):
        self._connections: Dict[str, Dict[str, Any]] = {}
        self._rooms: Dict[str, Set[str]] = {}
        self._lock = asyncio.Lock()

    async def connect(self, ws: WebSocket, client_id: str, rooms: Optional[list] = None):
        await ws.accept()
        async with self._lock:
            self._connections[client_id] = {"ws": ws, "rooms": set(rooms or [])}
        for room in (rooms or []):
            async with self._lock:
                if room not in self._rooms:
                    self._rooms[room] = set()
                self._rooms[room].add(client_id)
        logger.info(f"WebSocket client connected: {client_id}")

    async def disconnect(self, client_id: str):
        async with self._lock:
            info = self._connections.pop(client_id, None)
            if info:
                for room in info["rooms"]:
                    if room in self._rooms:
                        self._rooms[room].discard(client_id)
                        if not self._rooms[room]:
                            del self._rooms[room]
        logger.info(f"WebSocket client disconnected: {client_id}")

    async def join_room(self, client_id: str, room: str):
        async with self._lock:
            if client_id in self._connections:
                self._connections[client_id]["rooms"].add(room)
                if room not in self._rooms:
                    self._rooms[room] = set()
                self._rooms[room].add(client_id)

    async def leave_room(self, client_id: str, room: str):
        async with self._lock:
            if client_id in self._connections:
                self._connections[client_id]["rooms"].discard(room)
            if room in self._rooms:
                self._rooms[room].discard(client_id)
                if not self._rooms[room]:
                    del self._rooms[room]

    async def broadcast(self, event_type: str, data: dict, room: Optional[str] = None):
        async with self._lock:
            targets = {}
            if room:
                for cid in self._rooms.get(room, set()):
                    if cid in self._connections:
                        targets[cid] = self._connections[cid]["ws"]
            else:
                targets = {cid: info["ws"] for cid, info in self._connections.items()}

        message = json.dumps({"type": event_type, "data": data})
        for cid, ws in targets.items():
            try:
                await ws.send_text(message)
            except Exception as e:
                logger.error(f"WebSocket send to {cid} failed: {e}")

    async def send_to(self, client_id: str, event_type: str, data: dict):
        async with self._lock:
            info = self._connections.get(client_id)
            if not info:
                return
            ws = info["ws"]
        try:
            await ws.send_text(json.dumps({"type": event_type, "data": data}))
        except Exception as e:
            logger.error(f"WebSocket send to {client_id} failed: {e}")

    @property
    def connected_count(self) -> int:
        return len(self._connections)

    @property
    def room_count(self) -> int:
        return len(self._rooms)


_ws_manager: Optional[WebSocketManager] = None


def get_ws_manager() -> WebSocketManager:
    global _ws_manager
    if _ws_manager is None:
        _ws_manager = WebSocketManager()
    return _ws_manager


async def _event_bridge(event: Event):
    manager = get_ws_manager()
    if event.event_type.startswith("private:"):
        parts = event.event_type.split(":", 2)
        if len(parts) >= 3:
            await manager.send_to(parts[1], parts[2], event.data)
    elif event.event_type.startswith("room:"):
        parts = event.event_type.split(":", 2)
        if len(parts) >= 3:
            await manager.broadcast(parts[2], event.data, room=parts[1])
    else:
        await manager.broadcast(event.event_type, event.data)


def init_ws_event_bridge():
    bus = get_event_bus()
    bus.on("*", _event_bridge)
    logger.info("WebSocket event bridge initialized")
