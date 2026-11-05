from src.shared.domain.event_bus import app_event_bus
from src.contexts.dining.domain.events import (
    MealRecordedDomainEvent,
    MealDeniedDomainEvent,
)
from src.shared.infrastructure.realtime.tenant_connection_manager import tenant_ws_manager


async def on_meal_recorded(event: MealRecordedDomainEvent) -> None:
    await tenant_ws_manager.broadcast_to_tenant(
        tenant_id=event.tenant_id,
        message={
            "type": "MEAL_RECORDED",
            "data": {
                "meal_id": event.meal_id,
                "employee_id": event.employee_id,
                "meal_type": event.meal_type,
                "badge_code": event.badge_code,
                "status": event.status,
                "timestamp": event.occurred_on.isoformat(),
            },
        },
    )


async def on_meal_denied(event: MealDeniedDomainEvent) -> None:
    await tenant_ws_manager.broadcast_to_tenant(
        tenant_id=event.tenant_id,
        message={
            "type": "MEAL_DENIED",
            "data": {
                "employee_id": event.employee_id,
                "meal_type": event.meal_type,
                "reason": event.reason,
                "timestamp": event.occurred_on.isoformat(),
            },
        },
    )


def register_dining_subscribers() -> None:
    """Subscribes dining real-time WebSocket broadcasters to the application event bus."""
    app_event_bus.subscribe(MealRecordedDomainEvent, on_meal_recorded)
    app_event_bus.subscribe(MealDeniedDomainEvent, on_meal_denied)
