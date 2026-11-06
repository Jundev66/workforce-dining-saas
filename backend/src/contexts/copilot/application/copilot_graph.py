import uuid
from typing import Dict, Any, Literal
from langgraph.graph import StateGraph, START, END

from src.contexts.copilot.domain.schemas import (
    CopilotState,
    PolicyVerdict,
    DiningAction,
)
from src.contexts.copilot.infrastructure.llm_client import CopilotLlmClient


class CopilotWorkflow:
    def __init__(self, llm_client: CopilotLlmClient = None):
        self.llm_client = llm_client or CopilotLlmClient()
        self.graph = self._build_graph()

    def _build_graph(self):
        builder = StateGraph(CopilotState)

        builder.add_node("supervisor", self.supervisor_node)
        builder.add_node("policy_agent", self.policy_node)
        builder.add_node("dining_agent", self.dining_node)
        builder.add_node("guardrail", self.guardrail_node)

        builder.add_edge(START, "supervisor")
        builder.add_edge("supervisor", "policy_agent")

        def route_after_policy(state: CopilotState) -> Literal["dining_agent", "guardrail"]:
            policy = state.get("policy_verdict") or {}
            intent = state.get("intent") or {}
            # If policy is approved and the employee requested meal cancellation
            if policy.get("approved") and intent.get("cancel_meal"):
                return "dining_agent"
            return "guardrail"

        builder.add_conditional_edges("policy_agent", route_after_policy)
        builder.add_edge("dining_agent", "guardrail")
        builder.add_edge("guardrail", END)

        return builder.compile()

    async def supervisor_node(self, state: CopilotState) -> Dict[str, Any]:
        """Node 1: Classifies employee intent and extracts entities."""
        message = state.get("user_message", "")
        extracted = await self.llm_client.classify_intent(message)
        
        audit = list(state.get("audit_trail", []))
        audit.append(f"SupervisorNode: Intent classified as '{extracted.intent}' (date={extracted.absence_date}, cancel_meal={extracted.cancel_meal})")
        
        return {
            "intent": extracted.model_dump(),
            "audit_trail": audit,
        }

    async def policy_node(self, state: CopilotState) -> Dict[str, Any]:
        """Node 2: Evaluates workforce HR labor agreements and notice requirements."""
        intent = state.get("intent") or {}
        reason = intent.get("absence_reason", "personal")
        audit = list(state.get("audit_trail", []))

        if intent.get("intent") in ["absence_request", "combined_request"]:
            lower_reason = reason.lower()
            if "medic" in lower_reason or "médic" in lower_reason:
                verdict = PolicyVerdict(
                    approved=True,
                    policy_code="HR-MED-01",
                    reason="Licencia médica aprobada. Se requiere presentar certificado dentro de las 48 hs hábiles.",
                    requires_documentation=True,
                )
            else:
                verdict = PolicyVerdict(
                    approved=True,
                    policy_code="HR-PER-02",
                    reason="Permiso personal registrado conforme al convenio interno.",
                    requires_documentation=False,
                )
        else:
            verdict = PolicyVerdict(
                approved=True,
                policy_code="HR-INFO-00",
                reason="Consulta informativa sin impacto en presentismo.",
                requires_documentation=False,
            )

        audit.append(f"PolicyAgent: Verdict code '{verdict.policy_code}', approved={verdict.approved}")
        return {
            "policy_verdict": verdict.model_dump(),
            "audit_trail": audit,
        }

    async def dining_node(self, state: CopilotState) -> Dict[str, Any]:
        """Node 3: Executes dining hall cancellation use-case to prevent food waste."""
        audit = list(state.get("audit_trail", []))
        confirmation = f"CANC-{uuid.uuid4().hex[:8].upper()}"

        action = DiningAction(
            meal_cancelled=True,
            confirmation_code=confirmation,
            saved_portion_kg=0.45,
            reason="Cancelación preventiva por ausencia del comensal",
        )

        audit.append(f"DiningAgent: Meal slot cancelled with code {confirmation} (saved 0.45kg food quota)")
        return {
            "dining_action": action.model_dump(),
            "audit_trail": audit,
        }

    async def guardrail_node(self, state: CopilotState) -> Dict[str, Any]:
        """
        Node 4 (Deterministic Anti-Hallucination Guardrail):
        Validates state consistency, verifies no unauthorized actions occurred,
        and constructs the verified production response.
        """
        audit = list(state.get("audit_trail", []))
        intent = state.get("intent") or {}
        policy = state.get("policy_verdict") or {}
        dining = state.get("dining_action")

        # Invariant 1: Policy must be evaluated
        if not policy:
            audit.append("GuardrailViolation: Missing policy evaluation")
            return {
                "guardrail_passed": False,
                "final_response": "Error de seguridad: La solicitud no pudo ser auditada por las políticas de RRHH.",
                "audit_trail": audit,
            }

        # Invariant 2: If dining cancellation happened without policy approval -> Hallucination/Illegal state
        if dining and not policy.get("approved"):
            audit.append("GuardrailViolation: Dining cancellation executed without approved policy")
            return {
                "guardrail_passed": False,
                "final_response": "Error de integridad: No se permite cancelar vianda sin aprobación de RRHH.",
                "audit_trail": audit,
            }

        # Synthesize production-ready message
        parts = []
        if policy.get("approved") and intent.get("intent") in ["absence_request", "combined_request"]:
            parts.append(f"Tu aviso de ausencia para el {intent.get('absence_date')} fue registrado ({policy.get('policy_code')}). {policy.get('reason')}")

        if dining and dining.get("meal_cancelled"):
            parts.append(f"Tu vianda fue cancelada exitosamente (Código {dining.get('confirmation_code')}), evitando desperdicio de comida.")

        if not parts:
            parts.append("Tu consulta ha sido procesada correctamente.")

        final_msg = " ".join(parts)
        audit.append("GuardrailNode: All business invariants verified. Production payload approved.")

        return {
            "guardrail_passed": True,
            "final_response": final_msg,
            "audit_trail": audit,
        }

    async def run(self, tenant_id: str, employee_id: str, message: str) -> Dict[str, Any]:
        initial_state: CopilotState = {
            "tenant_id": tenant_id,
            "employee_id": employee_id,
            "user_message": message,
            "intent": None,
            "policy_verdict": None,
            "dining_action": None,
            "final_response": None,
            "guardrail_passed": False,
            "audit_trail": ["GraphInitialized: Multi-agent execution started"],
        }
        return await self.graph.ainvoke(initial_state)
