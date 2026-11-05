from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, List
import uuid


@dataclass(frozen=True)
class ValueObject:
    """Base class for all immutable Value Objects."""
    pass


@dataclass(frozen=True)
class DomainEvent:
    """Base class for all Domain Events."""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    occurred_on: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class AggregateRoot:
    """Base Aggregate Root that records and releases Domain Events."""
    def __init__(self):
        self._domain_events: List[DomainEvent] = []

    def record_event(self, event: DomainEvent) -> None:
        self._domain_events.append(event)

    def pull_domain_events(self) -> List[DomainEvent]:
        events = list(self._domain_events)
        self._domain_events.clear()
        return events
