export interface MealScanResult {
  id: string;
  status: string;
  approved: boolean;
  employee_id: string;
  employee_name: string;
  department: string;
  meal_type: string;
  badge_code: string;
  message: string;
  consumed_at: string;
}

export interface DiningMetrics {
  total_meals_today: number;
  breakfast_count: number;
  lunch_count: number;
  dinner_count: number;
  rejected_count: number;
}

export interface AiForecast {
  date: string;
  active_workforce_count: number;
  forecasted_lunch_headcount: number;
  forecasted_breakfast_headcount: number;
  recommended_food_prep_kg: number;
  confidence_score: number;
  insights: string[];
}
