"""
Finovate Audit Nexus AI - WebSocket Endpoint
نقطة اتصال WebSocket للاتصال المباشر
"""

from jose import jwt, JWTError
from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect, status

from backend.api.endpoints.auth import _get_jwt_secret
from backend.api.websocket import get_ws_manager

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(ws: WebSocket, token: str = Query(...), company_id: int = Query(0)):
    try:
        payload = jwt.decode(token, _get_jwt_secret(), algorithms=["HS256"],
                             options={"verify_exp": True, "require": ["exp"]})
        user_id = payload.get("sub", "anonymous")
        role = payload.get("role", "viewer")
    except Exception:
        await ws.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    manager = get_ws_manager()
    client_id = f"{user_id}_{id(ws)}"
    rooms = ["all", f"user:{user_id}"]
    if company_id:
        rooms.append(f"company:{company_id}")
    if role == "admin":
        rooms.append("admins")

    await manager.connect(ws, client_id, rooms)
    try:
        while True:
            data = await ws.receive_text()
            if data == "ping":
                await ws.send_text('{"type":"pong"}')
    except WebSocketDisconnect:
        await manager.disconnect(client_id)
    except Exception:
        await manager.disconnect(client_id)
