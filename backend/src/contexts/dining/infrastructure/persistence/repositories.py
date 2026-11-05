from datetime import date, datetime, time
from typing import Dict, List
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.contexts.dining.domain.entities import MealRecord
from src.contexts.dining.domain.value_objects import MealType, MealStatus
from src.contexts.dining.domain.ports import MealRepository
from src.contexts.dining.infrastructure.persistence.models import MealRecordModel
from src.shared.infrastructure.tenant_context import get_current_tenant_id


class SQLAlchemyMealRepository(MealRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_domain(self, model: MealRecordModel) -> MealRecord:
        return MealRecord(
            id=model.id,
            tenant_id=model.tenant_id,
            employee_id=model.employee_id,
            meal_type=MealType(model.meal_type),
            badge_code=model.badge_code,
            status=MealStatus(model.status),
            notes=model.notes,
            consumed_at=model.consumed_at,
        )

    async def save(self, meal: MealRecord) -> MealRecord:
        model = MealRecordModel(
            id=meal.id,
            tenant_id=meal.tenant_id,
            employee_id=meal.employee_id,
            meal_type=meal.meal_type.value,
            badge_code=meal.badge_code,
            status=meal.status.value,
            notes=meal.notes,
            consumed_at=meal.consumed_at,
        )
        self.session.add(model)
        await self.session.flush()
        return self._to_domain(model)

    async def has_consumed_meal_on_date(
        self,
        employee_id: str,
        meal_type: MealType,
        target_date: date,
    ) -> bool:
        start_of_day = datetime.combine(target_date, time.min)
        end_of_day = datetime.combine(target_date, time.max)

        stmt = select(func.count()).select_from(MealRecordModel).where(
            and_(
                MealRecordModel.employee_id == employee_id,
                MealRecordModel.meal_type == meal_type.value,
                MealRecordModel.status == MealStatus.APPROVED.value,
                MealRecordModel.consumed_at >= start_of_day,
                MealRecordModel.consumed_at <= end_of_day,
            )
        )
        tenant_id = get_current_tenant_id()
        if tenant_id:
            stmt = stmt.where(MealRecordModel.tenant_id == tenant_id)

        result = await self.session.execute(stmt)
        count = result.scalar_one()
        return count > 0

    async def get_daily_metrics(
        self,
        tenant_id: str,
        target_date: date,
    ) -> Dict[str, int]:
        start_of_day = datetime.combine(target_date, time.min)
        end_of_day = datetime.combine(target_date, time.max)

        stmt = (
            select(MealRecordModel.meal_type, MealRecordModel.status, func.count())
            .where(
                and_(
                    MealRecordModel.tenant_id == tenant_id,
                    MealRecordModel.consumed_at >= start_of_day,
                    MealRecordModel.consumed_at <= end_of_day,
                )
            )
            .group_by(MealRecordModel.meal_type, MealRecordModel.status)
        )

        result = await self.session.execute(stmt)
        rows = result.all()

        metrics: Dict[str, int] = {"breakfast": 0, "lunch": 0, "dinner": 0, "rejected": 0}
        for meal_type, status_val, count in rows:
            if status_val == MealStatus.APPROVED.value:
                metrics[meal_type] = metrics.get(meal_type, 0) + count
            else:
                metrics["rejected"] += count

        return metrics

    async def list_recent(
        self,
        skip: int = 0,
        limit: int = 50,
    ) -> List[MealRecord]:
        stmt = select(MealRecordModel).order_by(MealRecordModel.consumed_at.desc()).offset(skip).limit(limit)
        tenant_id = get_current_tenant_id()
        if tenant_id:
            stmt = stmt.where(MealRecordModel.tenant_id == tenant_id)

        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._to_domain(m) for m in models]
