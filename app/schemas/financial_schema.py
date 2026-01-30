"""
Schemas for Financial Agent API
"""

from typing import Any

from pydantic import BaseModel, Field


class FinancialQuestionSchema(BaseModel):
    """Request schema for financial questions."""

    question: str = Field(
        ...,
        description="Natural language question about payments",
        examples=["How much did I spend this month?", "Who are my top 5 expenses?"],
    )
    consumer_phone_number: str | None = Field(
        default=None,
        description="Optional phone number to filter payments by specific user",
    )


class ToolCall(BaseModel):
    """Schema for a single tool call made by the agent."""

    tool: str = Field(..., description="Name of the tool that was called")
    params: dict[str, Any] = Field(..., description="Parameters passed to the tool")
    result: dict[str, Any] | list[dict[str, Any]] | None = Field(
        default=None, description="Result returned by the tool"
    )


class FinancialAnswerSchema(BaseModel):
    """Response schema for financial questions."""

    answer: str = Field(
        ..., description="Natural language answer to the user's question"
    )
    tool_calls: list[ToolCall] = Field(
        default_factory=list,
        description="List of tools called to answer the question (for transparency)",
    )
    confidence: str = Field(
        default="medium",
        description="Confidence level of the answer: high, medium, or low",
    )


class FinancialAnswerTextSchema(BaseModel):
    """Response schema for financial questions."""

    answer: str = Field(
        ..., description="Natural language answer to the user's question"
    )
