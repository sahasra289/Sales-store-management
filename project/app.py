# app.py
from flask import Flask, render_template, request, redirect
import database

app = Flask(__name__)

# make sure DB exists / tables created
database.init_db()

# ---------- HOME ----------
@app.route("/")
def index():
    return render_template("index.html")

# ---------- CUSTOMERS ----------
@app.route("/customers")
def customers():
    rows = database.get_customers()
    return render_template("customers.html", customers=rows)

@app.route("/add_customer", methods=["POST"])
def add_customer():
    name = request.form.get("name", "").strip()
    phone = request.form.get("phone", "").strip()
    email = request.form.get("email", "").strip()
    if name:
        database.add_customer(name, phone, email)
    return redirect("/customers")

@app.route("/delete_customer/<int:id>")
def delete_customer(id):
    database.delete_customer(id)
    return redirect("/customers")


# ---------- ITEMS ----------
@app.route("/items")
def items():
    rows = database.get_items()
    return render_template("items.html", items=rows)

@app.route("/add_item", methods=["POST"])
def add_item():
    name = request.form.get("name", "").strip()
    stock = request.form.get("stock", "0").strip()
    price = request.form.get("price", "0").strip()
    try:
        stock = int(stock)
    except:
        stock = 0
    try:
        price = float(price)
    except:
        price = 0.0
    if name:
        database.add_item(name, stock, price)
    return redirect("/items")

@app.route("/delete_item/<int:id>")
def delete_item(id):
    database.delete_item(id)
    return redirect("/items")


# ---------- SALES ----------
@app.route("/sales")
def sales():
    customers = database.get_customers()
    items = database.get_items()
    sales = database.get_sales()
    return render_template("sales.html", customers=customers, items=items, sales=sales)

@app.route("/add_sale", methods=["POST"])
def add_sale():
    customer_id = request.form.get("customer_id")
    item_id = request.form.get("item_id")
    quantity = request.form.get("quantity", "1")
    try:
        quantity = int(quantity)
        if quantity <= 0:
            quantity = 1
    except:
        quantity = 1

    # compute item price
    conn = database.get_db()
    row = conn.execute("SELECT price, stock FROM items WHERE id=?", (item_id,)).fetchone()
    conn.close()
    if row:
        price = float(row["price"])
        stock = int(row["stock"]) if row["stock"] is not None else 0
    else:
        price = 0.0
        stock = 0

    total = price * quantity

    # if not enough stock, still allow (you can change behavior)
    database.add_sale(customer_id, item_id, quantity, total)
    return redirect("/sales")

@app.route("/delete_sale/<int:id>")
def delete_sale(id):
    database.delete_sale(id)
    return redirect("/sales")


# ---------- DUE ----------
@app.route("/due")
def due():
    customers = database.get_customers()
    dues = database.get_dues()
    return render_template("due.html", customers=customers, due=dues)

@app.route("/add_due", methods=["POST"])
def add_due():
    customer_id = request.form.get("customer_id")
    amount = request.form.get("amount", "0")
    try:
        amount = float(amount)
    except:
        amount = 0.0
    if customer_id and amount > 0:
        database.add_due(customer_id, amount)
    return redirect("/due")

@app.route("/delete_due/<int:id>")
def delete_due(id):
    database.delete_due(id)
    return redirect("/due")


if __name__ == "__main__":
    app.run(debug=True)
