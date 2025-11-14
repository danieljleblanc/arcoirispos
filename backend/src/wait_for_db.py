import asyncio
import asyncpg
import os

DB_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://arcoiris_user:ArcoirisDevP@ss2025@postgres:5432/arcoirispos_dev"
)

async def wait_for_postgres():
    print(f"🔄 Waiting for database: {DB_URL}")

    for attempt in range(30):
        try:
            conn = await asyncpg.connect(DB_URL)
            await conn.close()
            print("✅ Postgres is ready!")
            return
        except Exception as e:
            print(f"⏳ Attempt {attempt+1}/30 - DB not ready yet: {e}")
            await asyncio.sleep(1)

    raise Exception("❌ Postgres did not become ready")

if __name__ == "__main__":
    asyncio.run(wait_for_postgres())
