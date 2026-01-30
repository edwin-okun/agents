"""
Test script for AI-powered natural language formatter

This script demonstrates the format_response_naturally method which uses
AI to convert structured responses into conversational English.

Run with: uv run python test_ai_formatter.py
"""

import asyncio

from tortoise import Tortoise

from app.core.database import TORTOISE_ORM
from app.repositories.payment_repository import PaymentRepository
from app.schemas.financial_schema import FinancialAnswerSchema, ToolCall
from app.services.financial_agent_service import FinancialAgentService
from app.services.financial_tools import FinancialTools


async def test_ai_formatter():
    """Test the AI-powered natural language formatter."""

    # Initialize database
    await Tortoise.init(config=TORTOISE_ORM)

    # Initialize services
    repo = PaymentRepository()
    tools = FinancialTools(repo)
    agent = FinancialAgentService(tools)

    print("\n" + "=" * 70)
    print("TESTING AI-POWERED NATURAL LANGUAGE FORMATTER")
    print("=" * 70)
    print("\nThis formatter uses AI to convert structured JSON responses")
    print("into natural, conversational English.\n")

    # Test 1: Spending Summary
    print("\n" + "=" * 70)
    print("TEST 1: Spending Summary")
    print("=" * 70)

    spending_result = await tools.get_spending_summary("this_month", "outgoing")

    response1 = FinancialAnswerSchema(
        answer=f"You spent {spending_result['total']:,.2f} KES this month.",
        tool_calls=[
            ToolCall(
                tool="get_spending_summary",
                params={"period": "this_month", "direction": "outgoing"},
                result=spending_result,
            )
        ],
        confidence="high",
    )

    print("\nSTRUCTURED RESPONSE (JSON):")
    print(f"Answer: {response1.answer}")
    print(f"Tool: {response1.tool_calls[0].tool}")
    print(f"Result: {response1.tool_calls[0].result}")

    print("\nAI-FORMATTED NATURAL LANGUAGE:")
    print("-" * 70)
    natural_text = await agent.format_response_naturally(response1)
    print(natural_text)

    # Test 2: Top Recipients
    print("\n\n" + "=" * 70)
    print("TEST 2: Top Recipients")
    print("=" * 70)

    top_recipients = await tools.get_top_recipients("outgoing", limit=5)

    response2 = FinancialAnswerSchema(
        answer="Here are your top 5 expenses.",
        tool_calls=[
            ToolCall(
                tool="get_top_recipients",
                params={
                    "direction": "outgoing",
                    "limit": 5,
                    "period": "all_time",
                },
                result=top_recipients,
            )
        ],
        confidence="high",
    )

    print("\nSTRUCTURED RESPONSE (JSON):")
    print(f"Answer: {response2.answer}")
    print(f"Tool: {response2.tool_calls[0].tool}")
    print(f"Result count: {len(top_recipients)} recipients")

    print("\nAI-FORMATTED NATURAL LANGUAGE:")
    print("-" * 70)
    natural_text = await agent.format_response_naturally(response2)
    print(natural_text)

    # Test 3: Payment Trends
    print("\n\n" + "=" * 70)
    print("TEST 3: Payment Trends")
    print("=" * 70)

    trends = await tools.get_payment_trends("month", limit=6)

    response3 = FinancialAnswerSchema(
        answer="Here are your monthly spending trends.",
        tool_calls=[
            ToolCall(
                tool="get_payment_trends",
                params={"granularity": "month", "limit": 6},
                result=trends,
            )
        ],
        confidence="high",
    )

    print("\nSTRUCTURED RESPONSE (JSON):")
    print(f"Answer: {response3.answer}")
    print(f"Tool: {response3.tool_calls[0].tool}")
    print(f"Result count: {len(trends)} periods")

    print("\nAI-FORMATTED NATURAL LANGUAGE:")
    print("-" * 70)
    natural_text = await agent.format_response_naturally(response3)
    print(natural_text)

    print("\n\n" + "=" * 70)
    print("ALL TESTS COMPLETE")
    print("=" * 70)
    print("\nThe AI successfully converted structured JSON data into")
    print("natural, conversational English!")

    # Close database connection
    await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(test_ai_formatter())
