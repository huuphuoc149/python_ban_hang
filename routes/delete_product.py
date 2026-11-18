from flask import Blueprint, redirect, session
from db import get_connection

delete_product_bp = Blueprint("delete_product", __name__)


@delete_product_bp.route("/delete_product/<id>", methods=["POST"])
def delete_product(id):
    # Chặn truy cập nếu chưa LOGIN
    if not session.get("user_id"):
        return redirect("/login")

    # Kết nối database
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM product WHERE id = %s AND id_user =%s", (id, session["user_id"])
    )

    conn.commit()

    cur.close()
    conn.close()

    return redirect("/my_product")
