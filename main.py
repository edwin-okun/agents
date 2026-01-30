from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.ai import router as ai_router
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from tortoise.contrib.fastapi import RegisterTortoise
from app.core.database import TORTOISE_ORM


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    async with RegisterTortoise(
        app=app,
        config=TORTOISE_ORM,
        # generate_schemas=True,
    ):
        # db connected
        yield
        # app teardown


app = FastAPI(
    title="AI Agent",
    description="AI Agent",
    version="0.0.1",
    root_path="/api/v1",
    swagger_ui_parameters={
        "defaultModelsExpandDepth": -1,
        "displayRequestDuration": True,
        "docExpansion": "none",
    },
    lifespan=lifespan,
)


app.include_router(ai_router)

# Middleware
# CORS
# Allow all origins for development purposes
# In production, specify the allowed origins to restrict access to your API

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["POST", "GET", "PUT", "DELETE"],
    allow_headers=["*"],
)
