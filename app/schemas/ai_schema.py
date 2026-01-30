from pydantic import BaseModel

class AIPayloadSchema(BaseModel):
    message: str

class AIResponseSchema(BaseModel):
    message: str