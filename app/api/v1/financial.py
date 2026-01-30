"""
Financial Agent API Endpoints
"""

from fastapi import APIRouter, Depends

from app.schemas.financial_schema import (
    FinancialAnswerSchema,
    FinancialQuestionSchema,
)
from app.services.financial_agent_service import FinancialAgentService

router = APIRouter(prefix="/financial", tags=["Financial Agent"])


@router.post("/ask", response_model=FinancialAnswerSchema)
async def ask_financial_question(
    payload: FinancialQuestionSchema,
    agent_service: FinancialAgentService = Depends(),
):
    """
    Ask a financial question in natural language.

    The agent will analyze your question, select appropriate tools,
    and provide a clear answer with supporting data.

    Examples:
    - "How much did I spend this month?"
    - "Who are my top 5 expenses?"
    - "Show me my spending trends over the last year"
    - "How much have I paid to Safaricom?"
    """
    return await agent_service.ask(
        question=payload.question,
        consumer_phone_number=payload.consumer_phone_number,
    )
