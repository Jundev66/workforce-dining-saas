from typing import TypedDict, Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field


class IntentClassification(BaseModel):
    intent: Literal["absence_request", "dining_cancellation", "combined_request", "general_inquiry"] = Field(
        ..., description="Classified intent from employee message"
    )
    absence_date: Optional[str] = Field(None, description="ISO date or description of absence")
    absence_reason: Optional[str] = Field(None, description="Reason for absence (e.g. medical, personal)")
    cancel_meal: bool = Field(False, description="Whether meal reservation should be cancelled")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Confidence of extraction")


class PolicyVerdict(BaseModel):
    approved: bool
    policy_code: str
    reason: str
    requires_documentation: bool = False


class DiningAction(BaseModel):
    meal_cancelled: bool
    confirmation_code: Optional[str] = None
    saved_portion_kg: float = 0.45
    reason: str


class CopilotState(TypedDict):
    tenant_id: str
    employee_id: str
    user_message: str
    intent: Optional[Dict[str, Any]]
    policy_verdict: Optional[Dict[str, Any]]
    dining_action: Optional[Dict[str, Any]]
    final_response: Optional[str]
    guardrail_passed: bool
    audit_trail: List[str]


class CopilotChatInput(BaseModel):
    message: str = Field(..., min_length=2, max_length=1000)
    employee_id: str = Field(..., description="ID of employee sending the query")


class CopilotChatOutput(BaseModel):
    intent: str
    policy_approved: bool
    meal_cancelled: bool
    message: str
    guardrail_passed: bool
    audit_trail: List[str]
