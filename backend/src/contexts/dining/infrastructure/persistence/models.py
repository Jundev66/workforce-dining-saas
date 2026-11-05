from datetime import datetime
from typing import Optional
from sqlalchemy import String, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column
from src.shared.infrastructure.database import Base


class MealRecordModel(Base):
    __tablename__ = "meal_records"
    __table_args__ = (
        Index("ix_meal_records_tenant_date", "tenant_id", "consumed_at"),
        Index("ix_meal_records_emp_type_date", "employee_id", "meal_type", "consumed_at"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    employee_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True
    )
    meal_type: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    badge_code: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="approved", nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    consumed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
