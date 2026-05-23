import random
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path


DB_PATH = Path("data") / "events.db"

EVENT_TYPES = [
    "VIEW",
    "CLICK",
    "PURCHASE",
    "REFUND",
    "EXCHANGE",
    "LOGIN",
    "LOGOUT",
]

PRODUCTS = ["p1", "p2", "p3", "p4", "p5"]


def create_tables(conn):
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS events (
            event_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            event_type TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS transactions (
            event_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            product TEXT NOT NULL,
            amount INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS reviews (
            event_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            product TEXT NOT NULL,
            review_rating INTEGER NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )

    conn.commit()


def make_event():
    event_type = random.choice(EVENT_TYPES)

    event = {
        "event_id": str(uuid.uuid4()),
        "user_id": "user_" + str(random.randint(1, 100)),
        "event_type": event_type,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    return event


def make_transaction(event):
    quantity = random.randint(1, 5)
    price = random.choice([10000, 15000, 20000, 30000, 50000])

    transaction = {
        "event_id": event["event_id"],
        "user_id": event["user_id"],
        "product": random.choice(PRODUCTS),
        "amount": price * quantity,
        "quantity": quantity,
        "created_at": event["created_at"],
    }

    return transaction


def make_review(event, product):
    review = {
        "event_id": event["event_id"],
        "user_id": event["user_id"],
        "product": product,
        "review_rating": random.randint(1, 5),
        "created_at": event["created_at"],
    }

    return review


def insert_event(conn, event):
    conn.execute(
        """
        INSERT INTO events (event_id, user_id, event_type, created_at)
        VALUES (?, ?, ?, ?)
        """,
        (
            event["event_id"],
            event["user_id"],
            event["event_type"],
            event["created_at"],
        ),
    )


def insert_transaction(conn, transaction):
    conn.execute(
        """
        INSERT INTO transactions (
            event_id,
            user_id,
            product,
            amount,
            quantity,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            transaction["event_id"],
            transaction["user_id"],
            transaction["product"],
            transaction["amount"],
            transaction["quantity"],
            transaction["created_at"],
        ),
    )


def insert_review(conn, review):
    conn.execute(
        """
        INSERT INTO reviews (
            event_id,
            user_id,
            product,
            review_rating,
            created_at
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            review["event_id"],
            review["user_id"],
            review["product"],
            review["review_rating"],
            review["created_at"],
        ),
    )


def generate_data(count):
    DB_PATH.parent.mkdir(exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    create_tables(conn)

    for _ in range(count):
        event = make_event()
        insert_event(conn, event)

        if event["event_type"] in ["PURCHASE", "REFUND", "EXCHANGE"]:
            transaction = make_transaction(event)
            insert_transaction(conn, transaction)

            if event["event_type"] == "PURCHASE":
                review = make_review(event, transaction["product"])
                insert_review(conn, review)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    generate_data(2000)
    print("2000 events created.")
