from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import add_pagination
from starlette.exceptions import HTTPException as StarletteHTTPException
from tortoise.contrib.fastapi import RegisterTortoise

from app.api.v1.ai import router as ai_router
from app.api.v1.financial import router as financial_router
from app.api.v1.payments import router as payments_router
from app.core.database import TORTOISE_ORM
from app.core.exception_handlers import (
    ai_service_exception_handler,
    general_exception_handler,
    http_exception_handler,
    validation_exception_handler,
)
from app.core.exceptions import AIServiceException


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

add_pagination(app)

# Exception handlers
app.add_exception_handler(AIServiceException, ai_service_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Routers
app.include_router(ai_router)
app.include_router(financial_router)
app.include_router(payments_router)

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
