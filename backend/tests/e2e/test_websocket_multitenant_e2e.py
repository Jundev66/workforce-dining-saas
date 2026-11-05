import pytest
from starlette.testclient import TestClient
from src.main import app
from src.shared.infrastructure.security import create_access_token
from src.contexts.dining.domain.events import MealRecordedDomainEvent
from src.shared.domain.event_bus import app_event_bus
import json


def test_websocket_multitenant_isolation():
    client = TestClient(app)

    token_a = create_access_token(
        subject="user-a",
        tenant_id="tenant-alpha",
        role="admin",
    )

    token_b = create_access_token(
        subject="user-b",
        tenant_id="tenant-beta",
        role="admin",
    )

    # 1. Connect Tenant A WebSocket
    with client.websocket_connect(f"/api/v1/dining/ws?token={token_a}") as ws_a:
        init_a = ws_a.receive_json()
        assert init_a["type"] == "CONNECTED"
        assert "tenant-alpha" in init_a["message"]

        # 2. Connect Tenant B WebSocket
        with client.websocket_connect(f"/api/v1/dining/ws?token={token_b}") as ws_b:
            init_b = ws_b.receive_json()
            assert init_b["type"] == "CONNECTED"
            assert "tenant-beta" in init_b["message"]

            # 3. Ping pong test
            ws_a.send_text("ping")
            pong = ws_a.receive_text()
            assert pong == "pong"

            # 4. Publish a domain event for Tenant A
            import asyncio
            event_a = MealRecordedDomainEvent(
                meal_id="meal-101",
                tenant_id="tenant-alpha",
                employee_id="emp-1",
                meal_type="lunch",
                badge_code="QR-ALPHA",
                status="approved",
            )
            asyncio.run(app_event_bus.publish([event_a]))

            # 5. Tenant A must receive the broadcast event
            event_received_a = ws_a.receive_json()
            assert event_received_a["type"] == "MEAL_RECORDED"
            assert event_received_a["data"]["badge_code"] == "QR-ALPHA"
            assert event_received_a["data"]["status"] == "approved"


def test_websocket_rejects_unauthenticated_connection():
    client = TestClient(app)
    with pytest.raises(Exception):
        with client.websocket_connect("/api/v1/dining/ws?token=invalid_token") as ws:
            pass
