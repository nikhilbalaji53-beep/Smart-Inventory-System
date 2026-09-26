from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
from database import init_db, get_db_connection


import os
from datetime import datetime
import pymysql
import pymysql.cursors
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Database configuration
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "nikhil@143")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_NAME = os.getenv("DB_NAME", "smart_inventory")


class DBConnectionWrapper:
    """Wrapper that provides sqlite-style execute(..., (?)) on top of MySQL connection"""
    def __init__(self, raw_conn):
        self.raw_conn = raw_conn
        self._cursor = raw_conn.cursor()

    def execute(self, sql, params=()):
        # Convert ? placeholders to %s for MySQL/PyMySQL
        converted_sql = sql.replace("?", "%s")
        self._cursor.execute(converted_sql, params)
        return self

    def fetchone(self):
        return self._cursor.fetchone()

    def fetchall(self):
        return self._cursor.fetchall()

    def commit(self):
        self.raw_conn.commit()

    def close(self):
        try:
            self._cursor.close()
        except Exception:
            pass
        try:
            self.raw_conn.close()
        except Exception:
            pass


def get_db_connection():
    raw_conn = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT,
        database=DB_NAME,
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=False
    )
    return DBConnectionWrapper(raw_conn)


# -----------------------------------
# PRODUCT APIS
# -----------------------------------
@app.route("/api/products", methods=["GET"])
def get_products():
    conn = get_db_connection()
    products = conn.execute("SELECT * FROM products").fetchall()
    conn.close()
    return jsonify([dict(p) for p in products])


# -----------------------------------
# RECORD SALE
# -----------------------------------
@app.route("/api/sales", methods=["POST"])
def record_sale():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body is required"}), 400

    product_id = data.get("product_id")
    quantity = data.get("quantity")

    if not product_id or not quantity:
        return jsonify({"error": "product_id and quantity are required"}), 400

    conn = get_db_connection()

    # Check if product exists and has enough stock
    product = conn.execute(
        "SELECT * FROM products WHERE id = ?",
        (product_id,)
    ).fetchone()

    if not product:
        conn.close()
        return jsonify({"error": "Product not found"}), 404

    # Check stock (supporting both quantity and current_stock)
    stock_available = product.get("quantity") if product.get("quantity") is not None else product.get("current_stock", 0)
    if stock_available < quantity:
        conn.close()
        return jsonify({"error": "Insufficient stock quantity"}), 400

    # Deduct stock from products table
    conn.execute("""
        UPDATE products
        SET quantity = quantity - ?,
            current_stock = current_stock - ?
        WHERE id = ?
    """, (quantity, quantity, product_id))

    # Insert record into sales table
    conn.execute("""
        INSERT INTO sales (product_id, quantity, sale_date)
        VALUES (?, ?, ?)
    """, (
        product_id,
        quantity,
        data.get("sale_date", datetime.today().strftime("%Y-%m-%d"))
    ))

    conn.commit()
    conn.close()

    return jsonify({"message": "Sale recorded successfully and stock updated"}), 201


# -----------------------------------
# GET SALES HISTORY
# -----------------------------------
@app.route("/api/sales", methods=["GET"])
def get_sales():
    conn = get_db_connection()
    sales = conn.execute("""
        SELECT sales.id, products.name as product_name, sales.quantity, sales.sale_date
        FROM sales
        JOIN products ON sales.product_id = products.id
        ORDER BY sales.id DESC
    """).fetchall()
    conn.close()

    return jsonify([dict(sale) for sale in sales])

# -----------------------------------
# RECORD SALE & UPDATE STOCK
# -----------------------------------
@app.route("/api/sales", methods=["POST"])
def record_sale():
    data = request.get_json()

    if not data or "product_id" not in data or "quantity" not in data:
        return jsonify({
            "error": "product_id and quantity are required"
        }), 400

    product_id = data["product_id"]
    sale_quantity = data["quantity"]

    conn = get_db_connection()

    product = conn.execute(
        "SELECT * FROM products WHERE id = ?",
        (product_id,)
    ).fetchone()

    if not product:
        conn.close()
        return jsonify({"error": "Product not found"}), 404

    if product["quantity"] < sale_quantity:
        conn.close()
        return jsonify({"error": "Insufficient stock"}), 400

    # Reduce product stock
    conn.execute("""
        UPDATE products
        SET quantity = quantity - ?
        WHERE id = ?
    """, (sale_quantity, product_id))

    # Record sales entry
    conn.execute("""
        INSERT INTO sales (product_id, quantity, sale_date)
        VALUES (?, ?, ?)
    """, (
        product_id,
        sale_quantity,
        data.get("sale_date", datetime.today().strftime("%Y-%m-%d"))
    ))

    conn.commit()
    conn.close()

    return jsonify({
        "message": "Sale recorded and stock updated successfully"
    }), 201


# -----------------------------------
# GET SALES HISTORY
# -----------------------------------
@app.route("/api/sales", methods=["GET"])
def get_sales():
    conn = get_db_connection()
    sales = conn.execute("""
        SELECT sales.id, products.name, sales.quantity, sales.sale_date 
        FROM sales 
        JOIN products ON sales.product_id = products.id
        ORDER BY sales.id DESC
    """).fetchall()
    conn.close()

