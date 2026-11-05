import pytest
from src.contexts.dining.domain.entities import MealRecord
from src.contexts.dining.domain.value_objects import MealType, MealStatus
from tests.mothers.meal_mother import MealRecordMother


def test_should_create_approved_meal_and_record_domain_event():
    # GIVEN / WHEN
    meal = MealRecordMother.create_approved(badge_code="QR-ALPHA")

    # THEN
    assert meal.id is not None
    assert meal.status == MealStatus.APPROVED
    assert meal.meal_type == MealType.LUNCH
    assert meal.badge_code == "QR-ALPHA"

    events = meal.pull_domain_events()
    assert len(events) == 1
    assert events[0].meal_id == meal.id
    assert events[0].status == "approved"


def test_should_create_denied_meal_and_record_denied_domain_event():
    # GIVEN / WHEN
    meal = MealRecord.record_denied(
        tenant_id="tenant-1",
        employee_id="emp-1",
        meal_type=MealType.LUNCH,
        badge_code="QR-BETA",
        status=MealStatus.DUPLICATE_REJECTED,
        reason="Ya consumió almuerzo hoy",
    )

    # THEN
    assert meal.status == MealStatus.DUPLICATE_REJECTED
    events = meal.pull_domain_events()
    assert len(events) == 1
    assert events[0].reason == "Ya consumió almuerzo hoy"
