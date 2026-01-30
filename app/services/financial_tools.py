"""
Financial Tools for AI Agent

This module provides explicit, well-documented tools that the AI agent can use
to query payment data. Each tool has a clear purpose, comprehensive documentation,
and predictable behavior.

Design Philosophy: Following Anthropic's agent building principles
- Simplicity: Each tool does ONE thing well
- Transparency: Clear inputs, outputs, and error messages
- Testability: Predictable behavior with comprehensive tests
"""

import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Literal

from fastapi import Depends

from app.repositories.payment_repository import PaymentRepository

logger = logging.getLogger(__name__)

PeriodType = Literal["this_month", "last_month", "this_year", "last_year", "all_time"]
DirectionType = Literal["outgoing", "incoming", "all"]
GranularityType = Literal["day", "week", "month"]


def get_date_range(period: PeriodType) -> tuple[datetime | None, datetime | None]:
    """
    Convert a period string into start and end datetime objects.

    Args:
        period: Time period identifier. Options:
            - "this_month": Current calendar month
            - "last_month": Previous calendar month
            - "this_year": Current calendar year
            - "last_year": Previous calendar year
            - "all_time": All available data (returns None, None)

    Returns:
        Tuple of (start_date, end_date) as datetime objects.
        Returns (None, None) for "all_time".

    Raises:
        ValueError: If period is not recognized

    Examples:
        >>> get_date_range("this_month")  # On 2026-01-31
        (datetime(2026, 1, 1, 0, 0), datetime(2026, 1, 31, 23, 59, 59))

        >>> get_date_range("all_time")
        (None, None)
    """
    now = datetime.now()

    if period == "all_time":
        return None, None

    elif period == "this_month":
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        # Last day of current month
        if now.month == 12:
            end = now.replace(day=31, hour=23, minute=59, second=59, microsecond=999999)
        else:
            next_month = now.replace(month=now.month + 1, day=1)
            end = (next_month - timedelta(days=1)).replace(
                hour=23, minute=59, second=59, microsecond=999999
            )
        return start, end

    elif period == "last_month":
        # First day of current month
        first_of_this_month = now.replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        )
        # Last day of last month
        end = (first_of_this_month - timedelta(days=1)).replace(
            hour=23, minute=59, second=59, microsecond=999999
        )
        # First day of last month
        start = end.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        return start, end

    elif period == "this_year":
        start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        end = now.replace(
            month=12, day=31, hour=23, minute=59, second=59, microsecond=999999
        )
        return start, end

    elif period == "last_year":
        start = now.replace(
            year=now.year - 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0
        )
        end = now.replace(
            year=now.year - 1,
            month=12,
            day=31,
            hour=23,
            minute=59,
            second=59,
            microsecond=999999,
        )
        return start, end

    else:
        raise ValueError(
            f"Unknown period: {period}. "
            f"Valid options: this_month, last_month, this_year, last_year, all_time"
        )


def format_period_name(period: PeriodType) -> str:
    """
    Convert a period identifier to a human-readable name.

    Args:
        period: Period identifier

    Returns:
        Human-readable period name

    Examples:
        >>> format_period_name("this_month")  # On January 2026
        "January 2026"

        >>> format_period_name("all_time")
        "All Time"
    """
    now = datetime.now()

    if period == "all_time":
        return "All Time"
    elif period == "this_month":
        return now.strftime("%B %Y")
    elif period == "last_month":
        last_month = now.replace(day=1) - timedelta(days=1)
        return last_month.strftime("%B %Y")
    elif period == "this_year":
        return str(now.year)
    elif period == "last_year":
        return str(now.year - 1)
    else:
        return period