# -----------------------------------
# RECORD SALE & UPDATE STOCK
# -----------------------------------
@app.route("/api/sales", methods=["POST"])
def record_sale():
    data = request.get_json()

    if not data or "product_id" not in data or "quantity" not in data:
        return jsonify({
            "error": "product_id and quantity are required"
        }), 400

    product_id = data["product_id"]
    sale_quantity = data["quantity"]

    conn = get_db_connection()

    product = conn.execute(
        "SELECT * FROM products WHERE id = ?",
        (product_id,)
    ).fetchone()

    if not product:
        conn.close()
        return jsonify({"error": "Product not found"}), 404

    if product["quantity"] < sale_quantity:
        conn.close()
        return jsonify({"error": "Insufficient stock"}), 400

    # Reduce product stock
    conn.execute("""
        UPDATE products
        SET quantity = quantity - ?
        WHERE id = ?
    """, (sale_quantity, product_id))

    # Record sales entry
    conn.execute("""
        INSERT INTO sales (product_id, quantity, sale_date)
        VALUES (?, ?, ?)
    """, (
        product_id,
        sale_quantity,
        data.get("sale_date", datetime.today().strftime("%Y-%m-%d"))
    ))

    conn.commit()
    conn.close()

    return jsonify({
        "message": "Sale recorded and stock updated successfully"
    }), 201


# -----------------------------------
# GET SALES HISTORY
# -----------------------------------
@app.route("/api/sales", methods=["GET"])
def get_sales():
    conn = get_db_connection()
    sales = conn.execute("""
        SELECT sales.id, products.name, sales.quantity, sales.sale_date 
        FROM sales 
        JOIN products ON sales.product_id = products.id
        ORDER BY sales.id DESC
    """).fetchall()
    conn.close()


# RECORD SALE & UPDATE STOCK
# -----------------------------------
@app.route("/api/sales", methods=["POST"])
def record_sale():
    data = request.get_json()

    if not data or "product_id" not in data or "quantity" not in data:
        return jsonify({
            "error": "product_id and quantity are required"
        }), 400

    product_id = data["product_id"]
    sale_quantity = data["quantity"]

    conn = get_db_connection()

    product = conn.execute(
        "SELECT * FROM products WHERE id = ?",
        (product_id,)
    ).fetchone()

    if not product:
        conn.close()
        return jsonify({"error": "Product not found"}), 404

    if product["quantity"] < sale_quantity:
        conn.close()
        return jsonify({"error": "Insufficient stock"}), 400

    # Reduce product stock
    conn.execute("""
        UPDATE products
        SET quantity = quantity - ?
        WHERE id = ?
    """, (sale_quantity, product_id))

    # Record sales entry
    conn.execute("""
        INSERT INTO sales (product_id, quantity, sale_date)
        VALUES (?, ?, ?)
    """, (
        product_id,
        sale_quantity,
        data.get("sale_date", datetime.today().strftime("%Y-%m-%d"))
    ))

    conn.commit()
    conn.close()

    return jsonify({
        "message": "Sale recorded and stock updated successfully"
    }), 201


# -----------------------------------
# GET SALES HISTORY
# -----------------------------------
@app.route("/api/sales", methods=["GET"])
def get_sales():
    conn = get_db_connection()
    sales = conn.execute("""
        SELECT sales.id, products.name, sales.quantity, sales.sale_date 
        FROM sales 
        JOIN products ON sales.product_id = products.id
        ORDER BY sales.id DESC
    """).fetchall()
    conn.close()

# -----------------------------------
# RECORD SALE & UPDATE STOCK
# -----------------------------------
@app.route("/api/sales", methods=["POST"])
def record_sale():
    data = request.get_json()

    if not data or "product_id" not in data or "quantity" not in data:
        return jsonify({
            "error": "product_id and quantity are required"
        }), 400

    product_id = data["product_id"]
    sale_quantity = data["quantity"]

    conn = get_db_connection()

    product = conn.execute(
        "SELECT * FROM products WHERE id = ?",
        (product_id,)
    ).fetchone()

    if not product:
        conn.close()
        return jsonify({"error": "Product not found"}), 404

    if product["quantity"] < sale_quantity:
        conn.close()
        return jsonify({"error": "Insufficient stock"}), 400

    # Reduce product stock
    conn.execute("""
        UPDATE products
        SET quantity = quantity - ?
        WHERE id = ?
    """, (sale_quantity, product_id))

    # Record sales entry
    conn.execute("""
        INSERT INTO sales (product_id, quantity, sale_date)
        VALUES (?, ?, ?)
    """, (
        product_id,
        sale_quantity,
        data.get("sale_date", datetime.today().strftime("%Y-%m-%d"))
    ))

    conn.commit()
    conn.close()

    return jsonify({
        "message": "Sale recorded and stock updated successfully"
    }), 201


# -----------------------------------
# GET SALES HISTORY
# -----------------------------------
@app.route("/api/sales", methods=["GET"])
def get_sales():
    conn = get_db_connection()
    sales = conn.execute("""
        SELECT sales.id, products.name, sales.quantity, sales.sale_date 
        FROM sales 
        JOIN products ON sales.product_id = products.id
        ORDER BY sales.id DESC
    """).fetchall()
    conn.close()

    return jsonify([dict(sale) for sale in sales])
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
    
