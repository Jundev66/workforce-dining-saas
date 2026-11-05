from typing import Dict, Set, Any
from fastapi import WebSocket
import json


class TenantConnectionManager:
    """
    Manages active WebSocket connections partitioned strictly by tenant_id.
    Ensures complete isolation: messages broadcast to Tenant A will NEVER reach Tenant B.
    """

    def __init__(self):
        # tenant_id -> Set of active WebSocket connections
        self._tenant_rooms: Dict[str, Set[WebSocket]] = {}

    async def connect(self, tenant_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        if tenant_id not in self._tenant_rooms:
            self._tenant_rooms[tenant_id] = set()
        self._tenant_rooms[tenant_id].add(websocket)

    def disconnect(self, tenant_id: str, websocket: WebSocket) -> None:
        if tenant_id in self._tenant_rooms:
            self._tenant_rooms[tenant_id].discard(websocket)
            if not self._tenant_rooms[tenant_id]:
                del self._tenant_rooms[tenant_id]

    async def broadcast_to_tenant(self, tenant_id: str, message: Dict[str, Any]) -> None:
        """Broadcasts a JSON payload exclusively to active sockets belonging to the specified tenant."""
        sockets = self._tenant_rooms.get(tenant_id, set()).copy()
        if not sockets:
            return

        payload_text = json.dumps(message)
        dead_sockets = set()

        for ws in sockets:
            try:
                await ws.send_text(payload_text)
            except Exception:
                dead_sockets.add(ws)

        # Cleanup any disconnected sockets discovered during write
        for dead_ws in dead_sockets:
            self.disconnect(tenant_id, dead_ws)

    def get_active_count(self, tenant_id: str) -> int:
        return len(self._tenant_rooms.get(tenant_id, set()))


# Global singleton instance for connection routing
tenant_ws_manager = TenantConnectionManager()
