from abc import ABC, abstractmethod
from typing import List, Dict, Type, Callable, Awaitable
from src.shared.domain.base import DomainEvent

EventHandler = Callable[[DomainEvent], Awaitable[None]]


class EventBus(ABC):
    """Domain port for publishing domain events across bounded contexts or outbox handlers."""

    @abstractmethod
    async def publish(self, events: List[DomainEvent]) -> None:
        pass

    @abstractmethod
    def subscribe(self, event_type: Type[DomainEvent], handler: EventHandler) -> None:
        pass


class InMemoryEventBus(EventBus):
    """In-memory event bus implementation supporting subscriber dispatch and test verification."""

    def __init__(self):
        self.published_events: List[DomainEvent] = []
        self._subscribers: Dict[Type[DomainEvent], List[EventHandler]] = {}

    def subscribe(self, event_type: Type[DomainEvent], handler: EventHandler) -> None:
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)

    async def publish(self, events: List[DomainEvent]) -> None:
        for event in events:
            self.published_events.append(event)
            handlers = self._subscribers.get(type(event), [])
            for handler in handlers:
                try:
                    await handler(event)
                except Exception:
                    # Robustness: handler failure should not crash the publisher pipeline
                    pass

    def clear(self) -> None:
        self.published_events.clear()


# Global application event bus
app_event_bus = InMemoryEventBus()
