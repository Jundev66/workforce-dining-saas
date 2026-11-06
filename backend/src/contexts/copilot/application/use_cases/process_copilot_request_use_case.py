from typing import Optional
from src.contexts.copilot.domain.schemas import CopilotChatOutput
from src.contexts.copilot.application.copilot_graph import CopilotWorkflow
from src.contexts.copilot.infrastructure.llm_client import CopilotLlmClient


class ProcessCopilotRequestUseCase:
    """
    Use Case: Executes the Multi-Agent Workforce & Dining LangGraph workflow.
    Validates tenant scoping, runs the graph, and returns deterministic outputs.
    """

    def __init__(self, workflow: Optional[CopilotWorkflow] = None):
        self.workflow = workflow or CopilotWorkflow(llm_client=CopilotLlmClient())

    async def execute(self, tenant_id: str, employee_id: str, message: str) -> CopilotChatOutput:
        result = await self.workflow.run(
            tenant_id=tenant_id,
            employee_id=employee_id,
            message=message,
        )

        intent_data = result.get("intent") or {}
        policy_data = result.get("policy_verdict") or {}
        dining_data = result.get("dining_action") or {}

        return CopilotChatOutput(
            intent=intent_data.get("intent", "general_inquiry"),
            policy_approved=bool(policy_data.get("approved", False)),
            meal_cancelled=bool(dining_data.get("meal_cancelled", False)),
            message=result.get("final_response", ""),
            guardrail_passed=bool(result.get("guardrail_passed", False)),
            audit_trail=result.get("audit_trail", []),
        )