class FinancialTools:
    """
    Financial analysis tools for the AI agent.

    Each method is a tool that the AI can call to retrieve specific
    financial information from the end_user_payments table.
    """

    def __init__(self, payment_repository: PaymentRepository = Depends()):
        self.payment_repository = payment_repository

    async def get_spending_summary(
        self,
        period: PeriodType = "this_month",
        direction: DirectionType = "outgoing",
        consumer_phone_number: str | None = None,
    ) -> dict:
        """
        Get total spending summary for a specific time period.

        Use this tool when the user asks about total spending, income, or
        transaction counts for a specific time period.

        Args:
            period: Time period to analyze. Options:
                - "this_month": Current calendar month (default)
                - "last_month": Previous calendar month
                - "this_year": Current calendar year
                - "last_year": Previous calendar year
                - "all_time": All available data
            direction: Payment direction to analyze:
                - "outgoing": Money spent (default)
                - "incoming": Money received
                - "all": Both incoming and outgoing
            consumer_phone_number: Optional phone number to filter by specific user

        Returns:
            Dictionary with:
                - total: Total amount as Decimal
                - count: Number of transactions as int
                - period: Human-readable period description
                - start_date: Period start datetime (None for all_time)
                - end_date: Period end datetime (None for all_time)
                - direction: Direction filter applied

        Examples:
            User: "How much did I spend this month?"
            >>> await get_spending_summary("this_month", "outgoing")
            {
                "total": Decimal("45000.00"),
                "count": 23,
                "period": "January 2026",
                "start_date": datetime(2026, 1, 1),
                "end_date": datetime(2026, 1, 31, 23, 59, 59),
                "direction": "outgoing"
            }

            User: "How much money did I receive last year?"
            >>> await get_spending_summary("last_year", "incoming")
            {
                "total": Decimal("120000.00"),
                "count": 45,
                "period": "2025",
                ...
            }

        Raises:
            ValueError: If period or direction is invalid
        """
        logger.info(
            f"get_spending_summary called: period={period}, direction={direction}, "
            f"consumer_phone_number={consumer_phone_number}"
        )

        start_date, end_date = get_date_range(period)

        result = await self.payment_repository.get_total_by_period(
            start_date=start_date,
            end_date=end_date,
            direction=direction,
            consumer_phone_number=consumer_phone_number,
        )

        return {
            "total": result["total"] or Decimal("0.00"),
            "count": result["count"] or 0,
            "period": format_period_name(period),
            "start_date": start_date,
            "end_date": end_date,
            "direction": direction,
        }

    async def get_payments_by_recipient(
        self,
        name: str,
        limit: int = 10,
        consumer_phone_number: str | None = None,
    ) -> list[dict]:
        """
        Get payments to/from a specific recipient.

        Use this tool when the user asks about payments to a specific person,
        business, or entity. Uses fuzzy name matching to handle variations.

        Args:
            name: Recipient name to search for (case-insensitive, fuzzy match)
            limit: Maximum number of payments to return (default: 10, max: 100)
            consumer_phone_number: Optional phone number to filter by specific user

        Returns:
            List of payment dictionaries, each containing:
                - name: Recipient name
                - amount: Payment amount
                - date: Payment date
                - direction: "outgoing" or "incoming"
                - transaction_id: Unique transaction identifier

        Examples:
            User: "How much have I paid to Safaricom?"
            >>> await get_payments_by_recipient("Safaricom", limit=10)
            [
                {
                    "name": "Safaricom Ltd",
                    "amount": Decimal("1000.00"),
                    "date": datetime(2026, 1, 15),
                    "direction": "outgoing",
                    "transaction_id": "TXN123"
                },
                ...
            ]

            User: "Show me my last 5 payments to John"
            >>> await get_payments_by_recipient("John", limit=5)
            [...]

        Raises:
            ValueError: If limit is invalid (< 1 or > 100)

        Note:
            Returns empty list if no matching payments found.
        """
        logger.info(
            f"get_payments_by_recipient called: name={name}, limit={limit}, "
            f"consumer_phone_number={consumer_phone_number}"
        )

        if limit < 1 or limit > 100:
            raise ValueError("Limit must be between 1 and 100")

        payments = await self.payment_repository.get_payments_by_name_fuzzy(
            name=name,
            limit=limit,
            consumer_phone_number=consumer_phone_number,
        )

        return [
            {
                "name": payment.name,
                "amount": payment.amount,
                "date": payment.paid_at or payment.created_at,
                "direction": payment.direction,
                "transaction_id": payment.transaction_id,
            }
            for payment in payments
        ]

    async def get_top_recipients(
        self,
        direction: DirectionType = "outgoing",
        limit: int = 5,
        period: PeriodType = "all_time",
        consumer_phone_number: str | None = None,
    ) -> list[dict]:
        """
        Get top recipients by total payment amount.

        Use this tool when the user asks about their biggest expenses,
        top vendors, or main income sources.

        Args:
            direction: Payment direction to analyze:
                - "outgoing": Top expenses (default)
                - "incoming": Top income sources
                - "all": Top recipients regardless of direction
            limit: Number of top recipients to return (default: 5, max: 20)
            period: Time period to analyze (default: "all_time")
            consumer_phone_number: Optional phone number to filter by specific user

        Returns:
            List of recipient dictionaries, each containing:
                - name: Recipient name
                - total: Total amount paid/received
                - count: Number of transactions
                - average: Average transaction amount

        Examples:
            User: "Who are my top 5 expenses?"
            >>> await get_top_recipients("outgoing", limit=5)
            [
                {
                    "name": "Safaricom Ltd",
                    "total": Decimal("15000.00"),
                    "count": 12,
                    "average": Decimal("1250.00")
                },
                ...
            ]

            User: "Show me my biggest expenses this month"
            >>> await get_top_recipients("outgoing", limit=10, period="this_month")
            [...]

        Raises:
            ValueError: If limit is invalid (< 1 or > 20)

        Note:
            Returns empty list if no payments found for the period.
        """
        logger.info(
            f"get_top_recipients called: direction={direction}, limit={limit}, "
            f"period={period}, consumer_phone_number={consumer_phone_number}"
        )

        if limit < 1 or limit > 20:
            raise ValueError("Limit must be between 1 and 20")

        start_date, end_date = get_date_range(period)

        recipients = await self.payment_repository.get_top_recipients_aggregated(
            direction=direction,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            consumer_phone_number=consumer_phone_number,
        )

        return recipients

    async def get_spending_by_category(
        self,
        period: PeriodType = "this_month",
        consumer_phone_number: str | None = None,
    ) -> list[dict]:
        """
        Get spending grouped by payment method (sender_id).

        Use this tool when the user asks about spending breakdown by
        payment method, channel, or category.

        Args:
            period: Time period to analyze (default: "this_month")
            consumer_phone_number: Optional phone number to filter by specific user

        Returns:
            List of category dictionaries, each containing:
                - sender_id: Payment method (e.g., "MPESA", "AIRTELMONEY")
                - total: Total amount spent via this method
                - count: Number of transactions
                - percentage: Percentage of total spending

        Examples:
            User: "Break down my spending by payment method this month"
            >>> await get_spending_by_category("this_month")
            [
                {
                    "sender_id": "MPESA",
                    "total": Decimal("30000.00"),
                    "count": 15,
                    "percentage": 66.7
                },
                {
                    "sender_id": "AIRTELMONEY",
                    "total": Decimal("15000.00"),
                    "count": 8,
                    "percentage": 33.3
                }
            ]

        Note:
            Returns empty list if no payments found for the period.
        """
        logger.info(
            f"get_spending_by_category called: period={period}, "
            f"consumer_phone_number={consumer_phone_number}"
        )

        start_date, end_date = get_date_range(period)

        categories = await self.payment_repository.get_spending_by_sender(
            start_date=start_date,
            end_date=end_date,
            consumer_phone_number=consumer_phone_number,
        )

        # Calculate percentages
        total_spending = sum(cat["total"] for cat in categories)
        for cat in categories:
            if total_spending > 0:
                cat["percentage"] = float((cat["total"] / total_spending) * 100)
            else:
                cat["percentage"] = 0.0

        return categories

    async def get_payment_trends(
        self,
        granularity: GranularityType = "month",
        limit: int = 12,
        consumer_phone_number: str | None = None,
    ) -> list[dict]:
        """
        Get spending trends over time.

        Use this tool when the user asks about spending patterns,
        trends, or historical analysis.

        Args:
            granularity: Time grouping for trends:
                - "day": Daily trends
                - "week": Weekly trends
                - "month": Monthly trends (default)
            limit: Number of periods to return (default: 12, max: 365)
            consumer_phone_number: Optional phone number to filter by specific user

        Returns:
            List of trend dictionaries, each containing:
                - period: Period label (e.g., "2026-01" for month)
                - total: Total amount for the period
                - count: Number of transactions
                - average: Average transaction amount

        Examples:
            User: "Show me my spending trends over the last year"
            >>> await get_payment_trends("month", limit=12)
            [
                {
                    "period": "2026-01",
                    "total": Decimal("45000.00"),
                    "count": 23,
                    "average": Decimal("1956.52")
                },
                {
                    "period": "2025-12",
                    "total": Decimal("38000.00"),
                    "count": 19,
                    "average": Decimal("2000.00")
                },
                ...
            ]

            User: "What's my daily spending for the last week?"
            >>> await get_payment_trends("day", limit=7)
            [...]

        Raises:
            ValueError: If limit is invalid (< 1 or > 365)

        Note:
            Returns data in reverse chronological order (most recent first).
        """
        logger.info(
            f"get_payment_trends called: granularity={granularity}, limit={limit}, "
            f"consumer_phone_number={consumer_phone_number}"
        )

        if limit < 1 or limit > 365:
            raise ValueError("Limit must be between 1 and 365")

        trends = await self.payment_repository.get_trend_data(
            granularity=granularity,
            limit=limit,
            consumer_phone_number=consumer_phone_number,
        )

        return trends
