from fastapi import WebSocket, WebSocketDisconnect, status
from src.shared.infrastructure.security import decode_access_token
from src.shared.infrastructure.realtime.tenant_connection_manager import tenant_ws_manager


class DiningWebSocketController:
    """
    Single-Action Controller for Real-Time Multi-Tenant WebSocket connections.
    Authenticates JWT tokens on handshake and scopes the connection strictly to the client's tenant.
    """

    @staticmethod
    async def handle(websocket: WebSocket, token: str | None = None) -> None:
        if not token:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        payload = decode_access_token(token)
        if not payload:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        tenant_id = payload.get("tenant_id")
        if not tenant_id:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        # Connect to tenant-isolated room
        await tenant_ws_manager.connect(tenant_id, websocket)

        try:
            # Send initial connection confirmation
            await websocket.send_json({
                "type": "CONNECTED",
                "message": f"Conexión en tiempo real activa para tenant: {tenant_id}",
            })

            # Keep listening for client pings or heartbeats
            while True:
                data = await websocket.receive_text()
                if data == "ping":
                    await websocket.send_text("pong")
        except WebSocketDisconnect:
            tenant_ws_manager.disconnect(tenant_id, websocket)
        except Exception:
            tenant_ws_manager.disconnect(tenant_id, websocket)
