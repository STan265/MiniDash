
import sqlite3
from pathlib import Path

DATABASE_PATH = Path("minidash.db")


def get_connection():
    """Create and return a SQLite database connection."""
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    """Create database tables and insert sample restaurants."""
    connection = get_connection()

    connection.executescript("""
        CREATE TABLE IF NOT EXISTS restaurants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            cuisine TEXT NOT NULL,
            opens_at TEXT NOT NULL,
            closes_at TEXT NOT NULL,
            avg_prep_minutes INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS menu_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            restaurant_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            price_cents INTEGER NOT NULL,
            FOREIGN KEY (restaurant_id) REFERENCES restaurants(id)
        );

        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            restaurant_id INTEGER NOT NULL,
            status TEXT NOT NULL,
            total_cents INTEGER NOT NULL,
            address TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (restaurant_id) REFERENCES restaurants(id)
        );

        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            menu_item_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(id),
            FOREIGN KEY (menu_item_id) REFERENCES menu_items(id)
        );
    """)
    # Add scheduled delivery support to existing databases.
    order_columns = connection.execute(
        "PRAGMA table_info(orders)"
    ).fetchall()

    column_names = {
        column["name"] for column in order_columns
    }

    if "scheduled_for" not in column_names:
        connection.execute(
            "ALTER TABLE orders ADD COLUMN scheduled_for TEXT"
        )
        
    restaurant_count = connection.execute(
        "SELECT COUNT(*) FROM restaurants"
    ).fetchone()[0]

    if restaurant_count == 0:
        restaurants = [
            ("Golden Dragon", "Chinese", "10:00", "22:00", 25),
            ("Mario's Pizza", "Italian", "11:00", "23:00", 20),
            ("Tokyo Sushi", "Japanese", "11:00", "21:00", 30),
            ("Green Garden", "American", "09:00", "21:00", 15),
            ("Taco Fiesta", "Mexican", "10:00", "22:00", 20),
        ]

        connection.executemany("""
            INSERT INTO restaurants
            (name, cuisine, opens_at, closes_at, avg_prep_minutes)
            VALUES (?, ?, ?, ?, ?)
        """, restaurants)


    menu_count = connection.execute(
        "SELECT COUNT(*) FROM menu_items"
    ).fetchone()[0]

    if menu_count == 0:
        menu_items = [
            (1, "Chicken Fried Rice", 1299),
            (1, "Beef Lo Mein", 1499),
            (1, "Spring Rolls", 599),
            (2, "Pepperoni Pizza", 1599),
            (2, "Cheese Pizza", 1399),
            (2, "Garlic Bread", 699),
            (3, "Salmon Sushi Roll", 1299),
            (3, "California Roll", 1099),
            (3, "Miso Soup", 499),
            (4, "Grilled Chicken Salad", 1399),
            (4, "Veggie Burger", 1299),
            (4, "French Fries", 499),
            (5, "Beef Tacos", 1099),
            (5, "Chicken Burrito", 1299),
            (5, "Nachos", 899),
        ]

        connection.executemany("""
            INSERT INTO menu_items
            (restaurant_id, name, price_cents)
            VALUES (?, ?, ?)
        """, menu_items)

    connection.commit()
    connection.close()
