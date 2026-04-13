import sqlite3
from datetime import datetime
from typing import Optional, List, Tuple

class Database:
    def __init__(self, db_path="vogue_bot.db"):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                username TEXT,
                type TEXT,
                deadline TEXT,
                execution_option TEXT,  -- 'full' or 'print_only'
                extras TEXT,            -- 'poster', 'magnet', 'both'
                photos TEXT,
                texts TEXT,
                status TEXT DEFAULT 'new',
                tracking TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.commit()

    def add_order(self, user_id, username, order_type, deadline, execution_option, extras, photos, texts):
        self.cursor.execute("""
            INSERT INTO orders (user_id, username, type, deadline, execution_option, extras, photos, texts)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, username, order_type, deadline, execution_option, extras, photos, texts))
        self.conn.commit()
        return self.cursor.lastrowid

    def get_order(self, order_id):
        self.cursor.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
        return self.cursor.fetchone()

    def get_user_orders(self, user_id):
        self.cursor.execute("SELECT * FROM orders WHERE user_id = ? ORDER BY id DESC", (user_id,))
        return self.cursor.fetchall()

    def get_all_orders(self):
        self.cursor.execute("SELECT * FROM orders ORDER BY id DESC")
        return self.cursor.fetchall()

    def update_status(self, order_id, status):
        self.cursor.execute("UPDATE orders SET status = ? WHERE id = ?", (status, order_id))
        self.conn.commit()

    def update_tracking(self, order_id, tracking):
        self.cursor.execute("UPDATE orders SET tracking = ? WHERE id = ?", (tracking, order_id))
        self.conn.commit()