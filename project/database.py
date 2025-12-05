# database.py
import sqlite3

DB_NAME = "store.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    # Customers
    cur.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT NOT NULL,
        email TEXT
    )
    """)

    # Items (with stock)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        stock INTEGER DEFAULT 0,
        price REAL NOT NULL
    )
    """)

    # Sales (references customers & items)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL,
        item_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        total REAL NOT NULL,
        date TEXT DEFAULT (datetime('now','localtime')),
        FOREIGN KEY(customer_id) REFERENCES customers(id),
        FOREIGN KEY(item_id) REFERENCES items(id)
    )
    """)

    # Due table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS due (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        date TEXT DEFAULT (datetime('now','localtime')),
        FOREIGN KEY(customer_id) REFERENCES customers(id)
    )
    """)

    conn.commit()
    conn.close()


def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


# Customer helpers
def add_customer(name, phone, email):
    conn = get_db()
    conn.execute("INSERT INTO customers (name, phone, email) VALUES (?, ?, ?)",
                 (name, phone, email))
    conn.commit()
    conn.close()

def get_customers():
    conn = get_db()
    rows = conn.execute("SELECT * FROM customers ORDER BY id DESC").fetchall()
    conn.close()
    return rows

def delete_customer(id):
    conn = get_db()
    conn.execute("DELETE FROM customers WHERE id=?", (id,))
    conn.commit()
    conn.close()


# Item helpers
def add_item(name, stock, price):
    conn = get_db()
    conn.execute("INSERT INTO items (name, stock, price) VALUES (?, ?, ?)", (name, stock, price))
    conn.commit()
    conn.close()

def get_items():
    conn = get_db()
    rows = conn.execute("SELECT * FROM items ORDER BY id DESC").fetchall()
    conn.close()
    return rows

def delete_item(id):
    conn = get_db()
    conn.execute("DELETE FROM items WHERE id=?", (id,))
    conn.commit()
    conn.close()


# Sales helpers
def add_sale(customer_id, item_id, quantity, total):
    conn = get_db()
    # insert sale and reduce stock atomically
    cur = conn.cursor()
    cur.execute("INSERT INTO sales (customer_id, item_id, quantity, total) VALUES (?,?,?,?)",
                 (customer_id, item_id, quantity, total))
    # reduce stock
    cur.execute("UPDATE items SET stock = stock - ? WHERE id = ?", (quantity, item_id))
    conn.commit()
    conn.close()

def get_sales():
    conn = get_db()
    rows = conn.execute("""
        SELECT s.id, c.name AS customer, i.name AS item, s.quantity, s.total, s.date
        FROM sales s
        JOIN customers c ON s.customer_id = c.id
        JOIN items i ON s.item_id = i.id
        ORDER BY s.date DESC
    """).fetchall()
    conn.close()
    return rows

def delete_sale(id):
    conn = get_db()
    conn.execute("DELETE FROM sales WHERE id=?", (id,))
    conn.commit()
    conn.close()


# Due helpers
def add_due(customer_id, amount):
    conn = get_db()
    conn.execute("INSERT INTO due (customer_id, amount) VALUES (?, ?)", (customer_id, amount))
    conn.commit()
    conn.close()

def get_dues():
    conn = get_db()
    rows = conn.execute("""
        SELECT d.id, c.name AS customer, d.amount, d.date
        FROM due d
        JOIN customers c ON d.customer_id = c.id
        ORDER BY d.date DESC
    """).fetchall()
    conn.close()
    return rows

def delete_due(id):
    conn = get_db()
    conn.execute("DELETE FROM due WHERE id=?", (id,))
    conn.commit()
    conn.close()
