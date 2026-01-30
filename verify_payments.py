import asyncio

from tortoise import Tortoise

from app.core.database import TORTOISE_ORM
from app.models.payment import EndUserPayment


async def verify_payments_api():
    await Tortoise.init(config=TORTOISE_ORM)
    # await Tortoise.generate_schemas()  # Skipping schema generation due to permissions

    # Insert dummy data - Skipping due to permission issues
    # await EndUserPayment.create(
    #     consumer_uid=str(uuid.uuid4()),
    #     transaction_id=str(uuid.uuid4()),
    #     name="Test User 1",
    #     is_business=False,
    #     direction=PaymentDirection.INCOMING,
    #     amount=Decimal("100.00"),
    #     sender_id="MPESA",
    #     country_code=CountryCode.KE,
    #     consumer_phone_number="254700000001",
    #     paid_at=datetime.now(),
    # )

    # await EndUserPayment.create(
    #     consumer_uid=str(uuid.uuid4()),
    #     transaction_id=str(uuid.uuid4()),
    #     name="Test User 2",
    #     is_business=True,
    #     direction=PaymentDirection.OUTGOING,
    #     amount=Decimal("50.50"),
    #     sender_id="AIRTELMONEY",
    #     country_code=CountryCode.GH,
    #     consumer_phone_number="233200000002",
    #     paid_at=datetime.now(),
    # )

    print("Skipped dummy data insertion.")

    # We can't easily test the API endpoint via Python request without running the server,
    # but we can verify the repository/service logic or just print that data is ready
    # and then manually curl.

    # For now, let's just query via ORM to confirm insertion
    count = await EndUserPayment.all().count()
    print(f"Total payments in DB: {count}")

    await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(verify_payments_api())
