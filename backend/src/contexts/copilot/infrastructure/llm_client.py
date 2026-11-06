import logging
import re
from typing import Optional
from langchain_openai import ChatOpenAI
from src.shared.infrastructure.config import settings
from src.contexts.copilot.domain.schemas import IntentClassification

logger = logging.getLogger(__name__)


class CopilotLlmClient:
    """
    LLM Gateway Client:
    Communicates with OpenAI-compatible endpoints (such as local `biz` gateway, Ollama, or OpenAI).
    Enforces structured output parsing and provides deterministic fallbacks when offline.
    """

    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None, model: Optional[str] = None):
        self.base_url = base_url or settings.LLM_BASE_URL
        self.api_key = api_key or settings.LLM_API_KEY
        self.model = model or settings.LLM_MODEL
        try:
            self._llm = ChatOpenAI(
                base_url=self.base_url,
                api_key=self.api_key,
                model=self.model,
                temperature=0.0,
                timeout=5.0,
                max_retries=1,
            )
        except Exception as e:
            logger.warning(f"Could not initialize ChatOpenAI client: {e}")
            self._llm = None

    async def classify_intent(self, message: str) -> IntentClassification:
        """
        Attempts LLM structured output classification; falls back to deterministic rule-based
        extraction if the gateway is offline or returns an unparseable response.
        """
        if self._llm:
            try:
                structured_llm = self._llm.with_structured_output(IntentClassification)
                prompt = (
                    "Sos un asistente de RRHH y comedor empresarial. "
                    "Clasificá el pedido del empleado determinando intención, fecha, motivo y si pide cancelar el almuerzo.\n\n"
                    f"Mensaje del empleado: \"{message}\""
                )
                result = await structured_llm.ainvoke(prompt)
                if isinstance(result, IntentClassification):
                    return result
            except Exception as e:
                logger.info(f"LLM gateway unavailable or failed ({e}), falling back to deterministic extractor")

        # Deterministic Rule-Based Fallback (Zero-flakiness & Anti-Hallucination)
        lowered = message.lower()

        # Informational question check
        is_query = any(q in lowered for q in ["cómo", "como", "política", "politica", "funciona", "cuál", "cual", "info"]) and not any(
            act in lowered for act in ["cancela", "cancelar", "falto", "no voy", "no asisto"]
        )

        if is_query:
            return IntentClassification(
                intent="general_inquiry",
                absence_date=None,
                absence_reason="consulta informativa",
                cancel_meal=False,
                confidence=0.98,
            )

        cancel_meal = any(k in lowered for k in ["vianda", "almuerzo", "comida", "cancelar", "baja"])
        has_absence = any(k in lowered for k in ["falto", "faltar", "ausente", "ausencia", "asisto", "asistencia", "licencia", "permiso", "examen", "médico", "medico"])

        if has_absence and cancel_meal:
            intent = "combined_request"
        elif has_absence:
            intent = "absence_request"
        elif cancel_meal:
            intent = "dining_cancellation"
        else:
            intent = "general_inquiry"

        reason = "médico" if "medic" in lowered else "personal"

        # Simple date regex detection (e.g., 'viernes', '2026-11-20', etc.)
        date_match = re.search(r"\b(lunes|martes|miércoles|miercoles|jueves|viernes|sábado|sabado|\d{4}-\d{2}-\d{2})\b", lowered)
        extracted_date = date_match.group(0) if date_match else "próximo día hábil"

        return IntentClassification(
            intent=intent,
            absence_date=extracted_date,
            absence_reason=reason,
            cancel_meal=cancel_meal,
            confidence=0.95,
        )
