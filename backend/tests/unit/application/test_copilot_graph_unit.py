import pytest
from src.contexts.copilot.application.copilot_graph import CopilotWorkflow
from src.contexts.copilot.domain.schemas import CopilotState, IntentClassification
from src.contexts.copilot.infrastructure.llm_client import CopilotLlmClient


class MockLlmClient(CopilotLlmClient):
    """Deterministic LLM Test Double for Unit Tests."""
    def __init__(self, forced_intent: str = "combined_request", cancel_meal: bool = True):
        self.forced_intent = forced_intent
        self.cancel_meal = cancel_meal
        self._llm = None

    async def classify_intent(self, message: str) -> IntentClassification:
        return IntentClassification(
            intent=self.forced_intent,
            absence_date="viernes",
            absence_reason="consulta médica",
            cancel_meal=self.cancel_meal,
            confidence=0.99,
        )


@pytest.mark.asyncio
async def test_copilot_combined_request_flow_success():
    # Arrange
    mock_client = MockLlmClient(forced_intent="combined_request", cancel_meal=True)
    workflow = CopilotWorkflow(llm_client=mock_client)

    # Act
    result = await workflow.run(
        tenant_id="tenant-123",
        employee_id="emp-456",
        message="El viernes no asisto por consulta médica y por favor cancelar mi vianda",
    )

    # Assert
    assert result["guardrail_passed"] is True
    assert result["intent"]["intent"] == "combined_request"
    assert result["intent"]["cancel_meal"] is True
    assert result["policy_verdict"]["approved"] is True
    assert result["policy_verdict"]["policy_code"] == "HR-MED-01"
    assert result["dining_action"]["meal_cancelled"] is True
    assert "CANC-" in result["dining_action"]["confirmation_code"]
    assert "Tu aviso de ausencia para el viernes fue registrado" in result["final_response"]
    assert "Tu vianda fue cancelada exitosamente" in result["final_response"]

    # Verify complete multi-agent audit trail
    audit = result["audit_trail"]
    assert any("SupervisorNode:" in step for step in audit)
    assert any("PolicyAgent:" in step for step in audit)
    assert any("DiningAgent:" in step for step in audit)
    assert any("GuardrailNode:" in step for step in audit)


@pytest.mark.asyncio
async def test_copilot_absence_only_skips_dining_node():
    # Arrange: Absence without meal cancellation
    mock_client = MockLlmClient(forced_intent="absence_request", cancel_meal=False)
    workflow = CopilotWorkflow(llm_client=mock_client)

    # Act
    result = await workflow.run(
        tenant_id="tenant-123",
        employee_id="emp-789",
        message="El lunes falto por trámites personales",
    )

    # Assert
    assert result["guardrail_passed"] is True
    assert result["intent"]["cancel_meal"] is False
    assert result["policy_verdict"]["approved"] is True
    assert result["dining_action"] is None  # Dining node was bypassed by conditional edge!
    assert not any("DiningAgent:" in step for step in result["audit_trail"])


@pytest.mark.asyncio
async def test_copilot_guardrail_rejects_hallucinated_or_illegal_state():
    # Arrange: Create workflow and test guardrail directly with invalid state
    workflow = CopilotWorkflow()
    corrupted_state: CopilotState = {
        "tenant_id": "tenant-123",
        "employee_id": "emp-456",
        "user_message": "test",
        "intent": {"intent": "absence_request", "cancel_meal": True},
        "policy_verdict": {"approved": False, "reason": "No tiene días disponibles"},
        "dining_action": {"meal_cancelled": True, "confirmation_code": "ILLEGAL-123"},
        "final_response": None,
        "guardrail_passed": False,
        "audit_trail": [],
    }

    # Act
    evaluation = await workflow.guardrail_node(corrupted_state)

    # Assert
    assert evaluation["guardrail_passed"] is False
    assert "Error de integridad" in evaluation["final_response"]
    assert any("GuardrailViolation:" in step for step in evaluation["audit_trail"])
