import aiosqlite

DB_PATH = "bot_database.db"

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                username TEXT NOT NULL,
                plan TEXT NOT NULL,
                photo_id TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()

async def add_transaction(user_id: int, username: str, plan: str, photo_id: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO transactions (user_id, username, plan, photo_id) VALUES (?, ?, ?, ?)",
            (user_id, username, plan, photo_id)
        )
        await db.commit()

async def update_payment_status(user_id: int, status: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE transactions SET status = ? WHERE user_id = ? AND status = 'pending'",
            (status, user_id)
        )
        await db.commit()
