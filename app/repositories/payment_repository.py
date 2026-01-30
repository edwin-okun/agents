from datetime import datetime
from decimal import Decimal

from tortoise.functions import Count, Sum
from tortoise.queryset import QuerySet

from app.models.payment import EndUserPayment


class PaymentRepository:
    def get_all_payments(self) -> QuerySet[EndUserPayment]:
        return EndUserPayment.all()

    async def get_total_by_period(
        self,
        start_date: datetime | None,
        end_date: datetime | None,
        direction: str,
        consumer_phone_number: str | None = None,
    ) -> dict:
        """
        Get total amount and count of payments for a specific period.

        Args:
            start_date: Period start (None for all time)
            end_date: Period end (None for all time)
            direction: "outgoing", "incoming", or "all"
            consumer_phone_number: Optional phone number filter

        Returns:
            Dict with "total" (Decimal) and "count" (int)
        """
        query = EndUserPayment.all()

        # Apply date filters
        if start_date:
            query = query.filter(paid_at__gte=start_date)
        if end_date:
            query = query.filter(paid_at__lte=end_date)

        # Apply direction filter
        if direction != "all":
            query = query.filter(direction=direction)

        # Apply user filter
        if consumer_phone_number:
            query = query.filter(consumer_phone_number=consumer_phone_number)

        # Aggregate
        result = await query.annotate(total=Sum("amount"), count=Count("id")).values(
            "total", "count"
        )

        if result:
            return {
                "total": result[0]["total"] or Decimal("0.00"),
                "count": result[0]["count"] or 0,
            }
        return {"total": Decimal("0.00"), "count": 0}

    async def get_payments_by_name_fuzzy(
        self,
        name: str,
        limit: int,
        consumer_phone_number: str | None = None,
    ) -> list[EndUserPayment]:
        """
        Get payments matching a recipient name (case-insensitive fuzzy match).

        Args:
            name: Name to search for
            limit: Maximum results
            consumer_phone_number: Optional phone number filter

        Returns:
            List of EndUserPayment objects
        """
        query = EndUserPayment.filter(name__icontains=name)

        if consumer_phone_number:
            query = query.filter(consumer_phone_number=consumer_phone_number)

        return await query.order_by("-paid_at").limit(limit).all()

    async def get_top_recipients_aggregated(
        self,
        direction: str,
        start_date: datetime | None,
        end_date: datetime | None,
        limit: int,
        consumer_phone_number: str | None = None,
    ) -> list[dict]:
        """
        Get top recipients by total amount with aggregated data.

        Args:
            direction: "outgoing", "incoming", or "all"
            start_date: Period start (None for all time)
            end_date: Period end (None for all time)
            limit: Maximum results
            consumer_phone_number: Optional phone number filter

        Returns:
            List of dicts with name, total, count, average
        """
        query = EndUserPayment.all()

        # Apply filters
        if start_date:
            query = query.filter(paid_at__gte=start_date)
        if end_date:
            query = query.filter(paid_at__lte=end_date)
        if direction != "all":
            query = query.filter(direction=direction)
        if consumer_phone_number:
            query = query.filter(consumer_phone_number=consumer_phone_number)

        # Filter out null names
        query = query.filter(name__isnull=False)

        # Group by name and aggregate
        results = (
            await query.group_by("name")
            .annotate(total=Sum("amount"), count=Count("id"))
            .order_by("-total")
            .limit(limit)
            .values("name", "total", "count")
        )

        # Calculate averages
        for result in results:
            if result["count"] > 0:
                result["average"] = result["total"] / result["count"]
            else:
                result["average"] = Decimal("0.00")

        return results

    async def get_spending_by_sender(
        self,
        start_date: datetime | None,
        end_date: datetime | None,
        consumer_phone_number: str | None = None,
    ) -> list[dict]:
        """
        Get spending grouped by sender_id (payment method).

        Args:
            start_date: Period start (None for all time)
            end_date: Period end (None for all time)
            consumer_phone_number: Optional phone number filter

        Returns:
            List of dicts with sender_id, total, count
        """
        query = EndUserPayment.filter(direction="outgoing")

        if start_date:
            query = query.filter(paid_at__gte=start_date)
        if end_date:
            query = query.filter(paid_at__lte=end_date)
        if consumer_phone_number:
            query = query.filter(consumer_phone_number=consumer_phone_number)

        results = (
            await query.group_by("sender_id")
            .annotate(total=Sum("amount"), count=Count("id"))
            .order_by("-total")
            .values("sender_id", "total", "count")
        )

        return results

    async def get_trend_data(
        self,
        granularity: str,
        limit: int,
        consumer_phone_number: str | None = None,
    ) -> list[dict]:
        """
        Get payment trends over time.

        Args:
            granularity: "day", "week", or "month"
            limit: Number of periods to return
            consumer_phone_number: Optional phone number filter

        Returns:
            List of dicts with period, total, count, average
        """
        # This is a simplified implementation
        # For production, you'd want to use database-specific date functions
        # via raw SQL for better performance

        from tortoise import connections

        # Build the SQL query based on granularity
        date_format_map = {
            "day": "YYYY-MM-DD",
            "week": "IYYY-IW",  # ISO year and week
            "month": "YYYY-MM",
        }

        date_format = date_format_map.get(granularity, "YYYY-MM")

        # Build WHERE clause
        where_clauses = ["direction = 'outgoing'"]
        if consumer_phone_number:
            where_clauses.append(f"consumer_phone_number = '{consumer_phone_number}'")

        where_sql = " AND ".join(where_clauses)

        sql = f"""
            SELECT 
                TO_CHAR(paid_at, '{date_format}') as period,
                SUM(amount) as total,
                COUNT(*) as count,
                AVG(amount) as average
            FROM end_user_payments
            WHERE {where_sql}
            GROUP BY TO_CHAR(paid_at, '{date_format}')
            ORDER BY period DESC
            LIMIT {limit}
        """

        conn = connections.get("default")
        results = await conn.execute_query_dict(sql)

        # Convert to proper types
        for result in results:
            result["total"] = (
                Decimal(str(result["total"])) if result["total"] else Decimal("0.00")
            )
            result["average"] = (
                Decimal(str(result["average"]))
                if result["average"]
                else Decimal("0.00")
            )

        return results
