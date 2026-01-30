from fastapi import APIRouter, Depends
from app.services.ai_service import AIService
from app.schemas.ai_schema import AIPayloadSchema, AIResponseSchema


router = APIRouter(prefix="/ai")

@router.post("/chat", response_model=AIResponseSchema)
async def chat(payload: AIPayloadSchema, ai_service: AIService = Depends()):
    return await ai_service.chat(payload.message)
