"""
Test script for financial tools

This script tests the financial tools directly without requiring the AI.
Run with: uv run python test_financial_tools.py
"""

import asyncio

from tortoise import Tortoise

from app.core.database import TORTOISE_ORM
from app.repositories.payment_repository import PaymentRepository
from app.services.financial_tools import FinancialTools


async def test_tools():
    """Test all financial tools with sample queries."""

    # Initialize database
    await Tortoise.init(config=TORTOISE_ORM)

    # Initialize tools
    repo = PaymentRepository()
    tools = FinancialTools(repo)

    print("=" * 60)
    print("FINANCIAL TOOLS TEST")
    print("=" * 60)

    # Test 1: Spending Summary
    print("\n1. Testing get_spending_summary()")
    print("-" * 60)
    try:
        result = await tools.get_spending_summary("this_month", "outgoing")
        print("✓ This month's spending:")
        print(f"  Total: {result['total']} KES")
        print(f"  Count: {result['count']} transactions")
        print(f"  Period: {result['period']}")
    except Exception as e:
        print(f"✗ Error: {e}")

    # Test 2: Payments by Recipient
    print("\n2. Testing get_payments_by_recipient()")
    print("-" * 60)
    try:
        payments = await tools.get_payments_by_recipient("Safaricom", limit=5)
        print(f"✓ Found {len(payments)} payments to 'Safaricom':")
        for p in payments[:3]:  # Show first 3
            print(f"  - {p['name']}: {p['amount']} KES on {p['date']}")
        if len(payments) > 3:
            print(f"  ... and {len(payments) - 3} more")
    except Exception as e:
        print(f"✗ Error: {e}")

    # Test 3: Top Recipients
    print("\n3. Testing get_top_recipients()")
    print("-" * 60)
    try:
        top = await tools.get_top_recipients("outgoing", limit=5, period="all_time")
        print("✓ Top 5 expenses (all time):")
        for i, recipient in enumerate(top, 1):
            print(
                f"  {i}. {recipient['name']}: {recipient['total']} KES "
                f"({recipient['count']} payments)"
            )
    except Exception as e:
        print(f"✗ Error: {e}")

    # Test 4: Spending by Category
    print("\n4. Testing get_spending_by_category()")
    print("-" * 60)
    try:
        categories = await tools.get_spending_by_category("this_month")
        print("✓ Spending by payment method (this month):")
        for cat in categories:
            print(
                f"  - {cat['sender_id']}: {cat['total']} KES ({cat['percentage']:.1f}%)"
            )
    except Exception as e:
        print(f"✗ Error: {e}")

    # Test 5: Payment Trends
    print("\n5. Testing get_payment_trends()")
    print("-" * 60)
    try:
        trends = await tools.get_payment_trends("month", limit=6)
        print("✓ Monthly spending trends (last 6 months):")
        for trend in trends:
            print(
                f"  {trend['period']}: {trend['total']} KES "
                f"({trend['count']} payments, avg: {trend['average']} KES)"
            )
    except Exception as e:
        print(f"✗ Error: {e}")

    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)

    # Close database connection
    await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(test_tools())
