from flask import Blueprint, render_template, request, redirect, session
from db import get_connection
from werkzeug.security import generate_password_hash, check_password_hash

account_bp = Blueprint("account", __name__)


@account_bp.route("/account", methods=["GET", "POST"])
def account():
    if not session.get("user_id"):
        return redirect("/login")
    errors = {}  # Chứa lỗi

    # Nếu user bấm submit
    if request.method == "POST":
        # Lấy data từ form
        # strip(): bỏ khoảng trắng 2 đầu, chỉ gõ dấu cách cũng tính là trống
        name = request.form["name"].strip()
        email = request.form["email"].strip()
        # không strip: dấu cách có thể là 1 phần mật khẩu
        password = request.form["password"]

        if not name:
            errors["name"] = "Vui lòng nhập tên"
        if not email:
            errors["email"] = "Vui lòng nhập Email"

        if not errors:
            conn = get_connection()
            cur = conn.cursor()

            # Nếu có nhập password -> đổi mk (phải mã hóa nếu kh LOGIN sẽ lỗi)
            if password:
                hashed_password = generate_password_hash(password)
                cur.execute(
                    "UPDATE `user` SET name = %s, email = %s, password = %s WHERE id = %s",
                    (name, email, hashed_password, session["user_id"]),
                )
            # Để trống, mật khẩu giữ nguyên chỉ đổi name & email
            else:
                cur.execute(
                    "UPDATE `user` SET name = %s, email =%s WHERE id =%s",
                    (name, email, session["user_id"]),
                )

            # Phải commit nếu kh thì dữ liệu kh vào bảng
            conn.commit()

            cur.close()
            conn.close()

            return redirect("/account")

    # Hiển thị thông tin user khi LOGIN
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM `user` WHERE id = %s", (session["user_id"],))

    user = cur.fetchone()

    cur.close()
    conn.close()
    return render_template("account.html", user=user, errors=errors)
