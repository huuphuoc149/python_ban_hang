from flask import Blueprint, render_template, request, redirect, session
from db import get_connection

my_product_bp = Blueprint("my_product", __name__)


@my_product_bp.route("/my_product")
def product():
    if not session.get("user_id"):
        return redirect("/login")

    # Kết nối database
    conn = get_connection()
    cur = conn.cursor()

    # Lấy all sản phẩm
    cur.execute("SELECT * FROM product WHERE id_user = %s", (session["user_id"],))

    products = cur.fetchall()

    cur.close()
    conn.close()

    return render_template("my_product.html", products=products)
