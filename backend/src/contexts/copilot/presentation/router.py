from fastapi import APIRouter
from src.contexts.copilot.domain.schemas import CopilotChatOutput
from src.contexts.copilot.presentation.controllers.copilot_controller import (
    CopilotChatController,
)

router = APIRouter(prefix="/copilot", tags=["Copilot Multi-Agent"])

router.add_api_route(
    "/chat",
    CopilotChatController.handle,
    methods=["POST"],
    response_model=CopilotChatOutput,
    summary="Multi-Agent Workforce & Dining Assistant (LangGraph)",
)
