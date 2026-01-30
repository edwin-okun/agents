"""
Test script for financial tools with phone number filtering

This script tests the financial tools with consumer_phone_number filtering.
Run with: uv run python test_phone_filter.py
"""

import asyncio

from tortoise import Tortoise

from app.core.database import TORTOISE_ORM
from app.repositories.payment_repository import PaymentRepository
from app.services.financial_tools import FinancialTools


async def test_phone_filter():
    """Test financial tools with phone number filtering."""

    # Initialize database
    await Tortoise.init(config=TORTOISE_ORM)

    # Initialize tools
    repo = PaymentRepository()
    tools = FinancialTools(repo)

    print("=" * 60)
    print("PHONE NUMBER FILTER TEST")
    print("=" * 60)

    # First, let's get a sample phone number from the database
    from app.models.payment import EndUserPayment

    sample_payment = await EndUserPayment.first()
    if not sample_payment:
        print("No payments found in database!")
        await Tortoise.close_connections()
        return

    test_phone = sample_payment.consumer_phone_number
    print(f"\nTesting with phone number: {test_phone}")
    print("-" * 60)

    # Test 1: Spending Summary with phone filter
    print("\n1. Spending summary for specific phone number")
    print("-" * 60)
    try:
        result = await tools.get_spending_summary(
            "all_time", "outgoing", consumer_phone_number=test_phone
        )
        print(f"✓ Total spending for {test_phone}:")
        print(f"  Total: {result['total']} KES")
        print(f"  Count: {result['count']} transactions")
    except Exception as e:
        print(f"✗ Error: {e}")

    # Test 2: Top recipients for specific phone
    print("\n2. Top recipients for specific phone number")
    print("-" * 60)
    try:
        top = await tools.get_top_recipients(
            "outgoing", limit=3, period="all_time", consumer_phone_number=test_phone
        )
        print(f"✓ Top 3 expenses for {test_phone}:")
        for i, recipient in enumerate(top, 1):
            print(
                f"  {i}. {recipient['name']}: {recipient['total']} KES "
                f"({recipient['count']} payments)"
            )
    except Exception as e:
        print(f"✗ Error: {e}")

    # Test 3: Compare with no filter
    print("\n3. Comparison: With filter vs Without filter")
    print("-" * 60)
    try:
        with_filter = await tools.get_spending_summary(
            "this_month", "outgoing", consumer_phone_number=test_phone
        )
        without_filter = await tools.get_spending_summary("this_month", "outgoing")

        print("✓ This month's spending:")
        print(
            f"  For {test_phone}: {with_filter['total']} KES ({with_filter['count']} txns)"
        )
        print(
            f"  All users: {without_filter['total']} KES ({without_filter['count']} txns)"
        )
    except Exception as e:
        print(f"✗ Error: {e}")

    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)

    # Close database connection
    await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(test_phone_filter())
