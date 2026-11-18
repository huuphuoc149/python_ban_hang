from flask import Blueprint, render_template
from db import get_connection

index_bp = Blueprint("index", __name__)


@index_bp.route("/")
def index():
    # Kết nối database
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM product ")

    products = cur.fetchall()

    cur.close()
    conn.close()
    return render_template("index.html", products=products)
