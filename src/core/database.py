import json
from pathlib import Path

import aiosqlite

DB_PATH = Path("invoices.db")


async def init_db() -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                parsed_data TEXT NOT NULL,
                raw_text TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()


async def save_invoice(filename: str, parsed_data: dict, raw_text: str) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "INSERT INTO invoices (filename, parsed_data, raw_text) VALUES (?, ?, ?)",
            (filename, json.dumps(parsed_data), raw_text),
        )
        await db.commit()
        return cursor.lastrowid


async def get_invoice(invoice_id: int) -> dict | None:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM invoices WHERE id = ?", (invoice_id,))
        row = await cursor.fetchone()
        if row:
            return {
                "id": row["id"],
                "filename": row["filename"],
                "parsed_data": json.loads(row["parsed_data"]),
                "raw_text": row["raw_text"],
                "created_at": row["created_at"],
            }
        return None


async def list_invoices(limit: int = 50, offset: int = 0) -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT id, filename, created_at FROM invoices ORDER BY id DESC LIMIT ? OFFSET ?",
            (limit, offset),
        )
        rows = await cursor.fetchall()
        return [
            {"id": row["id"], "filename": row["filename"], "created_at": row["created_at"]}
            for row in rows
        ]
