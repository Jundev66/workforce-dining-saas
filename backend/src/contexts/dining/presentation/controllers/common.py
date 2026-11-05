from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.shared.infrastructure.database import get_db_session
from src.contexts.dining.infrastructure.persistence.repositories import SQLAlchemyMealRepository
from src.contexts.dining.infrastructure.external.ai_predictor_service import HeuristicAiDiningPredictor
from src.contexts.workforce.presentation.controllers.common import get_employee_repo, get_current_user

_ai_predictor_instance = HeuristicAiDiningPredictor()


def get_meal_repo(db: AsyncSession = Depends(get_db_session)) -> SQLAlchemyMealRepository:
    return SQLAlchemyMealRepository(db)


def get_dining_ai_predictor() -> HeuristicAiDiningPredictor:
    return _ai_predictor_instance
