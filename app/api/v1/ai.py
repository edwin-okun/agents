from fastapi import APIRouter, Depends

from app.schemas.ai_schema import AIPayloadSchema, AIResponseSchema
from app.services.ai_service import AIService

router = APIRouter(prefix="/ai", tags=["AI"])


@router.post("/chat", response_model=AIResponseSchema)
async def chat(payload: AIPayloadSchema, ai_service: AIService = Depends()):
    return await ai_service.chat(payload.message)
