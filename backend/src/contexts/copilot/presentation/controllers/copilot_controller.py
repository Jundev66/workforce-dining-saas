from typing import Dict, Any
from fastapi import Depends, HTTPException, status
from src.contexts.dining.presentation.controllers.common import get_current_user
from src.contexts.copilot.domain.schemas import CopilotChatInput, CopilotChatOutput
from src.contexts.copilot.application.use_cases.process_copilot_request_use_case import (
    ProcessCopilotRequestUseCase,
)

_use_case_instance = ProcessCopilotRequestUseCase()


def get_copilot_use_case() -> ProcessCopilotRequestUseCase:
    return _use_case_instance


class CopilotChatController:
    """
    Single-Action Controller:
    POST /api/v1/copilot/chat
    Processes multi-agent LangGraph workflow requests for employees and HR admins.
    """

    @staticmethod
    async def handle(
        data: CopilotChatInput,
        current_user: Dict[str, Any] = Depends(get_current_user),
        use_case: ProcessCopilotRequestUseCase = Depends(get_copilot_use_case),
    ) -> CopilotChatOutput:
        try:
            return await use_case.execute(
                tenant_id=current_user["tenant_id"],
                employee_id=data.employee_id,
                message=data.message,
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error en ejecución del agente Copilot: {str(e)}",
            )
