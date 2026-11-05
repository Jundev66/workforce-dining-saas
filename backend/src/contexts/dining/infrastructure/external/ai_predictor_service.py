from typing import Dict, Any
from src.contexts.dining.domain.ports import DiningAiPredictorPort


class HeuristicAiDiningPredictor(DiningAiPredictorPort):
    """
    AI Service Adapter: Computes meal headcount forecasting, portion estimation,
    and waste reduction recommendations using workforce metrics and shift patterns.
    """

    async def predict_demand(
        self,
        active_staff_count: int,
        day_of_week: int,
        historical_ratios: Dict[str, float],
    ) -> Dict[str, Any]:
        # Fridays and Mondays typically exhibit minor attendance variations (-5% on Friday afternoon)
        day_factor = 0.95 if day_of_week in (0, 4) else 1.0

        lunch_ratio = historical_ratios.get("lunch", 0.85) * day_factor
        breakfast_ratio = historical_ratios.get("breakfast", 0.40) * day_factor

        forecasted_lunch = int(round(active_staff_count * lunch_ratio))
        forecasted_breakfast = int(round(active_staff_count * breakfast_ratio))

        # Standard catering portion: 0.45 kg per meal
        prep_kg = round(forecasted_lunch * 0.45, 1)

        confidence = 0.94 if active_staff_count > 10 else 0.85

        insights = [
            f"Asistencia proyectada para almuerzo: {forecasted_lunch} comensales ({round(lunch_ratio * 100)}% de la nómina activa).",
            f"Preparación recomendada: {prep_kg} kg de alimentos para evitar sobreproducción.",
            "Franja de mayor congestión estimada: 12:45 a 13:30.",
        ]

        return {
            "forecasted_lunch": forecasted_lunch,
            "forecasted_breakfast": forecasted_breakfast,
            "recommended_kg": prep_kg,
            "confidence": confidence,
            "insights": insights,
        }
