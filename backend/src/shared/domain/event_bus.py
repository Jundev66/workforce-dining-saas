from abc import ABC, abstractmethod
from typing import List
from src.shared.domain.base import DomainEvent


class EventBus(ABC):
    """Domain port for publishing domain events across bounded contexts or outbox handlers."""

    @abstractmethod
    async def publish(self, events: List[DomainEvent]) -> None:
        pass


class InMemoryEventBus(EventBus):
    """In-memory event bus implementation for execution and unit test verification."""

    def __init__(self):
        self.published_events: List[DomainEvent] = []

    async def publish(self, events: List[DomainEvent]) -> None:
        for event in events:
            self.published_events.append(event)

    def clear(self) -> None:
        self.published_events.clear()
